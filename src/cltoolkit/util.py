"""
Utility functions for lexicore.
"""
import inspect
import pathlib
import functools

from lingpy.sequence.sound_classes import syllabify
from pycldf import Dataset
from pycldf.util import DictTuple as BaseDictTuple
from pylexibank import Dataset as LexiSet

__all__ = [
    'valid_tokens', 'identity', 'jaccard', 'iter_syllables',
    'DictTuple', 'NestedAttribute', 'MutatedDataValue', 'MutatedNestedDictValue']


def dataset_from_module(mod):
    for _, obj in inspect.getmembers(mod):
        if inspect.isclass(obj) and issubclass(obj, LexiSet) and not obj.__subclasses__():
            return Dataset.from_metadata(obj().cldf_dir / 'cldf-metadata.json')


def valid_tokens(sounds):
    """
    Make sure tokens conform to transcription system.

    :param sounds: List of Sound objects (pyclts.Sound).
    """
    if not sounds:
        return []
    tokens = [s for s in sounds]
    while str(tokens[0]) in ["+", "_"]:
        tokens = tokens[1:]
    while str(tokens[-1]) in ["+", "_"]:
        tokens = tokens[:-1]
    out = []
    for i, token in enumerate(tokens):
        if str(tokens[i]) in ["+", "_"] and i > 0 and str(tokens[i - 1]) in ["+", "_"]:
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
    return i / u if u else 0


def iter_syllables(form):
    """
    Return the syllables of a given form with tokens.
    """
    for morpheme in form.tokens.n:
        for syllable in syllabify(morpheme, output='nested'):
            yield syllable


class NestedAttribute:
    """
    A descriptor implementing a nested attribute getter.

    Used to implement Facade-pattern-style access to complex attribute data.

    .. code-block:: python

        >>> class C:
        ...     a = 'ABC'
        ...     b = NestedAttribute('a', 'lower')
        ...
        >>> C().b()
        'abc'

    .. seealso:: https://en.wikipedia.org/wiki/Facade_pattern
    """
    def __init__(self, outer_attribute, inner_attribute):
        self._outer = outer_attribute
        self._inner = inner_attribute

    def __get__(self, obj, objtype=None):
        return getattr(getattr(obj, self._outer), self._inner, None)


class MutatedNestedDictValue:
    """
    Descriptor to retrieve a mutated value of a nested `dict`.

    Used to implement Facade-pattern-style access to complex attribute data.

    .. code-block:: python

        >>> class C:
        ...     a = {'x': 5}
        ...     b = MutatedNestedDictValue('a', 'x', transform=lambda x: x + 5)
        ...
        >>> C().b
        10

    .. seealso:: https://en.wikipedia.org/wiki/Facade_pattern
    """
    def __init__(self, attribute, key, transform=identity):
        self.transform = transform
        self.attr, self.key = attribute, key

    def __get__(self, obj, objtype=None):
        return self.transform(getattr(obj, self.attr).get(self.key, None))


MutatedDataValue = functools.partial(MutatedNestedDictValue, 'data')


class DictTuple(BaseDictTuple):
    def get(self, item, default=None):
        try:
            return self.__getitem__(item)
        except KeyError:
            return default

    def __getitem__(self, item):
        if not isinstance(item, (int, slice)):
            if item not in self._d:
                raise KeyError(item)
        return super(DictTuple, self).__getitem__(item)

    def __contains__(self, item):
        return getattr(item, 'id', item) in self._d

    def items(self):
        for k, v in self._d.items():
            yield k, self[v[0]]


def datasets_by_id(*ids, path='*/*/cldf/cldf-metadata.json', base_dir="."):
    """
    Return `pycldf` dataset instances by searching for their identifiers.
    """
    datasets = []
    for path in pathlib.Path(base_dir).glob(path):
        if any(did in str(path) for did in ids):
            datasets.append(Dataset.from_metadata(path))
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
