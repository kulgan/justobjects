import json

import pytest

from justobjects import schemas
from tests.models import Actor, Manager, Movie, Role, Unknown


def test_show_isolated_model() -> None:
    js = schemas.show(Actor)

    assert js["type"] == "object"
    model = js["definitions"]["Actor"]
    assert model["required"] == ["name", "sex", "role"]


def test_validate_isolated_model() -> None:
    actor = Actor(name="Same", sex="Male", age=10, role=Role(name="Simons", race="white"))
    assert actor.__dict__
    schemas.is_valid(actor)


def test_show_nested_object_property() -> None:
    js = schemas.show(Movie)

    print(json.dumps(js, indent=2))
    assert js["type"] == "object"
    assert js["definitions"]


def test_validate_nested_object() -> None:
    actor = Actor(name="Same", sex="Male", age=10, role=Role(name="Edgar Samson", race="black"))
    movie = Movie(main=actor, title="T")

    with pytest.raises(schemas.ValidationException) as v:
        schemas.is_valid(movie)
    assert len(v.value.errors) == 1
    error = v.value.errors[0]
    assert error.element == "title"


def test_show_array_type() -> None:
    js = schemas.show(Manager)

    print(json.dumps(js, indent=2))


def test_unknown_model() -> None:
    with pytest.raises(ValueError) as v:
        schemas.show(Unknown)
    assert v.value


if __name__ == "__main__":
    schemas.show(Manager)
