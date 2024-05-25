#!/usr/bin/python3

## @package makeJson
#
#  The gen2dot script produces decay-chain graphs reading PDG codes from the
#  input files. The makeJson script provides the mapping between PDG codes
#  and particle names, using the particle.Particle package. The mapping is
#  saved in a gzipped JSON file. A copy of the generated JSON file is included
#  in the repository, to spare users from the need to install the necessary
#  dependency (particle.Particle); it is expected that the JSON file seldom
#  needs to be updated.
#  A special case that requires an update: the particle.Particle package
#  assigns three strings to each particle: name, pdg_name, and latex_name.
#  One may want to modify the main function below to choose a different
#  string. Let it be noted that latex_name requires one to use dot2tex in
#  gen2dot to generate a TEX file, to be processed with pdflatex.

import argparse
import gzip, json
from particle import Particle

##
#  @return argparse object with user input via command-line options
def parsed_args():

    parser = argparse.ArgumentParser(
        description="""Create JSON file for gen2dot script.
                       Use particle.Particle python package.
                       """)
    parser.add_argument("-o","--out-file",
                        help="name of JSON file; use only for debugging! "\
                        "(default: %(default)s)",
                        default="pdgnames.json.gz")
    return parser.parse_args()

##
#  The workhorse: the dictionary generation and JSON file creation take place
#  here. This is also where the user may want which type of string that
#  identifies particles is written to the dictionary.
#
#  @param args command line options
def main(args):

    dictionary = {}
    for part in Particle.all():
        # Note: particle objects, in the particle module, have three
        # different names: name, pdg_name, latex_name
        # The latex_name is appealing, but it requires one to use
        # dot2tex (python module) to produce a tex file, followed by pdflatex
        dictionary[part.pdgid] = part.name
        
    with gzip.open(args.out_file, "wt", encoding="ascii") as output_json:
        json.dump(dictionary, output_json)

if __name__ == '__main__':

    try:
        main(parsed_args())
    except KeyboardInterrupt:
        pass
