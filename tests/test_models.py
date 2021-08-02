from cltoolkit import Wordlist
from cltoolkit.models import (
        CLCore, WithForms, WithDataset,
        Language, Sense, Form, Sound,
        Inventory)


def test_core_models(clts, ds_dummy):
    datasets = [ds_dummy]
    wl = Wordlist(datasets, clts.bipa)

    clc = CLCore(id="a", wordlist=wl, data={})
    assert clc.__repr__() == "<CLCore a>"

    wf = WithForms(forms=[wl.forms[0], wl.forms[1]])
    assert len(wf.bipa_forms) == 2
    assert len(wf.segmented_forms) == 2


    #clb = CLBase(id="a", wordlist=wl, data={}, obj=clc, dataset="a")
    #assert repr(clb) == "<CLBase a>"

    #clbwf = CLBaseWithForms(id="a", wordlist=wl, data={}, obj=clc, dataset="a",
    #        forms=[wl.forms[0],
    #        wl.forms[1]])
    #assert len(clbwf.bipa_forms) == 2
    #assert len(clbwf.segmented_forms) == 2

    lng = Language(
            id="dummy-Anyi", wordlist=wl, data=wl.languages[0].data, senses=[],
            concepts=[], forms=[wl.forms[0], wl.forms[1]])

    inv = Inventory.from_list(clts.bipa, *[s for s in
        wl.forms[0].segments]+[s for s in wl.forms[1].segments])
    assert len(lng.sound_inventory) == len(inv)
    assert wl.senses[0].__repr__() == "<Sense dummy-all>"
    assert wl.senses[0].__eq__(wl.senses[0]) == True
    assert wl.concepts[0].__repr__() == '<Concept all>'

    assert len(wl.forms[0].sounds) == len(wl.forms[0].segments) == len(
            wl.forms[0].tokens)
    assert len(wl.sounds[0]) == 1
    assert wl.sounds[0].__eq__(wl.sounds[1]) == False
    assert wl.sounds[0].name == 'voiced bilabial nasal consonant'
    assert wl.sounds[0].__repr__() == '<Sound m>'
    assert wl.sounds[0].__str__() == wl.sounds[0].grapheme

    assert round(wl.sounds[0].similarity(wl.sounds[2]), 2) == 0.33
    sound = Sound(id="a", grapheme="+", wordlist=wl, obj=clts.bipa["+"], data={"name": "dummy sound", "type": "marker", "featureset": frozenset(["f"])})
    soundB = Sound(id="Z", grapheme="Z", wordlist=wl, obj=clts.bipa["Z"], data={"name": "dummy sound", "type": "marker", "featureset": frozenset(["f"])})
    assert soundB.similarity(sound) == 0

    assert sound.similarity(wl.sounds[0]) == 0.0
    assert sound.similarity(sound) == 1

    sense1 = Sense(id="a", data={"name": "bbb"})
    sense2 = Sense(id="b", data={"name": "ccc"})
    assert sense1 == sense2
    assert sense1 != sound

    form = Form(id="a", data={"Form": "b", "Segments": ["a", "p", "a"]},
        tokens= ["a", "p", "a"],
            wordlist=wl, dataset="dummy")
    assert form.__repr__() == '<Form b>'
    assert form.graphemes[0].grapheme == "a"

    assert form.sounds[0] != form.graphemes[0]
    assert str(form.graphemes[0]) == str(form.sounds[0])
    

def test_inventory(clts):
    invA = Inventory.from_list(clts.bipa, "a", "u", "p", "k")
    invB = Inventory.from_list(clts.bipa, "a", "u", "b", "g")
    invC = Inventory.from_list(clts.bipa, "aː", "a", "u:", "b")
    assert len(invC.vowels_by_quality) == 2

    assert round(invA.strict_similarity(invB), 2) == 0.33
    assert invA.strict_similarity(invB, aspects=["vowels"]) == 1
    assert invA.approximate_similarity(invB) > 0.33
    assert Inventory.from_list(clts.bipa, "A", "u").approximate_similarity(invB) > 0.1
    assert invA.sounds['a'].__eq__(invB.sounds['a']) == True
    assert Inventory.from_list(clts.bipa).strict_similarity(Inventory.from_list(clts.bipa)) == 0
    assert Inventory.from_list(clts.bipa).approximate_similarity(Inventory.from_list(clts.bipa)) == 0
    assert Inventory.from_list(clts.bipa, "p", "t", "k", "a", "e", "u").approximate_similarity(
            Inventory.from_list(clts.bipa, "a", "e", "u"), aspects=["consonants",
                "vowels"]) == 0.5
    assert Inventory.from_list(clts.bipa, "p", "t", "k", ).approximate_similarity(
            Inventory.from_list(clts.bipa, "a", "e", "u"), aspects=["consonants",
                "vowels"]) == 0.0

    for sound in invA:
        assert isinstance(sound, Sound)
    assert invA["u"] == invA.sounds["u"]
