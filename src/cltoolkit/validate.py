"""
Rudimentary validators for cltoolkit data.
"""
from cltoolkit import log
from lingpy.basictypes import lists

def valid_segments(segments, bipa):
    """
    Make sure that a list of segments does not have any wrong segmentations.
    """
    if not segments:
        return False
    else:
        if (
                '_' in segments or 
                '#' in segments or
                segments[0] == "+" or
                segments[-1] == "+" or
                (
                    "+" in segments and 
                    segments[segments.index("+")+1] == "+"
                    )
                ):
            return False
        else:
            bipa_sounds = list(map(lambda x: bipa[x], segments))
            if 'unknownsound' in [sound.type for sound in bipa_sounds]:
                return False
            return bipa_sounds

