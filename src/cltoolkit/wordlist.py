"""
Class for handling wordlist data.
"""
from collections import OrderedDict, defaultdict
import pycldf
from pycldf.util import DictTuple

from importlib import import_module

from pyclts import CLTS
import lingpy

from cltoolkit.util import progressbar, DictList, identity, lingpy_columns
from cltoolkit import log
from cltoolkit.models import (
        Language, Concept, Grapheme,
        Form, Sense, Sound)

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

    def __getitem__(self, idf):
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
            if concept_id and concept_id not in self.concepts:
                new_concept = Concept.from_sense(
                            new_sense,
                            id=concept_id,
                            name=concept_id.lower(),
                            wordlist=self,
                            forms=DictList([]),
                            senses=DictList([])
                            )
                self.concepts.append(new_concept)
                self.objects.append(new_concept)
            if concept_id:
                self.concepts[concept_id].senses.append(new_sense)
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
                    gid = dsid+'-'+segment
                    try:
                        self.graphemes[gid].forms.append(new_form)
                    except KeyError:
                        self.graphemes.append(Grapheme(
                                id=gid,
                                grapheme=segment,
                                dataset=dsid,
                                wordlist=self, 
                                obj=sound,
                                occs=OrderedDict(),
                                forms=DictList([new_form])))
                    try:
                        self.graphemes[gid].occs[lid].append((i, new_form))
                    except KeyError:
                        self.graphemes[gid].occs[lid] = [(i, new_form)]
                    if valid_bipa:
                        try:
                            self.sounds[str(sound)].forms.append(new_form)
                        except KeyError:
                            self.sounds.append(Sound.from_grapheme(
                                    self.graphemes[gid],
                                    graphemes_in_source=DictList([]),
                                    grapheme=str(sound),
                                    obj=sound,
                                    occs=OrderedDict(),
                                    forms=DictList([new_form]),
                                    id=str(sound)))
                        self.sounds[str(sound)].graphemes_in_source.append(
                                self.graphemes[gid])
                        try:
                            self.sounds[str(sound)].occs[lid].append((i, new_form))
                        except KeyError:
                            self.sounds[str(sound)].occs[lid] = [(i, new_form)]
            self.forms.append(new_form)
            self.objects.append(new_form)
            if cid and cid not in self.languages[lid].concepts:
                self.languages[lid].concepts.append(
                    Concept.from_concept(
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
                        Sense.from_sense(
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

    def as_lingpy(
            self,
            language_filter=None,
            sense_filter=None,
            form_filter=None,
            columns=None,
            transform=None,
            ):
        transform = lingpy.Wordlist
        if not form_filter:
            form_filter = identity
        if not language_filter:
            language_filter = identity
        if not sense_filter:
            sense_filter = identity
        columns = columns or lingpy_columns()
        D = {0: [x[1] for x in columns]}
        idx = 1
        for form in self.forms:
            if form_filter(form) and language_filter(form.language) and sense_filter(form.sense):
                row = []
                for (obj, att), name in columns:
                    if obj == "form":
                        row += [getattr(form, att)]
                    elif obj == "language":
                        row += [getattr(form.language, att)]
                    elif obj == "concept":
                        if form.concept:
                            row += [getattr(form.concept, att)]
                        else:
                            row += ['']
                    elif obj == "sense":
                        row += [getattr(form.sense, att)]
                D[idx] = row
                idx += 1
        return transform(D)

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

        :param concepts: List of concept identifiers, all concepts if not specified.
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
        return len(self.concepts)

    @property
    def width(self):
        return len(self.languages)


    @property
    def length(self):
        return len(self)

    def coverage(self, concepts="concepts", aspect="bipa_forms"):
        out = {}
        for language in self.languages:
            out[language.id] = 0
            for concept in getattr(language, concepts):
                if getattr(concept, aspect):
                    out[language.id] += 1
        return out
    
