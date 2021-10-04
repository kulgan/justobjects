from collections import abc as ca
from typing import (
    Any,
    AnyStr,
    ByteString,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Text,
    Type,
    Union,
    cast,
)

import attr
from jsonschema import Draft7Validator

from justobjects import typings
from justobjects.jsontypes import (
    AnyOfType,
    ArrayType,
    BasicType,
    BooleanType,
    CompositionType,
    IntegerType,
    JustSchema,
    NotType,
    NumericType,
    ObjectType,
    RefType,
    SchemaType,
    StringType,
    as_dict,
)

BOOLS = (bool, BooleanType)
INTEGERS = (int, IntegerType)
ITERABLES = (list, set)
NUMERICS = (float, NumericType)
OBJECTS = (object, dict)
TYPED_ITERABLES_ORIGINS = (Sequence, Iterable, ca.Sequence, ca.Iterable, list, List, set, Set)
TYPED_OBJECTS_ORIGINS = (dict, Dict, Mapping)
STRINGS = (str, AnyStr, StringType)

TYPE_MAP: Dict[Type, Type[JustSchema]] = {
    bool: BooleanType,
    dict: ObjectType,
    int: IntegerType,
    float: NumericType,
    list: ArrayType,
    object: ObjectType,
    set: ArrayType,
    str: StringType,
    AnyStr: StringType,
    ByteString: StringType,
    Text: StringType,
}

JUST_OBJECTS: Dict[str, SchemaType] = {}

JO_TYPE = "__jo__type__"
JO_SCHEMA = "__jo__"
JO_REQUIRED = "__jo__required__"
JO_OBJECT_DESC = "__jo__object_desc__"

__all__ = [
    "get",
    "get_type",
    "show",
    "is_valid",
    "is_valid_data",
    "ValidationError",
    "ValidationException",
]


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


def add(cls: typings.AttrClass, obj: SchemaType) -> None:
    JUST_OBJECTS[f"{cls.__name__}"] = obj


def _resolve_ref(ref: RefType, sc: SchemaType):
    schema = get(ref)
    sc.definitions.update(schema.definitions)
    sc.definitions[ref.ref_name()] = schema.as_object()


def extract(cls: typings.AttrClass) -> None:
    """Extract schema from a data object class

    Attributes:
        cls: Data object class
    """
    sc = SchemaType(
        title=f"Draft7 JustObjects schema for data object '{cls.__module__}.{cls.__name__}'",
        additionalProperties=False,
        description=cls.__doc__,
    )
    for prop in cls.__attrs_attrs__:
        prop_type = prop.metadata.get(JO_TYPE, prop.type)

        if prop.metadata.get(JO_REQUIRED, False):
            sc.add_required(prop.name)
        prop_desc: str = prop.metadata.get(JO_OBJECT_DESC)
        prop_schema = prop.metadata.get(JO_SCHEMA) or get_type(prop_type)

        # retrieve referenced entries
        if isinstance(prop_schema, RefType):
            _resolve_ref(prop_schema, sc)

        # negation type
        if isinstance(prop_schema, NotType) and isinstance(prop_schema.mustNot, RefType):
            _resolve_ref(prop_schema.mustNot, sc)

        # array types
        if isinstance(prop_schema, ArrayType) and isinstance(prop_schema.items, RefType):
            _resolve_ref(prop_schema.items, sc)

        # composition types
        if isinstance(prop_schema, CompositionType):
            for _type in prop_schema.get_types():
                if not isinstance(_type, RefType):
                    continue
                _resolve_ref(_type, sc)

        # transform objects to reference types
        if is_referencable(prop_type) and isinstance(prop_schema, SchemaType):
            sc.definitions[f"{prop_type.__name__}"] = prop_schema.as_object()
            sc.definitions.update(prop_schema.definitions)
            sc.properties[prop.name] = as_ref(prop_type, prop_schema, prop_desc)
            continue

        sc.properties[prop.name] = prop_schema

    def __jo__(cls) -> Dict[str, Any]:
        return sc.as_dict()

    setattr(cls, "__jo__", classmethod(__jo__))
    add(cls, sc)


def get(cls: Union[Type, RefType, BasicType]) -> Union[JustSchema, SchemaType]:
    """Retrieves a justschema representation for the class or object instance

    Args:
        cls: a class type which is expected to be a pre-defined data object or an instance of json type
    """
    if isinstance(cls, BasicType):
        return cls

    class_name = None
    if isinstance(cls, RefType):
        class_name = cls.ref_name()

    cls_name = class_name or f"{cls.__name__}"
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

    ref = cast(typings.AttrClass, cls)
    return ref.__jo__()


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
    if typings.is_generic_type(cls):
        return get_typed(cls)

    if cls in TYPE_MAP:
        sch = TYPE_MAP[cls]
        return sch()

    # capture all custom json types
    if issubclass(cls, JustSchema):
        return cls()

    return get(cls)


def get_typed(cls: "typing.GenericMeta") -> JustSchema:  # type: ignore
    if not typings.is_generic_type(cls):
        raise ValueError()

    if cls.__origin__ in TYPED_ITERABLES_ORIGINS:
        obj_cls = cls.__args__[0]
        is_set = cls in [Set, set]
        ref = as_ref(obj_cls, get_type(obj_cls))
        return ArrayType(items=ref, minItems=1, uniqueItems=is_set)

    if cls.__origin__ == Union:
        has_none_type = False
        types: List[JustSchema] = []
        for arg in cls.__args__:
            if arg.__name__ == "NoneType":
                has_none_type = True
                continue
            types.append(as_ref(arg, get_type(arg)))
        if len(types) > 1:
            return AnyOfType(anyOf=types)
        if len(types) == 1:
            return types[0]
    if cls.__origin__ in TYPED_OBJECTS_ORIGINS:
        _, val_type = cls.__args__

        obj_schema = SchemaType()
        val_schema = get_type(val_type)
        if is_referencable(val_type) and isinstance(val_schema, SchemaType):
            obj_schema.definitions.update(val_schema.definitions)
            obj_schema.definitions[f"{val_type.__name__}"] = val_schema.as_object()
        obj_schema.patternProperties["^.*$"] = as_ref(val_type, get_type(val_type))
        return obj_schema
    raise ValueError(f"Unknown data type {cls}")


def as_ref(obj_cls: Type, obj: JustSchema, description: Optional[str] = None) -> JustSchema:
    if not is_referencable(obj_cls):
        return obj
    return RefType(ref=f"#/definitions/{obj_cls.__name__}", description=description)


def is_referencable(cls: Type) -> bool:
    if typings.is_generic_type(cls):
        return False
    if isinstance(cls, (set, list)):
        return False
    return cls.__name__ in JUST_OBJECTS


def resolve_dict(cls: Type) -> SchemaType:
    _, val_type = cls.__args__

    obj_type = get_type(val_type)
    obj = as_ref(val_type, get_type(val_type))
    return SchemaType(patternProperties={"^.*$": obj}, additionalProperties=True)
