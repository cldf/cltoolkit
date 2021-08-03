# Example of working with `cltoolkit`

In this example we'll use `cltoolkit` to compute linguistic features from lexical data from the
[WOLD dataset](https://github.com/lexibank/wold) 
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5139859.svg)](https://doi.org/10.5281/zenodo.5139859).


## Loading CLDF Wordlists

`cltoolkit` provides an abstraction layer to access (collections of) `pycdlf.Wordlist`, thus we load data
as follows:
```python
>>> from cltoolkit import Wordlist
>>> from pycldf import Dataset
>>> wl = Wordlist([Dataset.from_metadata("https://raw.githubusercontent.com/lexibank/wold/v4.0/cldf/cldf-metadata.json")])
loading forms for wold: 100%|██████████| 64289/64289 [00:01<00:00, 33125.96it/s]
>>> print(wl)
<cltoolkit.wordlist.Wordlist object at 0x7fa8de7504f0>
```


## `cltoolkit.features.Feature`

A [cltoolkit.features.Feature](https://cltoolkit.readthedocs.io/en/latest/features.html#cltoolkit.features.collection.Feature) 
bundles basic metadata with a [Python callable](https://docs.python.org/3/library/functions.html#callable)
implementing the feature computation. In the simplest case this could be a `lambda` (i.e. an ad-hoc function)
as shown below:

```python
>>> from cltoolkit.features import Feature
>>> latitude = Feature(id="lat", name="Geographic Latitude", function=lambda l: l.latitude)
>>> for lang in wl.languages:
...     print('{}: {}'.format(lang.name, latitude(lang)))
...     break
...
Swahili: -6.5
```
A `Feature` is computed for a language by calling the `Feature` instance, passing a `cltoolkit.models.Language`
instance.

`cltoolkit` provides a couple of base classes for (sometimes parametrizable) derived feature implementations
(for [phonology](src/cltoolkit/features/phonology.py) and [lexicon](src/cltoolkit/features/lexicon.py)).
E.g. we can compute basic properties if a language's phoneme inventory:
```python
>>> from cltoolkit.features.phonology import InventoryQuery
>>> number_of_consonants = Feature(id='1', name="Number of consonants", function=InventoryQuery('consonants'))
```

Let's apply this feature:
```python
>>> for lang in wl.languages:
    ...     print('{}: {}'.format(lang.name, number_of_consonants(lang)))
...     break
...
Traceback (most recent call last):
File "<stdin>", line 2, in <module>
File "/home/robert_forkel/projects/cldf/cltoolkit/src/cltoolkit/features/collection.py", line 85, in __call__
return self.function(param)
File "/home/robert_forkel/projects/cldf/cltoolkit/src/cltoolkit/features/reqs.py", line 58, in wrapper_requires
raise MissingRequirement(' '.join(s[0] for s in status if not s[1]))
cltoolkit.features.reqs.MissingRequirement: inventory
```

Oops. Something went wrong. `cltoolkit.features.reqs.MissingRequirement` exceptions are used to signal
that a feature implementation can not be applied to a particular `Language` object, because required
properties are missing (see [reqs.py](src/cltoolkit/features/reqs.py)). Here, we have loaded a wordlist without 
passing a CLTS transcription system; thus `cltoolkit` could not compute CLTS-mapped phoneme inventories.

Let's fix this: We need to download the [CLTS data](https://github.com/cldf-clts/clts/releases/tag/v2.1.0), and 
pass the `bipa` transcription system from an appropriately initialized `pyclts.CLTS` object when creating the wordlist:
```python
>>> from pyclts import CLTS
>>> wl = Wordlist([Dataset.from_metadata("https://raw.githubusercontent.com/lexibank/wold/v4.0/cldf/cldf-metadata.json")], ts=CLTS('clts').bipa)
loading forms for wold: 100%|███████████| 64289/64289 [00:10<00:00, 6271.07it/s]
>>> for lang in wl.languages:
    ...     print('{}: {}'.format(lang.name, number_of_consonants(lang)))
...     break
...
Swahili: 31
```


## Persisting feature metadata

The main goal of `cltoolkit` is enabling rapid explorative analysis of lexical data. Thus, it is expected
that feature implementations may start out as simple functions (as shown above).
Once feature implementations evolve into something worth keeping (and sharing), the importance of the metadata 
layer provided by the `Feature` class becomes apparent.

Let's add our parametrized `InventoryQuery` to a `FeatureCollection` and dump the feature specification to
a JSON file:
```python
>>> from cltoolkit.features import FeatureCollection
>>> fc = FeatureCollection([number_of_consonants])
>>> fc.dump('features.json')
```

`features.json` looks as follows:
```python
[
    {
        "id": "1",
        "name": "Number of consonants",
        "function": {
            "class": "cltoolkit.features.phonology.InventoryQuery",
            "args": [
                "consonants"
            ]
        },
        "type": "int",
        "note": null,
        "categories": null,
        "requires": [
            "cltoolkit.features.reqs.inventory"
        ]
    }
]
```

If the feature implementation (here `cltoolkit.features.phonology.InventoryQuery`) is available
from a properly distributed and installable python package, we can share the JSON spec, and allow
others to recreate our features:

```python
>>> from cltoolkit.features import FeatureCollection
>>> fc = FeatureCollection.load('features.json')
>>> fc[0].function
<cltoolkit.features.phonology.InventoryQuery object at 0x7f42a4e07820>
>>> from pyclts import CLTS
>>> from cltoolkit import Wordlist
>>> from pycldf import Dataset
>>> wl = Wordlist([Dataset.from_metadata("https://raw.githubusercontent.com/lexibank/wold/v4.0/cldf/cldf-metadata.json")], ts=CLTS('/home/robert_forkel/projects/cldf-clts/clts-data').bipa)
loading forms for wold: 100%|███████████| 64289/64289 [00:09<00:00, 6655.21it/s]
>>> fc[0](wl.languages[0])
31
```


## Persisting feature data

The metadata bundled in the `Feature` objects does not only help with sharing feature implementations,
but also with sharing the computed feature values. Creating a CLDF StructureDataset with the computed
feature values can be done as follows:
```python
>>> from pycldf import StructureDataset
>>> cldf = StructureDataset.in_dir('.')
>>> cldf.add_component('ParameterTable')
>>> cldf.add_component('LanguageTable')
>>> langs = [dict(ID=l.id, Name=l.name) for l in wl.languages]
>>> params = [dict(ID=f.id, Name=f.name) for f in fc]
>>> values = [dict(ID='{}-{}'.format(l.id, f.id), Value=f(l), Language_ID=l.id, Parameter_ID=f.id) for f in fc for l in wl.languages]
>>> cldf.write(LanguageTable=langs, ParameterTable=params, ValueTable=values)
```

This will create valid data with metadata in `StructureDataset-metadata.json`:
```shell
$ cldf validate StructureDataset-metadata.json
$ head values.csv 
ID,Language_ID,Parameter_ID,Value,Code_ID,Comment,Source
wold-Swahili-1,wold-Swahili,1,31,,,
wold-Iraqw-1,wold-Iraqw,1,34,,,
wold-Gawwada-1,wold-Gawwada,1,26,,,
wold-Hausa-1,wold-Hausa,1,47,,,
wold-Kanuri-1,wold-Kanuri,1,21,,,
wold-TarifiytBerber-1,wold-TarifiytBerber,1,72,,,
wold-SeychellesCreole-1,wold-SeychellesCreole,1,21,,,
wold-Romanian-1,wold-Romanian,1,40,,,
wold-SeliceRomani-1,wold-SeliceRomani,1,44,,,
$ head parameters.csv 
ID,Name,Description
1,Number of consonants,
```
