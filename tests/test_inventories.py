import pytest
from pyclts import CLTS
#from cltoolkit.inventories import (
#        normalize, from_metadata, from_dataset, retrieve_data, InventoryData)




#def test_normalize():
#    assert normalize('aa') == 'aa'
#    assert normalize('a\u2019') == 'a\u02bc'
#
#
#
#def test_from_metadata():
#    clts = CLTS(
#        Path(__file__).parent.joinpath(
#            'repos', 'clts'))
#    
#    languages, bib = from_metadata(
#            'jipa',
#            Path(__file__).parent.joinpath(
#                'repos', 'jipa', 'cldf'),
#            clts.transcriptiondata_dict['jipa'],
#            clts.bipa
#            )
#
#def test_from_dataset():
#    pass
#
#
#def test_retrieve_data():
#    pass
#
#
#def test_InventoryData():
#    clts = CLTS(
#        Path(__file__).parent.joinpath(
#            'repos', 'clts'))
#
#    invs = InventoryData.from_metadata(
#            'jipa',
#            Path(__file__).parent.joinpath(
#                'repos', 'jipa', 'cldf'),
#            clts.transcriptiondata_dict['jipa'],
#            clts.bipa)
#    
#    for language in invs:
#        if language.name != 'Amharic':
#            assert len(language.inventory.vowels) > 0
#        else:
#            assert len(language.inventory.vowels) == 0



