import enum
from functools import partial
from typing import Callable, Iterable, Optional, Type

import attr

from justobjects import schemas, typings
from justobjects.jsontypes import ObjectType, StringType, get_type

JO_SCHEMA = "__jo__"
JO_REQUIRED = "__jo__required__"


class JustData(typings.Protocol):
    @classmethod
    def schema(cls) -> None:
        ...


class AttrClass(typings.Protocol):

    __attrs_attrs__: Iterable[attr.Attribute]


def extract_schema(cls: AttrClass, sc: ObjectType) -> None:
    sc.properties = {}
    attributes = cls.__attrs_attrs__
    for attrib in attributes:
        psc = attrib.metadata.get(JO_SCHEMA) or get_type(attrib.type)
        is_required = attrib.metadata.get(JO_REQUIRED, False) or attrib.default == attr.NOTHING
        field_name = attrib.name
        if is_required:
            sc.add_required(field_name)
        sc.properties[field_name] = psc
    schemas.add(cls, sc)


def data(frozen: bool = True, auto_attribs: bool = False) -> Callable[[Type], Type]:
    """decorates a class automatically binding it to a Schema instance
    This technically extends `attr.s` amd pulls out a Schema instance in the process
    Args:
        frozen: frozen data class
        auto_attribs: set to True to use typings
    Returns:
        attr.s: and attr.s wrapped class
    Example:
        .. code-block::
            import justobjects as jo
            @jo.data()
            class Sample(object):
                age = jo.integer(required=True, minimum=18)
                name = jo.string(required=True)
    """

    def wraps(cls: Type) -> Type:
        sc = ObjectType(
            additional_properties=False,
        )
        js = partial(extract_schema, sc=sc)
        cls = attr.s(cls, auto_attribs=auto_attribs, frozen=frozen)
        js(cls)
        return cls

    return wraps


def string(
    default: Optional[str] = None,
    required: bool = False,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    enums: Optional[Iterable[str]] = None,
    description: Optional[str] = None,
) -> attr.Attribute:
    """Creates a json schema of type string
    Args:
        default (str): default value
        required (bool): True if it should be required in the schema
        min_length (int): minimum length of the string
        max_length (int): maximum length of the strin
        enums: represent schema as an enum instead of free text
        description (str): Property description
    Returns:
        attr.ib: field definition
    """
    enum_vals = enums or []
    if isinstance(enums, enum.Enum):
        if enums.member_type != str:
            raise ValueError("Invalid enum")
    sc = StringType(
        min_length=min_length,
        max_length=max_length,
        enum=enum_vals,
        description=description,
    )
    return attr.ib(type=str, default=default, metadata={JO_SCHEMA: sc, JO_REQUIRED: required})
