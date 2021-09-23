from pkg_resources import get_distribution

from justobjects.decorators import data, ref, string
from justobjects.jsontypes import BasicType, IntegerType, NumericType, ObjectType, RefType

VERSION = get_distribution(__name__).version

__all__ = ["data", "ref", "string", "BasicType", "IntegerType", "NumericType", "ObjectType", "RefType", "VERSION"]
