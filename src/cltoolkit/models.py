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
class CLBase:
    """
    Base class.
    """
    id = attr.ib()
    cldf = attr.ib(default=None, repr=False)
    dataset = attr.ib(default=None, repr=False)
    wordlist = attr.ib(default=None, repr=False)
    data = attr.ib(default=None, repr=False)

    def __repr__(self):
        return self.id


@attr.s(repr=False)
class Language(CLBase):
    """
    Base class for handling languages.
    """
    glottocode = GetValueFromData("Glottocode")
    name = GetValueFromData("Name")
    macroarea = GetValueFromData("Macroarea")
    latitude = GetValueFromData("latitude")
    longitude = GetValueFromData("longitude")
    family = GetValueFromData("Family")
    subgroup = GetValueFromData("SubGroup")
    forms = attr.ib(default=[], repr=False)
    concepts = attr.ib(default=[], repr=False)

    def __repr__(self):
        return '<Language '+self.id+">"
    
    #@cached_property
    #def forms(self):
    #    return DictList([
    #        form for form in self.wordlist.forms if form.language.id = self.id])

    #@cached_property
    #def concepts(self):
    #    concepts = DictList([])
    #    for form in self.forms:
    #        try:
    #            concepts[self.id+"-"+form.concept.id]["forms"] += [form]
    #        except KeyError:
    #            concepts.append(
    #                    ConceptSet(


    @cached_property
    def inventory(self):
        sounds = DictList([])
        for sound in self.wordlist.sounds:
            if self.id in sound.occs:
                sounds.append(Phoneme.from_sound(sound, language=self))
        return Inventory(language=self, ts=self.wordlist.ts,
                sounds=sounds)



@attr.s(repr=False)
class ConceptInSource(CLBase):
    """
    Concepts in source are the original concepts in the individual wordlists.
    """
    name = GetValueFromData("Name")

    def __repr__(self):
        return '<ConceptInSource '+self.id+'>'


@attr.s(repr=False)
class ConceptSet:
    """
    Base class for the concepts in a dataset.
    """
    id = attr.ib()
    wordlist = attr.ib(default=None, repr=False)
    name = attr.ib(default=None, repr=False)
    concepticon_id = attr.ib(default=None, repr=False)
    concepticon_gloss = attr.ib(default=None, repr=False)
    forms = attr.ib(default=[], repr=False)

    def __repr__(self):
        return "<ConceptSet «"+ self.name+"»>"

    @classmethod
    def from_concept_in_source(cls, concept, wordlist=None, forms=DictList([])):
        return cls(
                id=concept.data["Concepticon_Gloss"],
                name=concept.data["Concepticon_Gloss"].lower(),
                concepticon_id=concept.data["Concepticon_ID"],
                concepticon_gloss=concept.data["Concepticon_Gloss"],
                forms=forms
                )


@attr.s(repr=False)
class Concept(ConceptSet):
    """
    Base class for concepts in individual languages.
    """
    language = attr.ib(default=None)
    concept_set = attr.ib(default=None)
    concepts_in_source = attr.ib(default=None)

    def __repr__(self):
        return "<Concept «"+ self.name+"»>"

    @classmethod
    def from_concept_set(cls, concept, language, forms=DictList([]),
            concepts_in_source=DictList([]), wordlist=None, dataset=None):
        return cls(
                id=concept.id,
                name=concept.name,
                concept_set=concept,
                concepticon_id=concept.concepticon_id,
                concepticon_gloss=concept.concepticon_gloss,
                concepts_in_source=concepts_in_source,
                forms=forms
                )


@attr.s(repr=False)
class Form(CLBase):
    
    concept = attr.ib(default=None, repr=False)
    language = attr.ib(default=None, repr=False)
    concept_in_source = attr.ib(default=None, repr=False)
    sounds = attr.ib(default=None, repr=False)
    tokens = attr.ib(default=None, repr=False)
    value = GetValueFromData("Value")
    form = GetValueFromData("Form")
    segments = GetValueFromData("Segments", transform=lingpy.basictypes.lists)
    
    def __repr__(self):
        return "[ "+str(self.segments)+" ]"
    

@attr.s(repr=False)
class Sound:
    """
    All sounds in a dataset.
    """
    id = attr.ib(default=None)
    data = attr.ib(default=None)
    clts = attr.ib(default=None)
    dataset = attr.ib(default=None)
    wordlist = attr.ib(default=None)
    grapheme = attr.ib(default=None)
    graphemes_in_source = attr.ib(default=None)
    occs = attr.ib(default=None)

    type = GetValueFromData("type")
    name = GetAttributeFromObject("name", data="clts")
    featureset = GetAttributeFromObject("featureset", data="clts")

    def __len__(self):
        return len(self.occs or [])

    def __str__(self):
        return self.grapheme

    def __repr__(self):
        return "//"+self.grapheme+"//"

    def similarity(self, other):
        if self.type not in ["marker", "unknownsound"]:
            return self.sound.similarity(other.sound)
        if self == other:
            return 1
        return 0


@attr.s(repr=False)
class Phoneme(Sound):
    """
    Base class for handling sounds in individual languages.
    """
    language = attr.ib(default=None)
    sound = attr.ib(default=None)

    def __repr__(self):
        return "/"+self.grapheme+"/"

    @classmethod
    def from_sound(cls, sound, language):
        return cls(
                id=sound.id,
                sound=sound,
                language=language,
                data=sound.data,
                clts=sound.clts,
                dataset=sound.dataset,
                wordlist=sound.wordlist,
                grapheme=sound.grapheme,
                graphemes_in_source=attr.ib(default=None),
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
                sounds[str(sound)] = Phoneme(
                    id=sound.name.replace(' ','_'),
                    clts=sound,
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
