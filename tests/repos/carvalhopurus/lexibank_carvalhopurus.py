from pathlib import Path
from pylexibank.dataset import Dataset as BaseDataset 
from pylexibank import Concept, Lexeme, FormSpec
from pylexibank import progressbar

from clldutils.misc import slug
import attr


@attr.s
class CustomConcept(Concept):
    Number = attr.ib(default=None)


@attr.s
class CustomLexeme(Lexeme):
    Concept_in_Source = attr.ib(default=None)
    Value_in_Source = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "carvalhopurus"
    concept_class = CustomConcept
    lexeme_class = CustomLexeme
    form_spec = FormSpec(
            separators='~/',
            first_form_only=True,
            missing_data=[('-')]
            )

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.
        """
        concepts = {}
        for concept in self.conceptlists[0].concepts.values():
            cid = '{0}_{1}'.format(concept.number, slug(concept.english))
            args.writer.add_concept(
                    ID=cid,
                    Name=concept.english,
                    Number=concept.number,
                    Concepticon_ID=concept.concepticon_id,
                    Concepticon_Gloss=concept.concepticon_gloss
                    )
            concepts[concept.english] = cid
        args.writer.add_languages()
        args.writer.add_sources()

        for row in self.raw_dir.read_csv(
                'data.tsv', delimiter='\t', dicts=True):
            concept = row['Concept']
            puru = row['Proto-Purus']
            cogid = row['Number']
            if puru.strip():
                lexeme = args.writer.add_form(
                        Language_ID='ProtoPurus',
                        Parameter_ID=concepts[concept],
                        Value=puru,
                        Form=puru.strip('*').strip('-'),
                        Source='Carvalho2021'
                        )
                args.writer.add_cognate(
                        lexeme=lexeme,
                        Cognateset_ID=cogid,
                        Cognate_Detection_Method='expert',
                        Source='Carvalho2021'
                        )

            for language in ['Inapari', 'Apurina', 'Yine']:
                value, form, gloss, source = [row[language+'-'+key] for key
                        in ['Value', 'Form', 'Concept', 'Source']]
                if form.strip() and form != '-':
                    lexeme = args.writer.add_forms_from_value(
                            Language_ID=language,
                            Parameter_ID=concepts[concept],
                            Concept_in_Source=gloss,
                            Value_in_Source=value,
                            Value=form,
                            Source=''
                            )[0]
                    args.writer.add_cognate(
                            lexeme=lexeme,
                            Cognateset_ID=cogid,
                            Cognate_Detection_Method='expert',
                            Source='Carvalho2021'
                            )


