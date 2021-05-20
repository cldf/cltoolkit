"""
Module handles different aspects of inventory comparison.
"""
import attr
from collections import OrderedDict, namedtuple
from pyclts.api import CLTS
import statistics
from pyclts.util import jaccard
from pycldf.util import DictTuple
from cltoolkit.util import GetAttributeFromData
from cltoolkit.models import Phoneme
from cltoolkit.util import jaccard


def jaccard(a, b):
    i, u = len(a.intersection(b)), len(a.union(b))
    if u:
        return i / u
    return 0


class GetSubInventoryByType:
    def __init__(self, types):
        def select_sounds(inventory):
            return DictTuple( 
                [v for v in inventory if v.type in types]
            )
        self.select_sounds = select_sounds

    def __get__(self, obj, objtype=None):
        return self.select_sounds(obj.sounds)


class GetSubInventoryByProperty(GetSubInventoryByType):
    def __init__(self, types, properties):
        GetSubInventoryByType.__init__(self, types)
        self.properties = properties

    def __get__(self, obj, objtype=None):
        out = []
        # todo manage "contains" statement here
        sounds = self.select_sounds(obj.sounds)
        sound_set = set([sound.grapheme for sound in sounds])
        for v in sounds:
            stripped = obj.ts.features.get(
                frozenset([s for s in v.featureset if s not in self.properties])
            )
            if str(stripped) != str(v) and str(stripped) not in sound_set:
                out += [v]
            elif str(stripped) == str(v):
                out += [v]
        return DictTuple(out)


@attr.s
class Inventory:
    language = attr.ib(default=None)
    sounds = attr.ib(default=None, repr=False)
    ts = attr.ib(default=None, repr=False)

    consonants = GetSubInventoryByType(["consonant"])
    consonants_by_quality = GetSubInventoryByProperty(
        ["consonant"], ["long", "ultra-long", "mid-long", "ultra-short"]
    )
    consonant_sounds = GetSubInventoryByType(["consonant", "cluster"])
    vowels = GetSubInventoryByType(["vowel"])
    vowels_by_quality = GetSubInventoryByProperty(
        ["vowel"], ["long", "ultra-long", "mid-long", "ultra-short"]
    )
    vowel_sounds = GetSubInventoryByType(["vowel", "diphthong"])
    segments = GetSubInventoryByType(["consonant", "vowel", "cluster", "diphthong"])
    tones = GetSubInventoryByType(["tone"])
    markers = GetSubInventoryByType(["marker"])
    clusters = GetSubInventoryByType(["cluster"])
    diphthongs = GetSubInventoryByType(["diphthong"])
    unknownsounds = GetSubInventoryByType(["unknownsound"])

    @classmethod
    def from_list(cls, *list_of_sounds, language=None, ts=None):
        ts = ts or CLTS().bipa
        sounds = OrderedDict()
        for itm in list_of_sounds:
            sound = ts[itm]
            try:
                sounds[str(sound)].graphemes_in_source.append(itm)
            except KeyError:
                sounds[str(sound)] = Phoneme(
                    id=sound.name,
                    grapheme=str(sound),
                    graphemes_in_source=[sound.grapheme],
                    occs=[],
                    sound=sound)
        return cls(sounds=DictTuple(sounds.values()), ts=ts, language=language)

    def __len__(self):
        return len(self.sounds)

    def __iter__(self):
        return iter(self.sounds)

    def strict_similarity(self, other, aspects=None):
        aspects = aspects or ["sounds"]
        scores = []
        for aspect in aspects:
            soundsA, soundsB = (
                {sound.grapheme for sound in getattr(self, aspect)},
                {sound.grapheme for sound in getattr(other, aspect)},
            )
            if soundsA or soundsB:
                scores += [jaccard(soundsA, soundsB)]
        if not scores:
            return 0
        return statistics.mean(scores)

    def approximate_similarity(self, other, aspects=None):
        aspects = aspects or ["sounds"]

        def approximate(soundsA, soundsB):
            matches = []
            for soundA in soundsA:
                best_match, best_sim = None, 0
                for soundB in soundsB:
                    current_sim = soundA.similarity(soundB)
                    if current_sim > best_sim:
                        best_match = soundB
                        best_sim = current_sim
                if best_match is not None:
                    matches += [best_sim]
                    soundsB = [s for s in soundsB if s != best_match]
            matches += [0 for s in soundsB]
            return statistics.mean(matches)

        scores = []
        for aspect in aspects:
            soundsA, soundsB = (
                getattr(self, aspect),
                getattr(other, aspect),
            )
            if soundsA and soundsB:
                scores += [
                    statistics.mean(
                        [approximate(soundsA, soundsB), approximate(soundsB, soundsA)]
                    )
                ]
            elif soundsA or soundsB:
                scores += [0]
        if not scores:
            return 0
        return statistics.mean(scores)
