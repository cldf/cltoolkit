"""
Utility functions for lexicore.
"""
from collections import OrderedDict
from lingpy.sequence.sound_classes import syllabify
from cltoolkit import log
from functools import partial
from tqdm import tqdm as progressbar


def lower_key(dictionary, **keywords):
    out = OrderedDict([(k.lower(), v) for k, v in dictionary.items()])
    out.update(keywords)
    return out


def syllables(form):
    out = []
    for morpheme in form.tokens.n:
        for syllable in syllabify(morpheme, output='nested'):
            if not '+' in syllable:
                yield syllable
            else:
                log.warning('problematic syllable encountered in {0}'.format(
                    form.id))


class GetValueFromDict:
    def __init__(self, attr, data=None, transform=None):
        if not transform:
            self.transform = lambda x: x
        else:
            self.transform = transform
        self.attr, self.data = attr, data

    def __get__(self, obj, objtype=None):
        return self.transform(getattr(obj, self.data).get(self.attr, None))


GetValueFromData = partial(GetValueFromDict, data="data")


