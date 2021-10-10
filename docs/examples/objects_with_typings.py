import justobjects as jo


@jo.data(typed=True)
class Model:
    a: int
    b: float
    c: str


# display schema
print(jo.show_schema(Model))


try:
    # fails validation
    jo.validate(Model(a=3.1415, b=2.72, c="123"))
except jo.schemas.ValidationException as err:
    print(err.errors)
