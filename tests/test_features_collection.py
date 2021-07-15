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
        if hasattr(feature.function, "keywords"):
            for key, value in feature.function.keywords.items():
                if key in ["alist", "blist", "ablist", "concepts"]:
                    for concept in value:
                        if concept not in valid_glosses:
                            raise ValueError("gloss {0} not in concepticon".format(concept))


def test_clts(clts):
    c = FeatureCollection.from_metadata(pkg_path / 'features' / 'features.json')
    for feature in c.features:
        if hasattr(feature.function, "keywords"):
            for key, value in feature.function.keywords.items():
                if key in ["features"]:
                    for featureset in value:
                        for feature in featureset:
                            if feature not in clts.bipa.feature_system:
                                raise ValueError("feature value {0} not in clts".format(concept))
