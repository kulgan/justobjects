import sys
from typing import Any, Dict, Iterable, Tuple, Type

if sys.version_info >= (3, 8):
    from typing import (  # pylint: disable=no-name-in-module
        Final,
        Literal,
        Protocol,
        TypedDict,
    )
else:
    from typing_extensions import Final, Literal, Protocol, TypedDict

import attr

__all__ = [
    "AttrClass",
    "Final",
    "GenericMeta",
    "Literal",
    "Protocol",
    "TypedContainer",
    "TypedDict",
    "is_typed_container",
]
TypedContainer = Type["GenericMeta"]


class AttrClass(Protocol):
    __name__: str
    __attrs_attrs__: Iterable[attr.Attribute]

    @classmethod
    def __jo__(cls) -> Dict[str, Any]:
        ...


class GenericMeta(Protocol):
    __args__: Tuple[Type, ...]
    __origin__: Type


def is_typed_container(cls: Any) -> bool:
    return hasattr(cls, "__origin__")
