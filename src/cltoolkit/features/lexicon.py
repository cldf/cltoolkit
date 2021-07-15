"""Miscellaneous features for lexical data.
"""
from functools import partial
from itertools import product


def has_a_b_colexified(language, alist=None, blist=None, ablist=None):
    """
    :rtype: boolean
    :return:
    - True: the language colexifies the specified concepts
    - False: the language does ot colexify the specified concepts
    - None: the language does not have counterparts for the specified concepts
    """
    aforms, bforms, abforms = [], [], []
    for xlist, xforms in zip([alist, blist, ablist], [aforms, bforms, abforms]):
        if xlist:
            for x in xlist:
                if x in language.concepts:
                    for form in language.concepts[x].forms:
                        xforms += [form.form]

    if aforms and bforms:
        return any(f in bforms for f in aforms)
    if abforms:
        return True


def has_a_in_b(
        language, alist=None, blist=None):
    """
    Check for partial colexification of a in b.

    :rtype: bool
    """
    aforms, bforms = [], []
    for xlist, xforms in zip([alist, blist], [aforms, bforms]):
        if xlist:
            for x in xlist:
                if x in language.concepts:
                    for form in language.concepts[x].forms:
                        xforms += [form.form]
    for aform, bform in product(aforms, bforms):
        if bform.startswith(aform) and len(aform) > 2 and len(bform) > 5:
            return True
        elif bform.endswith(aform) and len(aform) > 2 and len(bform) > 5:
            return True
    if aforms and bforms:
        return False


def shares_substring(
        language, alist=None, blist=None):
    """
    Check for a common substring in a and b.

    :rtype: bool
    """
    aforms, bforms = [], []
    for xlist, xforms in zip([alist, blist], [aforms, bforms]):
        if xlist:
            for x in xlist:
                if x in language.concepts:
                    for form in language.concepts[x].forms:
                        xforms += [form.form]
    for aform, bform in product(aforms, bforms):
        for i in range(1, len(aform)-1):
            morphA = aform[:i]
            morphB = aform[i:]
            if len(morphA) >= 3 and morphA in bform and bform != morphA:
                return True
            elif len(morphB) >= 3 and morphB in bform and bform != morphA:
                return True
    if aforms and bforms:
        return False


has_arm_and_hand_colexified = partial(
    has_a_b_colexified,
    alist=["ARM"],
    blist=["HAND"],
    ablist=["ARM OR HAND"]
)

has_finger_and_hand_colexified = partial(
    has_a_b_colexified,
    alist=["FINGER", "FINGER OR TOE"],
    blist=["HAND", "ARM OR HAND"],
)

has_green_and_blue_colexified = partial(
    has_a_b_colexified,
    alist=["GREEN", "GREEN OR UNRIPE", "LIGHT GREEN"],
    blist=["BLUE", "LIGHT BLUE"],
    ablist=["BLUE OR GREEN"],
)

has_red_and_yellow_colexified = partial(
    has_a_b_colexified,
    alist=["RED"],
    blist=["YELLOW", "BRIGHT YELLOW", "DARK YELLOW"],
)

has_leg_and_foot_colexified = partial(
    has_a_b_colexified,
    alist=["FOOT"],
    blist=["LEG"],
    ablist=["FOOT OR LEG"]
)

has_toe_and_foot_colexified = partial(
    has_a_b_colexified,
    alist=["FOOT", "FOOT OR LEG"],
    blist=["TOE", "FINGER OR TOE"]
)

has_eye_in_tear = partial(
    has_a_in_b,
    alist=["EYE"],
    blist=["TEAR (OF EYE)"]
)

has_water_in_tear = partial(
    has_a_in_b,
    alist=["WATER"],
    blist=["TEAR (OF EYE)"]
)

has_bark_and_skin_colexified = partial(
    has_a_b_colexified,
    alist=["BARK", "BARK OR SHELL"],
    blist=["SKIN", "SKIN (HUMAN)", "SKIN (ANIMAL)"],
    ablist=["BARK OR SKIN"]
)

has_skin_in_bark = partial(
    has_a_in_b,
    alist=["SKIN", "SKIN (HUMAN)", "SKIN (ANIMAL)"],
    blist=["BARK"]
)

has_tree_in_bark = partial(
    has_a_in_b,
    alist=["TREE", "TREE OR WOOD"],
    blist=["BARK"]
)


has_finger_and_toe = partial(
    has_a_b_colexified,
    alist=["FINGER"],
    blist=["TOE"],
    ablist=["FINGER OR TOE"]
)

has_hair_and_feather = partial(
    has_a_b_colexified,
    alist=["HAIR (BODY)", "HAIR (HEAD)", "HAIR"],
    blist=["FEATHER", "FUR"],
    ablist=["FEATHER OR FUR OR HAIR", "HAIR OR FUR"],
)

has_hear_and_smell = partial(
    has_a_b_colexified,
    alist=["HEAR", "EAR OR HEAR", "HEAR OR LISTEN"],
    blist=["SMELL", "SMELL (PERCEIVE)"]
)


