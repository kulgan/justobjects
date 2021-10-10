import collections
from typing import Any, Dict, Iterable, List, Mapping, Optional, Type

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
    """A marker denoting a json type"""

    def get_enclosed_type(self) -> "JustSchema":
        ...

    def as_dict(self) -> Dict[str, Any]:
        """Converts object instances to json schema"""

        return parse_dict(self.__dict__)


class PropertyDict(Dict[str, JustSchema]):
    def __init__(self) -> None:
        super(PropertyDict, self).__init__()
        self["id"] = StringType(default=None)
        self["schema"] = StringType(default="http://json-schema.org/draft-07/schema#")


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
        if k in ["ref", "schema", "id"]:
            k = f"${k}"
        dict_val = as_dict(v)
        if dict_val or isinstance(dict_val, bool):
            parsed[k] = dict_val
    return parsed


def as_dict(val: Any) -> Any:
    """Attempts to recursively convert any object to a dictionary"""

    if isinstance(val, JustSchema):
        return val.as_dict()
    if isinstance(val, (list, set, tuple)):
        return [as_dict(v) for v in val]
    if isinstance(val, collections.Mapping):
        return parse_dict(val)
    if hasattr(val, "__dict__"):
        return parse_dict(val.__dict__)

    return val


@attr.s(auto_attribs=True)
class RefType(JustSchema):
    ref: str
    description: Optional[str] = None

    def ref_name(self) -> str:
        return self.ref.split("/")[-1]

    def get_enclosed_type(self) -> JustSchema:
        return self


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
        raise ValueError(f"{attribute.name} on {instance} must be set to a positive number")


@attr.s(auto_attribs=True)
class NumericType(BasicType):
    """The number type is used for any numeric type, either integers or floating point numbers."""

    type: SchemaDataType = attr.ib(default="number", init=False)
    default: Optional[float] = None
    enum: List[int] = attr.ib(factory=list)
    maximum: Optional[float] = None
    minimum: Optional[float] = None
    multipleOf: Optional[int] = attr.ib(default=None, validator=validate_positive)
    exclusiveMaximum: Optional[float] = None
    exclusiveMinimum: Optional[float] = None


@attr.s(auto_attribs=True)
class IntegerType(NumericType):
    """The integer type is used for integral numbers

    Attributes:
        type (str): static value integer
        maximum (int): maximum possible value
        minimum (int): the minimum possible value
        exclusiveMaximum (int): the maximum possible value that cannot be reached
        exclusiveMinimu (int): the minimum possible value that cannot be reached
    """

    type: SchemaDataType = attr.ib(default="integer", init=False)
    maximum: Optional[int] = None
    minimum: Optional[int] = None
    multipleOf: Optional[int] = attr.ib(default=None, validator=validate_positive)
    exclusiveMaximum: Optional[int] = None
    exclusiveMinimum: Optional[int] = None


@attr.s(auto_attribs=True)
class StringType(BasicType):
    """The string type is used for strings of text."""

    type: SchemaDataType = attr.ib(default="string", init=False)
    default: Optional[str] = None
    enum: Optional[List[str]] = attr.ib(default=None)
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
    title: str = "Draft7 JustObjects schema"
    additionalProperties: bool = True
    required: List[str] = attr.ib(factory=list)
    properties: Dict[str, JustSchema] = attr.ib(factory=PropertyDict)
    patternProperties: Dict[str, JustSchema] = attr.ib(factory=dict)

    def add_required(self, field: str) -> None:
        if field in self.required:
            return
        self.required.append(field)


@attr.s(auto_attribs=True)
class SchemaType(ObjectType):
    definitions: Dict[str, ObjectType] = attr.ib(factory=dict)

    def as_object(self) -> ObjectType:
        return ObjectType(
            title=self.title,
            additionalProperties=self.additionalProperties,
            required=self.required,
            properties=self.properties,
            patternProperties=self.patternProperties,
        )


@attr.s(auto_attribs=True)
class ArrayType(BasicType):
    """Json schema array type object.

    This can be used to represent python iterables like list and set.
    NB: use of tuples is currently not supported

    Attributes:
        type (str): static string with value 'array'
        items: Json schema for the items within the array. This schema will be used to
            validate all of the items in the array
        contains: Json schema used to validate items within the array, the difference with items is
            that it only needs to validate against one or more items
        minItems: positive integer representing the minimum number of elements that can be on the array
        maxItems: positive integer representing the maximum number of elements that can be on the array
        uniqueItems: setting this to True, ensures only uniqueItems are found in the array
    """

    type: SchemaDataType = attr.ib(default="array", init=False)
    items: JustSchema = attr.ib(default=None)
    contains: JustSchema = attr.ib(default=None)
    minItems: Optional[int] = attr.ib(default=1, validator=validate_positive)
    maxItems: Optional[int] = attr.ib(default=None, validator=validate_positive)
    uniqueItems: Optional[bool] = False

    def get_enclosed_type(self) -> JustSchema:
        return self.items


@attr.s(auto_attribs=True)
class CompositionType(JustSchema):
    description: Optional[str] = None

    def get_enclosed_types(self) -> Iterable[JustSchema]:
        ...


@attr.s(auto_attribs=True)
class AnyOfType(CompositionType):
    """Json anyOf schema, entries must be valid against exactly one of the subschemas"""

    anyOf: Iterable[JustSchema] = attr.ib(factory=list)

    def get_enclosed_types(self) -> Iterable[JustSchema]:
        return self.anyOf


@attr.s(auto_attribs=True)
class OneOfType(CompositionType):
    """Json oneOf schema, entries must be valid against any of the subschemas"""

    oneOf: Iterable[JustSchema] = attr.ib(factory=list)

    def get_enclosed_types(self) -> Iterable[JustSchema]:
        return self.oneOf


@attr.s(auto_attribs=True)
class AllOfType(CompositionType):
    """Json allOf schema, entries must be valid against all of the subschemas"""

    allOf: Iterable[JustSchema] = attr.ib(factory=list)

    def get_enclosed_types(self) -> Iterable[JustSchema]:
        return self.allOf


@attr.s(auto_attribs=True)
class NotType(JustSchema):
    """The not keyword declares that an instance validates if it doesn’t validate against the given subschema."""

    mustNot: JustSchema
    description: Optional[str] = None

    def as_dict(self) -> Dict[str, Any]:
        return {"not": self.mustNot.as_dict()}

    def get_enclosed_type(self) -> JustSchema:
        return self.mustNot


if __name__ == "__main__":
    pd = PropertyDict()
    print(pd)
