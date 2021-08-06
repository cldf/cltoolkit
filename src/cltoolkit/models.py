"""
Basic models.
"""
import typing
import statistics
import collections

import attr
import lingpy
from clldutils.misc import lazyproperty as cached_property
import pyclts
from pyclts.models import Sound as CLTSSound, Symbol, Cluster, Consonant

from cltoolkit.util import NestedAttribute, DictTuple, jaccard, MutatedDataValue


@attr.s(repr=False)
class CLCore:
    """
    Base class to represent data in a wordlist.
    """
    id = attr.ib()
    wordlist = attr.ib(default=None)
    data = attr.ib(default=None)

    def __repr__(self):
        return "<" + self.__class__.__name__ + " " + self.id + ">"


@attr.s
class WithForms:
    """
    Mixin to represent data in a wordlist that contains forms.
    """
    forms = attr.ib(default=None)

    @cached_property
    def forms_with_sounds(self):
        return DictTuple([f for f in self.forms if f.sounds])

    @cached_property
    def forms_with_graphemes(self):
        return DictTuple([f for f in self.forms if f.graphemes])


@attr.s
class WithDataset:
    """
    Mixin to represent data in a wordlist from a specific dataset.
    """
    obj = attr.ib(default=None, repr=False)
    dataset = attr.ib(default=None, repr=False)


@attr.s(repr=False)
class Language(CLCore, WithForms, WithDataset):
    """
    Base class for handling languages.

    :ivar senses: `DictTuple` of senses, i.e. glosses for forms.
    :ivar concepts: `DictTuple` of senses with explicit Concepticon mapping.
    :ivar glottocode: `str`, Glottocode for the language.

    .. note::

       A language variety is defined for a specific dataset only.
    """
    senses = attr.ib(default=None)
    concepts = attr.ib(default=None)
    glottocode = MutatedDataValue("Glottocode")
    name = MutatedDataValue("Name")
    macroarea = MutatedDataValue("Macroarea")
    latitude = MutatedDataValue("Latitude")
    longitude = MutatedDataValue("Longitude")
    family = MutatedDataValue("Family")
    subgroup = MutatedDataValue("SubGroup")

    @cached_property
    def sound_inventory(self):
        sounds = []
        for sound in self.wordlist.sounds:
            if self.id in sound.occurrences:
                sounds.append(Sound.from_sound(sound, language=self))
        return Inventory(language=self, ts=self.wordlist.ts, sounds=DictTuple(sounds))


@attr.s(repr=False, eq=False)
class Sense(CLCore, WithForms, WithDataset):
    """
    A sense description (concept in source) which does not need to be linked to the Concepticon.

    :ivar language: :class:`Language` instance
    :ivar name: `str`, the gloss

    .. note::

        Unlike senses in a wordlist, which are dataset-specific, concepts in a wordlist are defined
        for all datasets.
    """
    language = attr.ib(default=None)
    name = MutatedDataValue("Name")

    def __repr__(self):
        return '<Sense ' + self.id + '>'

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        return False

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


@attr.s(repr=False, eq=False)
class Concept(CLCore, WithForms):
    """
    Base class for the concepts in a dataset.

    :ivar language: :class:`Language` instance
    :ivar name: `str`, the gloss
    :ivar senses: `iterable` of senses mapped to this concept
    :ivar concepticon_id: `str` ID of the Concepticon concept set the concept is mapped to.
    :ivar concepticon_gloss: `str` gloss of the Concepticon concept set the concept is mapped to.

    .. note::

       Unlike senses in a wordlist, which are dataset-specific, concepts in a
       wordlist are defined for all datasets. As a result, they lack a
       reference to the original dataset in which they occur, but they have an
       attribute `senses` which is a reference to the original senses as they
       occur in different datasets.

    """
    language = attr.ib(default=None)
    senses = attr.ib(default=None)
    name = attr.ib(default=None)
    concepticon_id = attr.ib(default=None)
    concepticon_gloss = attr.ib(default=None)

    @classmethod
    def from_sense(cls, concept, id=None, name=None, forms=None, senses=None):
        return cls(
            name=name,
            id=id,
            concepticon_id=concept.data.get("Concepticon_ID", ""),
            concepticon_gloss=concept.data.get("Concepticon_Gloss", ""),
            forms=forms,
            senses=senses
        )

    @classmethod
    def from_concept(cls, concept, forms=None, senses=None):
        return cls(
            id=concept.id,
            name=concept.name,
            concepticon_id=concept.concepticon_id,
            concepticon_gloss=concept.concepticon_gloss,
            senses=senses,
            forms=forms,
        )

    def __repr__(self):
        return "<Concept " + self.name + ">"


