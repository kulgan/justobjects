import collections
from typing import Any, Dict, Iterable, List, Mapping, Optional, Type

import attr

from justobjects import typings

SchemaType = typings.Literal["null", "boolean", "object", "array", "number", "integer", "string"]


def camel_case(snake_case: str) -> str:
    """Converts snake case strings to camel case
    Args:
        snake_case (str): raw snake case string, eg `sample_text`
    Returns:
        str: camel cased string
    """
    cpnts = snake_case.split("_")
    return cpnts[0] + "".join(x.title() for x in cpnts[1:])


class SchemaMixin:
    def json_schema(self) -> Dict[str, Any]:
        return self.parse(self.__dict__)

    def parse(self, val: Mapping[str, Any]) -> Dict[str, Any]:
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
            dict_val = self._to_dict(v)
            if dict_val:
                parsed[k] = dict_val
        return parsed

    def _to_dict(self, val: Any) -> Any:
        if isinstance(val, SchemaMixin):
            return val.json_schema()
        if isinstance(val, (list, set, tuple)):
            return [self._to_dict(v) for v in val]
        if isinstance(val, collections.Mapping):
            return self.parse(val)
        if hasattr(val, "__dict__"):
            return self.parse(val.__dict__)

        return val


@attr.s(auto_attribs=True)
class BasicType(SchemaMixin):
    type: SchemaType
    description: Optional[str] = None


@attr.s(auto_attribs=True)
class NumericType(BasicType):
    type: SchemaType = "number"
    default: Optional[int] = None
    enum: List[int] = attr.ib(factory=list)
    maximum: Optional[int] = None
    minimum: Optional[int] = None
    multiple_of: Optional[int] = None
    exclusive_maximum: Optional[int] = None
    exclusive_minimum: Optional[int] = None


@attr.s(auto_attribs=True)
class StringType(BasicType):
    type: SchemaType = "string"
    default: Optional[str] = None
    enum: Iterable[str] = attr.ib(factory=list)
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    pattern: Optional[str] = None


@attr.s(auto_attribs=True)
class ObjectType(BasicType):
    type: SchemaType = "object"
    additional_properties: bool = False
    required: List[str] = attr.ib(factory=list)
    properties: Dict[str, BasicType] = attr.ib(factory=dict)

    def add_required(self, field: str) -> None:
        if field in self.required:
            return
        self.required.append(field)


def get_type(cls: Optional[Type] = None) -> BasicType:
    if cls == str:
        return StringType()
    if cls == int:
        return NumericType()
    raise ValueError(f"Unknown type {cls} specified")
