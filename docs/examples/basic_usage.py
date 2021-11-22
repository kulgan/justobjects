import json
from typing import Iterable, List

import justobjects as jo


@jo.data()
class Model:
    a = jo.integer(minimum=3, maximum=30, multiple_of=3)
    b = jo.numeric(default=0.3, multiple_of=2)
    c = jo.string(default="123")


# display schema
print(json.dumps(jo.show_schema(Model), indent=2))


try:
    # fails validation
    Model(a=3.1415, b=2.72, c="123")
except jo.ValidationException as err:
    print(err.errors)


try:
    # fails validation
    jo.validate(Model, dict(a=3.1415, b=2.72, c="123"))
except jo.ValidationException as err:
    print(err.errors)


@jo.data(typed=True)
class TypedModel:
    a: int
    b: float = 0.3
    c: str = "123"


@jo.data(typed=True)
class StringModel:
    a: jo.EmailType
    b: jo.UuidType
    c: Iterable[jo.TimeType]
    d: List[jo.Ipv4Type]
    e: Model


print(json.dumps(jo.show_schema(StringModel), indent=2))
