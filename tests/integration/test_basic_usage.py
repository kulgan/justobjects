import pytest

import justobjects as jo
from tests.models import Role


def test_validate_dict() -> None:
    role = {"name": "Simons"}

    with pytest.raises(jo.ValidationException) as v:
        jo.is_valid_data(Role, role)
    assert len(v.value.errors) == 1
    err = v.value.errors[0]
    assert err.message == f"'race' is a required property"


def test_validate_multiple() -> None:
    roles = [{"name": "Edgar"}, {"race": "white"}]
    with pytest.raises(jo.ValidationException) as v:
        jo.is_valid_data(Role, roles)
    assert len(v.value.errors) == 2
