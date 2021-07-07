from lingpy.basictypes import lists

from cltoolkit.models import Form
from cltoolkit.util import (
    identity,
    jaccard,
    iter_syllables,
    valid_tokens,
)


def test_valid_tokens(clts):
    sounds = [clts.bipa[x] for x in ["_", "+", "a:", "b", "+", "_", "+", "c", "_", "_"]]
    assert valid_tokens(sounds)[0] == "aː"


def test_identity():
    assert identity("x") == "x"


def test_jaccard():
    assert jaccard(set([1, 2]), set([1, 2])) == 1
    assert jaccard(set([]), set([])) == 0


def test_syllables():
    form = Form(id="test", tokens=lists("t a k + t a k"))
    assert len(list(iter_syllables(form))) == 2
