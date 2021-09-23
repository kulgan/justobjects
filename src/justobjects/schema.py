from typing import Any, Dict, Type

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


def validate(node: Any) -> None:
    schema = show(node.__class__)
    val = Draft7Validator(schema=schema)
    for e in val.iter_errors(node.__dict__):
        str_path = ".".join([str(entry) for entry in e.path])
        print(str_path, e.message)


JUST_OBJECTS: Dict[str, BasicType] = {}
