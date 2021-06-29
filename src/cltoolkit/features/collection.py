"""
Basic handler for feature collections.
"""
import attr
from importlib import import_module
from csvw.dsv import UnicodeDictReader
from collections import OrderedDict
import json
from pycldf.util import DictTuple
from cltoolkit.util import cltoolkit_path


def feature_data():
    return json.load(open(cltoolkit_path('features', 'features.json')))


@attr.s(repr=False)
class Feature:
    id = attr.ib()
    name = attr.ib()
    type = attr.ib()
    target = attr.ib()
    module = attr.ib()
    function = attr.ib()
    note = attr.ib()

    def __call__(self, param):
        return self.function(param)

    def __repr__(self):
        return "<Feature "+self.id+">"


@attr.s
class FeatureCollection:
    features = attr.ib(default=None)
    
    @classmethod
    def from_metadata(cls, path):
        with open(path) as f:
            data = json.load(f)
        return cls.from_data(data)

    @classmethod
    def from_data(cls, data):
        features = []
        
        for vals in data:
            
            vals["function"] = getattr(
                    import_module(vals["module"]), vals["function"])
            features += [Feature(**vals)]
        return cls(features=DictTuple(features))

    def apply_to_language(self, feature, language):
        return self.features[feature](language)
        

