import pytest
from cltoolkit import Wordlist
from pycldf import Dataset
from pathlib import Path
from tabulate import tabulate
from pyclts import CLTS
from cltoolkit.models import (
        CLCore, CLCoreWithForms, CLBase, CLBaseWithForms,
        Language, Sense, Concept, Form, Grapheme, Sound, 
        Inventory)
from cltoolkit.util import cltoolkit_test_path

import sys

def test_core_models():


    clts = CLTS(cltoolkit_test_path("repos", "clts"))
    datasets =[
            Dataset.from_metadata(cltoolkit_test_path("repos", "dummy", "cldf",
            "cldf-metadata.json"))
            ]
    wl = Wordlist.from_datasets(datasets, load=True)

    clc = CLCore(id="a", wordlist=wl, data={})
    assert clc.__repr__() == "<CLCore a>"

    clcwf = CLCoreWithForms(id="a", wordlist=wl, data={}, forms=[wl.forms[0],
        wl.forms[1]])
    assert len(clcwf.bipa_forms) == 2
    assert len(clcwf.segmented_forms) == 2


    clb = CLBase(id="a", wordlist=wl, data={}, obj=clc, dataset="a")
    assert repr(clb) == "<CLBase a>"

    clbwf = CLBaseWithForms(id="a", wordlist=wl, data={}, obj=clc, dataset="a",
            forms=[wl.forms[0],
            wl.forms[1]])
    assert len(clbwf.bipa_forms) == 2
    assert len(clbwf.segmented_forms) == 2


    lng = Language(
            id="dummy-Anyi", wordlist=wl, data=wl.languages[0].data, senses=[],
            concepts=[], forms=[wl.forms[0], wl.forms[1]])

    inv = Inventory.from_list(*[s for s in
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

    assert sound.similarity(wl.sounds[0]) == 0.0
    assert sound.similarity(sound) == 1
