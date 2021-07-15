"""
Basic handler for feature collections.
"""
import textwrap
import importlib

import attr
from pycldf.util import DictTuple
from clldutils import jsonlib

from cltoolkit import pkg_path

__all__ = ['feature_data', 'Feature', 'FeatureCollection']


def feature_data():
    return jsonlib.load(pkg_path / 'features' / 'features.json')


@attr.s(repr=False)
class Feature:
    id = attr.ib()
    name = attr.ib()
    type = attr.ib()
    module = attr.ib()
    function = attr.ib()
    note = attr.ib()
    categories = attr.ib(default=None)
    requires = attr.ib(default=None)

    def help(self):
        if self.function.__doc__:
            print(textwrap.dedent(self.function.__doc__))

    def __call__(self, param):
        return self.function(param)

    def __repr__(self):
        return "<Feature " + self.id + ">"


class FeatureCollection:
    def __init__(self, features):
        self.features = DictTuple(features)

    @classmethod
    def from_metadata(cls, path):
        return cls.from_data(jsonlib.load(path))

    @classmethod
    def from_data(cls, data):
        features = []

        for vals in data:
            vals["function"] = getattr(importlib.import_module(vals["module"]), vals["function"])
            features += [Feature(**vals)]
        return cls(features)

    def __call__(self, feature, language):
        return self.features[feature](language)
