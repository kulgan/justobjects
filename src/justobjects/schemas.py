from collections import abc as ca
from typing import (
    Any,
    AnyStr,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Set,
    Type,
    Union,
    cast,
)

import attr
from jsonschema import Draft7Validator

from justobjects.jsontypes import (
    ArrayType,
    BasicType,
    BooleanType,
    IntegerType,
    JustSchema,
    NumericType,
    ObjectType,
    RefType,
    StringType,
    as_dict,
)
from justobjects.typings import is_generic_type

BOOLS = (bool, BooleanType)
INTEGERS = (int, IntegerType)
ITERABLES = (list, set)
NUMERICS = (float, NumericType)
OBJECTS = (object, dict)
TYPED_ITERABLES_ORIGINS = (Iterable, ca.Iterable, list, List, set, Set)
TYPED_OBJECTS_ORIGINS = (dict, Dict, Mapping)
STRINGS = (str, AnyStr, StringType)
JUST_OBJECTS: Dict[str, ObjectType] = {}

__all__ = [
    "get",
    "get_type",
    "show",
    "is_valid",
    "is_valid_data",
    "ValidationError",
    "ValidationException",
]


@attr.s(auto_attribs=True)
class SchemaRef(RefType):
    type: str = attr.ib(init=False, default="object")
    title: str = "Draft7 JustObjects schema"
    additionalProperties: bool = False
    definitions: Dict[str, ObjectType] = attr.ib(factory=dict)


@attr.s(frozen=True, auto_attribs=True)
class ValidationError:
    """Data object representation for validation errors

    Attributes:
        element (str): name of the affected column, can be empty
        message (str): associated error message
    """

    element: str
    message: str


class ValidationException(Exception):
    """Custom Exception class for validation errors

    Attributes:
        errors: list of errors encountered during validation
    """

    def __init__(self, errors: List[ValidationError]):
        super(ValidationException, self).__init__("Validation errors occurred")
        self.errors = errors


def add(cls: Any, obj: ObjectType) -> None:
    JUST_OBJECTS[f"{cls.__name__}"] = obj


def get(cls: Union[Type, JustSchema]) -> JustSchema:
    """Retrieves a justschema representation for the class or object instance

    Args:
        cls: a class type which is expected to be a pre-defined data object or an instance of json type
    """
    if isinstance(cls, JustSchema):
        return cls

    cls_name = f"{cls.__name__}"
    if cls_name not in JUST_OBJECTS:
        raise ValueError(f"Unrecognized data object class '{cls_name}'")
    return JUST_OBJECTS[cls_name]


def show(cls: Union[Type, JustSchema]) -> Dict:
    """Converts a data object class type into a valid json schema

    Args:
        cls: data object class type
    Returns:
        a json schema dictionary

    Examples:
        Creating and getting the schema associated with a simple integer type ::

            import justobjects as jo
            s = jo.IntegerType(minimum=3)
            jo.show(s)
            # {'minimum': 3, 'type': 'integer'}
    """
    if isinstance(cls, JustSchema):
        return cls.as_dict()

    ref = cast(RefType, as_ref(cls, get(cls)))
    obj = SchemaRef(
        ref=ref.ref,
        definitions=JUST_OBJECTS,
        title=f"Draft7 JustObjects schema for {cls.__name__}",
    )
    return obj.as_dict()


def parse_errors(validator: Draft7Validator, data: Dict) -> Iterable[ValidationError]:
    errors: List[ValidationError] = []
    for e in validator.iter_errors(data):
        str_path = ".".join([str(entry) for entry in e.path])
        errors.append(ValidationError(str_path, e.message))
    return errors


def is_valid_data(cls: Type, data: Union[Dict, Iterable[Dict]]) -> None:
    """Validates if a data sample is valid for the given data object type

    This is best suited for validating existing json data without having to creating instances of
    the model

    Args:
        cls: data object type with schema defined
        data: dictionary or list of data instances that needs to be validated
    Raises:
        ValidationException
    Examples:
       .. code-block:: python

          import justobjects as jo

          @jo.data()
          class Model:
            a = jo.integer(minimum=18)
            b = jo.boolean()

          is_valid_data(Model, {"a":4, "b":True})
    """
    schema = show(cls)
    validator = Draft7Validator(schema=schema)

    errors: List[ValidationError] = []
    if isinstance(data, dict):
        errors += parse_errors(validator, data)
    else:
        for entry in data:
            errors += parse_errors(validator, entry)
    if errors:
        raise ValidationException(errors=errors)


def is_valid(node: Any) -> None:
    """Validates an object instance against its associated json schema

    Args:
        node: a data object instance
    Raises:
        ValidationException: when there errors
    Examples:
        .. code-block:: python

          import justobjects as jo

          @jo.data()
          class Model:
            a = jo.integer(minimum=18)
            b = jo.boolean()

          is_valid(Model(a=4, b=True)
    """
    is_valid_data(node.__class__, as_dict(node))


def get_type(cls: Type) -> JustSchema:
    # generics
    if is_generic_type(cls):
        return get_typed(cls)

    # capture all custom json types
    if issubclass(cls, JustSchema):
        return cls()

    if cls in STRINGS:
        return StringType()
    if cls in NUMERICS:
        return NumericType()
    if cls in INTEGERS:
        return IntegerType()
    if cls in BOOLS:
        return BooleanType()
    if cls in ITERABLES:
        is_set = cls == set
        return ArrayType(items=StringType(), uniqueItems=is_set)
    if cls in OBJECTS:
        return ObjectType(additionalProperties=True)
    return get(cls)


def get_typed(cls: "typing.GenericMeta") -> BasicType:  # type: ignore
    if not is_generic_type(cls):
        raise ValueError()
    if cls.__origin__ in TYPED_ITERABLES_ORIGINS:
        obj_cls = cls.__args__[0]
        is_set = cls == Set
        ref = as_ref(cls, get_type(obj_cls))
        return ArrayType(items=ref, uniqueItems=is_set)
    if cls.__origin__ in TYPED_OBJECTS_ORIGINS:
        _, val_type = cls.__args__
        obj = as_ref(val_type, get_type(val_type))
        return ObjectType(patternProperties={"^.*$": obj}, additionalProperties=True)
    raise ValueError(f"Unknown data type {cls}")


def as_ref(obj_cls: Type, obj: JustSchema, description: Optional[str] = None) -> JustSchema:
    if not isinstance(obj, ObjectType) or is_generic_type(obj_cls):
        return obj
    return RefType(ref=f"#/definitions/{obj_cls.__name__}", description=description)
