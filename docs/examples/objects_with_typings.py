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
