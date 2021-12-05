from typing import Any

import pytest

import justobjects as jo
from justobjects import types


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
    assert types.camel_case(value) == expectation


def test_string_type() -> None:
    obj = jo.StringType(minLength=3, default="NAN")
    js = jo.as_dict(obj)

    assert js["type"] == "string"
    assert js["minLength"] == 3
    assert js["default"] == "NAN"


def test_mixin__json_schema() -> None:
    obj = jo.ObjectType(additionalProperties=True)
    obj.properties["label"] = jo.StringType(default="skin", maxLength=10)
    obj.add_required("label")
    js = jo.as_dict(obj)

    assert js["type"] == "object"
    assert js["additionalProperties"] is True
    assert js["required"] == ["label"]
    assert js["properties"]


def test_numeric_type() -> None:
    obj = jo.NumericType(default=10, maximum=100, multipleOf=2)
    js = obj.as_dict()

    assert js["type"] == "number"
    assert js["default"] == 10
    assert js["maximum"] == 100
    assert js["multipleOf"] == 2


def test_one_of_type() -> None:
    obj = jo.OneOfType(oneOf=(types.StringType(), types.IntegerType(), types.BooleanType()))
    js = obj.as_dict()
    assert len(js["oneOf"]) == 3


def test_any_of_type() -> None:
    obj = jo.AnyOfType(anyOf=(jo.StringType(), jo.IntegerType(), jo.BooleanType()))
    js = obj.as_dict()
    assert len(js["anyOf"]) == 3


def test_all_of_type() -> None:
    obj = jo.AllOfType(allOf=(jo.StringType(), jo.IntegerType(), jo.BooleanType()))
    js = obj.as_dict()
    assert len(js["allOf"]) == 3


@pytest.mark.parametrize("schema", [jo.StringType(), jo.StringType(maxLength=16)])
def test_not_type(schema: Any) -> None:
    obj = jo.NotType(mustNot=schema)
    js = obj.as_dict()

    assert js["not"]
    must_not = js["not"]
    assert must_not["type"] == "string"
