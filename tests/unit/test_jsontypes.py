import pytest

from justobjects import jsontypes


@pytest.mark.parametrize(
    "value,expectation",
    [
        ("oslo_health", "osloHealth"),
        ("a_b_c", "aBC"),
        ("oslo_health_a", "osloHealthA"),
        ("Oslo_health", "OsloHealth"),
    ],
)
def test_to_camel_case(value: str, expectation: str) -> None:
    assert jsontypes.camel_case(value) == expectation


def test_mixin__json_schema() -> None:
    obj = jsontypes.ObjectType(additionalProperties=True)
    obj.properties["label"] = jsontypes.StringType(default="skin", maxLength=10)
    obj.add_required("label")
    js = obj.json_schema()

    assert js["type"] == "object"
    assert js["additionalProperties"] is True
    assert js["required"] == ["label"]
    assert js["properties"]


def test_numeric_type() -> None:
    obj = jsontypes.NumericType(default=10, maximum=100, multipleOf=2)
    js = obj.json_schema()

    assert js["type"] == "number"
    assert js["default"] == 10
    assert js["maximum"] == 100
    assert js["multipleOf"] == 2


def test_oneof_type() -> None:
    obj = jsontypes.OneOfType(
        oneOf=[jsontypes.StringType, jsontypes.IntegerType, jsontypes.BasicType]
    )
    print(obj.json_schema())
