"""Miscellaneous features collected in typological databases.
"""
import functools
import collections

from cltoolkit.util import iter_syllables
from cltoolkit import log


def base_inventory_query(language, attr=None):
    return len(getattr(language.sound_inventory, attr))


def base_yes_no_query(language, attr=None):
    return int(bool(getattr(language.sound_inventory, attr)))


def base_ratio(language, attr1=None, attr2=None):
    return len(getattr(language.sound_inventory, attr1)) / len(
        getattr(language.sound_inventory, attr2))


def starts_with_sound(language, concepts=None, features=None):
    """
    Check if a language has a form for a concept starting with some sound.

    Note:
    The test can be used to account for certain cases of sound symbolism, or
    geographic / areal trends in languages to have word forms for certain
    concepts starting in certain words.
    """
    forms = []
    for concept in concepts:
        if concept in language.concepts:
            forms += list(language.concepts[concept].forms)
    for form in forms:
        if sound_match(form.sounds[0], features):
            return True
    if forms:
        return False



def sound_match(sound, features):
    """
    Match a sound by a subset of features.

    Note:
    The major idea of this function is to allow for the convenient matching of
    some sounds by defining them in terms of a part of their features alone.
    E.g., [m] and its variants can be defined as ["bilabial", "nasal"], since
    we do not care about the rest of the features.
    """
    for feature in features:
        if not set(feature).difference(sound.featureset):
            return True
    return False


first_person_with_m = functools.partial(
        starts_with_sound,
        ["I"],
        [["bilabial", "nasal"],["labio-dental", "nasal"]]
)

first_person_with_n = functools.partial(
        starts_with_sound,
        ["I"],
        [
            ["dental", "nasal"],
            ["retroflex", "nasal"],
            ["alveolar", "nasal"],
            ["alveolo-palatal", "nasal"],
            ["retroflex", "nasal"]
            ]
)


second_person_with_t = functools.partial(
        starts_with_sound,
        ["THOU", "THEE (OBLIQUE CASE OF YOU)"],
        [
            ["dental", "fricative"],
            ["dental", "affricate"],
            ["dental", "stop"],
            ["alveolar", "fricative"],
            ["alveolar", "affricate"],
            ["alveolar", "stop"],
            ["palatal", "fricative"],
            ["palatal", "affricate"],
            ["palatal", "stop"],
            ["alveolo-palatal", "fricative"],
            ["alveolo-palatal", "affricate"],
            ["alveolo-palatal", "stop"],
            ["retroflex-palatal", "fricative"],
            ["retroflex-palatal", "affricate"],
            ["retroflex-palatal", "stop"]
            ]
)

second_person_with_n = functools.partial(
        starts_with_sound,
        ["THOU", "THEE (OBLIQUE CASE OF YOU)"],
        [
            ["dental", "nasal"], 
            ["retroflex nasal"], 
            ["palatal", "nasal"], 
            ["alveolo-palatal", "nasal"],
            ["alveolar", "nasal"]
            ]
        )


second_person_with_m = functools.partial(
        starts_with_sound,
        ["THOU", "THEE (OBLIQUE CASE OF YOU)"],
        [["bilabial", "nasal"],["labio-dental", "nasal"]]
        )


vowel_quality_size = functools.partial(base_inventory_query, attr="vowels_by_quality")
consonant_quality_size = functools.partial(base_inventory_query, attr="consonants_by_quality")
vowel_size = functools.partial(base_inventory_query, attr="vowels")
consonant_size = functools.partial(base_inventory_query, attr="consonants")
vowel_sound_size = functools.partial(base_inventory_query, attr="vowel_sounds")
consonant_sound_size = functools.partial(base_inventory_query, attr="consonant_sounds")
has_tones = functools.partial(base_yes_no_query, attr="tones")
cv_ratio = functools.partial(base_ratio, attr1="consonants", attr2="vowels")
cv_quality_ratio = functools.partial(
    base_ratio, attr1="consonants_by_quality",
    attr2="vowels_by_quality")
cv_sounds_ratio = functools.partial(
    base_ratio,
    attr1="consonant_sounds",
    attr2="vowel_sounds")


def is_voiced(sound):
    """
    Check if a sound is voiced or not.
    """
    if sound.obj.phonation == "voiced" or sound.obj.breathiness or sound.obj.voicing:
        return True
    return False


def is_glide(sound):
    """Check if sound is a glide or a liquid."""
    return sound.obj.manner in {"trill", "approximant", "tap"}

def is_implosive(sound):
    """
    This groups stops and affricates into a group of sounds.
    """
    return sound.obj.manner in {"implosive"}


def stop_like(sound):
    """
    This groups stops and affricates into a group of sounds.
    """
    return sound.obj.manner in {"stop", "affricate"}


def is_uvular(sound):
    """
    Check if a sound is uvular or not.
    """
    return sound.obj.place == "uvular"


