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
        Language, Concept, ConceptInLanguage,
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

    def get(self, idf):
        return self.objects[idf]

    def load(self):
        """
        Load the data.
        """
        languages, concepts, forms, objects = [], [], [], []
        linked_concepts = []
        senses = []
        phonemes = DictList([])
        self.invalid = []
        for dataset in progressbar(self.datasets, desc="loading datasets"):
            dsid = dataset.metadata_dict["rdf:ID"]
            # add languages to the dataset
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
                            senses=DictList([]),
                            concepts=DictList([]),
                        )
                    ]
                objects + [languages[-1]]

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
                                )
                    concepts.append(new_concept)
                senses.append(new_sense)
                objects += [new_sense, new_concept]

            # assemble forms
            for form in dataset.objects("FormTable"):
                valid_bipa = True
                lid, cid, pid, fid = (
                        dsid+"-"+form.data["Language_ID"], 
                        form.parameter.data["Concepticon_Gloss"],
                        dsid+"-"+form.parameter.id,
                        dsid+"-"+form.id
                        )
                sounds = []
                if form.data["Segments"]: 
                    for i, segment in enumerate(form.data["Segments"]):
                        sound = self.ts[segment]
                        sound_id = sound.name
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
                            log.warning("warning: unknown sound {0}".format(segment))
                            valid_bipa = False
                        sounds += [sound]
                forms += [(valid_bipa, lid, cid, pid, fid, dsid, sounds, form)]
        
        self.sounds = phonemes
        self.languages = DictList(languages)
        self.concepts = DictList(concepts)
        self.senses = DictList(senses)
        self.forms = []
        self.objects = DictList(objects)
        for valid_bipa, lid, cid, pid, fid, dsid, sounds, form in forms:
            new_form = Form(
                        id=fid,
                        concept=self.concepts[cid] if cid else None,
                        language=self.languages[lid],
                        sounds = [self.sounds[sound.name] for sound in
                            sounds],
                        tokens = lingpy.basictypes.lists(
                            [str(sound) for sound in sounds]
                            ) if valid_bipa else None,
                        sense=self.senses[pid],
                        cldf=form,
                        data=form.data,
                        dataset=dsid,
                        wordlist=self
                        )
            
            self.forms.append(new_form)

            objects += [new_form]
            if cid and cid not in self.languages[lid].concepts:
                self.languages[lid].concepts.append(
                    ConceptInLanguage.from_concept(
                        self.concepts[cid],
                        self.languages[lid],
                        senses=DictList([]),
                        wordlist=self,
                        dataset=dsid,
                        forms=DictList([]),
                        segmented_forms=DictList([]),
                        bipa_forms=DictList([])
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

        # add concepts here
        self.forms = DictList(self.forms)
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


    
    # TODO: consider to modify the index self._d to yield not a list but the ID
    # index needs recalculation which is not that good for our purpose!
    def delete_forms(self, blacklist):
        languages, concepts = defaultdict(list), defaultdict(list)
        for fid in blacklist:
            languages[self.forms[fid].language.id] += [fid]
            concepts[self.forms[fid].concept.id] += [fid]
        for lid, forms in languages.items():
            for fid in forms:
                print(fid)
                try:
                    self.languages[lid].forms.remove(fid)
                except:
                    try:
                        self.forms.remove(fid)
                    except:
                        print("not found", fid)
            #if len(language.forms) == 0:
            #    self.languages.remove(lid)
        #for concept in concepts:
        #    if len(concept.forms) == 0:
        #        del self.concepts[self.concepts._d[concept.id][0]]

