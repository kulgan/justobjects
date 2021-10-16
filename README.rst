justobjects
===========
|Pypi version| |Python versions| |ci| |Documentation Status|

Simple python data objects management and validation based on standard jsonschema_ concepts. Project
requires python3.6+ and allows users define how data objects should look and relate with other data objects.
Supports python3.6+ typing annotations and customs attributes for more complex relationships.

Objectives
----------
1. Define and demarcate data objects with just python annotations
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

    import json
    import justobjects as jo


    @jo.data(typed=True)
    class Model:
        a: int
        b: float
        c: str


    # display schema
    print(json.dumps(jo.show_schema(Model), indent=2))


    try:
        # fails validation
        jo.validate(Model(a=3.1415, b=2.72, c="123"))
    except jo.ValidationException as err:
        print(err.errors)


Contributing
------------
The fastest way to get feedback on contributions/bugs is create a issues_

Running Tests
-------------
The project makes use of tox to run tests and other common tasks

.. code-block:: bash

   $ tox -e py36




.. _pydantic: https://pydantic-docs.helpmanual.io
.. _jsonschema: https://json-schema.org
.. _issues: https://github.com/kulgan/justobjects/issues

.. |PyPI version| image:: https://img.shields.io/pypi/v/justobjects.svg
   :target: https://pypi.python.org/pypi/justobjects
   :alt: PyPi version

.. |ci| image:: https://github.com/kulgan/justobjects/workflows/justobjects/badge.svg
   :target: https://github.com/kulgan/justobjects/actions
   :alt: CI status

.. |Python versions| image:: https://img.shields.io/pypi/pyversions/justobjects.svg
   :target: https://pypi.org/project/justobjects
   :alt: PyPi versions

.. |Documentation status| image:: https://readthedocs.org/projects/justobjects/badge/?version=latest
   :target: https://justobjects.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
