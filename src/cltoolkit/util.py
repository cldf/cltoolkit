"""
Utility functions for lexicore.
"""
from collections import OrderedDict, defaultdict
from lingpy.sequence.sound_classes import syllabify
from cltoolkit import log
from functools import partial
from tqdm import tqdm as progressbar
from pathlib import Path
import cltoolkit


def identity(x):
    return x


def cltoolkit_path(*comps):
    return Path(cltoolkit.__file__).parent.joinpath(*comps).as_posix()


def syllables(form):
    out = []
    for morpheme in form.tokens.n:
        for syllable in syllabify(morpheme, output='nested'):
            if not '+' in syllable:
                yield syllable
            else:
                log.warning('problematic syllable encountered in {0}'.format(
                    form.id))


class GetDataFromObject:
    def __init__(self, attr, data=None, transform=None):
        if not transform:
            self.transform = lambda x: x
        else:
            self.transform = transform
        self.attr, self.data = attr, data


class GetAttributeFromObject(GetDataFromObject):
    def __get__(self, obj, objtype=None):
        return getattr(getattr(obj, self.data), self.attr, None)


class GetValueFromDict(GetDataFromObject):
    def __get__(self, obj, objtype=None):
        return self.transform(getattr(obj, self.data).get(self.attr, None))


GetValueFromData = partial(GetValueFromDict, data="data")


class DictList(list):
    """
    A `list` that acts like a `dict` when a `str` is passed to `__getitem__`.

    Extends upon the DictTuple class of pycldf.util.
    """
    def __new__(cls, items, **kw):
        return super(DictList, cls).__new__(cls, list(items))

    def __init__(self, items, key=lambda i: i.id):
        """
        If `key` does not return unique values for all items, you may pass `multi=True` to
        retrieve `list`s of matching items for `l[key]`.
        """
        self._d = defaultdict(list)
        self._key = key
        list.__init__(self, items)
        for i, o in enumerate(self):
            self._d[key(o)].append(i)

    def __getitem__(self, item):
        if not isinstance(item, (int, slice)):
            if item not in self._d:
                raise KeyError("key not found")
            return self[self._d[item][0]]
        return super(DictList, self).__getitem__(item)


    def __add__(self, other):
        for item in other:
            idf = self._key(item)
            if idf not in self:
                list.append(self, item)
                self._d[idf] += [len(self)-1]
        return self

    def __iadd__(self, other):
        self.extend(other)

    def remove(self, item):
        if not isinstance(item, (int, slice)):
            if item not in self._d:
                raise KeyError("key not found")
            super(DictList, self).pop(self._d[item][0])
            del self._d[item]
        else:
            del self._d[self[item].id]
            super(DictList, self).pop(item)


    def get(self, item, default=None):
        try: 
            self.__getitem__(item)
        except KeyError:
            return default

    def append(self, item):
        idf = self._key(item)
        if idf not in self:
            list.append(self, item)
            self._d[idf] += [len(self)-1]

    def extend(self, others):
        for other in others:
            self.append(other)

    def __contains__(self, item):
        if hasattr(item, "id"):
            if item.id in self._d:
                return True
            return False
        elif item in self._d:
            return True
        return False


def lingpy_columns():
    return [(("form", "id"), "local_id"),
                (("language", "id"), "doculect"),
                (("concept", "id"), "concept"),
                (("sense", "name"), "concept_in_source"),
                (("form", "value"), "value"),
                (("form", "form"), "form"),
                (("form", "tokens"), "tokens")]
