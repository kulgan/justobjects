import functools
from typing import Any, Dict, Iterable, List, Type, Union

import attr
from jsonschema import Draft7Validator

from justobjects.jsontypes import (
    BasicType,
    BooleanType,
    IntegerType,
    JustSchema,
    NumericType,
    ObjectType,
    RefType,
    StringType,
    value_to_dict,
)

JUST_OBJECTS: Dict[str, ObjectType] = {}

__all__ = [
    "get",
    "get_type",
    "show",
    "validate",
    "validate_raw",
    "ValidationError",
    "ValidationException",
]


@functools.lru_cache()
def definitions(cls_name: str) -> Dict[str, Dict[str, Any]]:
    defs: Dict[str, Any] = {}
    for label, entry in JUST_OBJECTS.items():
        if label == cls_name:
            continue
        defs[label] = entry.json_schema()
    return defs


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
    JUST_OBJECTS[f"{cls.__module__}.{cls.__name__}"] = obj


def get(cls: Union[Type, JustSchema]) -> JustSchema:
    """Retrieves a justschema representation for the class or object instance

    Args:
        cls: a class type which is expected to be a pre-defined data object or an instance of json type
    """
    if isinstance(cls, JustSchema):
        return cls

    cls_name = f"{cls.__module__}.{cls.__name__}"
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
        return cls.json_schema()

    obj = get(cls)
    cls_name = f"{cls.__module__}.{cls.__name__}"
    raw = obj.json_schema()
    defs = definitions(cls_name)
    if defs:
        raw["definitions"] = defs
    return raw


def parse_errors(validator: Draft7Validator, data: Dict) -> Iterable[ValidationError]:
    errors: List[ValidationError] = []
    for e in validator.iter_errors(data):
        str_path = ".".join([str(entry) for entry in e.path])
        errors.append(ValidationError(str_path, e.message))
    return errors


def validate_raw(cls: Type, data: Union[Dict, Iterable[Dict]]) -> None:
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


def validate(node: Any) -> None:
    validate_raw(node.__class__, value_to_dict(node))


def get_type(cls: Type) -> JustSchema:
    if cls in (str, StringType):
        return StringType()
    if cls in (float, NumericType):
        return NumericType()
    if cls in (int, IntegerType):
        return IntegerType()
    if cls in (bool, BooleanType):
        return BooleanType()
    return get(cls)
