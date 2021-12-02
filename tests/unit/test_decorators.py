import json

import pytest

from justobjects import schemas, validation
from tests.models import Actor, Manager, Movie, Role, RoleManager, Unknown


def test_show_isolated_model() -> None:
    js = schemas.show_schema(Actor)

    assert js["type"] == "object"
    assert js["required"] == ["name", "sex", "role"]


def test_validate_isolated_model() -> None:
    actor = Actor(name="Same", sex="Male", age=10, role=Role(name="Simons", race="white"))
    assert actor.__dict__
    schemas.validate(actor)


def test_show_nested_object_property() -> None:
    js = schemas.show_schema(Movie)

    print(json.dumps(js, indent=2))
    assert js["type"] == "object"
    assert js["definitions"]


def test_validate_nested_object() -> None:
    with pytest.raises(validation.ValidationException) as v:
        actor = Actor(
            name="Same", sex="Male", age=10, role=Role(name="Edgar Samson", race="black")
        )
        movie = Movie(main=actor, title="T")

        print(json.dumps(schemas.show_schema(movie), indent=2))
        schemas.validate(movie)
    assert len(v.value.errors) == 1
    error = v.value.errors[0]
    assert error.element == "title"


def test_show_array_type() -> None:
    js = schemas.show_schema(Manager)
    print(json.dumps(js, indent=2))

    actor = Actor(name="Same", sex="Male", age=10, role=Role(name="Edgar Samson", race="black"))
    movie = Movie(main=actor, title="Telecon")

    mgr = Manager(actors=[actor], movies=[movie], personal={"tastes": actor})


def test_unknown_model() -> None:
    with pytest.raises(ValueError) as v:
        schemas.show_schema(Unknown)
    assert v.value


def test_from_dict() -> None:
    actor_data = {
        "name": "Mr. Brown",
        "sex": "male",
        "age": 55,
        "role": {"name": "Edgar Smith", "race": "black"},
    }
    actor = Actor(**actor_data)
    assert actor.role.name == "Edgar Smith"

    movie_data = {"main": actor_data, "title": "Space Masters"}
    movie = Movie(**movie_data)
    assert movie.title == "Space Masters"

    mgr = Manager(actors=[actor], movies=[movie], personal={"smith": actor})
    print(mgr.actors)


def test_complex_object():
    rm = RoleManager(
        roles=[
            Role(name="Captain America", race="white"),
            Role(name="Nick Fury", race="black"),
        ],
        allowed=[
            Role(name="Captain America", race="white"),
            Role(name="Nick Fury", race="black"),
        ],
        people=Actor(
            name="Steve Rogers",
            sex="male",
            age=21,
            height=5.1,
            married=True,
            role=Role(name="Captain America", race="American"),
        ),
        names="Steve",
        requires="A working bubble",
    )

    for role in rm.roles:
        assert role.name


if __name__ == "__main__":
    schemas.show_schema(Manager)
