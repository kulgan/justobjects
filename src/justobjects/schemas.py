from typing import Any, Dict, Type, Union, Iterable

from jsonschema import Draft7Validator

from justobjects.jsontypes import BasicType


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


def parse_errors(validator: Draft7Validator, data: Dict) -> None:
    for e in validator.iter_errors(data):
        str_path = ".".join([str(entry) for entry in e.path])
        print(str_path, e.message)


def validate_raw(cls: Type, data: Union[Dict, Iterable[Dict]]) -> None:
    schema = show(cls)
    validator = Draft7Validator(schema=schema)

    if isinstance(data, dict):
        parse_errors(validator, data)
    else:
        for entry in data:
            parse_errors(validator, entry)


def validate(node: Any) -> None:
    validate_raw(node.__class__, node.__dict__)


JUST_OBJECTS: Dict[str, BasicType] = {}
