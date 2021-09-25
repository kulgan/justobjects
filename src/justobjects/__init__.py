from pkg_resources import get_distribution

from justobjects.decorators import array, boolean, data, integer, numeric, ref, string
from justobjects.jsontypes import (
    BasicType,
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
    "array",
    "data",
    "ref",
    "show",
    "validate",
    "validate_raw",
    "string",
    "BasicType",
    "IntegerType",
    "NumericType",
    "ObjectType",
    "RefType",
    "ValidationError",
    "ValidationException",
    "VERSION",
]
