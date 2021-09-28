from pkg_resources import get_distribution

from justobjects.decorators import (
    all_of,
    any_of,
    array,
    boolean,
    data,
    integer,
    numeric,
    one_of,
    ref,
    string,
)
from justobjects.jsontypes import (
    AllOfType,
    AnyOfType,
    ArrayType,
    BasicType,
    BooleanType,
    IntegerType,
    NumericType,
    ObjectType,
    OneOfType,
    RefType,
)
from justobjects.schemas import (
    ValidationError,
    ValidationException,
    is_valid,
    is_valid_data,
    show,
)

VERSION = get_distribution(__name__).version

__all__ = [
    "all_of",
    "any_of",
    "array",
    "boolean",
    "data",
    "integer",
    "numeric",
    "one_of",
    "ref",
    "show",
    "is_valid",
    "is_valid_data",
    "string",
    "AllOfType",
    "AnyOfType",
    "ArrayType",
    "BasicType",
    "BooleanType",
    "IntegerType",
    "NumericType",
    "ObjectType",
    "OneOfType",
    "RefType",
    "ValidationError",
    "ValidationException",
    "VERSION",
]
