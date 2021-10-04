import sys
from typing import Any, Dict, Iterable, Type

if sys.version_info >= (3, 8):
    from typing import Literal, Protocol, TypedDict  # pylint: disable=no-name-in-module
else:
    from typing_extensions import Literal, Protocol, TypedDict

import attr

__all__ = ["AttrClass", "Literal", "Protocol", "TypedDict", "is_generic_type"]


class AttrClass(Protocol):
    __name__: str
    __attrs_attrs__: Iterable[attr.Attribute]

    @classmethod
    def __jo__(cls) -> Dict[str, Any]:
        ...


def is_generic_type(cls: Type) -> bool:
    return hasattr(cls, "__origin__")
