"""
Class for handling wordlist data.
"""
from collections import OrderedDict, defaultdict
import pycldf
from pycldf.util import DictTuple

from importlib import import_module

from pyclts import CLTS
import lingpy

from cltoolkit.util import progressbar, DictList, identity
from cltoolkit import log
from cltoolkit.models import (
        Language, Concept, ConceptInLanguage, Grapheme,
        SenseInLanguage, Form, Sense, Sound, Phoneme)

from functools import reduce

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

    def _add_languages(self, dsid, dataset):
        """Append languages to the wordlist.
        """
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

    def _add_senses(self, dsid, dataset):
        """Append senses (concepts) to the wordlist."""
        
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
                self.objects.append(new_concept)
            self.senses.append(new_sense)
            self.objects.append(new_sense)

    def _add_forms(self, dsid, dataset):
        """Add forms to the dataset."""
        for form in progressbar(
                dataset.objects("FormTable"), 
                desc="loading forms for {0}".format(dsid)
                ):
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
        for dataset in self.datasets:
            log.info("loading {0}".format(dataset))
            dsid = dataset.metadata_dict["rdf:ID"]
            self._add_languages(dsid, dataset)
            self._add_senses(dsid, dataset)
            self._add_forms(dsid, dataset)
        self.bipa_forms = DictList([f for f in self.forms if f.tokens])
        self.segmented_forms = DictList([f for f in self.forms if f.segments])
        log.info("loaded wordlist with {0} concepts and {1} languages".format(
            self.height, self.width))
    
    def __len__(self):
        return len(self.forms)

    def iter_forms_by_concepts(
            self, 
            concepts=None, 
            languages=None,
            aspect=None,
            filter_by=None,
            flat=False,
            ):
        """
        Iterate over the concepts in the data and return forms for a given language.

        :param concepts: List of concept identifiers. If not specified, will use all concepts linked to concepticon.
        :param language: List of language identifiers, all languages if not specified.
        :param aspect: Select attribute of the Form object instead of the Form object.
        :param filter_by: Use a function to filter the data to be output.  
        :param flatten: Return a one-dimensional array of the data.

        .. note::

          The function returns for each concept (selected by ID) the form for
          each language, or the specific aspect (attribute) of the form,
          provided this exists. 

        """
        flatten = identity if not flat else lambda x: [item for sublist in x
                for item in sublist]
        transform = identity if not aspect else lambda x: getattr(x, aspect)
        concepts = [self.concepts[c] for c in concepts] if concepts else self.concepts
        languages = [self.languages[l] for l in languages] if languages else self.languages
        for concept in concepts:
            out = []
            for language in languages:
                try:
                    out.append(
                            list(filter(
                                filter_by,
                                [transform(f) for f in language.concepts[concept.id].forms]
                                )))
                except KeyError:
                    out.append([])
            if any(out):
                yield concept, flatten(out)

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
    
