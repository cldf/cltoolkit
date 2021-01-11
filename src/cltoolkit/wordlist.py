"""
Class for handling wordlist data.
"""
from collections import defaultdict, OrderedDict
from csvw.dsv import UnicodeReader, UnicodeDictReader
import pycldf
from cldfbench import get_dataset

from lingpy.basictypes import lists
from lingpy import Wordlist as LingPyWordlist

from cldftk.util import progressbar
import attr

# reference catalogs (glottolog not needed)
from pyconcepticon import Concepticon
from pyclts import CLTS

# lexicore functions
from cldftk import log
from cldftk.util import lower_key
from cldftk.validate import valid_segments
from cldftk.models import (
        LanguageWithForms, LanguageWithSegments, Concept, Phoneme, Form)

def iter_rows(ds, table, *values):
    for item in ds.iter_rows(table):
        yield [item[v] for v in values]+[item]


def iter_dict(lst, *values):
    for item in lst:
        yield [item[v] for v in values]+[item]


def make_id(*elms, sep='-'):
    return sep.join(elms)


def validate_languages(dataset, ds, valid_coordinates, valid_glottocode):
    """
    Select those languages from the sample which conforms to the validation.
    """
    for language in ds.iter_rows('LanguageTable'):
        language['forms'] = []
        lid = make_id(dataset, language['ID'])
        if valid_coordinates and valid_glottocode:
            if language['Latitude'] and language['Glottocode']:
                yield lid, language
        elif valid_coordinates:
            if language['Latitude']:
                yield lid, language
        elif valid_glottocode:
            if language['Glottocode']:
                yield lid, language
        else:
            yield lid, language


def validate_forms(dataset, ds, ts, concepts, languages):
    for segments, _fid, _lid, pid, form in iter_rows(
            ds, 'FormTable', 'Segments', 'ID', 'Language_ID',
            'Parameter_ID'
            ):
        fid, lid = make_id(dataset, _fid), make_id(dataset, _lid)
        sounds = valid_segments(segments, ts)
        if sounds and pid in concepts and lid in languages:
            yield (
                    fid, lid, concepts[pid], form, 
                    sounds,
                    lists([str(s) for s in sounds]))
        elif not segments:
            log.warning('Invalid form {0}-{1} (Segments: {2}'.format(
                dataset, _fid, segments))


