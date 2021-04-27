"""
Basic class for handling inventory datasets.
"""
import attr
from pathlib import Path
from collections import defaultdict, OrderedDict
import pybtex
from cldfbench import get_dataset
import pycldf
from pycldf.sources import Source
from pyclts import CLTS
from pyclts.util import nfd
from pyclts.models import is_valid_sound
from cltoolkit.util import progressbar
from cltoolkit import log
from cltoolkit.models.language import Language
from cltoolkit.models.sounds import Inventory, Phoneme


def normalize(grapheme):
    for s, t in [('\u2019', '\u02bc')]:
        grapheme = grapheme.replace(s, t)
    return grapheme


def from_metadata(dataset, cldf, td, ts):
    if not cldf:
        cldf = Path(dataset).joinpath('cldf')
    else:
        cldf = Path(cldf)

    ds = pycldf.Dataset.from_metadata(
            cldf.joinpath('StructureDataset-metadata.json'))

    bib = pybtex.database.parse_string(
            open(cldf.joinpath(
                'sources.bib').as_posix()).read(), bib_format='bibtex')
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
    for lid, data in progressbar(varieties.items(), desc='identify inventories'):
        if 'graphemes' in data:
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
        else:
            log.warning('no data found for {0}'.format(lid))
    return languages, bib

@attr.s
class InventoryData:
    
    languages = attr.ib(default=None, repr=False)
    sources = attr.ib(default=None, repr=False)
    sounds = attr.ib(default=None, repr=False)
    
    @classmethod
    def from_metadata(cls, dataset, cldf_path=None, td=None, ts=None):
        ts = ts or CLTS().bipa
        td = td or dataset
        if isinstance(td, str):
            td = CLTS().transcriptiondata_dict[td]
        languages, bib = from_metadata(dataset, cldf_path, td, ts)
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



