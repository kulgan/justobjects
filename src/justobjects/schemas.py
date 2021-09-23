from typing import Any, Dict, Iterable, List, Type, Union

import attr
from jsonschema import Draft7Validator

from justobjects.jsontypes import BasicType, value_to_dict


@attr.s(frozen=True, auto_attribs=True)
class ValidationError:
    element: str
    message: str


class ValidationException(Exception):
    def __init__(self, errors: List[ValidationError]):
        super(ValidationException, self).__init__("Validation errors occurred")
        self.errors = errors


def add(cls: Any, obj: BasicType) -> None:
    JUST_OBJECTS[f"{cls.__module__}.{cls.__name__}"] = obj


def get(cls: Type) -> BasicType:
    obj = JUST_OBJECTS.get(f"{cls.__module__}.{cls.__name__}")
    if not obj:
        raise ValueError("Unknown data object")
    return obj


def show(cls: Type) -> Dict:
    obj = get(cls)
    return obj.json_schema()


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


JUST_OBJECTS: Dict[str, BasicType] = {}
