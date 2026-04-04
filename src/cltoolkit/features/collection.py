import json
from typing import Callable, Union, Optional, TYPE_CHECKING
import pathlib
import textwrap
import importlib
import collections
import dataclasses

from pycldf.util import DictTuple

if TYPE_CHECKING:
    from ..models import Language


__all__ = ['Feature', 'FeatureCollection', 'get_callable']


def get_callable(s: Union[str, dict, Callable]) -> Callable:
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


@dataclasses.dataclass(repr=False)
class Feature:
    """
    :ivar id: `str`
    :ivar name: `str`
    :ivar function: `callable`

    .. seealso:: :func:`get_callable`
    """
    id: str
    name: str
    function: Callable
    type: Optional[type] = None
    note: Optional[str] = None
    categories: dict[Union[int, bool, None], str] = dataclasses.field(default_factory=dict)
    requires: Optional[tuple[Callable[['Language'], bool]]] = None

    def __post_init__(self):
        self.function = get_callable(self.function)
        if getattr(self.function, 'categories', None):
            self.categories = self.function.categories
        if getattr(self.function, 'rtype', None):
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
            (f.name, j(getattr(self, f.name), field=f.name))
            for f in dataclasses.fields(self.__class__)])

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
        with pathlib.Path(path).open('w', encoding='utf-8') as fp:
            return json.dump([f.to_json() for f in self], fp, indent=4)

    @classmethod
    def load(cls, path):
        """
        Load feature specifications from a JSON file (e.g. as created with `FeatureCollection.dump`)
        """
        with pathlib.Path(path).open(encoding='utf-8') as fp:
            return cls([Feature(**f) for f in json.load(fp)])

    def __call__(self, feature, language):
        return self[feature](language)
