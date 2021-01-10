from pyclts import CLTS
from cldftk.inventories import InventoryData

lapsyd = CLTS().transcriptiondata_dict['lapsyd']

invs = InventoryData.from_metadata('data/jipa', td='jipa')

for language in invs:
    if language.inventory.unknownsounds:
        print('{0:20} | {1}'.format(
            language.name, len(language.inventory.unknownsounds)))
    #print(language.name, len(language.inventory.segmentals))
