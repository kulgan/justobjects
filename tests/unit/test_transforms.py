from tests.models import Actor, Manager, Movie, Role, RoleManager

ACTOR = {
    "name": "Steve Rogers",
    "sex": "male",
    "age": 21,
    "height": 5.1,
    "married": True,
    "role": {"name": "Captain America", "race": "American"},
}
ROLE_MANAGER = {
    "roles": [
        {"name": "Captain America", "race": "white"},
        {"name": "Nick Fury", "race": "black"},
    ],
    "allowed": [{"name": "Nick Fury", "race": "black"}],
    "people": ACTOR,
    "names": "Steve",
    "requires": "A working bubble",
}


def test_complex_dict() -> None:
    rm = RoleManager(**ROLE_MANAGER)

    assert len(rm.roles) == 2
    for role in rm.roles:
        assert isinstance(role, Role)

    assert len(rm.allowed) == 1
    for allowed in rm.allowed:
        assert isinstance(allowed, Role)

    assert isinstance(rm.people, Actor)


def test_with_ref() -> None:

    data = {
        "main": ACTOR,
        "title": "valid title",
    }

    movie = Movie(**data)
    assert movie.characters == 100
    assert movie.released is False
    assert movie.main.sex == "male"


def test_with_dict() -> None:
    movie = {
        "main": ACTOR,
        "title": "valid title",
    }
    mgr = Manager(**{"actors": [ACTOR], "movies": [movie], "personal": {"steve": ACTOR}})

    assert len(mgr.actors) == 1
    assert isinstance(mgr.actors[0], Actor)
