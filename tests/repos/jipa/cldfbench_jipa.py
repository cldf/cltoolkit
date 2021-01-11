"""
Generates a CLDF dataset for phoneme inventories from the "Journal of the IPA",
aggregated by Baird et al. (forth).
"""

import json
import unicodedata
from pathlib import Path
from unidecode import unidecode

from pyglottolog import Glottolog
from pyclts import CLTS, models

from pycldf import Sources
from cldfbench import CLDFSpec
from cldfbench import Dataset as BaseDataset
from clldutils.misc import slug

from cldfcatalog.config import Config
from collections import defaultdict
from tqdm import tqdm as progressbar
from clldutils.text import split_text_with_context, strip_brackets

def compute_id(text):
    """
    Returns a codepoint representation to an Unicode string.
    """

    unicode_repr = "".join(["u{0:0{1}X}".format(ord(char), 4) for char in text])

    label = slug(unidecode(text))

    return "%s_%s" % (label, unicode_repr)


def normalize_grapheme(text):
    """
    Apply simple, non-CLTS, normalization.
    """

    new_text = unicodedata.normalize("NFD", text)

    if new_text[0] == "(" and new_text[-1] == ")":
        new_text = new_text[1:-1]

    new_text = strip_brackets(new_text)
    if new_text:
        return new_text

def read_raw_source(filename):
    def _splitter(text):
        """
        Splits a list of phonemes as provided in the sourceself.

        We need to split by commas, provided they are not within parentheses (used to
        list allophones). This solution uses a negative-lookahead in regex.
        """ 
        # errors in files
        text = text.replace('\u032al', 'l̪')
        text = text.replace('\u2019', '\u02bc')
        text = text.replace('r (r, z)', 'r(r, z)')
        text = text.replace('eː (e:, é:, è:, êː)', 'eː(e:, é:, è:, êː)')
        text = text.replace('ɔ̤ (ɔ̤, ɔ̤́, ɔ̤̀, ɔ̤̌, ɔ̤̂)', 'ɔ̤(ɔ̤, ɔ̤́, ɔ̤̀, ɔ̤̌, ɔ̤̂)')
        text = text.replace('v ̼(v̼, ɸ, β, v, f)', 'v̼(v̼, ɸ, β, v, f)')
        items = split_text_with_context(text, "[ ,;]")
        out = []
        for item in items:
            out += [item]
        return out

    # Holds the label to the current section of data
    section = None

    data = {
        "source": None,
        "language_name": None,
        "iso_code": None,
        "consonants": '',
        "vowels": '',
    }

    # Iterate over all lines
    with open(filename) as handler:
        for line in handler:
            # Clear line (including BOM) and skip empty data
            line = line.replace("\ufeff", "").strip()

            if not line:
                continue

            if line.startswith("#"):
                section = line[1:-1].strip()
            elif section == "Reference":
                data["source"] = line
            elif section == "Language":
                data["language_name"] = line
            elif section == "ISO Code":
                data["iso_code"] = line
            elif section == "Consonant Inventory":
                data["consonants"] += ' '+line
            elif section == "Vowel Inventory":
                data["vowels"] += ' '+line
            elif section in [
                    "Phoneme inventory size",
                    "Phoneme invetory size",
                    "Size of phoneme inventory"
                    ]:
                data["inventory"] = int(line)
    data['consonants'] = _splitter(data['consonants'].strip())
    data['vowels'] = _splitter(data['vowels'].strip())

    return data


class Dataset(BaseDataset):
    """
    CLDF dataset for JIPA inventories.
    """

    dir = Path(__file__).parent
    id = "jipa"

    def cldf_specs(self):
        return CLDFSpec(
                module='StructureDataset',
                dir=self.cldf_dir,
                data_fnames={'ParameterTable': 'features.csv'}
            )

    def cmd_makecldf(self, args):

        glottolog = Glottolog(args.glottolog.dir)
        clts = CLTS(Config.from_file().get_clone('clts'))
        bipa = clts.bipa
        clts_jipa = clts.transcriptiondata_dict['jipa']

        # Add the bibliographic info
        sources = Sources.from_file(self.raw_dir / "sources.bib")
        args.writer.cldf.add_sources(*sources)

        # Add components
        args.writer.cldf.add_columns(
            "ValueTable",
            {"name": "InventorySize", "datatype": "integer"},
            {"name": "Value_in_Source", "datatype": "string"})

        args.writer.cldf.add_columns(
                    'ParameterTable',
                    {'name': 'CLTS_BIPA', 'datatype': 'string'},
                    {'name': 'CLTS_Name', 'datatype': 'string'})
        args.writer.cldf.add_component(
            "LanguageTable", "Family", "Glottolog_Name")

        languages = []
        all_glottolog = {lng.id: lng for lng in glottolog.languoids()}
        for row in progressbar(
                self.etc_dir.read_csv("languages.csv", dicts=True)):
            if row["Glottocode"] and row["Glottocode"] in all_glottolog:
                lang = all_glottolog[row["Glottocode"]]
                update = {
                    "Family": lang.family.name if lang.family else '',
                    "Glottocode": row["Glottocode"],
                    "Latitude": lang.latitude,
                    "Longitude": lang.longitude,
                    "Macroarea": lang.macroareas[0].name if lang.macroareas else None,
                    "Glottolog_Name": lang.name,
                }
                row.update(update)
            languages.append(row)

        # Build source map from language
        source_map = {lang["ID"]: lang["Source"] for lang in languages}

        # Parse sources
        segments = []
        values = []
        counter = 1
        source_files = list(self.raw_dir.glob("*.txt"))
        unknowns = defaultdict(list)
        for filename in source_files:
            contents = read_raw_source(filename)
            if not "inventory" in contents:
                args.log.warn('inventory size missing for {0}'.format(
                    filename))
                isize = -1
            else:
                isize = contents['inventory']
            all_segments = []
            for segment in contents["consonants"] + contents["vowels"]:
                all_segments.append(segment)
            lang_key = slug(contents["language_name"])

            for segment in all_segments:
                normalized = normalize_grapheme(segment)
                if normalized in clts_jipa.grapheme_map:
                    sound = bipa[clts_jipa.grapheme_map[normalized]]
                else:
                    sound = bipa['<NA>']
                    unknowns[normalized] += [(lang_key, segment)]
                par_id = compute_id(normalized)
                if sound.type == 'unknownsound':
                    bipa_grapheme = ''
                    desc = ''
                else:
                    bipa_grapheme = str(sound)
                    desc = sound.name

                segments.append((par_id, normalized, bipa_grapheme, desc))

                values.append(
                    {
                        "ID": str(counter),
                        "Language_ID": lang_key,
                        "Parameter_ID": par_id,
                        "Value_in_Source": segment,
                        "Value": normalized,
                        "Source": [source_map[lang_key]],
                        "InventorySize": isize 
                    }
                )
                counter += 1

        # Build segment data
        parameters = [
            {
                "ID": ID, 
                "Name": normalized,
                "Description": '',
                "CLTS_BIPA": bipa_grapheme,
                "CLTS_Name": desc}
            for ID, normalized, bipa_grapheme, desc in set(segments)
        ]

        # Write data and validate
        args.writer.write(**{
                "ValueTable": values,
                "LanguageTable": languages,
                "ParameterTable": parameters,})
        for g, rest in unknowns.items():
            print('\t'.join(
                [
                    repr(g), str(len(rest)), g]))
