"""Miscellaneous features for lexical data.
"""
from functools import partial


def has_a_b_colexified(language, alist=None, blist=None, ablist=None):
    aforms, bforms, abforms = [], [], []
    for xlist, xforms in zip([alist, blist, ablist], [aforms, bforms, abforms]):
        if xlist:
            for x in xlist:
                if x in language.concepts:
                    for form in language.concepts[x].forms:
                        xforms += [form.form]

    if aforms and bforms:
        if [f for f in aforms if f in bforms]:
            return 1
        return 0
    elif abforms:
        return 1
    return "NA"


has_hand_arm_colexified = partial(
        has_a_b_colexified, 
        alist=["ARM"], 
        blist=["HAND"], 
        ablist=["ARM OR HAND"]
        )


has_finger_hand_colexified = partial(
        has_a_b_colexified, 
        alist=["FINGER", "FINGER OR TOE"], 
        blist=["HAND", "HAND OR ARM"],
        )


has_green_blue_colexified = partial(
        has_a_b_colexified,
        alist=["GREEN", "GREEN OR UNRIPE", "LIGHT GREEN"],
        blist=["BLUE", "LIGHT BLUE"],
        ablist=["BLUE OR GREEN"],
        )



has_red_yellow_colexified = partial(
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
