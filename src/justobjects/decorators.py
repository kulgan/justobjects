import abc
from functools import partial
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)

import attr

from justobjects import schemas, transforms, typings
from justobjects.transforms import as_dict
from justobjects.types import (
    AllOfType,
    AnyOfType,
    ArrayType,
    BooleanType,
    IntegerType,
    NotType,
    NumericType,
    OneOfType,
    StringType,
)

JO_TYPE = "__jo__type__"
JO_SCHEMA = "__jo__"
JO_REQUIRED = "__jo__required__"
JO_OBJECT_DESC = "__jo__object_desc__"

T = TypeVar("T")


class JustObject(typings.Protocol):
    __name__: str
    __attrs_attrs__: Iterable[attr.Attribute]

    def __jo_post_init__(self) -> None:
        ...

    def __jo_attrs_post_init__(self) -> None:
        ...

    def __attrs_post_init__(self) -> None:
        ...

    @classmethod
    def from_dict(cls, item: Dict) -> "JustObject":
        ...


def __attrs_post_init__(self: JustObject) -> None:
    if hasattr(self, "__jo_attrs_post_init__"):
        self.__jo_attrs_post_init__()
    if hasattr(self, "__jo_post_init__"):
        self.__jo_post_init__()
    schemas.validate(self)


def __as_dict(self: Type) -> Dict[str, Any]:
    return as_dict(self)


def attribute_transformer(cls: Type, fields: List[attr.Attribute]) -> List[attr.Attribute]:
    results: List[attr.Attribute] = []
    for field in fields:
        field_type = field.metadata.get("__jo__type__", field.type)
        converter = partial(transforms.parse_value, field_type)
        results.append(field.evolve(converter=converter))
    return results


