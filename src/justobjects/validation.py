from typing import Any, Dict, Iterable, List

import attr
from jsonschema import Draft7Validator


@attr.s(frozen=True, auto_attribs=True)
class ValidationError:
    """Data object representation for validation errors

    Attributes:
        element (str): name of the affected column, can be empty
        message (str): associated error message
    """

    element: str
    message: str


def parse_errors(validator: Draft7Validator, instance: Dict) -> List[ValidationError]:
    errors: List[ValidationError] = []
    for e in validator.iter_errors(instance):
        str_path = ".".join([str(entry) for entry in e.path])
        errors.append(ValidationError(str_path, e.message))
    return errors


def validate(schema: Dict[str, Any], instance: Any) -> None:
    """Validates if a data sample is valid for the given data object type

    This is best suited for validating existing json data without having to creating instances of
    the model

    Args:
        schema: data object type with schema defined
        instance: dictionary or list of data instances that needs to be validated
    Raises:
        ValidationException
    Examples:
       .. code-block:: python

          import justobjects as jo

          @jo.data()
          class Model:
            a = jo.integer(minimum=18)
            b = jo.boolean()

          is_valid_data(Model, {"a":4, "b":True})
    """
    validator = Draft7Validator(schema=schema)

    errors: List[ValidationError] = parse_errors(validator, instance)
    if errors:
        raise ValidationException(errors=errors)


class ValidationException(Exception):
    """Custom Exception class for validation errors

    Attributes:
        errors: list of errors encountered during validation
    """

    def __init__(self, errors: List[ValidationError]):
        super(ValidationException, self).__init__(f"Data validation error: {errors}")
        self.errors = errors
