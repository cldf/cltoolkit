"""Miscellaneous phonological features found in typological databases.
"""
import textwrap
import collections
import typing

from cltoolkit.util import iter_syllables
from .reqs import requires, inventory, graphemes, inventory_with_occurrences
from . import util


class WithInventory(util.FeatureFunction):
    """
    Base class for feature callables requiring access to a phoneme inventory.
    """
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def run(self, inv):
        raise NotImplementedError()  # pragma: no cover

    @requires(inventory)
    def __call__(self, language):
        return self.run(language.sound_inventory)


class InventoryQuery(WithInventory):
    """
    Compute the length/sizte of some attribute of a sound inventory.

    .. code-block:: python

        number_of_consonants = InventoryQuery('consonants')
    """
    def __init__(self, attr):
        super().__init__(attr)
        self.attr = attr
        self.rtype = int
        self.doc = 'Number of items of type {} in the inventory.'.format(self.attr)

    def run(self, inv):
        return len(getattr(inv, self.attr))


class YesNoQuery(WithInventory):
    """
    Compute whether an inventory has some property.

    .. code-block:: python

        has_tones = YesNoQuery('tones')
    """
    def __init__(self, attr):
        super().__init__(attr)
        self.attr = attr
        self.rtype = bool
        self.doc = 'Does the inventory have {}?'.format(self.attr)

    def run(self, inv):
        return bool(len(getattr(inv, self.attr)))


class Ratio(WithInventory):
    """
    Computes the ratio between sizes of two properties of an inventory.
    """
    def __init__(self, attr1, attr2):
        super().__init__(attr1, attr2)
        self.attr1 = attr1
        self.attr2 = attr2
        self.rtype = float
        self.doc = 'Ratio between {} and {} in the inventory'.format(self.attr1, self.attr2)

    def run(self, inv):
        return len(getattr(inv, self.attr1)) / len(getattr(inv, self.attr2))


class StartsWithSound(util.FeatureFunction):
    """
    Check if a language has a form for {} starting with {}.

    .. note::

        Parametrized instances of this class can be used to check for certain cases of sound
        symbolism, or geographic / areal trends in languages to have word forms for certain
        concepts starting in certain words.

    .. seealso:: :func:`sound_match`

    .. code-block:: python

        mother_with_m = StartsWithSound(["MOTHER"], [["bilabial", "nasal"]], sound_label='[m]')
    """
    def __init__(self,
                 concepts: typing.List[str],
                 features: typing.List[typing.List[str]],
                 concept_label: typing.Optional[str] = None,
                 sound_label: typing.Optional[str] = None):
        """
        :param concepts: List of Concepticon conceptset glosses specifying a (broad) concept.
        :param features: List of lists of phonological features to check initial sounds against.
        """
        super().__init__(concepts, features, concept_label=concept_label, sound_label=sound_label)
        self.concepts = concepts
        self.features = features
        concept_label = util.concept_label(concepts, label=concept_label)
        sound_label = sound_label or str(self.features)
        self.rtype = bool
        self.doc = textwrap.dedent(
            self.__doc__.format(concept_label, sound_label)).split('Note:')[0].strip()
        self.categories = {
            True: "{} starts with {} or similar".format(concept_label, sound_label),
            False: "{} starts with another sound".format(concept_label),
            None: "missing data",
        }

    @requires(graphemes)
    def __call__(self, language):
        has_forms = False
        for concept in self.concepts:
            if concept in language.concepts:
                for form in language.concepts[concept].forms:
                    has_forms = True
                    if sound_match(form.sound_objects[0], self.features):
                        return True
        return False if has_forms else None


def sound_match(sound, features):
    """
    Match a sound by a subset of features.

    .. note::

        The major idea of this function is to allow for the convenient matching of
        some sounds by defining them in terms of a part of their features alone.
        E.g., [m] and its variants can be defined as ["bilabial", "nasal"], since
        we do not care about the rest of the features.
    """
    for feature in features:
        if not set(feature).difference(sound.featureset):
            return True
    return False


# vowel_sound_size = BaseInventoryQuery("vowel_sounds")
# consonant_sound_size = BaseInventoryQuery("consonant_sounds")
# has_tones =YesNoQuery("tones")


