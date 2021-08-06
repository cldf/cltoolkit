import logging
from argparse import Namespace

import pytest

from cltoolkit.features.reqs import *


def test_requires(caplog):
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

    @requires()
    def f(language):
        raise ValueError()

    with caplog.at_level(logging.DEBUG):
        with pytest.raises(ValueError):
            f(Namespace(dataset='xyz'))
    assert 'xyz' in caplog.records[-1].message