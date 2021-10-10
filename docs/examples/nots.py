import json

import justobjects as jo


@jo.data()
class Troll:
    sex = jo.string(default="male")


@jo.data()
class Sphinx:
    age = jo.integer(default=10, required=True)
    troll = jo.must_not(Troll)


print(json.dumps(jo.show_schema(Sphinx), indent=2))