def is_ejective(sound):
    return sound.obj.ejection


def is_nasal(sound):
    return sound.obj.manner == "nasal"


def is_lateral(sound):
    return sound.obj.airstream == "lateral"


def plosive_fricative_voicing(language):
    """
    WALS Feature 4A, check for voiced and unvoiced sounds

    Values:
    - 1: no voicing contrast
    - 2: in plosives alone
    - 3: in fricatives alone
    - 4: in both plosives and fricatives
    """
    inv = language.sound_inventory
    voiced = {
        sound.obj.manner for sound in inv.consonants if
        sound.obj.manner in ['stop', 'fricative'] and is_voiced(sound)# noqa: W504
        }
    if not voiced:
        return 1
    if len(voiced) == 2:
        return 4
    if 'stop' in voiced:
        return 2
    if 'fricative' in voiced:
        return 3


def has_ptk(language):
    """
    WALS Feature 5A, check for presence of certain sounds.

    Values:
    - 1: no p and no g in the inventory
    - 2: no g in the inventory
    - 3: no p in the inventory
    - 4: has less than 6 values of [p t t̪ k b d d̪ g]
    - 5: has at least 6 values of [p t t̪ k b d d̪ g]
    """
    inv = language.sound_inventory
    sounds = [sound.obj.s for sound in inv.consonants]

    if 'p' not in sounds and 'g' not in sounds:
        return 1
    elif 'g' not in sounds:
        return 2
    elif 'p' not in sounds:
        return 3
    elif len(set([x for x in sounds if x in ['p', 't', 't̪', 'k', 'b', 'd',
                                             'g', 'd̪']])) >= 6:
        return 5
    else:
        return 4


def has_uvular(language):
    """
    WALS Feature 6A, check for uvular sounds.

    Values:
    - 1: no uvulars
    - 2: has one uvular and this one is a stop
    - 3: has one uvular and this one is no stop
    - 4: has uvulars
    """
    inv = language.sound_inventory
    uvulars = set([sound.obj.manner for sound in inv.consonants if
                   is_uvular(sound)])
    if len(uvulars) == 0:
        return 1
    elif len(uvulars) == 1:
        if 'stop' in uvulars:
            return 2
        else:
            return 3
    else:
        return 4


def has_glottalized(language):
    """
    WALS Feature 7A, check for glottalized or implosive consonants.

    Values:
    - 1: no ejectives, no implosives
    - 2: has ejective stops or affricates, but no implosives
    - 3: has implosive stops or affricates but no ejectives
    - 4: has ejectives resonants
    - 5: has ejectives and implosives but no ejective resonants
    - 6: has ejectives and ejective resonants, but no implosives
    - 7: has implosives and ejective resonants but no ejective stops
    """
    inv = language.sound_inventory
    ejectives = [sound for sound in inv.consonants if
                 is_ejective(sound) and stop_like(sound)]
    resonants = [sound for sound in inv.consonants if 
                 is_ejective(sound) and not stop_like(sound)]
    implosives = [sound for sound in inv.consonants if
                  is_implosive(sound)]
    if not ejectives and not implosives and not resonants:
        return 1
    elif ejectives and not implosives and not resonants:
        return 2
    elif implosives and not ejectives and not resonants:
        return 3
    elif resonants and not implosives and not ejectives:
        return 4
    elif ejectives and implosives and not resonants:
        return 5
    elif ejectives and resonants and not implosives:
        return 6
    elif implosives and resonants and not ejectives:
        return 7

def has_laterals(language):
    """
    WALS Feature 8A, check for lateral sounds.

    Values:
    - 1: no laterals
    - 2: one lateral, and the lateral is l
    - 3: has laterals, but no stops and no l
    - 4: has laterals, including l and stops
    - 5: has laterals, including stops, but no l
    """
    inv = language.sound_inventory
    laterals = set([sound.obj.manner for sound in
                    inv.consonants if is_lateral(sound)])
    if not laterals:
        return 1
    elif len(laterals) == 1 and 'l' in inv.sounds:
        return 2
    elif "affricate" not in laterals and 'stop' not in laterals and 'l' not in inv.sounds:
        return 3
    elif ('stop' in laterals or "affricate" in laterals) and 'l' in inv.sounds:
        return 4
    elif ('stop' in laterals or "affricate" in laterals) and 'l' not in inv.sounds:
        return 5


def has_engma(language):
    """
    WALS Feature 9A, check for nasals.

    Values:
    - 1: ŋ occurs in the beginning of a word
    - 2: ŋ occurs but not in the beginning off words
    - 3: no ŋ
    """
    inv = language.sound_inventory
    consonants = [sound.obj.s for sound in inv.consonants]
    if 'ŋ' in consonants:
        for pos, fid in inv.sounds['ŋ'].occs:
            if pos == 0:
                return 1
        return 2
    return 3


