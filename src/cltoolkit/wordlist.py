import typing
import collections

import pycldf
from pyclts import TranscriptionSystem
import lingpy
from tqdm import tqdm as progressbar

from cltoolkit.util import identity, lingpy_columns, valid_sounds, DictTuple
from cltoolkit import log
from cltoolkit.models import Language, Concept, Grapheme, Form, Sense, Sound, Cognate


def idjoin(*comps):
    return '-'.join(comps)


class Wordlist:
    """
    A collection of one or more lexibank datasets, aligned by concept.

    :param datasets: The datasets you want to load, provided as list of \
    `pycldf.Dataset`.
    :param ts: A TranscriptionSystem (as provided  by pyclts), if you want to
       work with phonological features from CLTS.
    :ivar datasets:
    :ivar languages: :class:`DictTuple`
    :ivar senses: :class:`DictTuple`
    :ivar concepts: :class:`DictTuple`
    :ivar forms: :class:`DictTuple`
    :ivar Wordlist.graphemes: :class:`DictTuple`
    :ivar sounds: :class:`DictTuple`
    """
    def __init__(self,
                 datasets: typing.List[pycldf.Dataset],
                 ts: typing.Optional[TranscriptionSystem] = None,
                 concept_id_factory: typing.Callable[[dict], str] =
                 lambda x: x["Concepticon_Gloss"]):
        self.datasets = DictTuple(datasets, key=lambda x: x.metadata_dict["rdf:ID"])
        self.ts = ts
        self.concept_id_factory = concept_id_factory

        # During data loading, we use flexible, mutable dicts.
        self.languages = collections.OrderedDict()
        self.concepts = collections.OrderedDict()
        self.forms = collections.OrderedDict()
        self.senses = collections.OrderedDict()
        self.graphemes = collections.OrderedDict()
        self.sounds = collections.OrderedDict()

        for dsid, dataset in self.datasets.items():
            log.info("loading {0}".format(dsid))
            self._add_languages(dsid, dataset)
            self._add_senses(dsid, dataset)
            self._add_forms(dsid, dataset)

        self.forms_with_sounds = DictTuple([f for f in self.forms.values() if f.sounds])
        self.forms_with_graphemes = DictTuple([f for f in self.forms.values() if f.graphemes])
        log.info("loaded wordlist with {0} concepts and {1} languages".format(
            self.height, self.width))

        # Once the data is loaded, we "freeze" it, making read-only access more flexible.
        self.languages = DictTuple(self.languages.values())
        self.concepts = DictTuple(self.concepts.values())
        self.forms = DictTuple(self.forms.values())
        self.senses = DictTuple(self.senses.values())
        self.graphemes = DictTuple(self.graphemes.values())
        self.sounds = DictTuple(self.sounds.values())

        for lg in self.languages:
            lg.forms = DictTuple(lg.forms.values())
            lg.senses = DictTuple(lg.senses.values())
            lg.concepts = DictTuple(lg.concepts.values())
            for c in lg.concepts:
                c.forms = DictTuple(c.forms.values())
                c.senses = DictTuple(c.senses.values())
            for s in lg.senses:
                s.forms = DictTuple(s.forms.values())

        for s in self.senses:
            s.forms = DictTuple(s.forms.values())

        for c in self.concepts:
            c.forms = DictTuple(c.forms.values())
            c.senses = DictTuple(c.senses.values())

        for g in self.graphemes:
            g.forms = DictTuple(g.forms.values())

        for s in self.sounds:
            s.graphemes_in_source = DictTuple(s.graphemes_in_source.values())
            s.forms = DictTuple(s.forms.values())

    def _add_languages(self, dsid, dataset):
        """Append languages to the wordlist.
        """
        for language in dataset.objects("LanguageTable"):
            language_id = idjoin(dsid, language.id)
            self.languages[language_id] = Language(
                id=language_id,
                wordlist=self,
                data=language.data,
                obj=language,
                dataset=dsid,
                forms=collections.OrderedDict(),
                senses=collections.OrderedDict(),
                concepts=collections.OrderedDict(),
            )

    def _add_senses(self, dsid, dataset):
        """Append senses (concepts) to the wordlist."""
        for concept in dataset.objects("ParameterTable"):
            concept_id = self.concept_id_factory(concept.data)
            new_sense = Sense(
                id=idjoin(dsid, concept.id),
                wordlist=self,
                dataset=dsid,
                data=concept.data,
                forms=collections.OrderedDict(),
            )
            if concept_id and concept_id not in self.concepts:
                new_concept = Concept.from_sense(
                    new_sense,
                    id=concept_id,
                    name=concept_id.lower(),
                    forms=collections.OrderedDict(),
                    senses=collections.OrderedDict(),
                )
                self.concepts[new_concept.id] = new_concept
            if concept_id:
                self.concepts[concept_id].senses[new_sense.id] = new_sense
            self.senses[new_sense.id] = new_sense

    def _add_forms(self, dsid, dataset):
        """Add forms to the dataset."""
        for form in progressbar(
                dataset.objects("FormTable"), desc="loading forms for {0}".format(dsid)):
            lid, cid, pid, fid = (
                idjoin(dsid, form.cldf.languageReference),
                self.concept_id_factory(form.parameter.data),
                idjoin(dsid, form.parameter.id),
                idjoin(dsid, form.id)
            )
            new_form = Form(
                id=fid,
                concept=self.concepts[cid] if cid else None,
                language=self.languages[lid],
                sense=self.senses[pid],
                obj=form,
                data=form.data,
                dataset=dsid,
                cognates={},
                wordlist=self
            )
            self.forms[new_form.id] = new_form
            sounds = [self.ts[s] for s in new_form.graphemes] if self.ts else None
            if sounds:
                new_form.sounds = valid_sounds(sounds)
                for i, (segment, sound) in enumerate(zip(new_form.graphemes, sounds)):
                    gid = idjoin(dsid, segment)
                    if gid not in self.graphemes:
                        self.graphemes[gid] = Grapheme(
                            id=gid,
                            grapheme=segment,
                            dataset=dsid,
                            wordlist=self,
                            obj=sound,
                            occurrences=collections.OrderedDict(),
                            forms=collections.OrderedDict([(new_form.id, new_form)]))
                    self.graphemes[gid].forms[new_form.id] = new_form
                    try:
                        self.graphemes[gid].occurrences[lid].append((i, new_form))
                    except KeyError:
                        self.graphemes[gid].occurrences[lid] = [(i, new_form)]
                    if new_form.sounds:
                        sid = str(sound)
                        if sid not in self.sounds:
                            self.sounds[sid] = Sound.from_grapheme(
                                self.graphemes[gid],
                                graphemes_in_source=collections.OrderedDict(),
                                grapheme=str(sound),
                                obj=sound,
                                occurrences=collections.OrderedDict(),
                                forms=collections.OrderedDict([(new_form.id, new_form)]),
                                id=sid)
                        self.sounds[sid].forms[new_form.id] = new_form
                        self.sounds[sid].graphemes_in_source[gid] = self.graphemes[gid]
                        try:
                            self.sounds[sid].occurrences[lid].append((i, new_form))
                        except KeyError:
                            self.sounds[sid].occurrences[lid] = [(i, new_form)]
            if cid and cid not in self.languages[lid].concepts:
                self.languages[lid].concepts[cid] = Concept.from_concept(
                    self.concepts[cid],
                    senses=collections.OrderedDict(),
                    forms=collections.OrderedDict(),
                )

            if cid:
                self.languages[lid].concepts[cid].forms[new_form.id] = new_form
                self.concepts[cid].forms[new_form.id] = new_form
                if pid not in self.languages[lid].concepts[cid].senses:
                    self.languages[lid].concepts[cid].senses[pid] = self.senses[pid]

            if pid not in self.languages[lid].senses:
                self.languages[lid].senses[pid] = Sense.from_sense(
                    self.senses[pid], self.languages[lid], collections.OrderedDict())
            self.languages[lid].senses[pid].forms[new_form.id] = new_form
            self.languages[lid].forms[new_form.id] = new_form
            self.senses[pid].forms[new_form.id] = new_form

    def __len__(self):
        return len(self.forms)

    def load_cognates(self):
        self.cognates = collections.OrderedDict()
        for dsid, dataset in self.datasets.items():
            self._add_cognates(dsid, dataset)
        # TODO not sure this is the best way to handle this but loading this
        # multiple times seems also not useful

    def _add_cognates(self, dsid, dataset):
        """
        Add cognate sets for the data that has been loaded.
        """
        for cog in progressbar(
                dataset.objects("CognateTable"), desc="loading cognates for {0}".format(dsid)):
            # note that the cognateset Reference can be None, this needs to be
            # caught up here
            if cog.cldf.cognatesetReference:
                form_id = idjoin(dsid, cog.cldf.formReference)
                cogset = Cognate(
                    id=idjoin(dsid, cog.cldf.cognatesetReference),
                    wordlist=self,
                    obj=cog.cldf,
                    dataset=dsid,
                    data=cog.data,
                    form=self.forms[form_id],
                    contribution=cog.data.get("contribution", "default")
                )
                self.forms[form_id].cognates[cogset.contribution] = cogset
                self.cognates[cogset.id] = cogset
        self.cognates = DictTuple(self.cognates.values())

    def as_lingpy(
            self,
            language_filter=identity,
            sense_filter=identity,
            form_filter=identity,
            columns=None,
    ):
        transform = lingpy.Wordlist
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
                    elif obj == "cognates":
                        # we need to check if a cognate set exists for the
                        # reference, if not, we provide a fake-cognate object
                        # with an ID that is empty
                        row += [form.cognates.get(att, Cognate(id="")).id]
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
        flatten = identity if not flat else \
            lambda x: [item for sublist in x for item in sublist]
        transform = identity if not aspect else lambda x: getattr(x, aspect)
        concepts = [self.concepts[c] for c in concepts] if concepts else self.concepts
        languages = [self.languages[i] for i in languages] if languages else self.languages
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

    def coverage(self, concepts="concepts", aspect="forms_with_sounds"):
        out = {}
        for language in self.languages:
            out[language.id] = 0
            for concept in getattr(language, concepts):
                if getattr(concept, aspect):
                    out[language.id] += 1
        return out
