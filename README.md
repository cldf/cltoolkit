# CL ToolKit

[![Build Status](https://github.com/cldf/cltoolkit/workflows/tests/badge.svg)](https://github.com/cldf/cltoolkit/actions?query=workflow%3Atests)
[![Documentation Status](https://readthedocs.org/projects/cltoolkit/badge/?version=latest)](https://cltoolkit.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/cltoolkit.svg)](https://pypi.org/project/cltoolkit)

A Python Library for the Processing of Cross-Linguistic Data.

By Johann-Mattis List and Robert Forkel.

## Overview

While [pycldf](https://github.com/cldf/pycldf) provides a basic Python API to access cross-linguistic data 
encoded in [CLDF](https://cldf.clld.org) datasets,
`cltoolkit` goes one step further, turning the data into full-fledged Python objects rather than
shallow proxies for rows in a CSV file. Of course, as with `pycldf`'s ORM package, there's a trade-off
involved, gaining convenient access and a more pythonic API at the expense of performance (in particular 
memory footprint but also data load time) and write-access. But most of today's CLDF datasets (or aggregations 
of these) will be processable with `cltoolkit` on reasonable hardware in minutes - rather than hours.

The main idea behind `cltoolkit` is making (aggregated) CLDF data easily amenable for computation
of *linguistic features* in a general sense (e.g. typological features, etc.). This is done by
- providing the data for processing code [as Python objects](https://cltoolkit.readthedocs.io/en/latest/models.html),
- providing [a framework](https://cltoolkit.readthedocs.io/en/latest/features.html) that makes feature computation 
  as simple as writing a Python function acting on a `cltoolkit.models.Language` object.

In general, aggregated CLDF Wordlists provide limited (automated) comparability across datasets (e.g. one could
compare the number of words per language in each dataset). A lot more can be done when datasets use CLDF reference
properties to link to reference catalogs, i.e.
- [link language varieties](https://cldf.clld.org/v1.0/terms.rdf#glottocode) to [Glottolog](https://glottolog.org) languoids,
- [link senses](https://cldf.clld.org/v1.0/terms.rdf#concepticonReference) to [Concepticon concept sets](https://concepticon.clld.org/parameters),
- [link sound segments](https://cldf.clld.org/v1.0/terms.rdf#cltsReference) to [CLTS sounds](https://clts.clld.org/parameters).

`cltoolkit` objects exploit this extended comparability by distinguishing "senses" and "concepts" and "graphemes"
and "sounds" and providing convenient access to comparable subsets of objects in an aggregation 
(see [models.py](src/cltoolkit/models.py)).

See [example.md](example.md) for a walk-through of the typical workflow with `cltoolkit`.
