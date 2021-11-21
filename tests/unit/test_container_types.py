from typing import Set

import pytest

import justobjects as jo


@jo.data(typed=True)
class Answer:
    value: str


@jo.data(typed=True)
class Question:
    position: int
    answer: Answer


@jo.data(typed=True)
class Example:
    question: Question
    answers: Set[Answer]


def test_show_schema() -> None:
    schema = jo.show_schema(Question)
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    # assert "$id" in schema["properties"]
    assert "$schema" in schema["properties"]

    assert "#/definitions/Answer" == schema["properties"]["answer"]["$ref"]
    assert "Answer" in schema["definitions"]


def test_validation() -> None:

    with pytest.raises(jo.ValidationException) as v:
        qn = Question(position=1, answer=Answer(value=1))
        jo.validate(qn)
    ve = v.value.errors[0]
    assert ve.element == "value"
