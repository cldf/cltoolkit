"""
Class for handling wordlist data.
"""
from collections import OrderedDict, defaultdict
import pycldf
from pycldf.util import DictTuple

from cltoolkit.util import progressbar
from cltoolkit import log
from cltoolkit.models import Language, Concept, Form, ConceptInSource

import attr




@attr.s(repr=False)
class Wordlist:

    """
    A collection of one or more lexibank datasets, aligned by concept.
    """

    datasets = attr.ib(default=[])
    concepts = attr.ib(default=None, repr=False)
    languages = attr.ib(default=None, repr=False)
    forms = attr.ib(default=None, repr=False)

    @classmethod
    def from_datasets(cls, datasets):
        """
        Initialize from multiple datasets already loaded via pycldf.
        """
        return cls(datasets=DictTuple(
            datasets, key=lambda x: x.metadata_dict["rdf:ID"]))

    def load(self):
        """
        Load the data.
        """
        languages, concepts, forms = [], [], []
        concepts_in_source = []
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
                            forms=[]
                        )
                    ]

            # concepts need to be merged, so we treat them differently
            for concept in dataset.objects("ParameterTable"):
                concept_id = concept.data["Concepticon_Gloss"]
                if concept_id:
                    concepts_in_source += [
                            ConceptInSource(
                                id=concept.id,
                                wordlist=self,
                                dataset=dsid,
                                data=concept.data
                                )]
                    concepts += [
                            Concept(
                                id=concept_id,
                                wordlist=self,
                                name=concept_id.lower(),
                                concepticon_id=concept.data["Concepticon_ID"],
                                concepticon_gloss=concept.data["Concepticon_Gloss"],
                                forms=[]
                            )
                        ]

            for form in dataset.objects("FormTable"):
                # check for concepticon ID
                if form.parameter.data["Concepticon_Gloss"]:
                    lid, cid, pid, fid = (
                            dsid+"-"+form.data["Language_ID"], 
                            form.parameter.data["Concepticon_Gloss"],
                            form.parameter.id,
                            dsid+"-"+form.id
                            )
                    forms += [(lid, cid, pid, fid, dsid, form)]
                
        self.languages = DictTuple(languages)
        self.concepts = DictTuple(concepts)
        self.concepts_in_source = DictTuple(concepts_in_source)
        self.forms = []
        for lid, cid, pid, fid, dsid, form in forms:
            self.forms += [Form(
                        id=fid,
                        concept=self.concepts[cid],
                        language=self.languages[lid],
                        concept_in_source=self.concepts_in_source[pid],
                        cldf=form,
                        data=form.data,
                        dataset=dsid,
                        wordlist=self
                        )]
            self.concepts[cid].forms += [self.forms[-1]]
            self.languages[lid].forms += [self.forms[-1]]
        self.forms = DictTuple(self.forms)




