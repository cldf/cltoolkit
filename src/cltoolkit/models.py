"""
Basic models.
"""

from collections import OrderedDict
import attr
from cltoolkit.util import GetValueFromData
import lingpy
from pyclts.inventories import Phoneme as CLTSPhoneme, Inventory as CLTSInventory
from pycldf.util import DictTuple


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

    @property
    def inventory(self):
        sounds = OrderedDict()
        for phoneme in self.wordlist.phonemes:
            if self.id in phoneme.occs:
                sounds[phoneme.grapheme] = Phoneme(
                        grapheme=phoneme.grapheme,
                        graphemes_in_source=phoneme.graphemes_in_source,
                        occs=phoneme.occs[self.id],
                        sound=phoneme.sound
                        )
        return Inventory(id=self.id, language=self, ts=self.wordlist.ts,
                sounds=sounds)



@attr.s(repr=False)
class ConceptInSource(CLBase):
    """
    Concepts in source are the original concepts in the individual wordlists.
    """
    name = GetValueFromData("Name")


@attr.s(repr=False)
class Concept:
    """
    Base class for handling concepts.
    """
    id = attr.ib()
    wordlist = attr.ib(default=None, repr=False)
    name = attr.ib(default=None, repr=False)
    concepticon_id = attr.ib(default=None, repr=False)
    concepticon_gloss = attr.ib(default=None, repr=False)
    forms = attr.ib(default=[], repr=False)

    def __repr__(self):
        return "<concept «"+ self.name+"»>"



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
class Phoneme(CLTSPhoneme):
    
    def __repr__(self):
        return "/"+str(self)+"/"


@attr.s(repr=False)
class Inventory(CLTSInventory):

    def __repr__(self):
        return "<inventory "+self.language.id+">"
