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
^^^^^^^^^^^^^^^^^^
Validation can be performed on model instances like this

.. literalinclude:: ../examples/basic_usage.py
    :language: python
    :lines: 17-23

validation can also be performed on dictionary instances too

.. literalinclude:: ../examples/basic_usage.py
    :language: python
    :lines: 25-29


Object Fields
-------------
Class fields can be defined using either of the following:

- PEP-526_ annotations on Python 3.6+
- type arguments using ``jo`` field types


PEP 526 fields definitions
^^^^^^^^^^^^^^^^^^^^^^^^^^
``typed=True`` flag can be used to signify the model properties are defined using type annotations.

.. note::
  Type annotations can only be used for basic constraint definitions. For example they cannot be used to defined custom constraints on string fields like maxLenght or pattern. For these the provided custom field types are more suitable.

.. literalinclude:: ../examples/basic_usage.py
    :language: python
    :lines: 31-37

.. _PEP-526: https://www.python.org/dev/peps/pep-0526/
