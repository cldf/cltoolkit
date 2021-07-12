from cltoolkit import Wordlist

from clldutils.path import sys_path
from cltoolkit.util import lingpy_columns


def test_Wordlist(repos, ds_carvalhopurus, ds_wangbcd):
    # for lexibank load testing
    datasets = [ds_carvalhopurus, ds_wangbcd]

    with sys_path(repos / "carvalhopurus"):
        with sys_path(repos / "wangbcd"):
            wl2 = Wordlist.from_lexibank(["carvalhopurus", "wangbcd"])
            wl = Wordlist(datasets)

            assert wl2.height == wl.height

            apurina = wl.languages["carvalhopurus-Apurina"]

            assert wl.height == 305
            assert wl.width == 12
            assert wl.length == 2380
            assert len(wl.languages["wangbcd-Meixian"].forms) == 0
            assert len(wl.languages["carvalhopurus-Yine"].segmented_forms) == 195
            assert len(wl.languages["carvalhopurus-Yine"].sound_inventory) == 29
            assert len(wl.languages["carvalhopurus-Apurina"].segmented_forms) == 128
            assert len(wl.languages["carvalhopurus-Apurina"].bipa_forms) == 127
            assert len(wl.languages["carvalhopurus-Apurina"].concepts) == 105
            assert len(wl.languages["carvalhopurus-Apurina"].forms) == 128
    
            # lingpy wordlist has one concept more for all non-linked senses, not an
            # optimal behavior, but this is the expected behavior
            lp = wl.as_lingpy()
            assert lp.height-1 == wl.height and lp.width+1 == wl.width
    
    
            lp2 = wl.as_lingpy(
                language_filter=lambda x: len(x.concepts) > 100,
                form_filter=lambda x: x.segments)

            for concept, forms in wl.iter_forms_by_concepts():
                assert len(forms) == wl.width

            for concept, forms in wl.iter_forms_by_concepts(
                concepts=["BODY"],
                languages=[apurina.id],
            ):
                assert concept.name == forms[0][0].concept.id.lower()
                assert str(forms[0][0].segments) == "m a + n e"

            assert wl.coverage(aspect="segmented_forms")[apurina.id] == len(apurina.concepts)
    
    wl = Wordlist(datasets=[datasets[0]])
    wl.load_cognates()
    lpwl = wl.as_lingpy(columns=lingpy_columns(cognates="default"))
    assert "cognacy" in lpwl.columns


#
#
#wl = load_data()
#print("HEIGHT", wl.height)
#print("WIDTH ", wl.width)
#print("LENGTH", len(wl))
#print("")
#table = []
#coverage = wl.coverage()
#for language in wl.languages:
#    table += [(language.name, len(language.forms), len(language.concepts),
#        len(language.segmented_forms), 
#        len(language.bipa_forms),
#        len(language.inventory),
#        coverage[language.id]
#        )]
#print(tabulate(table,
#        headers = [
#            "language",
#            "forms",
#            "concepts",
#            "segmented forms",
#            "bipa forms",
#            "inventory",
#            "coverage"
#            ]
#        ))
