import attr

import justobjects as jo


@jo.data(auto_attribs=True)
class Actor:
    """A person that can play movie characters"""
    name: str
    sex: str
    age: int = 10


@jo.data()
class Movie:
    """A story with plot and characters"""
    main = jo.ref(ref_type=Actor, description="Actor playing the main character")
    title = jo.string(max_length=24, min_length=4, required=True, description="Formal title of the movie")
