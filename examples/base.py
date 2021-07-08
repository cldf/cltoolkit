from cltoolkit import Wordlist
from cltoolkit.features.collection import FeatureCollection, feature_data
from cltoolkit.util import dataset_from_module

wordlists = ['allenbai', 'liusinitic', 'walworthpolynesian']
datasets = [dataset_from_module('lexibank_' + ds) for ds in wordlists]

wl = Wordlist.from_lexibank(wordlists)
ft = FeatureCollection.from_data(feature_data())

for language in wl.languages:
    for feature in ft.features:
        print(language.id, feature.name, feature(language))
