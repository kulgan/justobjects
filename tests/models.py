from typing import Iterable, List

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
