"""
Basic class for handling languages.
"""
import attr
from functools import cached_property
from pyclts.inventories import Phoneme, Inventory
from pyclts import CLTS
from collections import OrderedDict
import argparse


class CLDFGetter:
    def __init__(self, attr):
        self.attr = self
    def __get__(self, obj, objtype=None):
        return getattr(obj.cldf, self.attr)

@attr.s
class Language:
    id = attr.ib()
    cldf = attr.ib(converter=lambda d: argparse.Namespace(**d), default=None, repr=False)
    data = attr.ib(default=None, repr=False)
    dataset = attr.ib(default=None, repr=False)

    name = CLDFGetter('name')
    glottocode = CLDFGetter('glottocode')
    latitude = CLDFGetter('latitude')
    longitude = CLDFGetter('longitude')
    macroarea = CLDFGetter('macroarea')

    @classmethod
    def from_row(cls, idf, row, cldf_property_map, dataset=None):
        cldf_props, data = {}, OrderedDict()
        for k, v in row.items():
            if k in cldf_property_map:
                cldf_props[cldf_property_map[k]] = v
            data[k] = v
        return cls(id=idf, cldf=cldf_props, data=data)


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
