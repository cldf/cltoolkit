from cltoolkit import pkg_path
from cltoolkit.wordlist import Wordlist
from cltoolkit.features.collection import FeatureCollection, feature_data


def test_FeatureCollection(ds_carvalhopurus, clts):
    wl = Wordlist([ds_carvalhopurus], clts.bipa)
    c = FeatureCollection.from_metadata(pkg_path / 'features' / 'features.json')
    _ = c('ConsonantQualitySize', wl.languages['carvalhopurus-Apurina'])
    assert repr(FeatureCollection.from_data(feature_data()).features['ConsonantQualitySize'])


def test_concepticon(concepticon):
    valid_glosses = set([c.gloss for c in concepticon.conceptsets.values()])
    c = FeatureCollection.from_metadata(pkg_path / 'features' / 'features.json')
    for feature in c.features:
        if feature.module.endswith("lexicon"):
            for key, value in feature.function.keywords.items():
                if key in ["alist", "blist", "ablist"]:
                    for concept in value:
                        if concept not in valid_glosses:
                            raise ValueError("gloss {0} not in concepticon".format(concept))


