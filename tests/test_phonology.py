import pytest

from cltoolkit.wordlist import Wordlist
from cltoolkit.models import Sound, Inventory, Language
from cltoolkit.features.phonology import (
    is_voiced,
    stop_like,
    is_uvular,
    is_ejective,
    is_lateral,
    is_nasal,
    HasPtk, HasUvular, HasGlottalized, HasSoundsWithFeature, HasRoundedVowels,
    LacksCommonConsonants, HasUncommonConsonants, PlosiveFricativeVoicing,
    HasLaterals, InventoryQuery, Ratio, YesNoQuery, StartsWithSound, HasEngma,
    SyllableStructure, SyllableOffset, SyllableOnset,
)


def test_properties(clts):

    assert is_nasal(Sound(id="s", obj=clts.bipa["n"]))
    assert not is_nasal(Sound(id="b", obj=clts.bipa["k"]))

    assert is_lateral(Sound(id="s", obj=clts.bipa["l"]))
    assert not is_lateral(Sound(id="b", obj=clts.bipa["k"]))

    assert is_uvular(Sound(id="s", obj=clts.bipa["q"]))
    assert not is_uvular(Sound(id="b", obj=clts.bipa["r"]))

    assert stop_like(Sound(id="s", obj=clts.bipa["ts"]))
    assert not stop_like(Sound(id="b", obj=clts.bipa["r"]))

    assert is_voiced(Sound(id="s", obj=clts.bipa["pʱ"]))
    assert not is_voiced(Sound(id="b", obj=clts.bipa["t"]))

    assert is_ejective(Sound(id="s", obj=clts.bipa["kʼ"]))
    assert not is_ejective(Sound(id="b", obj=clts.bipa["t"]))


@pytest.mark.parametrize(
    'func,inv,res',
    [
        (HasPtk(), "k t p l q r b d g u y ã", 5),
        (HasPtk(), "a e", 1),
        (HasPtk(), "a e p", 2),
        (HasPtk(), "a e g", 3),
        (HasPtk(), "p t g", 4),
        (HasUvular(), "p t g", 1),
        (HasUvular(), "p t q", 2),
        (HasUvular(), "p t χ", 3),
        (HasUvular(), "p t χ q", 4),
        (HasGlottalized(), "p t χ q", 1),
        (HasGlottalized(), "p t χ kʼ", 2),
        (HasGlottalized(), "p t χ fʼ", 4),
        (HasGlottalized(), "p t χ fʼ kʼ", 6),
        (HasGlottalized(), "p t χ ɓ", 3),
        (HasGlottalized(), "p t χ ɓ kʼ", 5),
        (HasGlottalized(), "p t χ ɓ fʼ", 7),
        (HasSoundsWithFeature("vowels", [["nasalized"]]), "p t χ ɓ ã", True),
        (HasSoundsWithFeature("vowels", [["nasalized"]]), "p t χ ɓ a", False),
        (HasRoundedVowels(), "p t χ ɓ a", 1),
        (HasRoundedVowels(), "p t χ ɓ u y", 3),
        (HasRoundedVowels(), "p t χ ɓ ʉ y", 2),
        (LacksCommonConsonants(), "b f n", 1),
        (LacksCommonConsonants(), "f b", 4),
        (LacksCommonConsonants(), "k g", 6),
        (LacksCommonConsonants(), "f", 5),
        (HasUncommonConsonants(), "f", 1),
        (HasUncommonConsonants(), "ǃ tˤ θ", 6),
        (HasUncommonConsonants(), "tˤ θ", 7),
        (HasUncommonConsonants(), "θ", 5),
        (HasUncommonConsonants(), "tˤ", 4),
        (HasUncommonConsonants(), "kʷ", 3),
        (HasUncommonConsonants(), "ǃ", 2),
        (PlosiveFricativeVoicing(), "p t k", 1),
        (PlosiveFricativeVoicing(), "b d g", 2),
        (PlosiveFricativeVoicing(), "v ð ɣ", 3),
        (PlosiveFricativeVoicing(), "v ð ɣ b d g", 4),
        (HasLaterals(), "p t k", 1),
        (HasLaterals(), "p t l", 2),
        (HasLaterals(), "p t ɬ", 3),
        (HasLaterals(), "p t l tɬ", 4),
        (HasLaterals(), "p t tɬ", 5),
        (InventoryQuery('consonants'), "k t p l q r b d g u y ã", 9),
        (YesNoQuery('vowels'), "k t p l q r b d g u y ã", True),
        (Ratio('consonants', 'vowels'), "k t p l q r b d g u y ã", 9 / 3),
    ]
)
def test_features(clts, func, inv, res):
    language = Language(id="dummy")
    language.sound_inventory = Inventory.from_list(clts.bipa, *inv.split())
    if isinstance(res, float):
        assert pytest.approx(res) == func(language)
    else:
        assert func(language) == res


@pytest.mark.parametrize(
    'func,lindex,res',
    [
        (StartsWithSound(["I"], [["bilabial", "voiced", "nasal"]]), 0, True),
        (StartsWithSound(["I"], [["alveolar", "nasal"]]), 0, True),
        (StartsWithSound(["I"], [["alveolar", "fricative"]]), 0, False),
        (StartsWithSound(["MOUTH"], [["alveolar", "stop"]]), 0, None),
        (HasEngma(), 0, 1),
        (HasEngma(), 1, 2),
        (HasEngma(), 2, 3),
        (SyllableStructure(), 0, 1),
        (SyllableStructure(), 1, 2),
        (SyllableStructure(), 2, 3),
        (SyllableOnset(), 0, 1),
        (SyllableOnset(), 1, 2),
        (SyllableOnset(), 2, 3),
        (SyllableOffset(), 0, 1),
        (SyllableOffset(), 1, 2),
        (SyllableOffset(), 2, 4),
        (SyllableOffset(), 3, 3),
    ]
)
def test_wordlist_features(func,lindex, res, repos, ds_features, clts):
    wl = Wordlist([ds_features], ts=clts.bipa)
    assert func(wl.languages[lindex]) is res
