import json
from typing import Dict, List, Optional, Set, Union

import justobjects as jo


@jo.data(typed=True)
class Troll:
    weight: Union[int, float]
    sex: str = "male"


@jo.data(typed=True)
class Droll:
    style: Optional[int] = 12
    trolls: Optional[Set[Troll]] = set()


@jo.data(typed=True)
class Sphinx:
    age: int
    drolls: Droll
    sexes = Union[bool, str]
    weights: Dict[str, List[Troll]]


print(json.dumps(jo.show_schema(Sphinx), indent=2))
