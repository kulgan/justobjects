import enum
from typing import Optional, Union, Iterable

import attr

from justobjects.jsontypes import ObjectType, StringType


JO_SCHEMA = "__jo__"
JO_REQUIRED = "__jo__required__"


def data(
    additional_properties=None,
    required=None,
):
    """decorates a class automatically binding it to a Schema instance
    This technically extends `attr.s` amd pulls out a Schema instance in the process
    Args:
        additional_properties (bool): True if additional properties are allowed
        required (list[str]): list of required property names
    Returns:
        attr.s: and attr.s wrapped class
    Example:
        .. code-block::
            import justobjects as jo
            @jo.data()
            class Sample(object):
                age = jo.integer(required=True, minimum=18)
                name = jo.string(required=True)
    """

    def wraps(cls):
        req = required or []
        setattr(cls, "additional_properties", additional_properties)

        def jo_schema(cls):
            sc = ObjectType(
                additional_properties=additional_properties,
            )
            sc.properties = {}
            attributes = cls.__attrs_attrs__
            for attrib in attributes:
                psc = attrib.metadata[JO_SCHEMA]
                is_required = attrib.metadata.get(JO_REQUIRED, False)
                field_name = attrib.name
                if is_required and field_name not in req:
                    req.append(field_name)
                sc.properties[field_name] = psc

            if req:
                sc.required = req
            return sc

        setattr(cls, "jo_schema", classmethod(jo_schema))
        return attr.s(cls)

    return wraps


def string(
    default: Optional[str] = None,
    required: bool = False,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    enums: Optional[Union[Iterable[str], enum.Enum]] = None,
    description: Optional[str] = None,
):
    """Creates a json schema of type string
    Args:
        default (str): default value
        required (bool): True if it should be required in the schema
        min_length (int): minimum length of the string
        max_length (int): maximum length of the strin
        enums: represent schema as an enum instead of free text
        description (str): Property description
    Returns:
        attr.ib: field definition
    """
    if isinstance(enums, enum.Enum):
        if enums.member_type != str:
            raise ValueError("Invalid enum")
    sc = StringType(
        min_length=min_length,
        max_length=max_length,
        enum=enums,
        description=description,
    )
    return attr.ib(type=str, default=default, metadata={JO_SCHEMA: sc, JO_REQUIRED: required})


class ex(enum.Enum):
    one = 1
    two = 2


@attr.s
class Past:
    gh = string(enums=ex)


if __name__ == '__main__':
    pas = Past(gh="2")
    print(pas)
