"""
Basic models.
"""

from collections import OrderedDict
import attr
from cltoolkit.util import GetValueFromData, GetAttributeFromObject, DictList
import lingpy
from pycldf.util import DictTuple
from pyclts import CLTS
from functools import cached_property



@attr.s(repr=False)
class CLCore:
    id = attr.ib()
    wordlist = attr.ib(default=None)
    data = attr.ib(default=None)


    def __repr__(self):
        return "<"+self.__class__.__name__+" "+self.id+">"


@attr.s(repr=False)
class CLCoreWithForms(CLCore):
    forms = attr.ib(default=None)
    
    @cached_property
    def bipa_forms(self):
        return DictList([f for f in self.forms if f.tokens])

    @cached_property
    def segmented_forms(self):
        return DictList([f for f in self.forms if f.segments])


@attr.s(repr=False)
class CLBase(CLCore):
    """
    Base class.
    """
    obj = attr.ib(default=None, repr=False)
    dataset = attr.ib(default=None, repr=False)


@attr.s(repr=False)
class CLBaseWithForms(CLCoreWithForms):
    obj = attr.ib(default=None, repr=False)
    dataset = attr.ib(default=None, repr=False)


@attr.s(repr=False)
class Language(CLBaseWithForms):
    """
    Base class for handling languages.
    """
    senses = attr.ib(default=None)
    concepts = attr.ib(default=None)
    glottocode = GetValueFromData("Glottocode")
    name = GetValueFromData("Name")
    macroarea = GetValueFromData("Macroarea")
    latitude = GetValueFromData("latitude")
    longitude = GetValueFromData("longitude")
    family = GetValueFromData("Family")
    subgroup = GetValueFromData("SubGroup")


    @cached_property
    def sound_inventory(self):
        sounds = DictList([])
        for sound in self.wordlist.sounds:
            if self.id in sound.occs:
                sounds.append(Sound.from_sound(sound, language=self))
        return Inventory(language=self, ts=self.wordlist.ts,
                sounds=sounds)



@attr.s(repr=False)
class Sense(CLBaseWithForms):
    """
    Concepts in source are the original concepts in the individual wordlists.
    """
    language = attr.ib(default=None)
    name = GetValueFromData("Name")

    def __repr__(self):
        return '<Sense '+self.id+'>'

    def __eq__(self, other):
        return self.name == other.name

    @classmethod
    def from_sense(cls, sense, language, forms):
        return cls(
                id=sense.id,
                data=sense.data,
                obj=sense.obj,
                forms=forms,
                dataset=sense.dataset,
                wordlist=sense.wordlist,
                language=language)


@attr.s(repr=False)
class Concept(CLCoreWithForms):
    """
    Base class for the concepts in a dataset.
    """
    language = attr.ib(default=None)
    senses = attr.ib(default=None)
    name = attr.ib(default=None)
    concepticon_id = attr.ib(default=None)
    concepticon_gloss = attr.ib(default=None)

    @classmethod
    def from_sense(
            cls, concept, id=None, name=None, wordlist=None, forms=None,
            senses=None):
        return cls(
                name=name,
                id=id,
                concepticon_id=concept.data["Concepticon_ID"],
                concepticon_gloss=concept.data["Concepticon_Gloss"],
                forms=forms,
                senses=senses
                )

    @classmethod
    def from_concept(cls, concept, language, forms=None,
            senses=None, wordlist=None, dataset=None):
        return cls(
                id=concept.id,
                name=concept.name,
                concepticon_id=concept.concepticon_id,
                concepticon_gloss=concept.concepticon_gloss,
                senses=senses,
                forms=forms,
                )

    def __repr__(self):
        return "<Concept "+ self.name+">"


@attr.s(repr=False)
class Form(CLBase):
    
    concept = attr.ib(default=None, repr=False)
    language = attr.ib(default=None, repr=False)
    sense = attr.ib(default=None, repr=False)
    tokens = attr.ib(default=None, repr=False)
    value = GetValueFromData("Value")
    form = GetValueFromData("Form")
    segments = GetValueFromData("Segments", transform=lingpy.basictypes.lists)

    @property
    def sounds(self):
        return [self.wordlist.sounds[self.wordlist.ts[t].name] for t in
                self.tokens]

    @property
    def graphemes(self):
        return [self.wordlist.graphemes["grapheme-"+s] for s in
                self.segments]

    def __repr__(self):
        return "<"+self.__class__.__name__+" "+self.form+">"


@attr.s(repr=False)
class Grapheme(CLBaseWithForms):
    occs = attr.ib(default=None)
    

@attr.s(repr=False)
class Sound(Grapheme):
    """
    All sounds in a dataset.
    """
    grapheme = attr.ib(default=None)
    graphemes_in_source = attr.ib(default=None)
    language = attr.ib(default=None)

    type = GetValueFromData("type")
    name = GetAttributeFromObject("name", data="obj")
    featureset = GetAttributeFromObject("featureset", data="obj")

    @classmethod
    def from_grapheme(cls, grapheme_, grapheme=None, occs=None, forms=None,
            id=None, graphemes_in_source=None):
        return cls(
                id=id, 
                grapheme=grapheme,
                wordlist=grapheme_.wordlist,
                occs=occs,
                data=grapheme_.obj.__dict__,
                graphemes_in_source=graphemes_in_source,
                forms=forms,
                obj=grapheme_.obj)

    def __len__(self):
        return len(self.occs or [])

    def __str__(self):
        return self.grapheme

    def __eq__(self, other):
        return self.grapheme == other.grapheme

    def __repr__(self):
        return "<"+self.__class__.__name__+" "+self.grapheme+">"

    def similarity(self, other):
        if self.type not in ["marker", "unknownsound"] and other.type not in ["marker", "unknownsound"]:
            return self.obj.similarity(other.obj)
        elif self.type in ["marker", "unknownsound"] and other.type in ["marker", "unknownsound"]:
            if self == other:
                return 1
            return 0
        return 0

    @classmethod
    def from_sound(cls, sound, language):
        return cls(
                id=sound.id,
                language=language,
                data=sound.data,
                obj=sound.obj,
                dataset=sound.dataset,
                wordlist=sound.wordlist,
                grapheme=sound.grapheme,
                occs=sound.occs[language.id]
                )



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
    def from_list(
            cls, 
            *list_of_sounds, 
            language=None, 
            ts=None, 
            wordlist=None, 
            dataset=None
            ):
        ts = ts or CLTS().bipa
        sounds = OrderedDict()
        for itm in list_of_sounds:
            sound = ts[itm]
            try:
                sounds[str(sound)].graphemes_in_source.append(itm)
            except KeyError:
                sounds[str(sound)] = Sound(
                    id=sound.name.replace(' ','_'),
                    obj=sound,
                    wordlist=wordlist,
                    dataset=dataset,
                    grapheme=str(sound),
                    graphemes_in_source=[sound.grapheme],
                    occs=[],
                    data=sound.__dict__)
        return cls(sounds=DictTuple(sounds.values()), ts=ts, language=language)

    def __len__(self):
        return len(self.sounds)

    def __iter__(self):
        return iter(self.sounds)

    def __getitem__(self, idx):
        return self.sounds[idx]

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
