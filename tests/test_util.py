from lingpy.basictypes import lists

from cltoolkit.models import Form
from cltoolkit.util import (
    identity,
    jaccard,
    iter_syllables,
    valid_sounds,
    DictTuple,
    datasets_by_id,
)


def test_datasets_by_id(tests_dir):
    assert len(datasets_by_id('wangbcd', base_dir=tests_dir)) == 1


def test_DictTuple():
    class C:
        id = 5

    d = DictTuple(list('abcde'), key=identity)
    assert 'a' in d
    assert d['a'] == d[0]
    assert d.get('x', 5) == 5

    d = DictTuple([C()])
    assert C() in d
    assert 5 in d


def test_valid_sounds(clts):
    sounds = [clts.bipa[x] for x in ["_", "+", "a:", "b", "+", "_", "+", "c", "_", "_"]]
    assert valid_sounds(sounds)[0] == "aː"
    assert valid_sounds([]) == []
    assert valid_sounds([clts.bipa['a'], clts.bipa['_'], clts.bipa['b']]) == ['a', '+', 'b']


def test_identity():
    assert identity("x") == "x"


def test_jaccard():
    assert jaccard(set([1, 2]), set([1, 2])) == 1
    assert jaccard(set([]), set([])) == 0


def test_syllables():
    form = Form(id="test", sounds=lists("t a k + t a k"))
    assert len(list(iter_syllables(form))) == 2
