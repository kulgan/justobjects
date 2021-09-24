from typing import Any, Dict, Iterable, List, Type, Union

import attr
from jsonschema import Draft7Validator

from justobjects.jsontypes import (
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
    entries = [obj]
    definitions = {}

    while entries:
        current = entries.pop()
        for v in current.properties.values():
            if not isinstance(v, RefType):
                continue

            ref = v.ref.split("/")[-1]
            print(ref)
            if ref in definitions:
                continue

            psc = JUST_OBJECTS[ref]
            entries.append(psc)
            definitions[ref] = psc.json_schema()
    raw = obj.json_schema()
    raw["definitions"] = definitions
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
    if cls in (str, StringType):
        return StringType()
    if cls in (float, NumericType):
        return NumericType()
    if cls in (int, IntegerType):
        return IntegerType()
    if cls in (bool, BooleanType):
        return BooleanType()
    return get(cls)
