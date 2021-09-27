import collections
from typing import Any, Dict, Iterable, List, Mapping, Optional

import attr

from justobjects import typings

SchemaDataType = typings.Literal[
    "null", "array", "boolean", "object", "array", "number", "integer", "string"
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


def validate_multiple_of(instance: Any, attribute: attr.Attribute, value: int) -> None:
    if value and value < 1:
        raise ValueError("multipleOf must be set to a positive number")


@attr.s(auto_attribs=True)
class NumericType(BasicType):
    """The number type is used for any numeric type, either integers or floating point numbers."""

    type: SchemaDataType = attr.ib(default="number", init=False)
    default: Optional[float] = None
    enum: List[int] = attr.ib(factory=list)
    maximum: Optional[float] = None
    minimum: Optional[float] = None
    multipleOf: Optional[int] = attr.ib(default=None, validator=validate_multiple_of)
    exclusiveMaximum: Optional[float] = None
    exclusiveMinimum: Optional[float] = None


@attr.s(auto_attribs=True)
class IntegerType(NumericType):
    """The integer type is used for integral numbers"""

    type: SchemaDataType = attr.ib(default="integer", init=False)
    maximum: Optional[int] = None
    minimum: Optional[int] = None
    exclusiveMaximum: Optional[int] = None
    exclusiveMinimum: Optional[int] = None


@attr.s(auto_attribs=True)
class StringType(BasicType):
    type: SchemaDataType = attr.ib(default="string", init=False)
    default: Optional[str] = None
    enum: Iterable[str] = attr.ib(factory=list)
    maxLength: Optional[int] = None
    minLength: Optional[int] = None
    pattern: Optional[str] = None


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


@attr.s(auto_attribs=True)
class ArrayType(BasicType):
    type: SchemaDataType = attr.ib(default="array", init=False)
    items: JustSchema = attr.ib(default=None)
    minItems: Optional[int] = None
    maxItems: Optional[int] = None


@attr.s(auto_attribs=True)
class AnyOfType(JustSchema):
    anyOf: Iterable[JustSchema] = attr.ib(factory=list)


@attr.s(auto_attribs=True)
class OneOfType(JustSchema):
    oneOf: Iterable[JustSchema] = attr.ib(factory=list)


@attr.s(auto_attribs=True)
class AllOfType(JustSchema):
    allOf: Iterable[JustSchema] = attr.ib(factory=list)
