from typing import Type

from mypy.plugin import ClassDefContext, Plugin
from mypy.plugins import attrs

from justobjects import typings

attrs.attr_dataclass_makers.add("justobjects.decorators.data")
# attrs.attr_class_makers.add("justobjects.data")
#
attrs.attr_attrib_makers.add("justobjects.decorators.all_of")
attrs.attr_attrib_makers.add("justobjects.decorators.any_of")
attrs.attr_attrib_makers.add("justobjects.decorators.array")
attrs.attr_attrib_makers.add("justobjects.decorators.boolean")
attrs.attr_attrib_makers.add("justobjects.decorators.integer")
attrs.attr_attrib_makers.add("justobjects.decorators.must_not")
attrs.attr_attrib_makers.add("justobjects.decorators.numeric")
attrs.attr_attrib_makers.add("justobjects.decorators.one_of")
attrs.attr_attrib_makers.add("justobjects.decorators.ref")
attrs.attr_attrib_makers.add("justobjects.decorators.string")


jo_class_markers: typings.Final = {"justobjects.data", "justobjects.decorators.data"}


class JustObjectsPlugin(Plugin):
    ...
    # def get_class_decorator_hook(
    #     self, fullname: str
    # ) -> Optional[Callable[[ClassDefContext], None]]:
    #     if fullname in jo_class_markers:
    #         # return attrs.attr_class_maker_callback
    #         return jo_class_marker_callback
    #     return None


def plugin(version: str) -> Type[Plugin]:
    return JustObjectsPlugin


def jo_class_marker_callback(ctx: ClassDefContext) -> None:
    return attrs.attr_class_maker_callback(ctx)
    # transformer = ClassTransformer(ctx)
    # transformer.transform()


class ClassTransformer:
    def __init__(self, ctx: ClassDefContext) -> None:
        self.ctx = ctx

    def transform(self) -> None:
        print(self.ctx)