@attr.s(repr=False)
class Form(CLCore, WithDataset):
    """
    Base class for handling the form part of linguistic signs.

    :ivar concept: The concept (if any) expressed by the form.
    :ivar language: The language in which the form occurs.
    :ivar sense: The meaning expressed by the form.
    :ivar sounds: The segmented strings defined by the B(road) IPA.
    :ivar graphemes: The segmented graphemes (possibly not BIPA conform).
    """
    concept = attr.ib(default=None, repr=False)
    language = attr.ib(default=None, repr=False)
    sense = attr.ib(default=None, repr=False)
    #: Sounds (graphemes recognized in the specified transcription system) in the segmented form:
    sounds = attr.ib(default=attr.Factory(list), repr=False)
    value = MutatedDataValue("Value")
    form = MutatedDataValue("Form")
    #: Graphemes in the segmented form:
    graphemes = MutatedDataValue("Segments", transform=lingpy.basictypes.lists)
    cognates = attr.ib(default=attr.Factory(dict), repr=False)

    @property
    def sound_objects(self):
        return [self.wordlist.sounds[str(self.wordlist.ts[t])] for t in self.sounds]

    @property
    def grapheme_objects(self):
        return [self.wordlist.graphemes[self.dataset + '-' + s] for s in self.graphemes or []]

    def __repr__(self):
        return "<" + self.__class__.__name__ + " " + self.form + ">"


@attr.s(repr=False)
class Cognate(CLCore, WithDataset):
    form = attr.ib(default=None, repr=False)
    contribution = attr.ib(default=None, repr=False)


@attr.s(repr=False)
class Grapheme(CLCore, WithDataset, WithForms):
    grapheme = attr.ib(default=None)
    occurrences = attr.ib(default=None)
    language = attr.ib(default=None)

    def __str__(self):
        return self.grapheme


@attr.s(repr=False, eq=False)
class Sound(CLCore, WithForms):
    """
    All sounds in a dataset.
    """
    grapheme = attr.ib(default=None)
    occurrences = attr.ib(default=None)
    graphemes_in_source = attr.ib(default=None)
    language = attr.ib(default=None)
    obj = attr.ib(default=None)

    type = NestedAttribute("obj", "type")
    name = NestedAttribute("obj", "name")
    featureset = NestedAttribute("obj", "featureset")

    @classmethod
    def from_grapheme(
            cls, grapheme_, grapheme=None, occurrences=None, forms=None,
            id=None, graphemes_in_source=None, obj=None):
        return cls(
            id=id,
            grapheme=grapheme,
            wordlist=grapheme_.wordlist,
            occurrences=occurrences,
            data=obj.__dict__,
            graphemes_in_source=graphemes_in_source,
            forms=forms,
            obj=obj)

    def __len__(self):
        return len(self.occurrences or [])

    def __str__(self):
        return self.grapheme

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.grapheme == other.grapheme
        return False

    def __repr__(self):
        return "<" + self.__class__.__name__ + " " + self.grapheme + ">"

    def similarity(self, other):
        if self.type not in ["marker", "unknownsound"] and \
                other.type not in ["marker", "unknownsound"]:
            return self.obj.similarity(other.obj)
        elif self.type in ["marker", "unknownsound"] and other.type in ["marker", "unknownsound"]:
            if self == other:
                return 1
            return 0
        return 0

    @classmethod
    def from_sound(cls, sound, language):
        return cls(
            id=str(sound),
            language=language,
            data=sound.data,
            obj=sound.obj,
            wordlist=sound.wordlist,
            grapheme=sound.grapheme,
            occurrences=sound.occurrences[language.id],
        )

    def consonant_or_cluster_attr(self, attribute):
        if isinstance(self.obj, Consonant):
            return getattr(self.obj, attribute)
        if isinstance(self.obj, Cluster):
            return getattr(self.obj.from_sound, attribute)
        raise AttributeError(attribute)

    @property
    def manner(self):
        return self.consonant_or_cluster_attr('manner')

    @property
    def place(self):
        return self.consonant_or_cluster_attr('place')

    @property
    def ejection(self):
        return self.consonant_or_cluster_attr('ejection')

    @property
    def airstream(self):
        return self.consonant_or_cluster_attr('airstream')


class GetSubInventoryByType:
    def __init__(self, types):
        def select_sounds(inventory):
            return DictTuple([v for v in inventory if v.type in types])
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
            ts: pyclts.TranscriptionSystem,
            *list_of_sounds: typing.Union[CLTSSound, Symbol, str],
            language=None,
            wordlist=None,
    ):
        sounds = collections.OrderedDict()
        for itm in list_of_sounds:
            sound = ts[itm]
            try:
                sounds[str(sound)].graphemes_in_source.append(itm)
            except KeyError:
                sounds[str(sound)] = Sound(
                    id=str(sound),
                    obj=sound,
                    wordlist=wordlist,
                    grapheme=str(sound),
                    graphemes_in_source=[sound.grapheme],
                    occurrences=[],
                    data=sound.__dict__
                )
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
                    if soundA.type != "unknownsound" and soundB.type != "unknownsound":
                        current_sim = soundA.similarity(soundB)
                    else:
                        current_sim = 0
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
        if not scores or not sum(scores):
            return 0
        return statistics.mean(scores)
