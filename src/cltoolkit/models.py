"""
Basic models.
"""
from typing import Optional, TYPE_CHECKING, Union
import functools
import statistics
import collections
from collections.abc import Iterable
import dataclasses

import lingpy
from lingpy.basictypes import lists
import pyclts
from pyclts.models import Sound as CLTSSound, Cluster, Consonant
from pycldf.orm import Language as PycldfLanguage

from cltoolkit.util import DictTuple, jaccard, idjoin

if TYPE_CHECKING:
    from .wordlist import Wordlist

LanguageIdType = str
OccurrencesType = list[tuple[int, 'Form']]
OccurrencesDictType = collections.OrderedDict[LanguageIdType, OccurrencesType]
INVALID_SOUND_TYPES = ["marker", "unknownsound"]


@dataclasses.dataclass
class CLCore:
    """
    Base class to represent data in a wordlist.
    """
    id: Optional[str] = None
    wordlist: Optional['Wordlist'] = None

    def __repr__(self):
        return "<" + self.__class__.__name__ + " " + self.id + ">"


@dataclasses.dataclass
class WithForms:
    """
    Mixin to represent data in a wordlist that contains forms.
    """
    forms: DictTuple['Form'] = dataclasses.field(default_factory=collections.OrderedDict)

    @functools.cached_property
    def forms_with_sounds(self):
        return DictTuple(f for f in self.forms if f.sounds)

    @functools.cached_property
    def forms_with_graphemes(self):
        return DictTuple(f for f in self.forms if f.graphemes)


@dataclasses.dataclass
class Language(CLCore, WithForms):
    """
    Base class for handling languages.

    :ivar senses: `DictTuple` of senses, i.e. glosses for forms.
    :ivar concepts: `DictTuple` of senses with explicit Concepticon mapping.
    :ivar glottocode: `str`, Glottocode for the language.

    .. note::

       A language variety is defined for a specific dataset only.
    """
    dataset: str = dataclasses.field(repr=False, default_factory=collections.OrderedDict)
    senses: Optional[DictTuple['Sense']] = dataclasses.field(
        default_factory=collections.OrderedDict)
    concepts: Optional[DictTuple['Concept']] = dataclasses.field(
        default_factory=collections.OrderedDict)
    glottocode: Optional[str] = None
    name: Optional[str] = None
    macroarea: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    family: Optional[str] = None
    subgroup: Optional[str] = None

    @classmethod
    def from_obj(cls, wl, dsid, language: PycldfLanguage):
        idjoin(dsid, language.id)
        return cls(
            id=idjoin(dsid, language.id),
            wordlist=wl,
            name=language.cldf.name,
            glottocode=language.cldf.glottocode,
            macroarea=language.cldf.macroarea,
            latitude=language.cldf.latitude,
            longitude=language.cldf.longitude,
            family=language.data.get('Family'),
            subgroup=language.data.get('SubGroup'),
            dataset=dsid,
        )

    @functools.cached_property
    def sound_inventory(self) -> 'Inventory':
        sounds: list[Sound] = []
        for sound in self.wordlist.sounds:  # Sound instances
            if self.id in sound.occurrences:
                sounds.append(Sound.from_sound(sound, language=self))

        return Inventory.from_list(
            language=self,
            ts=self.wordlist.ts,
            sounds=sounds)


@dataclasses.dataclass(repr=False, eq=False)
class Sense(CLCore, WithForms):
    """
    A sense description (concept in source) which does not need to be linked to the Concepticon.

    :ivar language: :class:`Language` instance
    :ivar name: `str`, the gloss

    .. note::

        Unlike senses in a wordlist, which are dataset-specific, concepts in a wordlist are defined
        for all datasets.
    """
    dataset: str = dataclasses.field(repr=False, default=None)
    language: Optional[Language] = None
    name: Optional[str] = None

    def __repr__(self):
        return '<Sense ' + self.id + '>'

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name
        return False

    @classmethod
    def from_sense(cls, sense: 'Sense', language: 'Language'):
        return cls(
            id=sense.id,
            name=sense.name,
            dataset=sense.dataset,
            wordlist=sense.wordlist,
            language=language)


