import sys

if sys.version_info >= (3, 8):
    from typing import Literal, Protocol, TypedDict, Type  # pylint: disable=no-name-in-module
else:
    from typing_extensions import Literal, Protocol, TypedDict


__all__ = [
    "Literal",
    "Protocol",
    "TypedDict",
]


def is_generic_type(cls: Type) -> bool:
    return hasattr(cls, "__origin__")
