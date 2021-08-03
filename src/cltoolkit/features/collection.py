import typing
import textwrap
import importlib
import collections

import attr
from pycldf.util import DictTuple
from clldutils import jsonlib

__all__ = ['Feature', 'FeatureCollection', 'get_callable']


def get_callable(s: typing.Union[str, dict, typing.Callable]) -> typing.Callable:
    """
    A "feature function" can be specified in 3 ways:

    - as Python callable object
    - as string of dot-separated names, where the part up to the last dot is taken as Python \
      module spec, and the last name as symbol to be looked up in this module
    - as `dict` with keys `class`, `args`, `kwargs`, where `class` is interpreted as above, and \
      `args` and `kwargs` are passed into the imported class to initialize an instance, the \
      `__call__` method of which will be used as "feature function".
    """
    if callable(s):
        return s
    if isinstance(s, str):
        comps = s.split('.')
        return getattr(importlib.import_module('.'.join(comps[:-1])), comps[-1])
    if isinstance(s, dict):
        return get_callable(s['class'])(*s.get('args') or [], **s.get('kwargs') or {})
    raise ValueError(s)


@attr.s(repr=False)
class Feature:
    """
    :ivar id: `str`
    :ivar name: `str`
    :ivar function: `callable`

    .. seealso:: :func:`get_callable`
    """
    id = attr.ib()
    name = attr.ib()
    function = attr.ib(converter=get_callable)
    type = attr.ib(default=None)
    note = attr.ib(default=None)
    categories = attr.ib(default=None)
    requires = attr.ib(default=None)

    def __attrs_post_init__(self):
        if hasattr(self.function, 'categories'):
            self.categories = self.function.categories
        if hasattr(self.function, 'rtype'):
            self.type = self.function.rtype
        func = getattr(self.function, '__call__', self.function)
        if hasattr(func, 'requires'):
            self.requires = func.requires

    def to_json(self) -> dict:
        def j(o, field=None):
            if field == 'type':
                return getattr(o, '__name__', str(o))
            if isinstance(o, (list, tuple)):
                return [j(oo) for oo in o]
            if hasattr(o, 'to_json'):
                return o.to_json()
            if callable(o):
                comps = [o.__module__] if o.__module__ != 'builtins' else []
                if type(o) == type(get_callable):
                    comps.append(o.__name__)
                else:
                    comps.append(o.__class__.__name__)
                res = '.'.join(comps)
                if type(o) == type(get_callable):
                    return res
                return {'class': res}
            return o
        return collections.OrderedDict([
            (f.name, j(getattr(self, f.name), field=f.name)) for f in attr.fields(self.__class__)])

    @property
    def doc(self) -> str:
        return getattr(self.function, 'doc', None) or textwrap.dedent(self.function.__doc__ or '')

    def help(self):
        print(self.doc)

    def __call__(self, param):
        return self.function(param)

    def __repr__(self):
        return "<Feature " + self.id + ">"


class FeatureCollection(DictTuple):
    """
    A collection of `Feature` instances.
    """
    def dump(self, path):
        """
        Dump feature specifications as JSON file.
        """
        jsonlib.dump([f.to_json() for f in self], path, indent=4)

    @classmethod
    def load(cls, path):
        """
        Load feature specifications from a JSON file (e.g. as created with `FeatureCollection.dump`)
        """
        return cls([Feature(**f) for f in jsonlib.load(path)])

    def __call__(self, feature, language):
        return self[feature](language)
