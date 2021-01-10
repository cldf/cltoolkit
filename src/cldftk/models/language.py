"""
Basic class for handling languages.
"""
import attr
from functools import cached_property
from pyclts.inventories import Phoneme, Inventory
from pyclts import CLTS
from collections import OrderedDict


@attr.s
class Language:
    id = attr.ib()
    cldf = attr.ib(default=None, repr=False)
    dataset = attr.ib(default=None, repr=False)

    @property
    def name(self):
        return self.cldf['Name']

    @property
    def glottolog_name(self):
        return self.cldf['Glottolog_Name']

    @property
    def glottocode(self):
        return self.cldf['Glottocode']

    @property
    def macroarea(self):
        return self.cldf['Macroarea']

    @property
    def family(self):
        return self.cldf['Family']

    @property
    def latitude(self):
        return self.cldf['Latitude']

    @property
    def longitude(self):
        return self.cldf['longitude']


@attr.s
class LanguageWithForms(Language):
    forms = attr.ib(default=None, repr=False)
    
    def __len__(self):
        return len(self.forms)
    

@attr.s
class LanguageWithInventory(Language):
    ts = attr.ib(default=CLTS().bipa, repr=False)
    inventory = attr.ib(default=None, repr=False)


@attr.s
class LanguageWithSegments(LanguageWithForms):
    ts = attr.ib(default=CLTS().bipa, repr=False)
    
    @cached_property
    def inventory(self):
        sounds = OrderedDict()
        for form in self.forms:
            for i, (sound, segment, token) in enumerate(zip(
                form.sounds, form.segments, form.tokens)):
                if sound.type != 'marker':
                    try:
                        sounds[token].occs += [(form.id, i)]
                        sounds[token].graphemes_in_source += [segment]
                    except KeyError:
                        sounds[token] = Phoneme(
                                grapheme=token,
                                graphemes_in_source=[segment],
                                sound=sound,
                                occs=[(form.id, i)]
                                )
        return Inventory(
                id=self.id,
                sounds=sounds,
                language=self,
                ts=self.ts
                )
