Field Types
===========

justobjects provides support for:
- standard library types
- custom justobjects type arguments
- custom justonjects classes that can be used as typed annotations

Standard Library Types
----------------------
Standard library types can be used to annotated properties in data objects


Types
-----
justobjects provides multiple types that can be used to annotated fields

StringType
^^^^^^^^^^
Generates a jsonschema with ``type = "string"``

.. autoclass:: justobjects.jsontypes.StringType


.. automodule:: justobjects.decorators
   :members: all_of, any_of, array, boolean, integer, must_not, numeric, one_of, ref
