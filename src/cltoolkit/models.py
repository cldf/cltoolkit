"""
Basic models.
"""

import attr
from cltoolkit.util import GetValueFromData
import lingpy


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



@attr.s(repr=False, repr_ns=False)
class Form(CLBase):
    
    concept = attr.ib(default=None, repr=False)
    language = attr.ib(default=None, repr=False)
    concept_in_source = attr.ib(default=None, repr=False)
    value = GetValueFromData("Value")
    form = GetValueFromData("Form")
    segments = GetValueFromData("Segments", transform=lingpy.basictypes.lists)
    
    def __repr__(self):
        return "[ "+str(self.segments)+" ]"
    
