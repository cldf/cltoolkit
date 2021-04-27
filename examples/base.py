from cltoolkit import Wordlist
from pycldf import Dataset

ds = Dataset.from_metadata('/home/mattis/data/datasets/cldf/lexibank-data/allenbai/cldf/cldf-metadata.json')

wl = Wordlist.from_datasets([ds])
wl.load()