def data(frozen: bool = True, typed: bool = False) -> Callable[[Type], Type]:
    """decorates a class automatically binding it to a Schema instance
    This technically extends `attr.s` amd pulls out a Schema instance in the process

    Args:
        frozen: frozen data class
        typed: set to True to use typings
    Returns:
        a JustSchema object wrapper
    Example:
        .. code-block:: python

            import justobjects as jo

            @jo.data()
            class Sample:
                age = jo.integer(required=True, minimum=18)
                name = jo.string(required=True)

            # show schema
            jo.show_schema(Sample)
    """

    def wraps(cls: Type) -> Type:

        if hasattr(cls, "__attrs_post_init__"):
            setattr(cls, "__jo_attrs_post_init__", cls.__attrs_post_init__)
        setattr(cls, "__attrs_post_init__", __attrs_post_init__)
        setattr(cls, "as_dict", __as_dict)

        cls = attr.s(
            cls, auto_attribs=typed, frozen=frozen, field_transformer=attribute_transformer
        )
        schemas.transform_properties(cast(typings.AttrClass, cls))
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
    Example:
        .. code-block:: python

            import justobjects as jo

            @jo.data()
            class Sample:
                age = jo.integer(required=True, minimum=18)
                name = jo.string(required=True, min_length=10)

            # show schema
            jo.show_schema(Sample)
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
    ref_type: Type,
    required: bool = False,
    description: Optional[str] = None,
    default: Optional[Type] = None,
) -> attr.Attribute:
    """Creates a json reference to another json object

    Args:
        ref_type: class type referenced
        required: True if field is required
        description: ref specific documentation/comments
        default: default value
    Returns:
        a schema reference attribute wrapper
    """
    obj = schemas.transform(ref_type)
    return attr.ib(
        type=ref_type,
        default=default,
        metadata={
            JO_SCHEMA: schemas.as_ref(ref_type, obj, description),
            JO_TYPE: ref_type,
            JO_REQUIRED: required,
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
        multiple_of: must be a positive value, restricts values to be multiples of the given
                    number
        exclusive_max: a number denoting maximum allowed value should be less that the given value
        exclusive_min: a number denoting minimum allowed value should be greater that the given
                    value
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
        multiple_of: must be a positive value, restricts values to be multiples of the given
                    number
        exclusive_max: a number denoting maximum allowed value should be less that the given value
        exclusive_min: a number denoting minimum allowed value should be greater that the given
                    value
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
        boolean schema wrapper
    """
    sc = BooleanType(default=default, description=description)
    return attr.ib(type=bool, default=default, metadata={JO_SCHEMA: sc, JO_REQUIRED: required})


def array(
    item: Type,
    contains: bool = False,
    min_items: Optional[int] = 1,
    max_items: Optional[int] = None,
    required: bool = False,
    unique_items: bool = False,
    description: Optional[str] = None,
) -> attr.Attribute:
    """Array schema data type

    If `item` is the class type of another data object, it will be converted to a reference

    Args:
        item: data object class type used as items in the array
        contains: schema only needs to validate against one or more items in the array.
        min_items: positive integer representing the minimum number of items that can be on
                    the array
        max_items: positive integer representing the maximum number of items that can be on
                    the array
        required: True if field is required
        unique_items: disallow duplicates
        description: field description
    Returns:
        A array attribute wrapper
    """
    _type = schemas.as_ref(item, schemas.transform(item))
    if contains:
        sc = ArrayType(
            contains=_type,
            minItems=min_items,
            maxItems=max_items,
            uniqueItems=unique_items,
            description=description,
        )
    else:
        sc = ArrayType(
            items=_type,
            minItems=min_items,
            maxItems=max_items,
            uniqueItems=unique_items,
            description=description,
        )
    return attr.ib(
        type=List[item],  # type: ignore
        factory=list,
        metadata={JO_SCHEMA: sc, JO_REQUIRED: required},
    )


def any_of(
    types: Iterable[Type],
    default: Optional[Any] = None,
    required: bool = False,
    description: Optional[str] = None,
) -> attr.Attribute:
    """JSON schema anyOf"""

    item_types = tuple(t for t in types)
    items = [schemas.as_ref(cls, schemas.transform(cls)) for cls in types]
    sc = AnyOfType(anyOf=items, description=description)
    return attr.ib(
        type=Union[item_types], default=default, metadata={JO_SCHEMA: sc, JO_REQUIRED: required}
    )


def one_of(
    types: Iterable[Type],
    default: Optional[Any] = None,
    required: bool = False,
    description: Optional[str] = None,
) -> attr.Attribute:
    """Applies to properties and complies with JSON schema oneOf property
    Args:
        types (list[type]): list of types that will be allowed
        default (object): default object instance that must be one of the allowed types
        required: True if property is required
        description: field comments/description
    Returns:
        attr.ib: field instance
    """
    item_types = tuple(t for t in types)
    items = [schemas.as_ref(cls, schemas.transform(cls)) for cls in types]
    sc = OneOfType(oneOf=items, description=description)
    return attr.ib(
        type=Union[item_types], default=default, metadata={JO_SCHEMA: sc, JO_REQUIRED: required}  # type: ignore
    )


def all_of(
    types: Iterable[Type],
    default: Optional[Any] = None,
    required: bool = False,
    description: Optional[str] = None,
) -> attr.Attribute:
    """JSON schema allOf"""

    item_types = tuple(t for t in types)
    items = [schemas.as_ref(cls, schemas.transform(cls)) for cls in types]
    sc = AllOfType(allOf=items, description=description)
    return attr.ib(
        type=List[Union[item_types]],  # type: ignore
        default=default,
        metadata={JO_SCHEMA: sc, JO_REQUIRED: required},
    )


def must_not(item: Type, description: Optional[str] = None) -> attr.Attribute:
    obj = schemas.as_ref(item, schemas.transform(item))
    sc = NotType(mustNot=obj, description=description)
    return attr.ib(type=object, default=None, metadata={JO_SCHEMA: sc})
