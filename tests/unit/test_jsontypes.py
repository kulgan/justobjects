from typing import Type, Union

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
    js = obj.as_dict()

    assert js["type"] == "object"
    assert js["additionalProperties"] is True
    assert js["required"] == ["label"]
    assert js["properties"]


def test_numeric_type() -> None:
    obj = jsontypes.NumericType(default=10, maximum=100, multipleOf=2)
    js = obj.as_dict()

    assert js["type"] == "number"
    assert js["default"] == 10
    assert js["maximum"] == 100
    assert js["multipleOf"] == 2


def test_one_of_type() -> None:
    obj = jsontypes.OneOfType(
        oneOf=(jsontypes.StringType(), jsontypes.IntegerType(), jsontypes.BooleanType())
    )
    jo = obj.as_dict()
    assert len(jo["oneOf"]) == 3


def test_any_of_type() -> None:
    obj = jsontypes.AnyOfType(
        anyOf=(jsontypes.StringType(), jsontypes.IntegerType(), jsontypes.BooleanType())
    )
    jo = obj.as_dict()
    assert len(jo["anyOf"]) == 3


def test_all_of_type() -> None:
    obj = jsontypes.AllOfType(
        allOf=(jsontypes.StringType(), jsontypes.IntegerType(), jsontypes.BooleanType())
    )
    jo = obj.as_dict()
    assert len(jo["allOf"]) == 3


@pytest.mark.parametrize("schema", [jsontypes.StringType(), jsontypes.StringType(maxLength=16)])
def test_not_type(schema: jsontypes.JustSchema) -> None:
    obj = jsontypes.NotType(mustNot=schema)
    js = obj.as_dict()

    assert js["not"]
    must_not = js["not"]
    assert must_not["type"] == "string"
