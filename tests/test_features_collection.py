import pytest

from cltoolkit.wordlist import Wordlist
from cltoolkit.features import FEATURES, FeatureCollection, Feature
from cltoolkit.features.lexicon import ConceptComparison
from cltoolkit.features.phonology import StartsWithSound, InventoryQuery


def test_Feature(capsys):
    with pytest.raises(ValueError):
        _ = Feature(id=1, name='n', function=3)

    class Func:
        """computes stuff"""
        def __call__(self, language):
            return language

    f = Feature(id="xy", name='n', function=Func())
    assert f(5) == 5
    assert f.to_json()['function'] == {'class': 'test_features_collection.Func'}
    assert "computes stuff" in f.doc
    f.help()
    out, _ = capsys.readouterr()
    assert "computes" in out
    assert "xy" in str(f)
    assert Feature(id=1, name='x', function=InventoryQuery('v')).to_json()['type'] == 'int'


def test_FeatureCollection(ds_carvalhopurus, clts, tmp_path):
    wl = Wordlist([ds_carvalhopurus], clts.bipa)
    _ = FEATURES('ConsonantQualitySize', wl.languages['carvalhopurus-Apurina'])
    FEATURES.dump(tmp_path / 'test.json')
    fc = FeatureCollection.load(tmp_path / 'test.json')
    for s, o in zip(FEATURES, fc):
        assert s.id == o.id and s.categories == o.categories
    #assert all(s.id == o.id and s.categories == o.categories
    #           for s, o in zip(FEATURES.features, fc.features))


def test_concepticon(concepticon):
    valid_glosses = set([c.gloss for c in concepticon.conceptsets.values()])
    for feature in FEATURES:
        if isinstance(feature.function, (ConceptComparison, StartsWithSound)):
            for key in ["alist", "blist", "ablist", "concepts"]:
                value = getattr(feature.function, key, [])
                for concept in value:
                    if concept not in valid_glosses:  # pragma: no cover
                        raise ValueError("gloss {0} not in concepticon".format(concept))


def test_clts(clts):
    for feature in FEATURES:
        if isinstance(feature.function, StartsWithSound):
            for featureset in feature.function.features:
                for feature in featureset:
                    if feature not in clts.bipa.feature_system:  # pragma: no cover
                        raise ValueError("feature value {0} not in clts".format(feature))
