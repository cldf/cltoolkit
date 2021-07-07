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
import statistics
from pycldf import Dataset


def valid_tokens(sounds):
    """
    Make sure tokens conform to transcription system.

    :param sounds: List of Sound objects (pyclts.Sound).
    """
    if not sounds:
        return []
    tokens = [s for s in sounds]
    while True:
        if str(tokens[0]) in ["+", "_"]:
            tokens = tokens[1:]
        else:
            break
    while True:
        if str(tokens[-1]) in ["+", "_"]:
            tokens = tokens[:-1]
        else:
            break
    out = []
    for i, token in enumerate(tokens):
        if str(tokens[i]) in ["+", "_"] and i > 0 and str(tokens[i-1]) in ["+", "_"]:
            pass
        elif str(token) == "_":
            out.append("+")
        elif token.type == 'unknownsound':
            return []
        else:
            out.append(str(token))
    return out


def identity(x):
    """
    Identity function used as a default for passing functions.
    """
    return x


def jaccard(a, b):
    """
    Returns the Jaccard distance between two sets.
    """
    i, u = len(a.intersection(b)), len(a.union(b))
    if u:
        return i / u
    return 0


def cltoolkit_path(*comps):
    return Path(cltoolkit.__file__).parent.joinpath(*comps).as_posix()


def syllables(form):
    """
    Return the syllables of a given form with tokens.
    """
    out = []
    for morpheme in form.tokens.n:
        for syllable in syllabify(morpheme, output='nested'):
            yield syllable



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
        self._d = {}
        self._key = key
        list.__init__(self, items)
        for i, o in enumerate(self):
            if key(o) in self._d:
                raise KeyError("non-unique IDs encountered in DictList")
            self._d[key(o)] = i

    def __getitem__(self, item):
        if not isinstance(item, (int, slice)):
            if item not in self._d:
                raise KeyError("key not found in DictList")
            return self[self._d[item]]
        return super(DictList, self).__getitem__(item)


    def __add__(self, other):
        for item in other:
            self.append(item)
        return self

    def __iadd__(self, other):
        self.extend(other)
        return self

    def get(self, item, default=None):
        try: 
            return self.__getitem__(item)
        except KeyError:
            return default

    def append(self, item):
        idf = self._key(item)
        if idf in self:
            raise KeyError("key already exists in DictList")
        list.append(self, item)
        self._d[idf] = len(self)-1
        

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


def datasets_by_id(*ids, path='*/*/cldf/cldf-metadata.json'):
    """
    Return `pycldf` dataset instances by searching for their identifiers.
    """
    datasets = []
    for path in Path("").glob(path):
        if [did for did in ids if did in path.as_posix()]:
            datasets += [Dataset.from_metadata(path)]
    return datasets



def lingpy_columns():
    """
    Define basic columns for export to LingPy wordlists.
    """
    return [(("form", "id"), "local_id"),
                (("language", "id"), "doculect"),
                (("concept", "id"), "concept"),
                (("sense", "name"), "concept_in_source"),
                (("form", "value"), "value"),
                (("form", "form"), "form"),
                (("form", "tokens"), "tokens")]
