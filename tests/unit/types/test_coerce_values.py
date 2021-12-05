from typing import Any, Union

import pytest

from justobjects import types, validation


@pytest.mark.parametrize(
    "value, expectation",
    [
        ("No", False),
        ("Yes", True),
        ("1", True),
        ("0", False),
        (True, True),
        (1, True),
        ("off", False),
        ("on", True),
        (b"yes", True),
        (b"no", False),
    ],
)
def test_cast_boolean(value: Union[bool, int, str], expectation: bool) -> None:
    bt = types.BooleanType()
    assert bt.coerce(value) == expectation


@pytest.mark.parametrize(
    "value",
    [10, "Aye", "fo", "s", -1, "Nana"],
)
def test_cast_boolean_invalids(value: Union[int, str]) -> None:
    bt = types.BooleanType()
    with pytest.raises(validation.ValidationException):
        bt.coerce(value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        ("10", 10.0),
        ("-1.0", -1.0),
        ("1", 1.0),
        ("0", 0.0),
        (True, 1.0),
        (False, 0.0),
        (1, 1.0),
    ],
)
def test_cast_numeric(value: Any, expectation: bool) -> None:
    nt = types.NumericType()
    assert nt.coerce(value) == expectation


@pytest.mark.parametrize(
    "value",
    ["", "Aye", "fo", "s", [], "Nana"],
)
def test_cast_numeric_invalids(value: Union[int, str]) -> None:
    nt = types.NumericType()
    with pytest.raises(validation.ValidationException):
        nt.coerce(value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        ("10", 10),
        ("-1", -1),
        ("1", 1),
        ("0", 0),
        (True, 1),
        (False, 0),
        (1, 1),
    ],
)
def test_cast_integer(value: Any, expectation: bool) -> None:
    nt = types.IntegerType()
    assert nt.coerce(value) == expectation


@pytest.mark.parametrize(
    "value",
    ["", "Aye", "fo", "s", [], "Nana"],
)
def test_cast_integer_invalids(value: Union[int, str]) -> None:
    nt = types.IntegerType()
    with pytest.raises(validation.ValidationException):
        nt.coerce(value)


@pytest.mark.parametrize(
    "value, expectation",
    [
        (bytearray("-1.0", "utf-8"), "-1.0"),
        (b"1", "1"),
        (b"0", "0"),
    ],
)
def test_cast_string(value: Any, expectation: bool) -> None:
    nt = types.StringType()
    assert nt.coerce(value) == expectation


@pytest.mark.parametrize(
    "value, expectation",
    [
        (b"9636ea5b-ede0-48c6-bfac-2a0f5f375f76", "9636ea5b-ede0-48c6-bfac-2a0f5f375f76"),
        ("97eb098c-5576-11ec-bf63-0242ac130002", "97eb098c-5576-11ec-bf63-0242ac130002"),
    ],
)
def test_cast_uuid(value: Any, expectation: str) -> None:
    nt = types.UuidType()
    assert nt.coerce(value) == expectation
