import json

import justobjects as jo


@jo.data()
class Troll:
    weight = jo.numeric(required=True)
    sex = jo.string(default="male")

    def __attrs_post_init__(self):
        print(self)


@jo.data()
class Droll:
    style = jo.numeric(default=12)
    trolls = jo.array(Troll)


@jo.data()
class Sphinx:
    age = jo.integer(default=10, required=True)
    trolls = jo.any_of(types=(Troll, Droll))
    sexes = jo.one_of(types=(bool, str))
    weights = jo.all_of(types=(jo.NumericType, jo.IntegerType))


# print(json.dumps(jo.show_schema(Sphinx), indent=2))

if __name__ == "__main__":
    troll = Troll(sex="female", weight=13)
