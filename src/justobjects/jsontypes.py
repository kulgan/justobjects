import collections
from typing import Any, Dict, Iterable, List, Mapping, Optional

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


def validate_positive(instance: Any, attribute: attr.Attribute, value: int) -> None:
    if value and value < 1:
        raise ValueError("multipleOf must be set to a positive number")


@attr.s(auto_attribs=True)
class NumericType(BasicType):
    """The number type is used for any numeric type, either integers or floating point numbers."""

    type: SchemaDataType = attr.ib(default="number", init=False)
    default: Optional[float] = None
    enum: List[int] = attr.ib(factory=list)
    maximum: Optional[int] = None
    minimum: Optional[int] = None
    multipleOf: Optional[int] = attr.ib(default=None, validator=validate_positive)
    exclusiveMaximum: Optional[int] = None
    exclusiveMinimum: Optional[int] = None


@attr.s(auto_attribs=True)
class IntegerType(NumericType):
    """The integer type is used for integral numbers"""

    type: SchemaDataType = attr.ib(default="integer", init=False)


@attr.s(auto_attribs=True)
class StringType(BasicType):
    """The string type is used for strings of text."""

    type: SchemaDataType = attr.ib(default="string", init=False)
    default: Optional[str] = None
    enum: List[str] = attr.ib(factory=list)
    maxLength: Optional[int] = attr.ib(default=None, validator=validate_positive)
    minLength: Optional[int] = attr.ib(default=None, validator=validate_positive)
    pattern: Optional[str] = None
    format: Optional[str] = None


@attr.s(auto_attribs=True)
class DateTimeType(StringType):
    format: str = attr.ib(init=False, default="data-time")


@attr.s(auto_attribs=True)
class TimeType(StringType):
    format: str = attr.ib(init=False, default="time")


@attr.s(auto_attribs=True)
class DateType(StringType):
    format: str = attr.ib(init=False, default="data")


@attr.s(auto_attribs=True)
class DurationType(StringType):
    format: str = attr.ib(init=False, default="duration")


@attr.s(auto_attribs=True)
class EmailType(StringType):
    format: str = attr.ib(init=False, default="email")


@attr.s(auto_attribs=True)
class HostnameType(StringType):
    format: str = attr.ib(init=False, default="hostname")


@attr.s(auto_attribs=True)
class Ipv4Type(StringType):
    format: str = attr.ib(init=False, default="ipv4")


@attr.s(auto_attribs=True)
class Ipv6Type(StringType):
    format: str = attr.ib(init=False, default="ipv6")


@attr.s(auto_attribs=True)
class UriType(StringType):
    format: str = attr.ib(init=False, default="uri")


@attr.s(auto_attribs=True)
class UuidType(StringType):
    format: str = attr.ib(init=False, default="uuid")


@attr.s(auto_attribs=True)
class ObjectType(BasicType):
    type: SchemaDataType = attr.ib(default="object", init=False)
    additionalProperties: bool = False
    required: List[str] = attr.ib(factory=list)
    properties: Dict[str, JustSchema] = attr.ib(factory=dict)

    def add_required(self, field: str) -> None:
        if field in self.required:
            return
        self.required.append(field)
