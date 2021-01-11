"""
Basic classes for handling forms.
"""

import attr


@attr.s
class Form:
    """
    Base class for handling forms.
    """
    id = attr.ib(default=None)
    language = attr.ib(default=None, repr=False)
    concept = attr.ib(default=None, repr=False)
    tokens = attr.ib(default=None)
    sounds = attr.ib(default=None)
    concept_in_source = attr.ib(default=None, repr=False)
    attributes = attr.ib(default=None, repr=False)

    @property
    def value(self):
        return self.attributes['Value']

    @property
    def form(self):
        return self.attributes['Form']

    @property
    def segments(self):
        return self.attributes['Segments']


