import pytest
from lingpy.basictypes import lists

from cltoolkit.models import Form
from cltoolkit.util import (
        identity,
        jaccard,
        cltoolkit_path,
        syllables,
        DictList,
        valid_tokens,
        )


def test_valid_tokens(clts):
    ts = clts.bipa
    sounds = [
        ts[x] for x in ["_", "+", "a:", "b", "+", "_", "+", "c", "_",
        "_"]]
    assert valid_tokens(sounds)[0] == "aː"


def test_identity():
    assert identity("x") == "x"


def test_jaccard():
    assert jaccard(
            set([1, 2]), set([1, 2])) == 1
    assert jaccard(set([]), set([])) == 0


def test_cltoolkit_path():
    assert "abc" in cltoolkit_path("abc")


def test_syllables():
    
    form = Form(id="test", tokens=lists("t a k + t a k"))
    assert len(list(syllables(form))) == 2


def test_DictList():

    lst = DictList([], key=lambda x: x)
    lst += ["a"]
    assert len(lst) == 1
    assert "a" in lst

    new_list = lst + ["b", "c"]
    assert len(new_list) == 3
    with pytest.raises(KeyError):
        lst + lst
    with pytest.raises(KeyError):
        DictList(["a", "a"], key=identity)

    assert lst.get("a") == "a"
    assert lst.get("x", "y") == "y"

