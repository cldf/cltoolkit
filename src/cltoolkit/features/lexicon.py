"""Miscellaneous features for lexical data.
"""
from itertools import product

from . import util
from .reqs import requires, concepts


class ConceptComparison(util.FeatureFunction):
    def __init__(self, alist, blist, ablist=None, alabel=None, blabel=None):
        util.FeatureFunction.__init__(
            self, alist, blist, ablist=ablist, alabel=alabel, blabel=blabel)
        self.alist = [alist] if isinstance(alist, str) else alist
        self.blist = [blist] if isinstance(blist, str) else blist
        self.ablist = [ablist] if isinstance(ablist, str) else (ablist or [])
        self.alabel = util.concept_label(alist, label=alabel)
        self.blabel = util.concept_label(blist, label=blabel)
        self.categories = {None: 'missing data'}

    def run(self, aforms, bforms, abforms):
        raise NotImplementedError()  # pragma: no cover

    @requires(concepts)
    def __call__(self, language):
        aforms, bforms, abforms = [], [], []
        for xlist, xforms in zip([self.alist, self.blist, self.ablist], [aforms, bforms, abforms]):
            for x in xlist:
                if x in language.concepts:
                    for form in language.concepts[x].forms:
                        xforms += [form.form]
        return self.run(aforms, bforms, abforms)


class Colexification(ConceptComparison):
    def __init__(self, *args, **kw):
        ConceptComparison.__init__(self, *args, **kw)
        self.categories.update({
            True: "colexifies {} and {}".format(self.alabel, self.blabel),
            False: "does not colexify {} and {}".format(self.alabel, self.blabel),
        })

    def run(self, aforms, bforms, abforms):
        if aforms and bforms:
            return any(f in bforms for f in aforms)
        if abforms:
            return True


class PartialColexification(ConceptComparison):
    def __init__(self, *args, **kw):
        ConceptComparison.__init__(self, *args, **kw)
        self.categories.update({
            True: "{} partially colexified in {}".format(self.alabel, self.blabel),
            False: "{} not partially colexified in {}".format(self.alabel, self.blabel),
        })

    def run(self, aforms, bforms, abforms):
        for aform, bform in product(aforms, bforms):
            if bform.startswith(aform) and len(aform) > 2 and len(bform) > 5:
                return True
            if bform.endswith(aform) and len(aform) > 2 and len(bform) > 5:
                return True
        if aforms and bforms:
            return False


class SharedSubstring(ConceptComparison):
    def __init__(self, *args, **kw):
        ConceptComparison.__init__(self, *args, **kw)
        self.categories.update({
            True: "common substring in {} and {}".format(self.alabel, self.blabel),
            False: "no common substring in {} and {}".format(self.alabel, self.blabel),
        })

    def run(self, aforms, bforms, abforms):
        for aform, bform in product(aforms, bforms):
            for i in range(1, len(aform) - 1):
                morphA = aform[:i]
                morphB = aform[i:]
                if len(morphA) >= 3 and morphA in bform and bform != morphA:
                    return True
                if len(morphB) >= 3 and morphB in bform and bform != morphA:
                    return True
        if aforms and bforms:
            return False
