"""
Utility functions for lexicore.
"""
import pathlib
import operator
from typing import Callable, Any, TypeVar
from collections.abc import Hashable

from lingpy.sequence.sound_classes import syllabify
from lingpy.basictypes import lists
from pycldf import Dataset

__all__ = ['valid_sounds', 'identity', 'jaccard', 'iter_syllables', 'DictTuple']

T = TypeVar('T')


def valid_sounds(sounds) -> list[str]:
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
    return lists(out)


def identity(x):
    """
    Identity function used as a default for passing functions.
    """
    return x


def jaccard(a: set, b: set) -> float:
    """
    Returns the Jaccard distance between two sets.
    """
    i, u = len(a.intersection(b)), len(a.union(b))
    return i / u if u else 0


def iter_syllables(form):
    """
    Return the syllables of a given form with tokens.
    """
    for morpheme in form.sounds.n:
        for syllable in syllabify(morpheme, output='nested'):
            yield syllable


class DictTuple(tuple[T]):
    """
    An object allowing access to items of a `tuple` as if it were a `dict` keyed with the `id`
    attribute of the contained objects.
    """
    def __new__(cls, items=None, **kw):
        return super().__new__(cls, tuple(items or []))

    def __init__(self, _=None, key: Callable[[Any], Hashable] = operator.attrgetter('id')):
        """
        If `key` does not return unique values for all items, you may pass `multi=True` to
        retrieve `list`s of matching items for `l[key]`.
        """
        self._index = {key(o): o for o in self}

    def get(self, item, default=None):
        try:
            return self.__getitem__(item)
        except KeyError:
            return default

    def __getitem__(self, item):
        if not isinstance(item, (int, slice)):
            return self._index[getattr(item, 'id', item)]
        if item in self._index:
            return self._index[item]
        return super().__getitem__(item)

    def __contains__(self, item):
        return (getattr(item, 'id', item) in self._index) or (super().__contains__(item))

    def items(self):
        yield from self._index.items()


def datasets_by_id(*ids, path='*/*/cldf/cldf-metadata.json', base_dir="."):
    """
    Return `pycldf` dataset instances by searching for their identifiers.
    """
    datasets = []
    for path in pathlib.Path(base_dir).glob(path):
        if any(did in str(path) for did in ids):
            datasets.append(Dataset.from_metadata(path))
    return datasets


def lingpy_columns(**kw):
    """
    Define basic columns for export to LingPy wordlists.
    """
    base = [
        (("form", "id"), "local_id"),
        (("language", "id"), "doculect"),
        (("concept", "id"), "concept"),
        (("sense", "name"), "concept_in_source"),
        (("form", "value"), "value"),
        (("form", "form"), "form"),
        (("form", "sounds"), "tokens")]
    if "cognates" in kw:
        base += [(("cognates", kw["cognates"]), "cognacy")]

    return base
