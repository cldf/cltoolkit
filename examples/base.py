from cltoolkit import Wordlist
from pycldf import Dataset
from cltoolkit.features.collection import FeatureCollection

ds = Dataset.from_metadata('/home/mattis/data/datasets/cldf/lexibank-data/allenbai/cldf/cldf-metadata.json')

wl = Wordlist.from_datasets([ds])
wl.load()
ft = FeatureCollection.from_metadata("features.json")
out = ft.apply_to_language("ConsonantQualitySize", wl.languages[1])
print(out)

for language in wl.languages:
    for feature in ft.features:
        print(language.id, feature.name, feature(language))