def has_nasal_vowels(language):
    """
    WALS Feature 10A, check for nasal vowels.
    """
    vowels = [sound for sound in language.sound_inventory.vowels if
              sound.obj.nasalization]
    if vowels:
        return 1
    return 2


def has_rounded_vowels(language):
    """
    WALS Feature 11A, check for front rounded vowels.
    """
    high = [sound for sound in language.sound_inventory.vowels if
            sound.obj.roundedness == 'rounded' and sound.obj.centrality in
            ['front', 'near-front']]
    mid = [sound for sound in language.sound_inventory.vowels if
           sound.obj.roundedness == 'rounded' and sound.obj.centrality in ['central']]
    if not high and not mid:
        return 1
    elif high and mid:
        return 2
    elif high and not mid:
        return 3




def syllable_structure(language):
    """
    WALS Feature 12A, check for syllable complexity.

    Values:
    - 1: simple syllable structure (only CV attested)
    - 2: moderately complex structure
    - 3: complex syllable structure
    """
    preceding, following = syllable_complexity(language)
    p, f = max(preceding), max(following)
    if f == 0 and p <= 1:
        return 1
    if p == 1 and f == 1:
        return 2
    if p == 2:
        for form, sounds, i in preceding[2]:
            if not is_glide(sounds[1]):
                return 3
        return 2
    return 3


def syllable_complexity(language):
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

    preceding, following = collections.defaultdict(list), collections.defaultdict(list)
    for form in language.bipa_forms:
        idx = 0
        sounds_in_form = [s for s in form.sounds if s.type != "marker"]
        for i, syllable in enumerate(iter_syllables(form)):
            sounds, count = [], 0
            sounds_in_syllable = []
            for token in syllable:
                sounds_in_syllable += [sounds_in_form[idx]]
                idx += 1
            for sound in sounds_in_syllable:
                if sound.type not in ['vowel', 'diphthong', 'tone', 'marker'] and \
                        'syllabic' not in sound.obj.featureset:
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


def syllable_onset(language):
    """
    Check for syllable complexity onset (based on APICS 118).
    """
    onsets = syllable_complexity(language)[0]
    if max(onsets) <= 1:
        return 1
    elif max(onsets) == 2:
        for form, sounds, i in onsets[2]:
            if not is_glide(sounds[1]):
                return 3
        return 2
    else:
        return 3



def syllable_offset(language):
    """
    Check for syllable complexity offset (based on APICS 119).
    """
    offsets = syllable_complexity(language)[1]
    if max(offsets) == 0:
        return 1
    elif max(offsets) == 1:
        return 2
    elif max(offsets) == 2:
        # important: the representation lists offsets in opposite order, so
        # "karb" is rendered as "br"!
        for form, sounds, i in offsets[2]:
            if is_glide(sounds[1]):
                pass
            elif is_nasal(sounds[1]):
                pass
            elif stop_like(sounds[1]) and stop_like(sounds[0]):
                pass
            else:
                return 4
        return 3
    else:
        return 4


def lacks_common_consonants(language):
    """
    WALS Feature 18A, check for absence of common consonants.
    """
    inv = language.sound_inventory
    bilabials = [sound for sound in inv.consonants if 'bilabial' in
                 sound.obj.featureset]
    fricatives = [sound for sound in inv.consonants if 'fricative' in
                  sound.obj.featureset]
    nasals = [sound for sound in inv.consonants if 'nasal' in
              sound.obj.featureset]
    if bilabials and fricatives and nasals:
        return 1
    elif not bilabials and fricatives and nasals:
        return 2
    elif not fricatives and bilabials and nasals:
        return 3
    elif not nasals and bilabials and fricatives:
        return 4
    elif not bilabials and not nasals and fricatives:
        return 5
    else:
        return 6


def has_uncommon_consonants(language):
    """
    WALS Feature 19A, check for presence of uncommon consonants.
    """
    inv = language.sound_inventory
    clicks = [sound for sound in inv.consonants if sound.obj.manner == "click"]
    labiovelars = [sound for sound in inv.consonants if sound.obj.labialization ==  # noqa: W504
                   "labialized" and sound.obj.place in ["velar", "uvular"]]
    dentalfrics = [sound for sound in inv.consonants if sound.obj.place == "dental"
                   and not sound.obj.airstream == "sibilant" and sound.obj.manner == "fricative"]
    pharyngeals = [sound for sound in inv.consonants if
                   sound.obj.place == "pharyngeal" or  # noqa: W504
                   sound.obj.pharyngealization == "pharyngealized"]
    if not clicks and not dentalfrics and not labiovelars and not pharyngeals:
        return 1
    if clicks and pharyngeals and dentalfrics:
        return 6
    if pharyngeals and dentalfrics:
        return 7
    if dentalfrics:
        return 5
    if pharyngeals:
        return 4
    if labiovelars:
        return 3
    if clicks:
        return 2
