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
from cltoolkit.models import (
        Language, Concept, ConceptInLanguage, Grapheme,
        SenseInLanguage, Form, Sense, Sound, Phoneme)

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

    def __getite__(self, idf):
        return self.objects[idf]

    def load(self):
        """
        Load the data.
        """
        (self.languages, self.concepts, self.forms, self.objects, self.senses,
                self.graphemes,
                self.sounds) = (
                DictList([]), DictList([]), DictList([]), DictList([]), DictList([]), 
                DictList([]), DictList([]))
        graphemes = {}
        for dataset in progressbar(self.datasets, desc="loading datasets"):
            dsid = dataset.metadata_dict["rdf:ID"]
            # add languages to the dataset
            for language in dataset.objects("LanguageTable"):
                language_id = dsid+"-"+language.id
                self.languages.append(
                        Language(
                            id=language_id, 
                            wordlist=self, 
                            data=language.data,
                            obj=language, 
                            dataset=dsid,
                            forms=DictList([]),
                            senses=DictList([]),
                            concepts=DictList([]),
                        ))
                self.objects.append(self.languages[-1])

            # add concepts
            for concept in dataset.objects("ParameterTable"):
                concept_id = concept.data["Concepticon_Gloss"]
                new_sense = Sense(
                            id=dsid+'-'+concept.id,
                            wordlist=self,
                            dataset=dsid,
                            data=concept.data,
                            forms=DictList([]),
                            )
                if concept_id:
                    new_concept = Concept.from_sense(
                                new_sense,
                                id=concept_id,
                                name=concept_id.lower(),
                                wordlist=self,
                                forms=DictList([])
                                )
                    self.concepts.append(new_concept)
                self.senses.append(new_sense)
                self.objects.extend([new_sense, new_concept])

            # assemble forms
            # TODO: make this only in this run that all is added already! TODO
            # so we create a grapheme, we create a sound from the grapheme
            for form in dataset.objects("FormTable"):
                valid_bipa = True
                lid, cid, pid, fid = (
                        dsid+"-"+form.data["Language_ID"], 
                        form.parameter.data["Concepticon_Gloss"],
                        dsid+"-"+form.parameter.id,
                        dsid+"-"+form.id
                        )
                new_form = Form(
                        id=fid,
                        concept=self.concepts[cid] if cid else None,
                        language=self.languages[lid],
                        sense=self.senses[pid],
                        obj=form,
                        data=form.data,
                        dataset=dsid,
                        wordlist=self
                        )
                self.forms.append(new_form)
                sounds = [self.ts[s] for s in new_form.segments]
                if sounds:
                    valid_bipa = False
                    if not [s for s in sounds if s.type == "unknownsound"]:
                        new_form.tokens = [str(s) for s in sounds]
                        valid_bipa = True
                    for i, (segment, sound) in enumerate(
                            zip(new_form.segments, sounds)):
                        try:
                            self.graphemes[segment].forms.append(new_form)
                        except KeyError:
                            self.graphemes.append(Grapheme(
                                    id=segment, 
                                    dataset=dsid,
                                    wordlist=self, 
                                    obj=sound,
                                    occs=OrderedDict(),
                                    forms=DictList([new_form])))
                        try:
                            self.graphemes[segment].occs[lid].append((i, new_form))
                        except KeyError:
                            self.graphemes[segment].occs[lid] = [(i, new_form)]
                        if valid_bipa:
                            try:
                                self.sounds[sound.name].forms.append(new_form)
                            except KeyError:
                                self.sounds.append(Sound.from_grapheme(
                                        self.graphemes[segment],
                                        graphemes_in_source=[],
                                        grapheme=str(sound),
                                        occs=OrderedDict(),
                                        forms=DictList([new_form]),
                                        id=sound.name))
                            try:
                                self.sounds[sound.name].occs[lid].append((i, new_form))
                            except KeyError:
                                self.sounds[sound.name].occs[lid] = [(i, new_form)]
                self.forms.append(new_form)
                self.objects.append(new_form)
                if cid and cid not in self.languages[lid].concepts:
                    self.languages[lid].concepts.append(
                        ConceptInLanguage.from_concept(
                            self.concepts[cid],
                            self.languages[lid],
                            senses=DictList([]),
                            wordlist=self,
                            dataset=dsid,
                            forms=DictList([]),
                        ))
                
                if cid:
                    self.languages[lid].concepts[cid].forms.append(new_form)
                    self.concepts[cid].forms.append(new_form)
                    self.languages[lid].concepts[cid].senses.append(self.senses[pid])
                
                if pid not in self.languages[lid].senses:
                    self.languages[lid].senses.append(
                            SenseInLanguage.from_sense(
                                self.senses[pid], self.languages[lid], DictList([])
                                ))
                self.languages[lid].senses[pid].forms.append(new_form)
                self.languages[lid].forms.append(new_form)
                self.senses[pid].forms.append(new_form)
        self.bipa_forms = DictList([f for f in self.forms if f.tokens])
        self.segmented_forms = DictList([f for f in self.forms if f.segments])
    
    def __len__(self):
        return len(self.forms)

    @property
    def height(self):
        return len(self.languages)

    @property
    def width(self):
        return len(self.concepts)

    def filter_data(
            self,
            tokens=100,
            forms=100, 
            concepts=None,
            languages=None
            ):
        blacklist = set()
        for language in self.languages:
            if len(language.forms) < forms:
                blacklist.update([f.id for f in language.forms])
            if len([form.tokens for f in language.forms if f.toknes]):
                pass


    def coverage(self, concepts="concepts", aspect="bipa_forms"):
        out = {}
        for language in self.languages:
            out[language.id] = 0
            for concept in getattr(language, concepts):
                if getattr(concept, aspect):
                    out[language.id] += 1
        return out
    
