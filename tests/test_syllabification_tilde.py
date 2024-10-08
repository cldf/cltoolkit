from lingpy.basictypes import lists
from collections import defaultdict
from cltoolkit.util import iter_syllables


def syllable_complexity(forms_with_sounds):
    """
    Compute the major syllabic patterns for a language.

    .. note::

       The computation follows the automated syllabification process described in
       List (2014) based on sonority. Based on this syllabification, we calculate
       the number of consonants preceding the syllable nucleus and those following
       it. For a given syllable, we store the form, the consonantal sounds, and
       the index of the syllable in the word. These values are returned in the
       form of two dictionaries, in which the number of sounds is the key.
    """

    preceding, following = defaultdict(list), defaultdict(list)
    for form in forms_with_sounds:
        idx = 0
        sounds_in_form = [s for s in form.sound_objects if (
            s.type != "marker" or s.obj.grapheme == '∼')]
        for i, syllable in enumerate(iter_syllables(form)):
            sounds, count = [], 0
            sounds_in_syllable = []
            for token in syllable:
                sounds_in_syllable += [sounds_in_form[idx]]
                idx += 1
            for sound in sounds_in_syllable:
                if (sound.type not in ['vowel', 'diphthong', 'tone', 'marker'] and
                        'syllabic' not in sound.obj.featureset
                    ) or sound.obj.grapheme == '∼':
                    count += 1
                    sounds += [sound]
                else:
                    break
            preceding[count] += [(form, sounds, i)]
            sounds, count = [], 0
            for sound in sounds_in_syllable[::-1]:
                if sound.type not in ['vowel', 'diphthong']:
                    if sound.type not in ['tone', 'marker']:
                        count += 1
                        sounds += [sound]
                else:
                    break
            following[count] += [(form, sounds, i)]

    return preceding, following


class Sound:
    def __init__(self, sound):
        self.obj = sound
        self.type = sound.type


class FormWithSounds:
    def __init__(self, seq, ts):
        self.sounds = lists(seq)
        self.sound_objects = [Sound(ts[s]) for s in self.sounds]
        self.seq = seq

    def __iter__(self):
        return iter(self.sounds)

    def __repr__(self):
        return str(self.sounds)


def test_features(clts):
    forms = [
            "t a t a t",
            "t a t + t a t",
            "t a t + t a ∼ k"
            ]

    ts = clts.bipa
    fws = [FormWithSounds(f, ts) for f in forms]
    p, f = syllable_complexity(fws)

    assert list(p[1][-1][0].__iter__()) == list(iter(lists(forms[-1])))
    assert p[1][-1][0].__repr__() == forms[-1]
