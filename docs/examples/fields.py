import json

import justobjects as jo

# display schema
from justobjects import IntegerType, OneOfType, StringType


@jo.data(typed=True)
class Smoke:
    name: str


sc = StringType(maxLength=16, minLength=2)
print(jo.show_schema(sc))

of = OneOfType(oneOf=[StringType(), IntegerType(), Smoke])

sc.validate("200")  # valid
print(of.as_dict())
of.validate({"names": "peace"})

#     # fails validation
#     jo.validate(Model(a=3.1415, b=2.72, c="123"))
# except jo.schemas.ValidationException as err:
#     print(err.errors)
