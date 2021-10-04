import json
from typing import Optional, Set

import justobjects as jo


@jo.data(auto_attribs=True)
class Troll:
    weight: int
    sex: str = "male"


@jo.data(auto_attribs=True)
class Droll:
    style: Optional[int] = 12
    trolls: Optional[Set[Troll]] = set()


@jo.data(auto_attribs=True)
class Sphinx:
    age: int
    drolls: Droll
    # sexes = jo.one_of(types=(bool, str))
    # weights = jo.all_of(types=(jo.NumericType, jo.IntegerType))


print(json.dumps(jo.show(Sphinx), indent=2))
