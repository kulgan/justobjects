import abc
import json

import attr

import justobjects as jo


@jo.data()
class Troll:
    sex = jo.string(default="male")


@jo.data()
class Sphinx:
    age = jo.integer(default=10)
    troll = jo.ref(Troll, default=None)


print(json.dumps(jo.show_schema(Sphinx), indent=2))


# class Smooth(abc.ABC):
#
#     def from_dict(self, data):
#         print(data)
#
#
# @attr.s(maybe_cls=Smooth, auto_attribs=True)
# class Smoother:
#     sex: str
#
#
# if __name__ == '__main__':
#     sm = Smoother(sex="M")
#     print(sm)
