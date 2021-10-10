import json

import justobjects as jo


@jo.data()
class Troll:
    weight = jo.numeric(required=True)
    sex = jo.string(default="male")


@jo.data()
class Sphinx:
    age = jo.integer(default=10, required=True)
    trolls = jo.array(item=Troll)
    sexes = jo.array(item=str)
    weights = jo.array(item=jo.NumericType)


print(json.dumps(jo.show_schema(Sphinx), indent=2))
