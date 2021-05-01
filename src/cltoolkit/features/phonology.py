"""Miscellaneous features collected typological databases.
"""
from collections import defaultdict, OrderedDict
from cltoolkit.util import syllables
from functools import partial


def base_inventory_query(language, attr=None):
    return len(getattr(language.inventory, attr))


def base_yes_no_query(language, attr=None):
    out = getattr(language.inventory, attr)
    if out:
        return 1
    return 0

def base_ratio(language, attr1=None, attr2=None):
    return len(getattr(language.inventory, attr1)) / len(
            getattr(language.inventory, attr2))


vowel_quality_size = partial(base_inventory_query, attr="vowels_by_quality")
consonant_quality_size = partial(base_inventory_query, attr="consonants_by_quality")
vowel_size = partial(base_inventory_query, attr="vowels")
consonant_size = partial(base_inventory_query, attr="consonants")
vowel_sound_size = partial(base_inventory_query, attr="vowel_sounds")
consonant_sound_size = partial(base_inventory_query, attr="consonant_sounds")
has_tones = partial(base_yes_no_query, attr="tones")
cv_ratio = partial(base_ratio, attr1="vowels", attr2="consonants")
cv_quality_ratio = partial(
        base_ratio, attr1="vowels_by_quality",
        attr2="consonants_by_quality")
cv_sounds_ratio = partial(
        base_ratio,
        attr1="vowel_sounds",
        attr2="consonant_sounds")



def plosive_fricative_voicing(language):
    """WALS Feature 4A, check for voiced and unvoiced sounds"""
    inv = language.inventory
    voiced = set([sound.clts.manner for sound in inv.consonants if
        (sound.clts.phonation=='voiced' and sound.clts.manner in
            ['stop', 'fricative']) or ( sound.clts.breathiness and
                sound.clts.manner in ['stop', 'fricative']) or (
                    sound.clts.voicing and sound.clts.manner in
                    ['stop', 'fricative'])])
    if not voiced:
        return 1
    elif len(voiced) == 2:
        return 4
    elif 'stop' in voiced:
        return 2
    elif 'fricative' in voiced:
        return 3


def has_ptk(language):
    """
    WALS Feature 5A, check for presence of certain sounds.
    """
    inv = language.inventory
    sounds = [sound.clts.s for sound in inv.consonants]
    
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
    """
    inv = language.inventory
    uvulars = set([sound.clts.manner for sound in inv.consonants if
            sound.clts.place=='uvular'])
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
    WALS Feature 7A, check for glottalized or implosive consonants."""
    inv = language.inventory
    ejectives = [sound for sound in inv.consonants if
            sound.clts.ejection and sound.clts.manner in 
            ['stop', 'affricate']]
    resonants = [sound for sound in inv.consonants if 
            sound.clts.ejection and sound.clts.manner not in
            ['stop', 'affricate']]
    implosives = [sound for sound in inv.consonants if 
            sound.clts.manner == 'implosive']
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
    WALS Feature 8A, check for lateral sounds."""
    inv = language.inventory
    laterals = set([sound.clts.manner for sound in
        inv.consonants if
        sound.clts.airstream == 'lateral'])
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
    WALS Feature 9A, check for nasals."""
    inv = language.inventory
    consonants = [sound.clts.s for sound in inv.consonants]
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
    vowels = [sound for sound in language.inventory.vowels if
            sound.clts.nasalization]
    if vowels:
        return 1
    return 2


def has_rounded_vowels(language):
    """
    WALS Feature 11A, check for front rounded vowels.
    """
    high = [sound for sound in language.inventory.vowels if
            sound.clts.roundedness == 'rounded' and sound.clts.height in
            ['open', 'near-open']]
    mid = [sound for sound in language.inventory.vowels if
            sound.clts.roundedness == 'rounded' and
            sound.clts.height in ['open-mid', 'mid']]
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
    
    preceding, following = defaultdict(list), defaultdict(list)
    for form in language.forms:
        for syllable in syllables(form):
            sounds, count = [], 0
            for sound in map(lambda x: language.wordlist.ts[x], syllable):
                if sound.type == 'marker':
                    log.warning(syllable, morpheme, form.id, form.segments)
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
    inv = language.inventory
    bilabials = [sound for sound in inv.consonants if 'bilabial' in
            sound.clts.featureset]
    fricatives = [sound for sound in inv.consonants if 'fricative' in
            sound.clts.featureset]
    nasals = [sound for sound in inv.consonants if 'nasal' in
            sound.clts.featureset]
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



