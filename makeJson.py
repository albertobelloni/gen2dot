#!/usr/bin/python3

import argparse
import gzip, json
from particle import Particle

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
