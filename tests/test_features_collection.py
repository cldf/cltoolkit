from cltoolkit import pkg_path
from cltoolkit.wordlist import Wordlist
from cltoolkit.features.collection import FeatureCollection


def test_FeatureCollection(ds_carvalhopurus):
    wl = Wordlist([ds_carvalhopurus])
    c = FeatureCollection.from_metadata(pkg_path / 'features' / 'features.json')
    res = c('ConsonantQualitySize', wl.languages['carvalhopurus-Apurina'])