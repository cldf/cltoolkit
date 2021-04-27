"""
Utility functions for lexicore.
"""
from collections import OrderedDict
from lingpy.sequence.sound_classes import syllabify
from cltoolkit import log
from functools import partial
from tqdm import tqdm as progressbar
from pathlib import Path
import cltoolkit


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



