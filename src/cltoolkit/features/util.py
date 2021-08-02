import collections

__all__ = ['concept_label']


def concept_label(concept_list, label=None):
    if label:
        return label
    if len(concept_list) == 1:
        return concept_list[0]
    return ', '.join(concept_list)


class FeatureFunction:
    """
    `FeatureFunction` instances may also define the following attributes which are recognized by
    `Feature.to_json`:
    - `rtype`
    - `doc`
    - `categories`
    """
    def __init__(self, *args, **kw):
        self._args = args
        self._kwargs = kw

    def to_json(self):
        data = collections.OrderedDict()
        data['class'] = '{}.{}'.format(self.__class__.__module__, self.__class__.__name__)
        if self._args:
            data['args'] = self._args
        if self._kwargs:
            data['kwargs'] = self._kwargs
        return data

    def __call__(self, language):
        raise NotImplementedError()  # pragma: no cover