def is_voiced(sound):
    """
    Check if a sound is voiced or not.
    """
    if sound.obj.phonation == "voiced" or sound.obj.breathiness or sound.obj.voicing:
        return True
    return False


def is_glide(sound):
    """Check if sound is a glide or a liquid."""
    return sound.manner in {"trill", "approximant", "tap"}


def is_implosive(sound):
    """
    This groups stops and affricates into a group of sounds.
    """
    return sound.manner in {"implosive"}


def stop_like(sound):
    """
    This groups stops and affricates into a group of sounds.
    """
    return sound.manner in {"stop", "affricate"}


def is_uvular(sound):
    """
    Check if a sound is uvular or not.
    """
    return sound.obj.place == "uvular"


def is_ejective(sound):
    return sound.obj.ejection


def is_nasal(sound):
    return sound.manner == "nasal"


def is_lateral(sound):
    return sound.airstream == "lateral"


class PlosiveFricativeVoicing(WithInventory):
    """
    .. seealso:: `WALS 4A - Voicing in Plosives and Fricatives <https://wals.info/feature/4A>`_
    """
    categories = {
        1: "no voicing contrast",
        2: "in plosives alone",
        3: "in fricatives alone",
        4: "in both plosives and fricatives"
    }

    def run(self, inv):
        voiced = {
            sound.manner for sound in inv.consonants if
            sound.manner in ['stop', 'fricative'] and is_voiced(sound)  # noqa: W504
        }
        if not voiced:
            return 1
        if len(voiced) == 2:
            return 4
        if 'stop' in voiced:
            return 2
        if 'fricative' in voiced:
            return 3


class HasPtk(WithInventory):
    """
    .. seealso:: `WALS 5A - Voicing and Gaps in Plosive Systems <https://wals.info/feature/5A>`_
    """
    doc = "WALS Feature 5A, presence of certain sounds."
    categories = {
        1: "no p and no g in the inventory",
        2: "no g in the inventory",
        3: "no p in the inventory",
        4: "has less than 6 values of [p t t̪ k b d d̪ g]",
        5: "has at least 6 values of [p t t̪ k b d d̪ g]"
    }

    def run(self, inv):
        sounds = [sound.obj.s for sound in inv.consonants]

        if 'p' not in sounds and 'g' not in sounds:
            return 1
        if 'g' not in sounds:
            return 2
        if 'p' not in sounds:
            return 3
        if len(set([x for x in sounds
                    if x in ['p', 't', 't̪', 'k', 'b', 'd', 'g', 'd̪']])) >= 6:
            return 5
        return 4


class HasUvular(WithInventory):
    """
    .. seealso:: `WALS 6A - Uvular Consonants <https://wals.info/feature/6A>`_
    """
    categories = {
        1: "no uvulars",
        2: "has one uvular and this one is a stop",
        3: "has one uvular and this one is no stop",
        4: "has uvulars"
    }

    def run(self, inv):
        uvulars = set([sound.manner for sound in inv.consonants if is_uvular(sound)])
        if len(uvulars) == 0:
            return 1
        if len(uvulars) == 1:
            if 'stop' in uvulars:
                return 2
            return 3
        return 4


class HasGlottalized(WithInventory):
    """
    .. seealso:: `WALS 7A - Glottalized Consonants <https://wals.info/feature/7A>`_
    """
    categories = {
        1: "no ejectives, no implosives",
        2: "has ejective stops or affricates, but no implosives",
        3: "has implosive stops or affricates but no ejectives",
        4: "has ejectives resonants",
        5: "has ejectives and implosives but no ejective resonants",
        6: "has ejectives and ejective resonants, but no implosives",
        7: "has implosives and ejective resonants but no ejective stops",
        8: "has implosvies, ejective resonants, and ejective stops"
    }

    def run(self, inv):
        ejectives = [
            sound for sound in inv.consonants if is_ejective(sound) and stop_like(sound)]
        resonants = [
            sound for sound in inv.consonants if is_ejective(sound) and not stop_like(sound)]
        implosives = [sound for sound in inv.consonants if is_implosive(sound)]

        if not ejectives and not implosives and not resonants:
            return 1
        if ejectives and not implosives and not resonants:
            return 2
        if implosives and not ejectives and not resonants:
            return 3
        if resonants and not implosives and not ejectives:
            return 4
        if ejectives and implosives and not resonants:
            return 5
        if ejectives and resonants and not implosives:
            return 6
        if implosives and resonants and not ejectives:
            return 7
        return 8


