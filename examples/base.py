from cltoolkit import Wordlist
from cltoolkit.features import FEATURES
from cltoolkit.util import dataset_from_module

wordlists = ['allenbai', 'liusinitic', 'walworthpolynesian']
datasets = [dataset_from_module('lexibank_' + ds) for ds in wordlists]

wl = Wordlist.from_lexibank(wordlists)

for language in wl.languages:
    for feature in FEATURES.features:
        print(language.id, feature.name, feature(language))
