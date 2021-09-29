import sys
from typing import Type

if sys.version_info >= (3, 8):
    from typing import Literal, Protocol, TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import Literal, Protocol, TypedDict


__all__ = ["Literal", "Protocol", "TypedDict", "is_generic_type"]


def is_generic_type(cls: Type) -> bool:
    return hasattr(cls, "__origin__")
