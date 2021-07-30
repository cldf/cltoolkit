import pytest

from cltoolkit.wordlist import Wordlist
from cltoolkit.features.lexicon import Colexification, PartialColexification, SharedSubstring


@pytest.mark.parametrize(
    'func,res',
    [
        (Colexification("HAND", "ARM"), True),
        (Colexification("FEMALE GOAT", "ARM", ablist="ARM OR HAND"), False),
        (Colexification("FEMALE GOAT", "ARM"), False),
        (Colexification("FEMALE GOAT", "MOUTH"), None),
        (PartialColexification("WATER", "TEAR (OF EYE)"), True),
        (PartialColexification("WATER", "EYE"), False),
        (PartialColexification("WATER", "MOUTH"), None),
        (SharedSubstring("FEMALE GOAT", "MALE GOAT"), True),
        (SharedSubstring("FEMALE GOAT", "ARM"), False),
        (SharedSubstring("FEMALE GOAT", "MOUTH"), None),
    ]
)
def test_colexification(repos, ds_features, clts, func, res):
    wl = Wordlist([ds_features], clts.bipa)
    assert func(wl.languages[0]) is res
