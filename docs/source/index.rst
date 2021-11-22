.. Just Objects documentation master file, created by
   sphinx-quickstart on Sat Sep 25 21:45:23 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Just Objects
============
A simple python data objects management and validation tool based on jsonschema_ standards.

Requirements
------------
* Python 3.6+

Objectives
----------
1. Define and demarcate data objects with just python annotations
2. Define constraints in simple jsonschema_ compliant manner
3. Validate data objects using standard jsonschema_ validators
4. Express complete jsonschema_ as simple data objects (its just objects)

Similar Projects
----------------
* pydantic_
* marshmallow_

Install
-------
install from pip

.. code-block:: bash

    $ pip install justobjects


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
        Model(a=3.1415, b=2.72, c="123")
    except jo.schemas.ValidationException as err:
        print(err.errors)


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   usage
   fields
   schemas


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _pydantic: https://pydantic-docs.helpmanual.io
.. _marshmallow: https://github.com/marshmallow-code/marshmallow
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
