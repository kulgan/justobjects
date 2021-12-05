from pkg_resources import get_distribution

from justobjects.decorators import (
    all_of,
    any_of,
    array,
    boolean,
    data,
    integer,
    must_not,
    numeric,
    one_of,
    ref,
    string,
)
from justobjects.schemas import show_schema, validate
from justobjects.transforms import as_dict
from justobjects.types import (
    AllOfType,
    AnyOfType,
    ArrayType,
    BasicType,
    BooleanType,
    DateTimeType,
    DateType,
    DurationType,
    EmailType,
    HostnameType,
    IntegerType,
    Ipv4Type,
    Ipv6Type,
    NotType,
    NumericType,
    ObjectType,
    OneOfType,
    RefType,
    StringType,
    TimeType,
    UriType,
    UuidType,
    cast,
)
from justobjects.validation import ValidationError, ValidationException

VERSION = get_distribution(__name__).version

__all__ = [
    "all_of",
    "any_of",
    "array",
    "as_dict",
    "boolean",
    "cast",
    "data",
    "integer",
    "must_not",
    "numeric",
    "one_of",
    "ref",
    "show_schema",
    "string",
    "validate",
    "AllOfType",
    "AnyOfType",
    "ArrayType",
    "BasicType",
    "DateType",
    "DateTimeType",
    "DurationType",
    "EmailType",
    "HostnameType",
    "BooleanType",
    "IntegerType",
    "Ipv4Type",
    "Ipv6Type",
    "NotType",
    "NumericType",
    "ObjectType",
    "OneOfType",
    "RefType",
    "TimeType",
    "UriType",
    "UuidType",
    "StringType",
    "ValidationError",
    "ValidationException",
    "VERSION",
]
