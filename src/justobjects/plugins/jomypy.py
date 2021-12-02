from typing import Type

from mypy.plugin import Plugin
from mypy.plugins import attrs

attrs.attr_dataclass_makers.add("justobjects.decorators.data")
attrs.attr_class_makers.add("justobjects.decorators.data")
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


class JustObjectsPlugin(Plugin):
    ...
    # def get_class_decorator_hook(
    #     self, fullname: str
    # ) -> Optional[Callable[[ClassDefContext], None]]:
    #     if fullname in attrs.attr_class_makers:
    #         print(fullname)
    #         return attrs.attr_class_maker_callback
    #
    #     elif fullname in attrs.attr_dataclass_makers:
    #         print(fullname)
    #         return partial(attrs.attr_class_maker_callback, auto_attribs_default=True)
    #
    #     # elif fullname in dataclass_makers:
    #     #     return dataclass_class_maker_callback
    #     return None
    #
    # def get_type_analyze_hook(self, fullname: str
    #                           ) -> Optional[Callable[[AnalyzeTypeContext], Type]]:


def plugin(version: str) -> Type[Plugin]:
    return JustObjectsPlugin