class HasLaterals(WithInventory):
    """
    .. seealso:: `WALS 8A - Lateral Consonants <https://wals.info/feature/8A>`_
    """
    categories = {
        1: "no laterals",
        2: "only lateral [l]",
        3: "has laterals, but no stops in laterals and no [l]",
        4: "has laterals, including [l] and stops",
        5: "has laterals, inlcuding stops, but no [l]",
        6: "has laterals, but no stops and no [l]"
    }

    def run(self, inv):
        laterals = set([sound.obj.manner for sound in inv.consonants if is_lateral(sound)])
        if not laterals:
            return 1
        if len(laterals) == 1 and 'l' in inv.sounds:
            return 2
        if "affricate" not in laterals and 'stop' not in laterals and 'l' not in inv.sounds:
            return 3
        if ('stop' in laterals or "affricate" in laterals) and 'l' in inv.sounds:
            return 4
        if ('stop' in laterals or "affricate" in laterals) and 'l' not in inv.sounds:
            return 5
        return 6


class HasEngma(util.FeatureFunction):
    """
    .. seealso:: `WALS 9A - The Velar Nasal <https://wals.info/feature/9A>`_
    """
    categories = {
        1: "velar nasal occurs in syllable-initial position",
        2: "velar nasal occurs but not in syllable-initial position",
        3: "velar nasal is missing"
    }

    @requires(inventory_with_occurrences)
    def __call__(self, language):
        inv = language.sound_inventory
        consonants = [sound.obj.s for sound in inv.consonants]
        if 'ŋ' in consonants:
            for pos, fid in inv.sounds['ŋ'].occurrences:
                if pos == 0:
                    return 1
            return 2
        return 3


class HasSoundsWithFeature(WithInventory):
    """
    Does the inventory contain at least one {}.

    .. code-block:: python

        prenasalized_consonants = phonology.HasSoundsWithFeature("consonants", [["pre-nasalized"]])
    """
    def __init__(self, attr, features):
        super().__init__(attr, features)
        self.attr = attr
        self.features = features
        self.rtype = bool
        sound_spec = '{} {}'.format('  or '.join(' '.join(f) for f in self.features), self.attr)
        self.doc = textwrap.dedent(self.__doc__.format(sound_spec)).strip()
        self.categories = {
            True: 'has {}'.format(sound_spec),
            False: 'does not have {}'.format(sound_spec),
        }

    def run(self, inv):
        for sound in getattr(inv, self.attr):
            for featureset in self.features:
                if not set(featureset).difference(sound.featureset):
                    return True
        return False


class HasRoundedVowels(WithInventory):
    """
    .. seealso:: `WALS 11A - Front Rounded Vowels <https://wals.info/feature/11A>`_
    """
    categories = {
        1: "no high and no mid vowels",
        2: "high and mid vowels",
        3: "high and no mid vowels",
        4: "mid and no high vowels"
    }
    doc = "WALS Feature 11A, check for front rounded vowels."

    def run(self, inv):
        high = [
            sound for sound in inv.vowels if
            sound.obj.roundedness == 'rounded' and sound.obj.centrality in ['front', 'near-front']]
        mid = [
            sound for sound in inv.vowels if
            sound.obj.roundedness == 'rounded' and sound.obj.centrality in ['central']]
        if not high and not mid:
            return 1
        if high and mid:
            return 2
        if high and not mid:
            return 3
        return 4


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

    preceding, following = collections.defaultdict(list), collections.defaultdict(list)
    for form in forms_with_sounds:
        idx = 0
        sounds_in_form = [s for s in form.sound_objects if (
            s.type != "marker" or s.obj.grapheme == '∼')]
        for i, syllable in enumerate(iter_syllables(form)):
            sounds, count = [], 0
            sounds_in_syllable = []
            for token in syllable:
                sounds_in_syllable += [sounds_in_form[idx]]
                idx +=  1
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


