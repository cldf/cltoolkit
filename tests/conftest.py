import pathlib

import pytest

from pycldf import Dataset
from pyclts import CLTS


@pytest.fixture
def tests_dir():
    return pathlib.Path(__file__).parent


@pytest.fixture
def repos(tests_dir):
    return tests_dir / 'repos'


@pytest.fixture
def clts(repos):
    return CLTS(repos / 'clts')


@pytest.fixture
def ds_carvalhopurus(repos):
    return Dataset.from_metadata(repos / "carvalhopurus" / "cldf" / "cldf-metadata.json")


@pytest.fixture
def ds_wangbcd(repos):
    return Dataset.from_metadata(repos / "wangbcd" / "cldf" / "cldf-metadata.json")


@pytest.fixture
def ds_dummy(repos):
    return Dataset.from_metadata(repos / "dummy" / "cldf" / "cldf-metadata.json")
