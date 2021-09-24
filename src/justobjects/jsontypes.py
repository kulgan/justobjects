import collections
from typing import Any, Dict, Iterable, List, Mapping, Optional, Type

import attr

from justobjects import typings

SchemaDataType = typings.Literal[
    "null", "boolean", "object", "array", "number", "integer", "string"
]


def camel_case(snake_case: str) -> str:
    """Converts snake case strings to camel case
    Args:
        snake_case (str): raw snake case string, eg `sample_text`
    Returns:
        str: camel cased string
    """
    cpnts = snake_case.split("_")
    return cpnts[0] + "".join(x.title() for x in cpnts[1:])


class JustSchema:
    def json_schema(self) -> Dict[str, Any]:
        return parse_dict(self.__dict__)


def parse_dict(val: Mapping[str, Any]) -> Dict[str, Any]:
    parsed = {}
    for k, v in val.items():
        if k.startswith("__"):
            # skip private properties
            continue
        # skip None values
        if v is None:
            continue
        # map ref
        if k == "ref":
            k = "$ref"
        k = camel_case(k)
        dict_val = value_to_dict(v)
        if dict_val or isinstance(dict_val, bool):
            parsed[k] = dict_val
    return parsed


def value_to_dict(val: Any) -> Any:
    if isinstance(val, JustSchema):
        return val.json_schema()
    if isinstance(val, (list, set, tuple)):
        return [value_to_dict(v) for v in val]
    if isinstance(val, collections.Mapping):
        return parse_dict(val)
    if hasattr(val, "__dict__"):
        return parse_dict(val.__dict__)

    return val


@attr.s(auto_attribs=True)
class RefType(JustSchema):
    ref: str
    description: Optional[str] = None


@attr.s(auto_attribs=True)
class BasicType(JustSchema):
    type: SchemaDataType
    description: Optional[str] = None


@attr.s(auto_attribs=True)
class BooleanType(BasicType):
    type: SchemaDataType = attr.ib(default="boolean", init=False)
    default: Optional[bool] = None


@attr.s(auto_attribs=True)
class NumericType(BasicType):
    type: SchemaDataType = attr.ib(default="number", init=False)
    default: Optional[int] = None
    enum: List[int] = attr.ib(factory=list)
    maximum: Optional[int] = None
    minimum: Optional[int] = None
    multiple_of: Optional[int] = None
    exclusive_maximum: Optional[int] = None
    exclusive_minimum: Optional[int] = None


@attr.s(auto_attribs=True)
class IntegerType(NumericType):
    type: SchemaDataType = attr.ib(default="integer", init=False)


@attr.s(auto_attribs=True)
class StringType(BasicType):
    type: SchemaDataType = attr.ib(default="string", init=False)
    default: Optional[str] = None
    enum: Iterable[str] = attr.ib(factory=list)
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    pattern: Optional[str] = None


@attr.s(auto_attribs=True)
class ObjectType(BasicType):
    type: SchemaDataType = attr.ib(default="object", init=False)
    additional_properties: bool = False
    required: List[str] = attr.ib(factory=list)
    definitions: Dict[str, BasicType] = attr.ib(factory=dict)
    properties: Dict[str, JustSchema] = attr.ib(factory=dict)

    def add_required(self, field: str) -> None:
        if field in self.required:
            return
        self.required.append(field)


def get_type(cls: Optional[Type] = None) -> BasicType:
    if cls in (str, StringType):
        return StringType()
    if cls in (float, NumericType):
        return NumericType()
    if cls in (int, IntegerType):
        return IntegerType()
    raise ValueError(f"Unknown type {cls} specified")
