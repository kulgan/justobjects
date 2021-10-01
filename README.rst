justobjects
===========
Simply python data objects management and validation based on standard jsonschema_ concepts. Project
requires python3.6+ and allows users define how data objects should look and relate with other data objects.
Supports python3.6+ typing annotations and customs attributes for more complex relationships.

Objectives
----------
1. Define and demarcate data objects just python annotations
2. Define constraints in simple jsonschema_ compliant manner
3. Validate data objects using standard jsonschema_ validators
4. Express complete jsonschema_ as simple data objects (its just objects)

Similar Projects
----------------
* pydantic_

Install
-------
install from pip

.. code-block:: bash

    $ pip install justobjects

install from source

.. code-block:: bash

    $ pip install git+https://github.com/kulgan/justobjects@<version>#egg=justobjects

Usage Example
-------------
.. code-block:: python

    import justobjects as jo


    @jo.data(auto_attribs=True)
    class Model:
        a: int
        b: float
        c: str


    # display schema
    print(jo.show(Model))


    try:
        # fails validation
        jo.is_valid(Model(a=3.1415, b=2.72, c="123"))
    except jo.schemas.ValidationException as err:
        print(err.errors)


Contributing
------------
The fastest way to get feedback on contributions/bugs is create a issues_

.. _pydantic: https://pydantic-docs.helpmanual.io
.. _jsonschema: https://json-schema.org
.. _issues: https://github.com/kulgan/justobjects/issues
