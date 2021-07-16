from cltoolkit.wordlist import Wordlist
from cltoolkit.features.lexicon import (
        has_a_b_colexified,
        has_a_in_b,
        shares_substring)


def test_colexification(repos, ds_features, clts):
    wl = Wordlist([ds_features], clts.bipa)
    language = wl.languages[0]

    assert has_a_b_colexified(
            language,
            alist=["HAND"],
            blist=["ARM"],
            )
    assert has_a_b_colexified(
            language,
            alist=["FEMALE GOAT"],
            blist=["ARM"],
            ablist=["ARM OR HAND"]
            ) == False
    
    assert has_a_b_colexified(
            language,
            alist=["FEMALE GOAT"],
            blist=["ARM"],
            ) == False


    assert has_a_b_colexified(
            language,
            alist=["FEMALE GOAT"],
            blist=["ARM"],
            ) == False

    assert has_a_b_colexified(
            language,
            alist=["FEMALE GOAT"],
            blist=["MOUTH"]
            ) is None

    assert has_a_in_b(
            language,
            alist=["WATER"],
            blist=["TEAR (OF EYE)"]
            )

    assert has_a_in_b(
            language,
            alist=["WATER"],
            blist=["EYE"]
            ) == False

    assert has_a_in_b(
            language,
            alist=["WATER"],
            blist=["MOUTH"]
            ) is None

    assert shares_substring(
            language,
            alist=["FEMALE GOAT"],
            blist=["MALE GOAT"]
            )

    assert shares_substring(
            language,
            alist=["FEMALE GOAT"],
            blist=["ARM"]
            ) == False

    assert shares_substring(
            language,
            alist=["FEMALE GOAT"],
            blist=["MOUTH"]
            ) is None
