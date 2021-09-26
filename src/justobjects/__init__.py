from pkg_resources import get_distribution

from justobjects.decorators import boolean, data, integer, numeric, ref, string
from justobjects.jsontypes import (
    BasicType,
    DateType,
    DateTimeType,
    DurationType,
    EmailType,
    HostnameType,
    Ipv4Type,
    Ipv6Type,
    TimeType,
    UriType,
    UuidType,
    IntegerType,
    NumericType,
    ObjectType,
    RefType,
)
from justobjects.schemas import (
    ValidationError,
    ValidationException,
    show,
    validate,
    validate_raw,
)

VERSION = get_distribution(__name__).version

__all__ = [
    "data",
    "ref",
    "show",
    "validate",
    "validate_raw",
    "string",
    "BasicType",
    "DateType",
    "DateTimeType",
    "DurationType",
    "EmailType",
    "HostnameType",
    "IntegerType",
    "Ipv4Type",
    "Ipv6Type",
    "NumericType",
    "ObjectType",
    "RefType",
    "TimeType",
    "UriType",
    "UuidType",
    "ValidationError",
    "ValidationException",
    "VERSION",
]
