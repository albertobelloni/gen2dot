#!/usr/bin/python3

## @package lhe2dot
#
#  A script to create graphs representing MC decay chains from LHE files,
#  using the pylhe to produce DOT files. 

import pylhe
import argparse

##
#  @return argparse object with user input via command-line options
def parsed_args():

    parser = argparse.ArgumentParser(
        description="""A script to create graphs from LHE files
                       Several options for the output format are available.
                       """)
    parser.add_argument("-m","--max-events",
                        help="max number of events to process "\
                        "(default: %(default)s)",
                        metavar="N",type=int, default=2)
    parser.add_argument("-i","--in-file",
                        help="name of input file", required=True)
    parser.add_argument("-o","--out-pattern",
                        help="pattern of output file(s) "\
                        "(default: %(default)s)",
                        default="output_")
    parser.add_argument("-e", "--extension",
                        help="extension of output file(s) "\
                        "(default: %(default)s)",
                        choices=['png','pdf','svg','dot'],default="png")
    return parser.parse_args()

##
#  Everything happens in this function: the input filename is passed to
#  pylhe, DOT graphs are generated and saved according to the output_pattern;
#  the user-provided extension defines the format of the output files.
#
#  @param input_filename name of LHE input file
#  @param output_pattern string used to define the name of the output files
#  @param extension define type of output file (PDF, PNG, SVG, ...)
#  @param max_events max number of graphs to produce, if enough events are
#                    available in the input file
def processFile(input_filename, output_pattern, extension, max_events):

    events = pylhe.read_lhe_with_attributes(input_filename)
    entries = pylhe.read_num_events(input_filename)
    
    print(f"Number of events in file: {entries}")

    # event counter
    i = 0
    for event in events:

        print(f"Event {i}")
        event.graph.render(filename=f"{output_pattern}{i}",
                           format=f"{extension}",
                           cleanup=True)

        i += 1
        if  i>= max_events or i >= entries:
            break

    print ("Done with task")

## 
#
def main():

    args = parsed_args()

    input_filename = args.in_file
    output_pattern = args.out_pattern
    max_events     = args.max_events
    extension      = args.extension
    
    processFile(input_filename,
                output_pattern,
                extension,
                max_events)
    
if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        pass
