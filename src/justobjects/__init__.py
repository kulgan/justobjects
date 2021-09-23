from pkg_resources import get_distribution

from justobjects.decorators import data, string

VERSION = get_distribution(__name__).version

__all__ = ["data", "string", "VERSION"]
