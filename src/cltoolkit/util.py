"""
Utility functions for lexicore.
"""
from collections import OrderedDict
from lingpy.sequence.sound_classes import syllabify
from cldftk import log
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
