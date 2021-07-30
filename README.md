# CL Toolkit

[![Build Status](https://github.com/cldf/cltoolkit/workflows/tests/badge.svg)](https://github.com/cldf/cltoolkit/actions?query=workflow%3Atests)
[![PyPI](https://img.shields.io/pypi/v/cltoolkit.svg)](https://pypi.org/project/cltoolkit)

Toolkit for processing Cross-Linguistic data.

## Data Structures in Wordlists

Lexical and phoneme inventory data is available in very different degrees of normalization. 
As a result, we have to represent the degree by which a collection of CLDF datasets forming a wordlist is comparable in a detailed class structure.

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
