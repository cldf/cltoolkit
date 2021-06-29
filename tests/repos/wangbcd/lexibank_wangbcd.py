import lingpy

from pathlib import Path
from clldutils.misc import slug
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import getEvoBibAsBibtex


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "wangbcd"

    def cmd_download(self, args):
        self.raw_dir.download_and_unpack(
            "https://zenodo.org/record/16760/files/"
            "Network-perspectives-on-Chinese-dialect-history-1.zip",
            self.raw_dir.joinpath("chinese.tsv"),
            self.raw_dir.joinpath("old_chinese.csv"),
            log=args.log,
        )

        self.raw_dir.write("sources.bib", getEvoBibAsBibtex("Hamed2006", "List2015d"))

    def cmd_makecldf(self, args):
        wl = lingpy.Wordlist(self.raw_dir.joinpath("chinese.tsv").as_posix())
        maxcogid = 0

        args.writer.add_sources()
        args.writer.add_languages(id_factory=lambda l: l["Name"])
        args.writer.add_concepts(id_factory=lambda c: slug(c.label, lowercase=False))

        # store list of proto-form to cognate set
        p2c = {}

        for k in wl:
            for row in args.writer.add_lexemes(
                Language_ID=wl[k, "doculect"],
                Parameter_ID=slug(wl[k, "concept"], lowercase=False),
                Value=wl[k, "ipa"],
                Source="Hamed2006",
                Cognacy=wl[k, "COGID"],
            ):
                args.writer.add_cognate(
                    lexeme=row, Cognateset_ID=wl[k, "cogid"],
                    Source=["Hamed2006", "List2015"]
                )
            maxcogid = max([maxcogid, int(wl[k, "cogid"])])
            p2c[wl[k, 'concept'], wl[k, "proto"]] = wl[k, "cogid"]
        idx = max([k for k in wl]) + 1
        for line in lingpy.csv2list(self.raw_dir.joinpath("old_chinese.csv").as_posix()):
            for val in line[1].split(", "):
                cogid = p2c.get((line[0], val))
                if not cogid:
                    maxcogid += 1
                    cogid = p2c[line[0], val] = maxcogid
                row = args.writer.add_form(
                    Language_ID="OldChinese",
                    Parameter_ID=slug(line[0], lowercase=False),
                    Form=val,
                    Value=val,
                    Source="Hamed2006",
                    Cognacy=p2c.get(val, val),
                )
                args.writer.add_cognate(lexeme=row, Cognateset_ID=cogid,
                        Source=["Hamed2006", "List2015"])
                idx += 1
