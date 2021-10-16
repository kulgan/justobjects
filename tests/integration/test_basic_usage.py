import pytest

import justobjects as jo
from tests.models import Role


def test_validate_dict() -> None:
    role = {"name": "Simons"}

    with pytest.raises(jo.ValidationException) as v:
        jo.validate(Role, role)
    assert len(v.value.errors) == 1
    err = v.value.errors[0]
    assert err.message == f"'race' is a required property"


@pytest.mark.skip(reason="Not supporting multiple data validation at this point")
def test_validate_multiple() -> None:
    roles = [{"name": "Edgar"}, {"race": "white"}]
    with pytest.raises(jo.ValidationException) as v:
        jo.validate(Role, roles)
    assert len(v.value.errors) == 2
