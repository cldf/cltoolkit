from cltoolkit import pkg_path
from cltoolkit.wordlist import Wordlist
from cltoolkit.features.collection import FeatureCollection, feature_data


def test_FeatureCollection(ds_carvalhopurus, clts):
    wl = Wordlist([ds_carvalhopurus], clts.bipa)
    c = FeatureCollection.from_metadata(pkg_path / 'features' / 'features.json')
    _ = c('ConsonantQualitySize', wl.languages['carvalhopurus-Apurina'])
    assert repr(FeatureCollection.from_data(feature_data()).features['ConsonantQualitySize'])
