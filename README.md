# CL Toolkit

[![Build Status](https://github.com/cldf/cltoolkit/workflows/tests/badge.svg)](https://github.com/cldf/cltoolkit/actions?query=workflow%3Atests)
[![PyPI](https://img.shields.io/pypi/v/cltoolkit.svg)](https://pypi.org/project/cltoolkit)

Toolkit for processing Cross-Linguistic data.


## Overview

While `pycldf` provides a basic Python API to access cross-linguistic data encoded in CLDF datassts,
`cltoolkit` goes one step further, turning the data into full-fledged Python objects rather than
shallow proxies for rows in a CSV file. Of course, as with `pycldf`'s ORM package, there's a trade-off
involved, gaining convenient access and a more pythonic API at the expense of performance (in particular 
memory footprint but also data load time) and write-access. But most of today's CLDF datasets (or aggregations 
of these) will be processable with `cltoolkit` on reasonable hardware in minutes - rather than hours.

The main idea behind `cltoolkit` is making (aggregated) CLDF data easily amenable for computation
of *linguistic features* in a general sense (e.g. typological features, etc.). This is done by
- providing the data for processing code as Python objects,
- providing [a framework](src/cltoolkit/__init__.py) that makes feature computation as simple as writing a Python 
  function acting on a `cltoolkit.models.Language` object.

In general, aggregated CLDF Wordlists provide limited (automated) comparability across datasets (e.g. one could
compare the number of words per language in each dataset). A lot more can be done when datasets use CLDF reference
properties to link to reference catalogs, i.e.
- link language varieties to Glottolog languoids,
- link senses to Concepticon concepts,
- link sound segments to CLTS B(road) IPA.

`cltoolkit` objects exploit this extended comparability by distinguishing "senses" and "concepts" and "segments"
and "bipa_segments" and providing convenient access to comparable subsets of objects in an aggregation 
(see [models.py](src/cltoolkit/models.py)).

See [example.md](example.md) for a walk-through of the typical workflow with `cltoolkit`.


## Data Structures in Wordlists

Lexical and phoneme inventory data is available in very different degrees of normalization. 
As a result, we have to represent the degree by which a collection of CLDF datasets forming a wordlist 
is comparable in a detailed class structure.

This results in the following models, which we distinguish:



name | attributes | description
--- | --- | --- 
`Sense` | `forms`, `segmented_forms`, `bipa_forms` | A sense description (concept in source) which does not need to be linked to the Concepticon.
`SenseInLanguage` | `forms`, `segmented_forms`, `bipa_formes` | A sense description in an individual `Language` object, the `forms` will only be the forms of this very language. 
`Concept` | `forms`, `segmented_formes`, `bipa_forms` | A sense that has a valid link to a Concepticon concept set. |
`ConceptInLanguage` | `forms`, `segmented_forms`, `bipa_forms` | A sense with a valid link to a Concepticon concept set in an individual language.

`Form` | `concept`, `conceptset`, `segments`, `bipa_segments`, `sounds` | an object that 
Language | `forms`, `segmented_forms`, `bipa_forms`, `concepts`, `conceptsets` | A

This results currently in the following `Wordlist` attributes:

attribute | description 
--- | ---
languages | a dict-list of language objects
conceptsets | a dict-list of conceptsets, defined as 
