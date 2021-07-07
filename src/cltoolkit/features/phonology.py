"""Miscellaneous features collected typological databases.
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
    voiced = set([sound.obj.manner for sound in inv.consonants if
        (sound.obj.phonation=='voiced' and sound.obj.manner in
            ['stop', 'fricative']) or (sound.obj.breathiness and
                sound.obj.manner in ['stop', 'fricative']) or (
                    sound.obj.voicing and sound.obj.manner in
                    ['stop', 'fricative'])])
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
    
    if not 'p' in sounds and not 'g' in sounds:
        return 1
    elif not 'g' in sounds:
        return 2
    elif not 'p' in sounds:
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
            sound.obj.place=='uvular'])
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
    - 8: 
    """
    inv = language.sound_inventory
    ejectives = [sound for sound in inv.consonants if
            sound.obj.ejection and sound.obj.manner in 
            ['stop', 'affricate']]
    resonants = [sound for sound in inv.consonants if 
            sound.obj.ejection and sound.obj.manner not in
            ['stop', 'affricate']]
    implosives = [sound for sound in inv.consonants if 
            sound.obj.manner == 'implosive']
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
    else:
        return 8


def has_laterals(language):
    """
    WALS Feature 8A, check for lateral sounds.
    
    Values:
    - 1: no laterals
    - 2: one lateral, and the lateral is l
    - 3: has laterals, but no stops and no l
    - 4: has laterals, including l and stops
    - 5: has laterals, including stops, but no l
    - 6: 

    """
    inv = language.sound_inventory
    laterals = set([sound.obj.manner for sound in
        inv.consonants if
        sound.obj.airstream == 'lateral'])
    if not laterals:
        return 1
    elif len(laterals) == 1 and 'l' in inv.sounds:
        return 2
    elif not 'stop' in laterals and not 'l' in inv.sounds:
        return 3
    elif 'stop' in laterals and 'l' in inv.sounds:
        return 4
    elif 'stop' in laterals and not 'l' in inv.sounds:
        return 5
    else:
        return 6


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
        for fid, pos in inv.sounds['ŋ'].occs:
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
            sound.obj.roundedness == 'rounded' and sound.obj.height in
            ['open', 'near-open']]
    mid = [sound for sound in language.sound_inventory.vowels if
            sound.obj.roundedness == 'rounded' and
            sound.obj.height in ['open-mid', 'mid']]
    if not high and not mid:
        return 1
    elif high and mid:
        return 2
    elif high and not mid:
        return 3
    else:
        return 4


def syllable_complexity(language):
    """
    WALS Feature 12A, check for syllable complexity.

    This feature is handled differently in our implementation, since we
    only measure the harmonic mean between preceding and following
    syllables.
    """
    
    preceding, following = collections.defaultdict(list), collections.defaultdict(list)
    for form in language.forms:
        for syllable in iter_syllables(form):
            sounds, count = [], 0
            for sound in map(lambda x: language.wordlist.ts[x], syllable):
                if sound.type == 'marker':
                    log.warning(syllable, form.id, form.segments)
                if sound.type not in ['vowel', 'diphthong', 'tone', 'marker'] and \
                        not 'syllabic' in sound.featureset:
                    count += 1
                    sounds += [sound]
                else:
                    break
            preceding[count] += [sounds]
            sounds, count = [], 0
            for sound in map(lambda x: language.wordlist.ts[x], syllable[::-1]):
                if sound.type not in ['vowel', 'diphthong']:
                    if sound.type not in ['tone', 'marker']:
                        count += 1
                        sounds += [sound]
                else:
                    break
            following[count] += [sounds]

    p = max(preceding)
    f = max(following)
    return 2 * (p*f)/(p+f)


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
    labiovelars = [sound for sound in inv.consonants if sound.obj.labialization ==
            "labialized" and sound.obj.place in ["velar", "uvular"]]
    dentalfrics = [sound for sound in inv.consonants if sound.obj.place == "dental"
            and not sound.obj.airstream == "sibilant" and sound.obj.manner == "fricative"]
    pharyngeals = [sound for sound in inv.consonants if \
            sound.obj.place == "pharyngeal" or sound.obj.pharyngealization == "pharyngealized"]
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
