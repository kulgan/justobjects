Data Objects
============
A data object is a python class annotated with ``@jo.data``. All data objects are automatically associated with a json
schema based on the properties of the class. The associated json schema is used for validation.

Define data objects
-------------------
.. literalinclude:: ../examples/basic_usage.py
    :language: python
    :lines: 1-16

This will output

.. code-block::

  {
    "type": "object",
    "title": "Draft7 JustObjects schema for data object '__main__.Model'",
    "additionalProperties": false,
    "properties": {
      "$schema": {
        "type": "string",
        "default": "http://json-schema.org/draft-07/schema#"
      },
      "a": {
        "type": "integer",
        "maximum": 30,
        "minimum": 3,
        "multipleOf": 3
      },
      "b": {
        "type": "number",
        "default": 0.3,
        "multipleOf": 2
      },
      "c": {
        "type": "string",
        "default": "123"
      }
    }
  }


Validate Instances
------------------
Validation can be performed on model instances like this

.. literalinclude:: ../examples/basic_usage.py
    :language: python
    :lines: 17-23

validation can also be performed on dictionary instances too

.. literalinclude:: ../examples/basic_usage.py
    :language: python
    :lines: 25-29
