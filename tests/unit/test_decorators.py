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


def test_object_property() -> None:
    js = schemas.show(Movie)

    print(js)
