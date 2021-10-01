from typing import Iterable, List

import justobjects as jo


@jo.data()
class Model:
    a = jo.integer(minimum=3, maximum=30, multiple_of=3)
    b = jo.numeric(default=0.3, multiple_of=2)
    c = jo.string(default="123")


# display schema
print(jo.show(Model))


try:
    # fails validation
    jo.is_valid(Model(a=3.1415, b=2.72, c="123"))
except jo.schemas.ValidationException as err:
    print(err.errors)


@jo.data(auto_attribs=True)
class StringModel:
    a: jo.EmailType
    b: jo.UuidType
    c: Iterable[jo.TimeType]
    d: List[jo.Ipv4Type]


print(jo.show(StringModel))
