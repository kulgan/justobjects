import enum
from functools import partial
from typing import Any, Callable, Iterable, List, Optional, Type

import attr

from justobjects import schemas, typings
from justobjects.jsontypes import (
    AllOfType,
    AnyOfType,
    ArrayType,
    BooleanType,
    IntegerType,
    NotType,
    NumericType,
    ObjectType,
    OneOfType,
    RefType,
    StringType,
)

JO_TYPE = "__jo__type__"
JO_SCHEMA = "__jo__"
JO_REQUIRED = "__jo__required__"
JO_OBJECT_DESC = "__jo__object_desc__"


class JustData(typings.Protocol):
    @classmethod
    def schema(cls) -> None:
        ...


class AttrClass(typings.Protocol):
    __name__: str
    __attrs_attrs__: Iterable[attr.Attribute]


def extract_schema(cls: AttrClass, sc: ObjectType) -> None:
    sc.properties = {}
    attributes = cls.__attrs_attrs__
    for attrib in attributes:
        cls_type = attrib.metadata.get(JO_TYPE, attrib.type)
        psc = attrib.metadata.get(JO_SCHEMA) or schemas.get_type(cls_type)
        is_required = attrib.metadata.get(JO_REQUIRED, False) or attrib.default == attr.NOTHING

        field_name = attrib.name
        if is_required:
            sc.add_required(field_name)

        if not isinstance(psc, ObjectType) or typings.is_generic_type(cls_type):
            sc.properties[field_name] = psc
            continue

        desc = attrib.metadata.get(JO_OBJECT_DESC)
        sc.properties[field_name] = schemas.as_ref(cls_type, psc, desc)
    schemas.add(cls, sc)


def data(frozen: bool = True, auto_attribs: bool = False) -> Callable[[Type], Type]:
    """decorates a class automatically binding it to a Schema instance
    This technically extends `attr.s` amd pulls out a Schema instance in the process

    Args:
        frozen: frozen data class
        auto_attribs: set to True to use typings
    Returns:
        a JustSchema object wrapper
    Example:
        .. code-block:: python

            import justobjects as jo

            @jo.data()
            class Sample(object):
                age = jo.integer(required=True, minimum=18)
                name = jo.string(required=True)

            # show schema
            jo.show(Sample)
    """

    def wraps(cls: Type) -> Type:
        sc = ObjectType(additionalProperties=False, description=cls.__doc__)
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
    enums: Optional[List[str]] = None,
    str_format: Optional[str] = None,
    pattern: Optional[str] = None,
    description: Optional[str] = None,
) -> attr.Attribute:
    """Creates a json schema of type string

    Args:
        default: default value
        required: True if it should be required in the schema
        min_length: minimum length of the string
        max_length: maximum length of the string
        str_format: string format
        pattern: regex pattern for value matching
        enums: represent schema as an enum instead of free text
        description: Property description
    Returns:
        a string attribute wrapper
    """
    sc = StringType(
        minLength=min_length,
        maxLength=max_length,
        enum=enums,
        default=default,
        format=str_format,
        pattern=pattern,
        description=description,
    )
    return attr.ib(type=str, default=default, metadata={JO_SCHEMA: sc, JO_REQUIRED: required})


def ref(
    ref_type: Type, required: bool = False, description: Optional[str] = None
) -> attr.Attribute:
    """Creates a json reference to another json object

    Args:
        ref_type: class type referenced
        required: True if field is required
        description: ref specific documentation/comments
    Returns:
        a schema reference attribute wrapper
    """
    obj = schemas.get(ref_type)
    return attr.ib(
        type=ref_type,
        metadata={
            JO_SCHEMA: obj,
            JO_TYPE: ref_type,
            JO_REQUIRED: required,
            JO_OBJECT_DESC: description,
        },
    )


