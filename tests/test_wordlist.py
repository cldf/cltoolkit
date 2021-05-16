from cltoolkit import Wordlist
from pycldf import Dataset
from pathlib import Path
from tabulate import tabulate

def load_data():
    wl = Wordlist.from_datasets(
            [Dataset.from_metadata(Path("repos", "carvalhopurus", "cldf",
            "cldf-metadata.json")),
            Dataset.from_metadata(Path("repos", "wangbcd", "cldf",
            "cldf-metadata.json")),

            ]
            )
    return wl


wl = load_data()
print("HEIGHT", wl.height)
print("WIDTH ", wl.width)
print("LENGTH", len(wl))
print("")
table = []
coverage = wl.coverage()
for language in wl.languages:
    table += [(language.name, len(language.forms), len(language.concepts),
        len(language.segmented_forms), 
        len(language.bipa_forms),
        len(language.inventory),
        coverage[language.id]
        )]
print(tabulate(table,
        headers = [
            "language",
            "forms",
            "concepts",
            "segmented forms",
            "bipa forms",
            "inventory",
            "coverage"
            ]
        ))
