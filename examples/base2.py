from cltoolkit import Wordlist
from pycldf import Dataset
from cltoolkit.features.collection import FeatureCollection, feature_data
from cltoolkit.util import cltoolkit_path
from importlib import import_module

wordlists = ['allenbai', 'liusinitic', 'walworthpolynesian']

datasets = [
        Dataset.from_metadata(import_module('lexibank_'+ds).Dataset().cldf_dir.joinpath('cldf-metadata.json'))
        for ds in wordlists]

wl = Wordlist.from_lexibank([wordlists[0]])
