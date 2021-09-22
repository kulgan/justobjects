import collections
from typing import Optional, List, Dict

import attr

from justobjects import typings

SchemaType = typings.Literal["null", "boolean", "object", "array", "number", "integer"]


@attr.s(auto_attribs=True)
class Schema:
    """The Schema Object allows the definition of input and output data types.
        These types can be objects, but also primitives and arrays. This object is an extended subset of the JSON Schema
        Specification Wright Draft 00. For more information about the properties, see JSON Schema Core and JSON Schema
        Validation. Unless stated otherwise, the property definitions follow the JSON Schema.
        """

    ref: Optional[str] = None
    title: Optional[str] = None
    multiple_of: Optional[float] = None
    # maximum = attr.ib(default=None, type=int)
    # minimum = attr.ib(default=None, type=int)
    # exclusive_maximum = attr.ib(default=None, type=bool)
    # exclusive_minimum = attr.ib(default=None, type=bool)
    # max_length = attr.ib(default=None, type=int)  # type: int
    # min_length = attr.ib(default=None, type=int)  # type: int
    # pattern = attr.ib(default=None, type=str)
    # max_items = attr.ib(default=None, type=int)  # type: ignore
    # min_items = attr.ib(default=None, type=int)  # type: ignore
    # unique_items = attr.ib(default=None, type=bool)
    # max_properties = attr.ib(default=None, type=int)  # type: ignore
    # min_properties = attr.ib(default=None, type=int)  # type: ignore
    # enum = attr.ib(default=None, type=List)
    # type = attr.ib(default=None, type=str)
    # all_of = attr.ib(default=None, type=List["Schema"])
    # one_of = attr.ib(default=None, type=List["Schema"])
    # any_of = attr.ib(default=None, type=List["Schema"])
    # _not = None  # type: ignore
    # items = attr.ib(default=None)
    # properties = attr.ib(default=None, type=dict)
    # additional_properties = attr.ib(type=bool, default=None)
    # description = attr.ib(default=None, type=str)
    # format = attr.ib(default=None, type=str)
    # default = attr.ib(default=None)
    # nullable = attr.ib(default=None, type=bool)
    # discriminator = attr.ib(default=None, type="Discriminator")
    # read_only = attr.ib(default=None, type=bool)
    # write_only = attr.ib(default=None, type=bool)
    # xml = attr.ib(default=None, type="XML")
    # external_docs = None
    # deprecated = attr.ib(default=None, type=bool)
    # example = attr.ib(default=None, type=dict)


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
    def json_schema(self):
        return self.parse(self.__dict__)

    def parse(self, val):
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
            if k.startswith("_"):
                k = k[1:]
                v = getattr(self, "q_" + k, None)
            k = camel_case(k)
            parsed[k] = self._to_dict(v)
        return parsed

    def _to_dict(self, val):
        if isinstance(val, SchemaMixin):
            return val.json_schema()
        if isinstance(val, list):
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
    type: str = "number"
    default: Optional[int] = None
    enum: List[int] = attr.ib(factory=list)
    maximum: Optional[int] = None
    minimum: Optional[int] = None
    multiple_of: Optional[int] = None
    exclusive_maximum: Optional[int] = None
    exclusive_minimum: Optional[int] = None


@attr.s(auto_attribs=True)
class StringType(BasicType):
    type: str = "string"
    default: Optional[str] = None
    enum: List[str] = attr.ib(factory=list)
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    pattern: Optional[str] = None


@attr.s(auto_attribs=True)
class ObjectType(BasicType):
    type: str = "object"
    additional_properties: bool = False
    required: List[str] = attr.ib(factory=list)
    properties: Dict[str, BasicType] = attr.ib(factory=dict)


if __name__ == '__main__':
    o = ObjectType(properties={
        'label': StringType(enum=["white", "black"])
    })

    print(o.json_schema())
