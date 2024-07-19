# gen2dot
Convert GEN particle information to a Graphviz DOT file.

## Installation

Editable installation: clone the repository, then:
```
pip install --user -e . 
```
Installation directly from `git`:
```
pip install --user gen2dot@git+https://github.com/albertobelloni/gen2dot
```
The three scripts described below will be installed in `~/.local/bin/`.

## Package content

#### `gen2dot`

Accepts NanoAOD as input (and probably, at some point, some form of
user-defined text files)

#### `lhe2dot`

Accepts (possibly gzipped) LHE files

#### `g2d_makejson`

Produces a gzipped JSON file that maps particle PDG IDs to particle names.
It is probably _not_ needed; the package already contains a working JSON file,
and PDG IDs do not change often...

## Dependencies

#### `gen2dot`: argparse, pydot, ROOT, gzip, json

All dependencies are usually installed by default

#### `lhe2dot`: argparse, pylhe

Install `pylhe` with: `pip install [--user] pylhe`

Documentation: https://pypi.org/project/pylhe/

#### `g2d_makejsony`: argparse, gzip, json, particle

Install `particle` with: `pip install [--user] particle`

Documentation: https://pypi.org/project/particle/
