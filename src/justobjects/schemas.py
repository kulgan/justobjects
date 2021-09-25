import functools
from typing import Any, Dict, GenericMeta, Iterable, List, Type, Union  # type: ignore

import attr
from jsonschema import Draft7Validator

from justobjects.jsontypes import (
    ArrayType,
    BasicType,
    BooleanType,
    IntegerType,
    NumericType,
    ObjectType,
    RefType,
    StringType,
    value_to_dict,
)

JUST_OBJECTS: Dict[str, ObjectType] = {}


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
    element: str
    message: str


class ValidationException(Exception):
    def __init__(self, errors: List[ValidationError]):
        super(ValidationException, self).__init__("Validation errors occurred")
        self.errors = errors


def add(cls: Any, obj: ObjectType) -> None:
    JUST_OBJECTS[f"{cls.__module__}.{cls.__name__}"] = obj


def get(cls: Type) -> ObjectType:
    cls_name = f"{cls.__module__}.{cls.__name__}"
    if cls_name not in JUST_OBJECTS:
        raise ValueError("Unknown data object")
    return JUST_OBJECTS[cls_name]


def show(cls: Type) -> Dict:
    obj = get(cls)
    raw = obj.json_schema()
    cls_name = f"{cls.__module__}.{cls.__name__}"
    raw["definitions"] = definitions(cls_name)
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


def get_type(cls: Type) -> BasicType:
    if isinstance(cls, GenericMeta):
        return get_typed(cls)
    if cls in (str, StringType):
        return StringType()
    if cls in (float, NumericType):
        return NumericType()
    if cls in (int, IntegerType):
        return IntegerType()
    if cls in (bool, BooleanType):
        return BooleanType()
    return get(cls)


def get_typed(cls: GenericMeta) -> BasicType:
    if cls.__name__ in ["Iterable", "List", "Set"]:
        obj_cls = cls.__args__[0]  # type: ignore
        ref = None
        obj = get_type(obj_cls)
        if obj.type == "object":
            ref = RefType(ref=f"#/definitions/{obj_cls.__module__}.{obj_cls.__name__}")
        return ArrayType(items=ref or obj)
    if cls.__name__ in ["Dict", "Mapping"]:
        return ObjectType(additionalProperties=True)
    raise ValueError(f"Unknown data type {cls}")