@dataclasses.dataclass(repr=False, eq=False)
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
    language: Optional[Language] = None
    senses: Optional[DictTuple[Sense]] = dataclasses.field(
        default_factory=collections.OrderedDict)
    name: Optional[str] = None
    concepticon_id: Optional[str] = None
    concepticon_gloss: Optional[str] = None

    @classmethod
    def from_concept(cls, concept: 'Concept'):
        return cls(
            id=concept.id,
            name=concept.name,
            concepticon_id=concept.concepticon_id,
            concepticon_gloss=concept.concepticon_gloss,
        )

    def __repr__(self):
        return f"<Concept {self.name}>"


@dataclasses.dataclass(repr=False)
class Form(CLCore):
    """
    Base class for handling the form part of linguistic signs.

    :ivar concept: The concept (if any) expressed by the form.
    :ivar language: The language in which the form occurs.
    :ivar sense: The meaning expressed by the form.
    :ivar sounds: The segmented strings defined by the B(road) IPA.
    :ivar graphemes: The segmented graphemes (possibly not BIPA conform).
    """
    dataset: str = dataclasses.field(repr=False, default=None)
    concept: Optional[Concept] = dataclasses.field(default=None, repr=False)
    language: Optional[Language] = dataclasses.field(default=None, repr=False)
    sense: Optional[Sense] = dataclasses.field(default=None, repr=False)
    #: Sounds (graphemes recognized in the specified transcription system) in the segmented form:
    sounds: lists = dataclasses.field(default_factory=lambda: lists([]), repr=False)
    cognates: Optional[DictTuple['Cognate']] = dataclasses.field(default_factory=dict, repr=False)
    value: Optional[str] = None
    form: Optional[str] = None
    graphemes: lingpy.basictypes.lists = dataclasses.field(default_factory=list)

    @property
    def sound_objects(self):
        return [self.wordlist.sounds[str(self.wordlist.ts[t])] for t in self.sounds]

    @property
    def grapheme_objects(self):
        return [self.wordlist.graphemes[self.dataset + '-' + s] for s in self.graphemes or []]

    def __repr__(self):
        return "<" + self.__class__.__name__ + " " + self.form + ">"


@dataclasses.dataclass(repr=False)
class Cognate(CLCore):
    dataset: str = dataclasses.field(repr=False, default=None)
    form: Optional[Form] = dataclasses.field(default=None, repr=False)
    contribution: Optional[str] = dataclasses.field(default=None, repr=False)


@dataclasses.dataclass(repr=False)
class Grapheme(CLCore, WithForms):
    dataset: str = dataclasses.field(repr=False, default=None)
    grapheme: Optional[str] = None
    occurrences: OccurrencesDictType = dataclasses.field(default_factory=collections.OrderedDict)
    language: Optional[Language] = None
    sound: Optional[CLTSSound] = None

    def __str__(self):
        return self.grapheme


