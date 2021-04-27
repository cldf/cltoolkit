"""Miscelleneous features collected from the WALS database.
"""
import attr
from collections import defaultdict, OrderedDict
from cltoolkit.util import syllables
from csvw.dsv import UnicodeDictReader
from importlib import import_module

def consonant_quality_size(language):
    sounds = []
    for s in language.inventory.consonants.values():
        sounds += [" ".join([s for s in s.name.split() if not "long" in s and not "short" in s])]
    return len(set(sounds))


def plosive_fricative_voicing(language):
    """WALS Feature 4A, check for voiced and unvoiced sounds"""
    inv = language.inventory
    voiced = set([sound.sound.manner for sound in inv.consonants.values() if
        (sound.sound.phonation=='voiced' and sound.sound.manner in
            ['stop', 'fricative']) or ( sound.sound.breathiness and
                sound.sound.manner in ['stop', 'fricative']) or (
                    sound.sound.voicing and sound.sound.manner in
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
    sounds = [sound.sound.s for sound in inv.consonants.values()]
    
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
    uvulars = set([sound.sound.manner for sound in inv.consonants.values() if
            sound.sound.place=='uvular'])
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
    ejectives = [sound for sound in inv.consonants.values() if
            sound.sound.ejection and sound.sound.manner in 
            ['stop', 'affricate']]
    resonants = [sound for sound in inv.consonants.values() if 
            sound.sound.ejection and sound.sound.manner not in
            ['stop', 'affricate']]
    implosives = [sound for sound in inv.consonants.values() if 
            sound.sound.manner == 'implosive']
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
    laterals = set([sound.sound.manner for sound in
        inv.consonants.values() if
        sound.sound.airstream == 'lateral'])
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
    consonants = [sound.sound.s for sound in inv.consonants.values()]
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
    vowels = [sound for sound in language.inventory.vowels.values() if
            sound.sound.nasalization]
    if vowels:
        return 1
    return 2


def has_rounded_vowels(language):
    """
    WALS Feature 11A, check for front rounded vowels.
    """
    high = [sound for sound in language.inventory.vowels.values() if
            sound.sound.roundedness == 'rounded' and sound.sound.height in
            ['open', 'near-open']]
    mid = [sound for sound in language.inventory.vowels.values() if
            sound.sound.roundedness == 'rounded' and
            sound.sound.height in ['open-mid', 'mid']]
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


def has_tones(inv):
    """
    WALS Feature 13A. Presence of tones.
    """
    if inv.tones:
        return 2
    return 1


def lacks_common_consonants(inv):
    """
    WALS Feature 18A, check for absence of common consonants.
    """
    bilabials = [sound for sound in inv.consonants.values() if 'bilabial' in
            sound.sound.featureset]
    fricatives = [sound for sound in inv.consonants.values() if 'fricative' in
            sound.sound.featureset]
    nasals = [sound for sound in inv.consonants.values() if 'nasal' in
            sound.sound.featureset]
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


def consonant_size(inv):
    return len(inv.consonants)


def vowel_size(inv):
    return len(inv.vowels)


def consonantal_size(inv):
    return len(inv.consonants)+len(inv.clusters)


def vocalic_size(inv):
    return len(inv.vowels)+len(inv.diphthongs)


def cv_ratio(inv):
    return len(inv.consonants) / len(inv.vowels)


def hand_and_arm(lng):
    """
    Return 0 for missing data
    """
    forms = [form for form in lng.forms if form.concept.concepticon_id in
            ['1673', '2121', '1277']]
    form_dict = defaultdict(list)
    for form in forms:
        form_dict[form.form] += [form.concept.concepticon_id]
    for k, v in form_dict.items():
        if ('1673' in v and '1277' in v) or '2121' in v:
            return 1
    concepts = [form.concept.concepticon_id for form in forms]
    if '1673' in concepts and '1277' in concepts:
        return 2
    return 0


def finger_and_hand(lng):
    forms = [form for form in lng.forms if form.concept.concepticon_id in
            ['1277', '1303', '2120']]
    form_dict = defaultdict(list)
    for form in forms:
        form_dict[form.form] += [form.concept.concepticon_id]
    for k, v in form_dict.items():
        if '1277' in v and ('1303' in v or '2120' in v):
            return 1
    concepts = [form.concept.concepticon_id for form in forms]
    if '1277' in concepts and ('1303' in concepts or '2120' in concepts):
        return 2
    return 0