def numeric(
    default: Optional[float] = None,
    minimum: Optional[float] = None,
    maximum: Optional[float] = None,
    multiple_of: Optional[int] = None,
    exclusive_min: Optional[float] = None,
    exclusive_max: Optional[float] = None,
    required: Optional[bool] = None,
    description: Optional[str] = None,
) -> attr.Attribute:
    """The number type is used for any numeric type, either integers or floating point numbers.

    Args:
        default: default value used for instances
        minimum: a number denoting the minimum allowed value for instances
        maximum: a number denoting the maximum allowed value for instances
        multiple_of: must be a positive value, restricts values to be multiples of the given number
        exclusive_max: a number denoting maximum allowed value should be less that the given value
        exclusive_min: a number denoting minimum allowed value should be greater that the given value
        required: True if field should be a required field
        description: Comments describing the field
    Returns:
        A wrapped NumericType
    """

    sc = NumericType(
        minimum=minimum,
        maximum=maximum,
        default=default,
        multipleOf=multiple_of,
        exclusiveMinimum=exclusive_min,
        exclusiveMaximum=exclusive_max,
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
) -> attr.Attribute:
    """The integer type is used for integral numbers

    Args:
        default: default value used for instances
        minimum: a number denoting the minimum allowed value for instances
        maximum: a number denoting the maximum allowed value for instances
        multiple_of: must be a positive value, restricts values to be multiples of the given number
        exclusive_max: a number denoting maximum allowed value should be less that the given value
        exclusive_min: a number denoting minimum allowed value should be greater that the given value
        required: True if field should be a required field
        description: Comments describing the field
    Returns:
        A wrapped IntegerType
    """

    sc = IntegerType(
        minimum=minimum,
        maximum=maximum,
        default=default,
        description=description,
        multipleOf=multiple_of,
        exclusiveMinimum=exclusive_min,
        exclusiveMaximum=exclusive_max,
    )
    return attr.ib(type=int, default=default, metadata={JO_SCHEMA: sc, JO_REQUIRED: required})


def boolean(
    default: Optional[bool] = None,
    required: Optional[bool] = None,
    description: Optional[str] = None,
) -> attr.Attribute:
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


def array(
    item: Type,
    contains: bool = False,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
    required: bool = False,
) -> attr.Attribute:
    """Array schema data type

    If `item` is the class type of another data object, it will be converted to a reference

    Args:
        item: data object class type used as items in the array
        contains: schema only needs to validate against one or more items in the array.
        min_items: positive integer representing the minimum number of items that can be on the array
        max_items: positive integer representing the maximum number of items that can be on the array
        required: True if field is required
    Returns:
        A array attribute wrapper
    """
    _type = schemas.as_ref(item, schemas.get_type(item))
    if contains:
        sc = ArrayType(contains=_type, minItems=min_items, maxItems=max_items)
    else:
        sc = ArrayType(items=_type, minItems=min_items, maxItems=max_items)
    return attr.ib(type=list, factory=list, metadata={JO_SCHEMA: sc, JO_REQUIRED: required})


def any_of(
    types: Iterable[Type], default: Optional[Any] = None, required: bool = False
) -> attr.Attribute:
    """JSON schema anyOf"""

    items = [schemas.as_ref(cls, schemas.get_type(cls)) for cls in types]
    sc = AnyOfType(anyOf=items)
    return attr.ib(type=list, default=default, metadata={JO_SCHEMA: sc, JO_REQUIRED: required})


def one_of(
    types: Iterable[Type], default: Optional[Any] = None, required: bool = False
) -> attr.Attribute:
    """Applies to properties and complies with JSON schema oneOf property
    Args:
        types (list[type]): list of types that will be allowed
        default (object): default object instance that must be one of the allowed types
        required: True if property is required
    Returns:
        attr.ib: field instance
    """
    items = [schemas.as_ref(cls, schemas.get_type(cls)) for cls in types]
    sc = OneOfType(oneOf=items)
    return attr.ib(type=list, default=default, metadata={JO_SCHEMA: sc, JO_REQUIRED: required})


def all_of(
    types: Iterable[Type], default: Optional[Any] = None, required: bool = False
) -> attr.Attribute:
    """JSON schema allOf"""

    items = [schemas.as_ref(cls, schemas.get_type(cls)) for cls in types]
    sc = AllOfType(allOf=items)
    return attr.ib(type=list, default=default, metadata={JO_SCHEMA: sc, JO_REQUIRED: required})


def must_not(item: Type) -> attr.Attribute:
    obj = schemas.get_type(item)
    sc = NotType(mustNot=obj)
    return attr.ib(type=dict, default=None, metadata={JO_SCHEMA: sc})