@attr.s
class Wordlist:
    """
    A wordlist is a collection of several CLDF lexibank datasets.
    """
    datasets = attr.ib(default=[])
    ts = attr.ib(default=CLTS().transcriptionsystem_dict['bipa'], repr=False)
    concepticon = attr.ib(default=Concepticon(), repr=False)
    concepts = attr.ib(default=OrderedDict(),
            repr=False)
    languages = attr.ib(default=OrderedDict(), repr=False)
    inventories = attr.ib(default=OrderedDict(), repr=False)
    forms = attr.ib(default=OrderedDict(), repr=False)
    invalid = []
    dataset_dict = {}

    @property
    def width(self):
        return len(self.languages)

    @property
    def height(self):
        return len(self.languages)

    @classmethod
    def from_file(cls, path, delimiter='\t'):
        datasets = []
        with UnicodeDictReader(path, delimiter=delimiter) as reader:
            for row in reader:
                if row['IGNORE'] != '1':
                    datasets += [row['ID']]
        return cls(datasets=datasets)

    @classmethod
    def from_datasets(cls, *datasets):
        return cls(datasets=datasets)

    def as_wordlist(
            self, format_language=None, wordlist=LingPyWordlist):
        if not format_language:
            format_language = lambda x: x.id.split('-')[1]
        D = {
                0: ['lexibank', 'dataset', 'doculect', 'doculect_in_source',
                    'glottolog', 'concept', 'concepticon', 'concept_in_source',
                    'latitude', 'longitude', 'family', 'value', 'form',
                    'tokens']
                }
        idx = 1
        for language_id, language in self.languages.items():
            for form in language.forms:
                D[idx] = [
                        form.id, 
                        form.language.dataset, 
                        format_language(form.language),
                        language.name, 
                        language.glottocode,
                        form.concept_name, 
                        form.concept.concepticon_id,
                        form.concept_in_source, 
                        language.latitude,
                        language.longitude, 
                        language.family, 
                        form.value,
                        form.form, 
                        form.tokens
                        ]
                idx += 1
        return wordlist(D)

    def load_datasets(self, mode='python', path=''):
        """
        Load the datasets from pylexibank and check if they exist.
        """
        if mode == 'python':
            for dataset in progressbar(self.datasets, desc="load datasets"):
                ds = get_dataset(
                        dataset,
                        ep='lexibank.dataset')
                if ds:
                    self.dataset_dict[dataset] = ds.cldf_reader()
                else:
                    log.warning('could not load {0}'.format(dataset))
        elif mode == 'path':
            for dataset in progressbar(self.datasets, desc="load datasets"):
                ds = pycldf.Dataset.from_metadata(
                        Path(path, dataset, 'cldf', 'cldf-metadata.json'))
                self.dataset_dict[dataset] = ds
    
    def load_forms(
            ):
        pass


    def load_segments(
            self, 
            threshold=100,
            valid_coordinates=True,
            valid_glottocode=True
            ):
        # validators from parameters


        for dataset, ds in progressbar(
                self.dataset_dict.items(),
                desc="load segments"
                ):

            # retrieve languages
            languages = OrderedDict(
                    validate_languages(
                        dataset, ds, valid_coordinates,
                        valid_glottocode))
            # TODO: allow to retrieve concepts not mapped to concepticon
            concepts = OrderedDict(
                    [(concept['ID'], concept
                        ) for concept in ds.iter_rows('ParameterTable') if \
                                concept['Concepticon_ID']])
            forms = OrderedDict()
            for (fid, lid, concept, form, sounds, tokens
                    ) in validate_forms(
                            dataset, ds, self.ts, concepts, languages
                    ):
                # store all essential attributes
                languages[lid]['forms'] += [
                        (
                            form, concept, tokens, sounds,
                            fid, concept['Concepticon_Gloss'])] 

            for lid, language in [(k, v) for k, v in languages.items() if
                    len(v['forms']) >= threshold]:
                # add language to the wordlist
                self.languages[lid] = LanguageWithSegments(
                        id=lid, 
                        cldf=language,
                        dataset=dataset,
                        ts=self.ts,
                        forms=[]
                        )

                # iterate over the forms to add forms and concepts
                for form, concept, tokens, sounds, fid, cid in language['forms']:
                    if not cid in self.concepts:
                        self.concepts[cid] = Concept(
                                id=cid,
                                forms=[],
                                concept=concept
                                )
                    self.forms[fid] = Form(
                            id=fid,
                            language=self.languages[lid],
                            concept=self.concepts[cid],
                            sounds=sounds,
                            tokens=tokens,
                            concept_in_source=concept,
                            attributes=form)
                    self.concepts[cid].forms += [self.forms[fid]]
                    self.languages[lid].forms += [self.forms[fid]]

    def __len__(self):
        return len(self.forms)

    def __iter__(self):
        for language in self.languages.values():
            yield language

    #def load_inventories(self):
    #    for lid, language in progressbar(
    #            self.languages.items(),
    #            desc="load inventories"):
    #        sounds = OrderedDict()
    #        for form in language.forms:
    #            for i, (sound, segment, token) in enumerate(zip(
    #                form.sounds, form.segments, form.tokens)):
    #                if sound.type != 'marker':
    #                    try:
    #                        sounds[token].occs += [(form.id, i)]
    #                        sounds[token].graphemes_in_source += [segment]
    #                    except KeyError:
    #                        sounds[token] = Phoneme(
    #                                grapheme=token,
    #                                graphemes_in_source=[segment],
    #                                name=sound.name,
    #                                type=sound.type,
    #                                sound=sound,
    #                                occs=[(form.id, i)]
    #                                )
    #        self.inventories[lid] = Inventory(
    #                id=lid,
    #                sounds=sounds,
    #                language=language,
    #                ts=self.ts
    #                )


