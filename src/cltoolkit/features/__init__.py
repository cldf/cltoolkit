"""
A feature is some aspect of language, e.g. the size of its phoneme inventory.

In `cltoolkit`, a :class:`Feature` is an object bundling some metadata with a python callable
accepting a :class:`cltoolkit.models.Language` instance as its sole argument, and returning the
value computed for this language.

A :class:`FeatureCollection` of predefined features is available in :data:`FEATURES`.
"""
from .collection import FeatureCollection, Feature
from . import phonology
from . import lexicon
from .reqs import requires

assert requires

#: Predefined lexical and phonological features.
FEATURES = FeatureCollection(Feature(**f) for f in [
    {
        "id": "ConsonantQualitySize",
        "name": "consonant quality size",
        "function": phonology.InventoryQuery("consonants_by_quality"),
    },
    {
        "id": "VowelQualitySize",
        "name": "vowel quality size",
        "function": phonology.InventoryQuery("vowels_by_quality"),
    },
    {
        "id": "VowelSize",
        "name": "vowel size",
        "function": phonology.InventoryQuery("vowels"),
    },
    {
        "id": "ConsonantSize",
        "name": "consonant size",
        "function": phonology.InventoryQuery("consonants"),
    },
    {
        "id": "CVRatio",
        "name": "consonant and vowel ratio",
        "function": phonology.Ratio("consonants", "vowels"),
    },
    {
        "id": "CVQualityRatio",
        "name": "consonant and vowel ratio (by quality)",
        "function": phonology.Ratio("consonants_by_quality", "vowels_by_quality"),
    },
    {
        "id": "CVSoundRatio",
        "name": "consonant and vowel ratio (including diphthongs and clusters)",
        "function": phonology.Ratio("consonant_sounds", "vowel_sounds"),
    },
    {
        "id": "HasNasalVowels",
        "name": "has nasal vowels or not",
        "function": phonology.HasSoundsWithFeature("vowels", [["nasalized"]]),
        "note": "same as: WALS 10A",
    },
    {
        "id": "HasRoundedVowels",
        "name": "has rounded vowels or not",
        "function": phonology.HasRoundedVowels(),
        "note": "same as: WALS 11A",
    },
    {
        "id": "VelarNasal",
        "name": "has the velar nasal (engma)",
        "function": phonology.HasEngma(),
        "note": "same as: WALS 9A",
    },
    {
        "id": "PlosiveVoicingGaps",
        "name": "voicing and gaps in plosives",
        "function": phonology.HasPtk(),
        "note": "same as: WALS 5A",
    },
    {
        "id": "LacksCommonConsonants",
        "name": "gaps in plosives",
        "function": phonology.LacksCommonConsonants(),
        "note": "same as: WALS 18A",
    },
    {
        "id": "HasUncommonConsonants",
        "name": "has uncommon consonants",
        "function": phonology.HasUncommonConsonants(),
        "note": "same as: WALS 19A",
    },
    {
        "id": "LegAndFoot",
        "name": "has the same word form for foot and leg",
        "function": lexicon.Colexification(["FOOT"], ["LEG"], ablist=["FOOT OR LEG"]),
    },
    {
        "id": "PlosiveFricativeVoicing",
        "name": "voicing in plosives and fricatives",
        "function": phonology.PlosiveFricativeVoicing(),
        "note": "same as: WALS 4A",
    },
    {
        "id": "UvularConsonants",
        "name": "presence of uvular consonants",
        "function": phonology.HasUvular(),
        "note": "same as: WALS 6A",
    },
    {
        "id": "GlottalizedConsonants",
        "name": "presence of glottalized consonants",
        "function": phonology.HasGlottalized(),
        "note": "same as: WALS 7A",
    },
    {
        "id": "HasLaterals",
        "name": "presence of lateral consonants",
        "function": phonology.HasLaterals(),
        "note": "same as: WALS 8A",
    },
    {
        "id": "SyllableStructure",
        "name": "complexity of the syllable structure",
        "function": phonology.SyllableStructure(),
        "note": "same as: WALS 12A",
    },
    {
        "id": "ArmAndHand",
        "name": "arm and hand distinguished or not",
        "function": lexicon.Colexification(["ARM"], ["HAND"], ablist=["ARM OR HAND"]),
        "note": "same as: WALS 129A, APICS 112",
    },
    {
        "id": "BarkAndSkin",
        "name": "bark and skin distinguished or not",
        "function": lexicon.Colexification(
            ["BARK", "BARK OR SHELL"],
            ["SKIN", "SKIN (HUMAN)", "SKIN (ANIMAL)"],
            ablist=["BARK OR SKIN"],
            alabel='BARK', blabel='SKIN',
        ),
    },
    {
        "id": "FingerAndHand",
        "name": "finger andhand distinguished or not",
        "function": lexicon.Colexification(
            ["FINGER", "FINGER OR TOE"], ["HAND", "ARM OR HAND"], alabel='finger', blabel='hand'),
        "note": "same as: WALS 130A",
    },
    {
        "id": "GreenAndBlue",
        "name": "green and blue colexified or not",
        "function": lexicon.Colexification(
            ["GREEN", "GREEN OR UNRIPE", "LIGHT GREEN"],
            ["BLUE", "LIGHT BLUE"],
            ablist=["BLUE OR GREEN"],
            alabel='GREEN',
            blabel='BLUE',
        ),
        "note": "similar to: APICS 116, WALS 134A",
    },
    {
        "id": "RedAndYellow",
        "name": "red and yellow colexified or not",
        "function": lexicon.Colexification(
            ["RED"], ["YELLOW", "BRIGHT YELLOW", "DARK YELLOW"], blabel='YELLOW'),
        "note": "similar to: WALS 135A",
    },
    {
        "id": "ToeAndFoot",
        "name": "toe and foot colexified or not",
        "function": lexicon.Colexification(
            ["FOOT", "FOOT OR LEG"],
            ["TOE", "FINGER OR TOE"],
            alabel='FOOT',
            blabel='TOE',
        ),
    },
    {
        "id": "SeeAndKnow",
        "name": "see and know colexified or not",
        "function": lexicon.Colexification(
            ["SEE"], ["KNOW", "KNOW (SOMETHING)"], blabel='KNOW'),
    },
    {
        "id": "SeeAndUnderstand",
        "name": "see and understand colexified or not",
        "function": lexicon.Colexification(["SEE"], ["UNDERSTAND"]),
    },
    {
        "id": "ElbowAndKnee",
        "name": "elbow and knee colexified or not",
        "function": lexicon.Colexification(alist=["ELBOW"], blist=["KNEE"]),
    },
    {
        "id": "FearAndSurprise",
        "name": "fear and surprise colexified or not",
        "function": lexicon.Colexification(
            ["FEAR (BE AFRAID)", "FEAR (FRIGHT)", "FEAR OR FRIGHTEN"],
            ["SURPRISE (SOMEBODY)", "SURPRISED", "SURPRISE (FEELING)"],
            alabel='FEAR',
            blabel='SURPRISE',
        ),
    },
    {
        "id": "CommonSubstringInElbowAndKnee",
        "name": "elbow and knee are partially colexified or not",
        "function": lexicon.SharedSubstring(alist=["ELBOW"], blist=["KNEE"]),
    },
    {
        "id": "CommonSubstringInManAndWoman",
        "name": "man and woman are partially colexified or not",
        "function": lexicon.SharedSubstring(
            ["MAN", "MALE PERSON"],
            ["WOMAN", "FEMALE PERSON"],
            alabel='MAN',
            blabel='WOMAN',
        ),
    },
    {
        "id": "CommonSubstringInFearAndSurprise",
        "name": "fear and surprise are partially colexified or not",
        "function": lexicon.SharedSubstring(
            ["FEAR (BE AFRAID)", "FEAR (FRIGHT)", "FEAR OR FRIGHTEN"],
            ["SURPRISE (SOMEBODY)", "SURPRISED", "SURPRISE (FEELING)"],
            alabel='FEAR',
            blabel='SURPRISE',
        ),
    },
    {
        "id": "CommonSubstringInBoyAndGirl",
        "name": "boy and girl are partially colexified or not",
        "function": lexicon.SharedSubstring(
            ["BOY", "BOY OR SON"],
            ["GIRL", "DAUGHTER OR GIRL"],
            alabel='BOY',
            blabel='GIRL',
        ),
    },
    {
        "id": "EyeInTear",
        "name": "eye partially colexified in tear",
        "function": lexicon.PartialColexification(
            ["EYE"], ["TEAR (OF EYE)"], blabel='TEAR'),
        "note": "similar to: APICS 111",
    },
    {
        "id": "BowInElbow",
        "name": "bow partially colexified in elbow",
        "function": lexicon.PartialColexification(["BOW"], ["ELBOW"])
    },
    {
        "id": "CornerInElbow",
        "name": "corner partially colexified in elbow",
        "function": lexicon.PartialColexification(["CORNER"], ["ELBOW"]),
    },
    {
        "id": "WaterInTear",
        "name": "water partially colexified in tear",
        "function": lexicon.PartialColexification(["WATER"], ["TEAR (OF EYE)"], blabel='TEAR'),
        "note": "similar to: APICS 111",
    },
    {
        "id": "TreeInBark",
        "name": "tree partially colexified in bark",
        "function": lexicon.PartialColexification(
            ["TREE", "TREE OR WOOD"], ["BARK"], alabel='TREE'),
    },
    {
        "id": "SkinInBark",
        "name": "skin partially colexified in bark",
        "function": lexicon.PartialColexification(
            ["SKIN", "SKIN (HUMAN)", "SKIN (ANIMAL)"], ["BARK"], alabel='SKIN'),
    },
    {
        "id": "MouthInLip",
        "name": "mouth partially colexified in lip",
        "function": lexicon.PartialColexification(["MOUTH"], ["LIP"]),
    },
    {
        "id": "SkinInLip",
        "name": "skin partially colexified in lip",
        "function": lexicon.PartialColexification(
            ["SKIN", "SKIN (HUMAN)", "SKIN (ANIMAL)"], ["LIP"], alabel='SKIN'),
    },
    {
        "id": "HandInFinger",
        "name": "hand partially colexified in finger",
        "function": lexicon.PartialColexification(
            ["HAND", "ARM OR HAND"],
            ["FINGER", "FINGER OR TOE"],
            alabel='HAND',
            blabel='FINGER',
        ),
    },
    {
        "id": "FootInToe",
        "name": "foot partially colexified in toe",
        "function": lexicon.PartialColexification(
            ["FOOT", "FOOT OR LEG"], ["TOE", "FINGER OR TOE"], alabel='FOOT', blabel='TOE'),
    },
    {
        "id": "ThreeInEight",
        "name": "three partially colexified in eight",
        "function": lexicon.PartialColexification(["THREE"], ["EIGHT"]),
    },
    {
        "id": "ThreeInThirteen",
        "name": "three partially colexified in thirteen",
        "function": lexicon.PartialColexification(["THREE"], ["THIRTEEN"]),
    },
    {
        "id": "FingerAndToe",
        "name": "finger and toe colexified or not",
        "function": lexicon.Colexification(["FINGER"], ["TOE"], ablist=["FINGER OR TOE"]),
        "note": "similar to: APICS 113",
    },
    {
        "id": "HairAndFeather",
        "name": "hair and feather colexified or not",
        "function": lexicon.Colexification(
            ["HAIR (BODY)", "HAIR (HEAD)", "HAIR"],
            ["FEATHER", "FUR"],
            ablist=["FEATHER OR FUR OR HAIR", "HAIR OR FUR"],
            alabel='HAIR',
        ),
        "note": "similar to: APICS 114",
    },
    {
        "id": "HearAndSmell",
        "name": "hear and smell colexified or not",
        "function": lexicon.Colexification(
            ["HEAR", "EAR OR HEAR", "HEAR OR LISTEN"],
            ["SMELL", "SMELL (PERCEIVE)"],
            alabel='HEAR',
            blabel='SMELL',
        ),
        "note": "similar to: APICS 115",
    },
    {
        "id": "FirstPersonWithM",
        "name": "fist person starts with an m-sound",
        "type": "bool",
        "function": phonology.StartsWithSound(
            ["I"],
            [["bilabial", "nasal"], ["labio-dental", "nasal"]],
            concept_label='first_person',
            sound_label='[m]'),
        "note": "similar to: WALS 136B",
    },
    {
        "id": "FirstPersonWithN",
        "name": "fist person starts with an n-sound",
        "function": phonology.StartsWithSound(
            ["I"],
            [
                ["dental", "nasal"],
                ["retroflex", "nasal"],
                ["alveolar", "nasal"],
                ["alveolo-palatal", "nasal"],
                ["retroflex", "nasal"]
            ],
            concept_label='first person',
            sound_label='[n]',
        ),
        "note": "see also: FirstPersonWithM, SecondPersonWithT, SecondPersonWithN, "
                "SecondPersonWithM",
    },
    {
        "id": "SecondPersonWithT",
        "name": "second person starts with a t-sound",
        "function": phonology.StartsWithSound(
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
                ["retroflex", "fricative"],
                ["retroflex", "affricate"],
                ["retroflex", "stop"]
            ],
            concept_label='second person',
            sound_label='[t]',
        ),
        "note": "see also: FirstPersonWithM, FirstPersonWithN, "
                "SecondPersonWithN, SecondPersonWithM",
    },
    {
        "id": "SecondPersonWithM",
        "name": "second person starts with an m-sound",
        "function": phonology.StartsWithSound(
            ["THOU", "THEE (OBLIQUE CASE OF YOU)"],
            [["bilabial", "nasal"], ["labio-dental", "nasal"]],
            concept_label='second person',
            sound_label='[m]',
        ),
        "note": "see also: FirstPersonWithM, FirstPersonWithN, "
                "SecondPersonWithT, SecondPersonWithN",
    },
    {
        "id": "SecondPersonWithN",
        "name": "second person starts with an n-sound",
        "function": phonology.StartsWithSound(
            ["THOU", "THEE (OBLIQUE CASE OF YOU)"],
            [
                ["dental", "nasal"],
                ["retroflex", "nasal"],
                ["palatal", "nasal"],
                ["alveolo-palatal", "nasal"],
                ["alveolar", "nasal"]
            ],
            concept_label='second person',
            sound_label='[n]',
        ),
        "note": "see also: FirstPersonWithM, FirstPersonWithN, "
                "SecondPersonWithT, SecondPersonWithM",
    },
    {
        "id": "MotherWithM",
        "name": "mother starts with m-sound",
        "function": phonology.StartsWithSound(
            ["MOTHER"], [["bilabial", "nasal"]], sound_label='[m]'),
        "note": "see also: FatherWithP",
    },
    {
        "id": "WindWithF",
        "name": "wind starts with f-sound",
        "function": phonology.StartsWithSound(
            ["WIND"],
            [["labio-dental", "fricative"], ["labio-dental", "affricate"]],
            sound_label='[f]'),
    },
    {
        "id": "HasPrenasalizedConsonants",
        "name": "inventory has pre-nasalized consonants",
        "function": phonology.HasSoundsWithFeature("consonants", [["pre-nasalized"]]),
    },
    {
        "id": "HasLabiodentalFricatives",
        "name": "inventory has labio-dental fricatives or affricates",
        "function": phonology.HasSoundsWithFeature(
            "consonants", [["labio-dental", "fricative"], ["labio-dental", "affricate"]]),
    },
    {
        "id": "FatherWithP",
        "name": "father starts with p-sound",
        "function": phonology.StartsWithSound(
            ["FATHER"], [["bilabial", "stop"], ["labio-dental", "fricative"]], sound_label='[p]'),
        "note": "see also: MotherWithM",
    },
    {
        "id": "SyllableOnset",
        "name": "complexity of the syllable onset",
        "function": phonology.SyllableOnset(),
        "note": "same as: APICS 118",
    },
    {
        "id": "SyllableOffset",
        "name": "complexity of the syllable offset",
        "function": phonology.SyllableOffset(),
        "note": "same as: APICS 118",
    }
])