class WithSyllableComplexity(util.FeatureFunction):
    def run(self, preceding, following):
        raise NotImplementedError()  # pragma: no cover

    @requires(graphemes)
    def __call__(self, language):
        return self.run(*syllable_complexity(language.forms_with_sounds))


class SyllableStructure(WithSyllableComplexity):
    """
    .. seealso::

        - :func:`syllable_complexity`
        - `WALS 12A - Syllable Structure <https://wals.info/feature/12A>`_
    """
    categories = {
        1: "simple syllable structure (only CV attested)",
        2: "moderately complex syllable structure (C(C)VC attested)",
        3: "complex syllable structure"
    }

    def run(self, preceding, following):
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


class SyllableOnset(WithSyllableComplexity):
    """
    .. seealso::

        - :func:`syllable_complexity`
        - `APiCS 118 - Syllable onsets <https://apics-online.info/parameters/118>`_
    """
    categories = {
        1: "simple syllable onset (only CV attested)",
        2: "moderately complex syllable onset (C(C)V attested)",
        3: "complex syllable onset"
    }

    def run(self, onsets, following):
        if max(onsets) <= 1:
            return 1
        if max(onsets) == 2:
            for form, sounds, i in onsets[2]:
                if not is_glide(sounds[1]):
                    return 3
            return 2
        return 3


class SyllableOffset(WithSyllableComplexity):
    """
    .. seealso::

        - :func:`syllable_complexity`
        - `APiCS 119 - Syllable codas <https://apics-online.info/parameters/119>`_
    """
    categories = {
        1: "simple syllable offset (only CV attested)",
        2: "moderately complex syllable offset (CVC attested)",
        3: "slightly complex syllable offset (CV(C)C attested)",
        4: "complex syllable offset"
    }

    def run(self, onsets, offsets):
        if max(offsets) == 0:
            return 1
        if max(offsets) == 1:
            return 2
        if max(offsets) == 2:
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
        return 4


class LacksCommonConsonants(WithInventory):
    """
    .. seealso:: `WALS 18A - Absence of Common Consonants <https://wals.info/feature/18A>`_
    """
    categories = {
        1: "bilabials and fricatives and nasals occur",
        2: "bilabials do not occur, fricatives and nasals occur",
        3: "fricatives do not occur, bilabials and nasals occur",
        4: "nasals do not occur, bilabials and fricatives occur",
        5: "bilabials and nasals do not occur, fricatives occur",
        6: "all other cases"
    }

    def run(self, inv):
        bilabials = [
            sound for sound in inv.consonants if 'bilabial' in sound.obj.featureset]
        fricatives = [
            sound for sound in inv.consonants if 'fricative' in sound.obj.featureset]
        nasals = [
            sound for sound in inv.consonants if 'nasal' in sound.obj.featureset]
        if bilabials and fricatives and nasals:
            return 1
        if not bilabials and fricatives and nasals:
            return 2
        if not fricatives and bilabials and nasals:
            return 3
        if not nasals and bilabials and fricatives:
            return 4
        if not bilabials and not nasals and fricatives:
            return 5
        return 6


class HasUncommonConsonants(WithInventory):
    """
    .. seealso:: `WALS 19A - Presence of Uncommon Consonants <https://wals.info/feature/19A>`_
    """
    categories = {
        1: "no clicsk and no dental fricatives and no labiovelars and no pharyngeals",
        2: "clicks and pharyngeals and dental fricatives",
        3: "pharyngeals and dental fricatives",
        4: "dentral fricatives",
        5: "pharyngeals",
        6: "labiovelars",
        7: "clicks"
    }

    def run(self, inv):
        clicks = [sound for sound in inv.consonants if sound.obj.manner == "click"]
        labiovelars = [
            sound for sound in inv.consonants if sound.obj.labialization ==  # noqa: W504
            "labialized" and sound.obj.place in ["velar", "uvular"]]
        dentalfrics = [
            sound for sound in inv.consonants if sound.obj.place == "dental"
            and not sound.obj.airstream == "sibilant" and sound.obj.manner == "fricative"]
        pharyngeals = [
            sound for sound in inv.consonants if
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
