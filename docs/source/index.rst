.. Just Objects documentation master file, created by
   sphinx-quickstart on Sat Sep 25 21:45:23 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Just Objects
============
Simple Python data object definitions and validation

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   jsontypes
   decorators
   schemas

Quickstart
----------
Install from pypi via ``pip`` or add to your project requirements/dependency

.. code-block:: bash

    $ pip install justobjects

installation requires python36+ and only depends on `attrs`, `jsonschema` and `typing_extensions` for
python < 3.8

Start Defining Objects
++++++++++++++++++++++
.. literalinclude:: ../examples/objects_with_jo.py
    :language: python
    :lines: 1-20


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
