import enum
from functools import partial
from typing import Callable, Iterable, Optional, Type

import attr

from justobjects import schemas, typings
from justobjects.jsontypes import (
    BooleanType,
    IntegerType,
    NumericType,
    ObjectType,
    RefType,
    StringType,
    get_type,
)

JO_SCHEMA = "__jo__"
JO_REQUIRED = "__jo__required__"
JO_OBJECT = "__jo__object__"
JO_OBJECT_DESC = "__jo__object_desc__"


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

        is_object = attrib.metadata.get(JO_OBJECT)
        if is_object:
            desc = attrib.metadata.get(JO_OBJECT_DESC)
            sc.definitions[f"{cls.__module__}.{cls.__name__}"] = psc
            sc.properties[field_name] = RefType(
                ref=f"#/definitions/{cls.__module__}.{cls.__name__}", description=desc
            )
            continue
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
        sc = ObjectType(additional_properties=False, description=cls.__doc__)
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
        default: default value
        required: True if it should be required in the schema
        min_length: minimum length of the string
        max_length: maximum length of the strin
        enums: represent schema as an enum instead of free text
        description: Property description
    Returns:
        attr field definition
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


def ref(ref_type: Type, required=False, description: Optional[str] = None) -> attr.Attribute:
    """Creates a json reference to another json object

    Args:
        ref_type: class type referenced
        required: True if field is required
        description: ref specific documentation/comments
    Returns:
        attr attribute definition
    """
    obj = schemas.get(ref_type)
    return attr.ib(
        type=ref_type,
        metadata={
            JO_SCHEMA: obj,
            JO_REQUIRED: required,
            JO_OBJECT: True,
            JO_OBJECT_DESC: description,
        },
    )


def number(
    default: Optional[int] = None,
    minimum: Optional[int] = None,
    maximum: Optional[int] = None,
    multiple_of: Optional[int] = None,
    exclusive_min: Optional[int] = None,
    exclusive_max: Optional[int] = None,
    required: Optional[bool] = None,
    description: Optional[str] = None,
):
    """Create a schema of type number"""

    sc = NumericType(
        minimum=minimum,
        maximum=maximum,
        multiple_of=multiple_of,
        exclusive_minimum=exclusive_min,
        exclusive_maximum=exclusive_max,
        description=description,
    )
    return attr.ib(type=float, default=default, metadata={JO_SCHEMA: sc, JO_REQUIRED: required})


def integer(
    default: Optional[int] = None,
    minimum: Optional[int] = None,
    maximum: Optional[int] = None,
    multiple_of: Optional[int] = None,
    exclusive_min: Optional[int] = None,
    exclusive_max: Optional[int] = None,
    required: Optional[bool] = None,
    description: Optional[str] = None,
):
    """Create a schema of type integer"""

    sc = IntegerType(
        minimum=minimum,
        maximum=maximum,
        description=description,
        multiple_of=multiple_of,
        exclusive_minimum=exclusive_min,
        exclusive_maximum=exclusive_max,
    )
    return attr.ib(type=float, default=default, metadata={JO_SCHEMA: sc, JO_REQUIRED: required})


def boolean(
    default: Optional[bool] = None,
    required: Optional[bool] = None,
    description: Optional[str] = None,
):
    """Boolean schema data type
    Args:
        default: default boolean value
        required (bool):
        description (str): summary/description
    Returns:
        attr.ib:
    """
    sc = BooleanType(default=default, description=description)
    return attr.ib(type=bool, default=default, metadata={JO_SCHEMA: sc, JO_REQUIRED: required})
