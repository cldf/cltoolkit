from cltoolkit import pkg_path
from cltoolkit.features.collection import FeatureCollection, feature_data
from cltoolkit.wordlist import Wordlist
from cltoolkit.models import Sound, Inventory, Language
from cltoolkit.features.phonology import (
        base_inventory_query,
        base_yes_no_query,
        base_ratio,
        starts_with_sound,
        sound_match,
        plosive_fricative_voicing,
        is_voiced,
        stop_like,
        is_uvular,
        is_ejective,
        is_lateral,
        is_nasal,
        has_ptk,
        has_uvular,
        has_glottalized,
        has_laterals,
        has_engma,
        has_nasal_vowels,
        has_rounded_vowels,
        syllable_structure,
        syllable_complexity,
        syllable_onset,
        syllable_offset,
        lacks_common_consonants,
        has_uncommon_consonants
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


def test_features(clts):
    inv = Inventory.from_list(clts.bipa, 
            "k", "t", "p", "l", "q", "r", "b", "d", "g", "u", "y", "ã")
    language = Language(id="dummy")
    language.sound_inventory = inv
    
    # has ptk
    assert has_ptk(language) == 5
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "a", "e")
    assert has_ptk(language) == 1
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "a", "e", "p")
    assert has_ptk(language) == 2
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "a", "e", "g")
    assert has_ptk(language) == 3
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "p", "t", "g")
    assert has_ptk(language) == 4


    assert has_uvular(language) == 1
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "p", "t", "q")
    assert has_uvular(language) == 2
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "p", "t", "χ")
    assert has_uvular(language) == 3
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "p", "t", "χ", "q")
    assert has_uvular(language) == 4


    assert has_glottalized(language) == 1
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "p", "t", "χ", "kʼ")
    assert has_glottalized(language) == 2
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "p", "t", "χ", "fʼ")
    assert has_glottalized(language) == 4
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "p", "t", "χ", "fʼ", "kʼ")
    assert has_glottalized(language) == 6
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "p", "t", "χ", "ɓ")
    assert has_glottalized(language) == 3
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "p", "t", "χ", "ɓ", "kʼ")
    assert has_glottalized(language) == 5
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "p", "t", "χ", "ɓ", "fʼ")
    assert has_glottalized(language) == 7


    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "p", "t", "χ", "ɓ", "ã")
    assert has_nasal_vowels(language)
    
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "p", "t", "χ", "ɓ", "a")
    assert not has_nasal_vowels(language)


    assert has_rounded_vowels(language) == 1
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "p", "t", "χ", "ɓ", "u", "y")
    assert has_rounded_vowels(language) == 3
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "p", "t", "χ", "ɓ", "ʉ", "y")
    assert has_rounded_vowels(language) == 2


    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "b", "f", "n")
    assert lacks_common_consonants(language) == 1
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "f", "n")
    assert lacks_common_consonants(language) == 2

    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "b", "n")
    assert lacks_common_consonants(language) == 3

    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "f", "b")
    assert lacks_common_consonants(language) == 4

    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "k", "g")
    assert lacks_common_consonants(language) == 6
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "f")
    assert lacks_common_consonants(language) == 5


    
    assert has_uncommon_consonants(language) == 1

    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "ǃ", "tˤ", "θ" )
    assert has_uncommon_consonants(language) == 6

    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "tˤ", "θ" )
    assert has_uncommon_consonants(language) == 7

    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "θ" )
    assert has_uncommon_consonants(language) == 5
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "tˤ" )
    assert has_uncommon_consonants(language) == 4
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "kʷ" )
    assert has_uncommon_consonants(language) == 3
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "ǃ" )
    assert has_uncommon_consonants(language) == 2


    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "p", "t", "k" )
    assert plosive_fricative_voicing(language) == 1
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "b", "d", "g")
    assert plosive_fricative_voicing(language) == 2
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "v", "ð", "ɣ")
    assert plosive_fricative_voicing(language) == 3
    language.sound_inventory = Inventory.from_list(
            clts.bipa,
            "v", "ð", "ɣ", "b", "d", "g")
    assert plosive_fricative_voicing(language) == 4

    for sounds, result in [
            [["p", "t", "k"], 1],
            [["p", "t", "l"], 2],
            [["p", "t", "ɬ"], 3],
            [["p", "t", "l", "tɬ"], 4],
            [["p", "t", "tɬ"], 5]]:
        language.sound_inventory = Inventory.from_list(
                clts.bipa, *sounds)
        assert has_laterals(language) == result



def test_inventory_queries(clts):
    inv = Inventory.from_list(clts.bipa, 
            "k", "t", "p", "l", "q", "r", "b", "d", "g", "u", "y", "ã")
    language = Language(id="dummy")
    language.sound_inventory = inv

    assert base_inventory_query(language, "consonants") == 9
    assert base_yes_no_query(language, "vowels")
    assert base_ratio(language, "consonants", "vowels") == 9 / 3

def test_wordlist_features(repos, ds_features, clts):
    wl = Wordlist([ds_features], ts=clts.bipa)
    
    assert starts_with_sound(wl.languages[0], concepts=["I"], features=[
        ["bilabial", "voiced", "nasal"]])
    assert starts_with_sound(wl.languages[0], concepts=["I"], features=[
        ["alveolar", "nasal"]])
    assert not starts_with_sound(wl.languages[0], concepts=["I"], features=[
        ["alveolar", "fricative"]])
    assert starts_with_sound(wl.languages[0], concepts=["MOUTH"], features=[
        ["alveolar", "stop"]]) is None

    assert has_engma(wl.languages[0]) == 1
    assert has_engma(wl.languages[1]) == 2
    assert has_engma(wl.languages[2]) == 3

    assert syllable_structure(wl.languages[0]) == 1
    assert syllable_structure(wl.languages[1]) == 2
    assert syllable_structure(wl.languages[2]) == 3

    assert syllable_onset(wl.languages[0]) == 1
    assert syllable_onset(wl.languages[1]) == 2
    assert syllable_onset(wl.languages[2]) == 3

    assert syllable_offset(wl.languages[0]) == 1
    assert syllable_offset(wl.languages[1]) == 2
    assert syllable_offset(wl.languages[2]) == 4
    assert syllable_offset(wl.languages[3]) == 3
