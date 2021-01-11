"""
Basic handler for feature collections.
"""
import attr
from importlib import import_module
from csvw.dsv import UnicodeDictReader
from collections import OrderedDict

@attr.s
class FeatureCollection:
    features = attr.ib(default=None)

    @classmethod
    def from_file(cls, path, modules=None):
        if modules:
            module_dicts = {module: import_module(module) for module in
                    modules} 
        else:
            module_dicts = {}
        features = OrderedDict()
        with UnicodeDictReader(path, delimiter='\t') as reader:
            for row in reader:
                if row['Module'] not in module_dicts:
                    module_dicts[row['Module']] = import_module(row['Module'])
                row['Function'] = getattr(
                        module_dicts[row['Module']], row['Function'])
                features[row['ID']] = row
        return cls(features=features)

    def apply(self, feature, obj):
        target = getattr(obj, self.features[feature]['Target'])
        fun = self.features[feature]['Function']
        for k, v in target.items():
            yield k, fun(v)

