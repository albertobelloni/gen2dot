# gen2dot
Convert GEN particle information to a Graphviz DOT file.

## Package content

#### `gen2dot.py`

Accepts NanoAOD as input (and probably, at some point, some form of
user-defined text files)

#### `lhe2dot.py`

Accepts (possibly gzipped) LHE files

#### `makeJson.py`

Produces a gzipped JSON file that maps particle PDG IDs to particle names.
It is probably _not_ needed; the package already contains a working JSON file,
and PDG IDs do not change often...

## Dependencies

#### `gen2dot.py`: argparse, pydot, ROOT, gzip, json

All dependencies are usually installed by default

#### `lhe2dot.py`: argparse, pylhe

Install `pylhe` with: `pip install [--user] pylhe`

Documentation: https://pypi.org/project/pylhe/

#### `makeJson.py`: argparse, gzip, json, particle

Install `particle` with: `pip install [--user] particle`

Documentation: https://pypi.org/project/particle/
