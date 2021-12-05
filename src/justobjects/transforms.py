from collections import abc, defaultdict
from datetime import datetime
from typing import (
    Any,
    Container,
    DefaultDict,
    Dict,
    Iterable,
    List,
    Mapping,
    Sequence,
    Set,
    Type,
    Union,
)

import attr

from justobjects import typings

DATE_TYPES = (
    datetime,
    "datetime",
)
ITERABLE_TYPES = (
    Sequence,
    Iterable,
    abc.Sequence,
    abc.Iterable,
    list,
    List,
    set,
    Set,
    abc.Set,
)
OBJECTS_TYPES = (
    abc.Mapping,
    abc.Container,
    defaultdict,
    dict,
    Container,
    DefaultDict,
    Dict,
    Mapping,
)


class JustData(typings.Protocol):
    __name__: str
    __attrs_attrs__: Iterable[attr.Attribute]

    def __jo_post_init__(self) -> None:
        ...

    def __jo_attrs_post_init__(self) -> None:
        ...

    @classmethod
    def schema(cls) -> None:
        ...

    @classmethod
    def from_dict(cls, data: Dict) -> "JustData":
        ...


def is_data_instance(cls: Type) -> bool:
    return getattr(cls, "__attrs_attrs__", None) is not None


def parse_multi(types: Iterable[Type], raw: Any) -> Any:
    for ty in types:
        try:
            return parse_value(ty, raw)
        except Exception as e:
            print(e)
            continue
    raise ValueError(f"'{raw}' cannot be parsed as one of '{types}'")


def parse_value(cls: Type, raw: Any) -> Any:
    if not raw:
        return raw

    if is_data_instance(cls) and isinstance(raw, dict):
        return cls(**raw)

    if cls in DATE_TYPES and isinstance(raw, str):
        return datetime.fromisoformat(raw)

    if not hasattr(cls, "__origin__"):
        return raw

    if getattr(cls, "__origin__") == Union:
        return parse_multi(cls.__args__, raw)

    if cls.__origin__ in OBJECTS_TYPES:
        _, val_type = cls.__args__
        return {k: parse_value(val_type, v) for k, v in raw.items()}

    if cls.__origin__ in ITERABLE_TYPES:
        base_cls = raw.__class__
        arg_type = cls.__args__[0]

        if arg_type != Union:
            return base_cls([parse_value(arg_type, v) for v in raw])

        return base_cls([parse_multi(arg_type.__args__, v) for v in raw])
    return raw


def parse_from_dict(cls: Type[JustData], data: Dict) -> JustData:

    for prop in cls.__attrs_attrs__:
        prop_type = prop.metadata.get("__jo__type__", prop.type)
        prop_value: Any = data.get(prop.name)

        if not prop_value:
            continue

        data[prop.name] = parse_value(prop_type, prop_value)

    return cls(**data)  # type: ignore


def parse_dict(val: Mapping[str, Any]) -> Dict[str, Any]:
    parsed = {}
    for k, v in val.items():
        if k.startswith("__"):
            # skip private properties
            continue
        # skip None values
        if v is None:
            continue
        # map ref
        if k in ["ref"]:
            k = f"${k}"
        dict_val = as_dict(v)
        if dict_val or isinstance(dict_val, bool):
            parsed[k] = dict_val
    return parsed


def as_dict(val: Any) -> Any:
    """Attempts to recursively convert any object to a dictionary"""

    if isinstance(val, (list, set, tuple)):
        return [as_dict(v) for v in val]
    if isinstance(val, abc.Mapping):
        return parse_dict(val)
    if hasattr(val, "__dict__"):
        return parse_dict(val.__dict__)

    return val
