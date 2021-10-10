from collections import abc as ca
from collections import defaultdict
from types import MethodType
from typing import (
    Any,
    AnyStr,
    ByteString,
    Container,
    DefaultDict,
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
TYPED_ITERABLES_ORIGINS = (
    Sequence,
    Iterable,
    ca.Sequence,
    ca.Iterable,
    list,
    List,
    set,
    Set,
    ca.Set,
)
TYPED_OBJECTS_ORIGINS = (
    ca.Mapping,
    ca.Container,
    defaultdict,
    dict,
    Container,
    DefaultDict,
    Dict,
    Mapping,
)
STRINGS = (str, AnyStr, StringType)

TYPE_MAP: Dict[Any, Type[JustSchema]] = {
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

__all__ = [
    "get_schema",
    "transform",
    "show_schema",
    "validate",
    "validate_raw",
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
        super(ValidationException, self).__init__(f"Data validation error: {errors}")
        self.errors = errors


def add_schema(cls: typings.AttrClass, obj: SchemaType) -> None:
    """Adds the schema of a data object to collection of schemas

    Raises:
        Exception if cls is not a class type with the __name__ attribute
    """

    JUST_OBJECTS[f"{cls.__name__}"] = obj


def _resolve_ref(ref: RefType, sc: SchemaType) -> None:
    schema = cast(SchemaType, get_schema(ref))
    sc.definitions.update(schema.definitions)
    sc.definitions[ref.ref_name()] = schema.as_object()


def _resolve_compositions(comp: CompositionType, sc: SchemaType) -> None:
    for _type in comp.get_enclosed_types():
        if not isinstance(_type, RefType):
            continue
        _resolve_ref(_type, sc)


def transform_properties(cls: typings.AttrClass) -> None:
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

        if prop.metadata.get(JO_REQUIRED, False) or prop.default == attr.NOTHING:
            sc.add_required(prop.name)
        prop_schema = prop.metadata.get(JO_SCHEMA, transform(prop_type))

        # negation, referenced and array type
        if isinstance(prop_schema, (ArrayType, NotType, RefType)) and isinstance(
            prop_schema.get_enclosed_type(), RefType
        ):
            enclosed = cast(RefType, prop_schema.get_enclosed_type())
            _resolve_ref(enclosed, sc)
            sc.properties[prop.name] = prop_schema
            continue

        # composition types
        if isinstance(prop_schema, CompositionType):
            _resolve_compositions(prop_schema, sc)
            sc.properties[prop.name] = prop_schema
            continue

        if hasattr(prop_type, "__jo__") and not isinstance(prop_schema, RefType):
            schema = cast(SchemaType, prop_schema)
            sc.definitions.update(schema.definitions)
            sc.definitions[prop_type.__name__] = schema.as_object()
            sc.properties[prop.name] = as_ref(prop_type, schema)
            continue

        # transform objects to reference types
        if typings.is_typed_container(prop_type) and isinstance(prop_schema, SchemaType):
            sc.definitions.update(prop_schema.definitions)
            sc.properties[prop.name] = prop_schema.as_object()
            continue

        sc.properties[prop.name] = prop_schema

    def __jo__(cls: Type[JustSchema]) -> Dict[str, Any]:
        return sc.as_dict()

    setattr(cls, "__jo__", classmethod(__jo__))
    add_schema(cls, sc)


def get_schema(cls: Union[Type[JustSchema], RefType, BasicType]) -> Union[JustSchema, SchemaType]:
    """Retrieves a justschema representation for the class or object instance

    Args:
        cls: a class type which is expected to be a pre-defined data object or an instance of json type
    """
    if isinstance(cls, BasicType):
        return cls

    if isinstance(cls, RefType):
        class_name = cls.ref_name()
    else:
        class_name = cls.__name__

    if not class_name or class_name not in JUST_OBJECTS:
        raise ValueError(f"Unrecognized data object class '{class_name}'")
    return JUST_OBJECTS[class_name]


def show_schema(model: Any) -> Dict:
    """Converts a data object class type into a valid json schema

    Args:
        model: data object class type or instance
    Returns:
        a json schema dictionary

    Examples:
        Creating and getting the schema associated with a simple integer type ::

            import justobjects as jo
            s = jo.IntegerType(minimum=3)
            jo.show_schema(s)
            # {'minimum': 3, 'type': 'integer'}
    """
    if isinstance(model, JustSchema):
        return model.as_dict()

    if hasattr(model, "__jo__"):
        return model.__jo__()

    if model in TYPE_MAP:
        return TYPE_MAP[model]().as_dict()

    # generics
    if typings.is_typed_container(model):
        return transform_typed_container(cast(typings.GenericMeta, model)).as_dict()

    raise ValueError(f"Unrecognized data object {model}")


def parse_errors(validator: Draft7Validator, data: Dict) -> Iterable[ValidationError]:
    errors: List[ValidationError] = []
    for e in validator.iter_errors(data):
        str_path = ".".join([str(entry) for entry in e.path])
        errors.append(ValidationError(str_path, e.message))
    return errors


def validate_raw(cls: Type[JustSchema], data: Union[Dict, Iterable[Dict]]) -> None:
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
    schema = show_schema(cls)
    validator = Draft7Validator(schema=schema)

    errors: List[ValidationError] = []
    if isinstance(data, dict):
        errors += parse_errors(validator, data)
    else:
        for entry in data:
            errors += parse_errors(validator, entry)
    if errors:
        raise ValidationException(errors=errors)


def validate(node: Any) -> None:
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
    validate_raw(node.__class__, as_dict(node))


def transform(cls: Type) -> JustSchema:
    """ "Attempts to transform any object class type into an appropriate schema type"""

    # generics
    if typings.is_typed_container(cls):
        return transform_typed_container(cast(typings.GenericMeta, cls))

    if cls in TYPE_MAP:
        sch = TYPE_MAP[cls]
        return sch()

    # capture all custom json types
    if issubclass(cls, JustSchema):
        return cls()

    return get_schema(cast(Type[JustSchema], cls))


def transform_typed_container(cls: typings.GenericMeta) -> JustSchema:  # type: ignore
    if not typings.is_typed_container(cls):
        raise ValueError()

    if cls.__origin__ in TYPED_ITERABLES_ORIGINS:
        return _resolve_typed_arrays(cls)

    if cls.__origin__ == Union:
        return _resolve_unions(cls)

    if cls.__origin__ in TYPED_OBJECTS_ORIGINS:
        _, val_type = cls.__args__

        obj_schema = SchemaType(title="")
        val_schema = transform(val_type)
        if is_referencable(val_type) and isinstance(val_schema, SchemaType):
            obj_schema.definitions.update(val_schema.definitions)
            obj_schema.definitions[f"{val_type.__name__}"] = val_schema.as_object()
        obj_schema.patternProperties["^.*$"] = as_ref(val_type, val_schema)
        return obj_schema
    raise ValueError(f"Unknown data type '{cls}'")


def as_ref(obj_cls: Type, obj: JustSchema, description: Optional[str] = None) -> JustSchema:
    if not is_referencable(obj_cls):
        return obj
    return RefType(ref=f"#/definitions/{obj_cls.__name__}", description=description)


def is_referencable(cls: Type) -> bool:
    if typings.is_typed_container(cls):
        return False
    if isinstance(cls, (set, list)):
        return False
    return cls.__name__ in JUST_OBJECTS


def _resolve_typed_arrays(cls: typings.GenericMeta) -> ArrayType:
    """Converts typed list based classes into ArrayType

    Examples:
        @jo.data(typed=True)
        class People:
            names: Set[str]
    """

    obj_cls = cls.__args__[0]
    is_set = cls.__origin__ in [ca.Set, Set, set]
    ref = as_ref(obj_cls, transform(obj_cls))
    return ArrayType(items=ref, minItems=1, uniqueItems=is_set)


def _resolve_unions(cls: typings.GenericMeta) -> Union[CompositionType, JustSchema]:
    types: List[JustSchema] = []
    for arg in cls.__args__:
        if arg.__name__ == "NoneType":
            continue

        types.append(as_ref(arg, transform(arg)))
    if len(types) > 1:
        return AnyOfType(anyOf=types)
    return types[0]
