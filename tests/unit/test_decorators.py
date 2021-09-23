import pytest

from justobjects import schemas
from tests.models import Actor, Movie


def test_show_isolated_model() -> None:
    js = schemas.show(Actor)

    assert js["type"] == "object"
    assert js["required"] == ["name", "sex"]


def test_validate_isolated_model() -> None:
    actor = Actor(name="Same", sex="Male", age=10)
    assert actor.__dict__
    schemas.validate(actor)


def test_show_nested_object_property() -> None:
    js = schemas.show(Movie)

    assert js["type"] == "object"
    assert js["definitions"]


def test_validate_nested_object() -> None:
    actor = Actor(name="Same", sex="Male", age=10)
    movie = Movie(main=actor, title="T")

    with pytest.raises(schemas.ValidationException) as v:
        schemas.validate(movie)
    assert len(v.value.errors) == 1
    error = v.value.errors[0]
    assert error.element == "title"
