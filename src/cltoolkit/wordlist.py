"""
Class for handling wordlist data.
"""
from collections import OrderedDict, defaultdict
import pycldf
from pycldf.util import DictTuple

from importlib import import_module

from pyclts import CLTS
import lingpy

from cltoolkit.util import progressbar, DictList
from cltoolkit import log
from cltoolkit.models import Language, ConceptSet, Concept, Form, ConceptInSource, Sound, Phoneme

import attr


@attr.s(repr=False)
class Wordlist:

    """
    A collection of one or more lexibank datasets, aligned by concept.
    """

    datasets = attr.ib(default=[])
    ts = attr.ib(default=CLTS().transcriptionsystem_dict['bipa'])

    @classmethod
    def from_datasets(cls, datasets, load=True):
        """
        Initialize from multiple datasets already loaded via pycldf.
        """
        this_class = cls(datasets=DictTuple(
            datasets, key=lambda x: x.metadata_dict["rdf:ID"]))
        if load:
            this_class.load()
        return this_class

    @classmethod
    def from_lexibank(cls, datasets, load=True):
        dsets = []
        for ds in datasets:
            dsets += [pycldf.Dataset.from_metadata(import_module(
                'lexibank_'+ds).Dataset().cldf_dir.joinpath('cldf-metadata.json'))]
        return cls.from_datasets(dsets, load=load)

    def load(self):
        """
        Load the data.
        """
        languages, concepts, forms = [], [], []
        concepts_in_source = []
        phonemes = DictList([])
        self.invalid = []
        for dataset in progressbar(self.datasets, desc="loading datasets"):
            dsid = dataset.metadata_dict["rdf:ID"]
            for language in dataset.objects("LanguageTable"):
                language_id = dsid+"-"+language.id
                languages += [
                        Language(
                            id=language_id, 
                            wordlist=self, 
                            data=language.data,
                            cldf=language, 
                            dataset=dsid,
                            forms=DictList([]),
                            concepts=DictList([])
                        )
                    ]

            # concepts need to be merged, so we treat them differently
            for concept in dataset.objects("ParameterTable"):
                concept_id = concept.data["Concepticon_Gloss"]
                if concept_id:
                    concepts_in_source += [
                            ConceptInSource(
                                id=dsid+'-'+concept.id,
                                wordlist=self,
                                dataset=dsid,
                                data=concept.data
                                )]
                    concepts += [
                            ConceptSet.from_concept_in_source(
                                concepts_in_source[-1],
                                wordlist=self,
                                forms=DictList([])
                                )
                        ]

            for form in dataset.objects("FormTable"):
                # check for concepticon ID
                valid = True
                if form.parameter.data["Concepticon_Gloss"]:
                    lid, cid, pid, fid = (
                            dsid+"-"+form.data["Language_ID"], 
                            form.parameter.data["Concepticon_Gloss"],
                            dsid+"-"+form.parameter.id,
                            dsid+"-"+form.id
                            )
                    sounds = []
                    for i, segment in enumerate(form.data["Segments"]):
                        sound = self.ts[segment]
                        sound_id = str(sound)
                        try:
                            phonemes[sound_id].graphemes_in_source.add(segment)
                            try:
                                phonemes[sound_id].occs[lid] += [(i, fid)]
                            except KeyError:
                                phonemes[sound_id].occs[lid] = [(i, fid)]
                        except KeyError:
                            phonemes.append(Sound(
                                id=sound_id,
                                grapheme=str(sound),
                                graphemes_in_source = set([segment]),
                                occs = {lid: [(i, fid)]},
                                data=sound.__dict__,
                                clts=sound
                                ))
                        if sound.type == 'unknownsound':
                            log.warning("unknown sound {0}".format(segment))
                            self.invalid += [form]
                            valid = False
                        sounds += [sound]
                    if valid:
                        forms += [(lid, cid, pid, fid, dsid, sounds, form)]
        
        self.sounds = phonemes
        self.languages = DictList(languages)
        self.concepts = DictList(concepts)
        self.concepts_in_source = DictList(concepts_in_source)
        self.forms = []
        for lid, cid, pid, fid, dsid, sounds, form in forms:
            self.forms += [Form(
                        id=fid,
                        concept=self.concepts[cid],
                        language=self.languages[lid],
                        sounds = [self.sounds[str(sound)] for sound in
                            sounds],
                        tokens = lingpy.basictypes.lists(
                            [str(sound) for sound in sounds]),
                        concept_in_source=self.concepts_in_source[pid],
                        cldf=form,
                        data=form.data,
                        dataset=dsid,
                        wordlist=self
                        )]
            if cid not in self.languages[lid].concepts:
                self.languages[lid].concepts.append(
                    Concept.from_concept_set(
                        self.concepts[cid],
                        self.languages[lid],
                        concepts_in_source=DictList([]),
                        wordlist=self,
                        dataset=dsid,
                        forms=DictList([])))
            self.languages[lid].concepts[cid].forms.append(self.forms[-1])
            self.languages[lid].concepts[cid].concepts_in_source.append(self.concepts_in_source[pid])
            self.concepts[cid].forms += [self.forms[-1]]
            self.languages[lid].forms += [self.forms[-1]]
        # add concepts here
        self.forms = DictList(self.forms)
        self.height = len(self.concepts)
        self.width = len(self.languages)
        if self.invalid:
            log.warning("there are {0} invalid forms".format(len(invalid)))




