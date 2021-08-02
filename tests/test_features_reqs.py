from argparse import Namespace

import pytest

from cltoolkit.features.reqs import *


def test_requires():
    @requires(inventory, graphemes, concepts)
    def f(language):
        return True

    with pytest.raises(MissingRequirement) as e:
        f(None)
    assert 'inventory' in str(e)

    with pytest.raises(MissingRequirement) as e:
        f(Namespace(sound_inventory=[1, 2]))
    assert 'inventory' not in str(e)

    with pytest.raises(MissingRequirement):
        f(Namespace(sound_inventory=[1, 2], forms_with_graphemes=[1, 2]))

    assert f(Namespace(sound_inventory=[1, 2], forms_with_graphemes=[1, 2], concepts=[1, 2]))
