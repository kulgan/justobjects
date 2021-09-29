from typing import Dict, Iterable, List

import justobjects as jo


@jo.data(auto_attribs=True)
class Role:
    name: str
    race: str


@jo.data(auto_attribs=True)
class Actor:
    """A person that can play movie characters"""

    name: str
    sex: str
    role: Role
    age: int = 10
    height: float = 10.0
    married: bool = False


@jo.data()
class Movie:
    """A story with plot and characters"""

    main = jo.ref(ref_type=Actor, description="Actor playing the main character")
    title = jo.string(
        max_length=24,
        min_length=4,
        required=True,
        description="Formal title of the movie",
        default="NA",
    )
    released = jo.boolean(default=False, required=False)
    characters = jo.integer(default=100, required=False)
    budget = jo.numeric(default=100000, required=False)


@jo.data(auto_attribs=True)
class Manager:
    actors: Iterable[Actor]
    movies: List[Movie]
    personal: Dict[str, Actor]


@jo.data()
class RoleManager:
    roles = jo.array(item=Role, min_items=1)
    allowed = jo.array(item=Role, contains=True, min_items=1)
    people = jo.any_of(types=[Actor, Manager])
    names = jo.one_of(types=[jo.StringType, jo.IntegerType])
    requires = jo.must_not(item=jo.BooleanType)


class Unknown:
    name: set
