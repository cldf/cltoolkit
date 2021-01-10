"""
Basic class for handling inventory datasets.
"""
import attr
from cldftk.models.sounds import Inventory, Phoneme
from cldfbench import get_dataset
import pycldf
from pyclts import CLTS
from collections import defaultdict, OrderedDict
from pyclts.util import nfd
from cldftk.util import progressbar
from cldftk import log
from cldftk.models.language import LanguageWithInventory
from pyclts.models import is_valid_sound
from pathlib import Path
import pybtex
from pycldf.sources import Source




def normalize(grapheme):
    for s, t in [('\u2019', '\u02bc')]:
        grapheme = grapheme.replace(s, t)
    return grapheme


def from_metadata(dataset, td, ts):
    ds = pycldf.Dataset.from_metadata(
            Path(dataset).joinpath('cldf', 'StructureDataset-metadata.json'))

    bib = pybtex.database.parse_string(
            open(Path(dataset).joinpath(
                'cldf', 'sources.bib').as_posix()).read(), bib_format='bibtex')
    bib_ = [Source.from_entry(k, e) for k, e in bib.entries.items()]
    bib = {source.id: source for source in bib_}

    return retrieve_data(dataset, ds, bib, td, ts)


def from_dataset(dataset, td, ts):
    ds = get_dataset(dataset)
    cldf = ds.cldf_reader()
    bib = {source.id: source for source in ds.cldf_dir.read_bib()}
    return retrieve_data(dataset, cldf, bib, td, ts)


def retrieve_data(dataset, ds, bib, td, ts):
    varieties = {row['ID']: row for row in ds.iter_rows('LanguageTable')}
    for row in progressbar(ds.iter_rows('ValueTable'), desc='load values'):
        lid = row['Language_ID']
        try:
            varieties[lid]['graphemes'] += [nfd(row['Value'])]
            varieties[lid]['sources'] += [row['Source'] if row['Source']
                    else '']
        except KeyError:
            varieties[lid]['graphemes'] = [nfd(row['Value'])]
            varieties[lid]['sources'] = [row['Source'] if row['Source']
                    else '']
        
    languages = {}
    sound_list = defaultdict(list)
    for lid, data in progressbar(varieties.items(), desc='identify inventories'):
        sounds = OrderedDict()
        
        for grapheme in data['graphemes']:
            sound = td.grapheme_map.get(grapheme, grapheme)
            try:
                sounds[sound].graphemes_in_source.append(grapheme)
            except KeyError:
                sounds[sound] = Phoneme(
                        grapheme=sound,
                        graphemes_in_source=[grapheme],
                        sound=ts[sound]
                        )
        languages[lid] = LanguageWithInventory(
                cldf=data,
                dataset=dataset,
                id=lid,
                inventory=Inventory(sounds=sounds, ts=ts))
    return languages, bib

@attr.s
class InventoryData:
    
    languages = attr.ib(default=None, repr=False)
    sources = attr.ib(default=None, repr=False)
    sounds = attr.ib(default=None, repr=False)
    
    @classmethod
    def from_metadata(cls, dataset, td, ts=None):
        ts = ts or CLTS().bipa
        if isinstance(td, str):
            td = CLTS().transcriptiondata_dict[td]
        languages, bib = from_metadata(dataset, td, ts)
        return cls(languages, bib)

    @classmethod
    def from_dataset(cls, dataset, td, ts=None):
        ts = ts or CLTS().bipa
        if isinstance(td, str):
            td = CLTS().transcriptiondata_dict[td]
        languages, bib = from_dataset(dataset, td, ts)
        return cls(languages, bib)

    def __iter__(self):
        for language in self.languages.values():
            yield language



