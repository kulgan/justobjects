import json

import justobjects as jo

# display schema
from justobjects import StringType

sc = StringType(maxLength=16, minLength=2)
print(jo.show_schema(sc))

sc.validate("200")  # valid
sc.validate("A")

#     # fails validation
#     jo.validate(Model(a=3.1415, b=2.72, c="123"))
# except jo.schemas.ValidationException as err:
#     print(err.errors)
