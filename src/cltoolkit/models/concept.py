"""
Basic class for handling concepts.
"""

import attr


@attr.s
class Concept:
    """
    Base class for handling concepts.
    """
    id = attr.ib()
    concept = attr.ib(default=None, repr=False)
    forms = attr.ib(default=None, repr=False)

    def __len__(self):
        return len(self.forms)
    
    @property
    def name(self):
        return self.concept['Name']
    
    @property
    def concepticon_id(self):
        return self.concept['Concepticon_ID']

    @property
    def concepticon_gloss(self):
        return self.concept['Concepticon_Gloss']
