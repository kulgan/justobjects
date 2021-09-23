import justobjects as jo


@jo.data(auto_attribs=True)
class Actor:
    name: str
    sex: str
    age: int = 10
