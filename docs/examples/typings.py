import json
from typing import Dict, Optional, Set, Union

import justobjects as jo


@jo.data(auto_attribs=True)
class Troll:
    weight: Union[int, float]
    sex: str = "male"


@jo.data(auto_attribs=True)
class Droll:
    style: Optional[int] = 12
    trolls: Optional[Set[Troll]] = set()


@jo.data(auto_attribs=True)
class Sphinx:
    age: int
    drolls: Droll
    sexes = Union[bool, str]
    weights: Dict[str, int]


print(json.dumps(jo.show(Sphinx), indent=2))