@dataclasses.dataclass(repr=False, eq=False)
class Sound(CLCore, WithForms):
    """
    All sounds in a dataset.
    """
    grapheme: Optional[str] = None
    occurrences: OccurrencesDictType = dataclasses.field(default_factory=collections.OrderedDict)
    graphemes_in_source: Optional[str] = None
    language: Optional[Language] = None
    obj: Optional[CLTSSound] = None

    @property
    def loccurrences(self) -> OccurrencesType:
        if self.language:
            return self.occurrences[self.language.id]
        if len(self.occurrences) == 1:  # pragma: no cover
            return list(self.occurrences.values())[0]
        return []  # pragma: no cover

    @property
    def type(self):
        return self.obj.type

    @property
    def name(self):
        return self.obj.name

    @property
    def featureset(self):
        return self.obj.featureset

    @classmethod
    def from_grapheme(
            cls, grapheme_, grapheme=None, occurrences=None, forms=None,
            id=None, graphemes_in_source=None, obj=None):
        return cls(
            id=id,
            grapheme=grapheme,
            wordlist=grapheme_.wordlist,
            occurrences=occurrences,
            #data=obj.__dict__,
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
        return f"<{self.__class__.__name__} {self.grapheme}>"

    def similarity(self, other):
        if self.type not in INVALID_SOUND_TYPES and other.type not in INVALID_SOUND_TYPES:
            return self.obj.similarity(other.obj)
        if self.type in INVALID_SOUND_TYPES and other.type in INVALID_SOUND_TYPES:
            if self == other:
                return 1
            return 0
        return 0

    @classmethod
    def from_sound(cls, sound, language):
        return cls(
            id=str(sound),
            language=language,
            obj=sound.obj,
            wordlist=sound.wordlist,
            grapheme=sound.grapheme,
            occurrences=collections.OrderedDict([(language.id, sound.occurrences[language.id])]),
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


PhonemeDictType = DictTuple


def _subinventory_by_type(sounds: Iterable[Sound], types: list[str]) -> PhonemeDictType:
    return DictTuple(v for v in sounds if v.obj.type in types)


def _subinventory_by_ignored_features(
        sounds: Iterable[Sound],
        types: list[str],
        features_to_sound: dict[frozenset[str], Sound],
        properties: list[str],
) -> PhonemeDictType:
    out = collections.OrderedDict()
    strsounds = map(str, sounds)
    for v in _subinventory_by_type(sounds, types):
        stripped = features_to_sound.get(
            frozenset(s for s in v.featureset if s not in properties))
        if str(stripped) != str(v) and str(stripped) not in strsounds:
            out[v.id] = v
        elif str(stripped) == str(v):
            out[v.id] = v
    return DictTuple(out.values())


@dataclasses.dataclass
class Inventory:
    language: Optional[str]
    ts: Optional = dataclasses.field(repr=False)

    sounds: PhonemeDictType = dataclasses.field(repr=False)
    consonants: PhonemeDictType = dataclasses.field(repr=False)
    # Consonants, ignoring differences just in length.
    consonants_by_quality: PhonemeDictType = dataclasses.field(repr=False)
    consonant_sounds: PhonemeDictType = dataclasses.field(repr=False)
    vowels: PhonemeDictType = dataclasses.field(repr=False)
    # Vowels, ignoring differences just in length.
    vowels_by_quality: PhonemeDictType = dataclasses.field(repr=False)
    vowel_sounds: PhonemeDictType = dataclasses.field(repr=False)
    segments: PhonemeDictType = dataclasses.field(repr=False)
    tones: PhonemeDictType = dataclasses.field(repr=False)
    markers: PhonemeDictType = dataclasses.field(repr=False)
    clusters: PhonemeDictType = dataclasses.field(repr=False)
    diphthongs: PhonemeDictType = dataclasses.field(repr=False)
    unknownsounds: PhonemeDictType = dataclasses.field(repr=False)

    @classmethod
    def from_list(
            cls,
            ts: pyclts.TranscriptionSystem,
            sounds: list[Union[Sound, str]],
            language=None,
            wordlist=None,
    ):
        new = collections.OrderedDict()
        for sound in sounds:
            if isinstance(sound, Sound):
                new[sound.id] = sound
            else:  # Initialization from lists of str is used in tests.
                sound = ts[sound]
                try:
                    new[str(sound)].graphemes_in_source.append(sound)
                except KeyError:
                    new[str(sound)] = Sound(
                        id=str(sound),
                        obj=sound,
                        wordlist=wordlist,
                        grapheme=str(sound),
                        graphemes_in_source=[sound.grapheme],
                        occurrences=[],
                    )
        sounds = list(new.values())

        kw = dict(  # pylint: disable=R1735
            consonants=_subinventory_by_type(sounds, ["consonant"]),
            # Consonants, ignoring differences just in length.
            consonants_by_quality=_subinventory_by_ignored_features(
                sounds,
                ["consonant"],
                ts.features,
                ["long", "ultra-long", "mid-long", "ultra-short"]),
            consonant_sounds=_subinventory_by_type(sounds, ["consonant", "cluster"]),
            vowels=_subinventory_by_type(sounds, ["vowel"]),
            # Vowels, ignoring differences just in length.
            vowels_by_quality=_subinventory_by_ignored_features(
                sounds,
                ["vowel"],
                ts.features,
                ["long", "ultra-long", "mid-long", "ultra-short"]),
            vowel_sounds=_subinventory_by_type(sounds, ["vowel", "diphthong"]),
            segments=_subinventory_by_type(
                sounds, ["consonant", "vowel", "cluster", "diphthong"]),
            tones=_subinventory_by_type(sounds, ["tone"]),
            markers=_subinventory_by_type(sounds, ["marker"]),
            clusters=_subinventory_by_type(sounds, ["cluster"]),
            diphthongs=_subinventory_by_type(sounds, ["diphthong"]),
            unknownsounds=_subinventory_by_type(sounds, ["unknownsound"]),
        )
        return cls(
            sounds=DictTuple(sounds),
            ts=ts,
            language=language,
            **kw)

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
