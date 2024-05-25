#!/usr/bin/python3

## @package gen2dot
#
#  A script to create graphs representing MC decay chains from various inputs,
#  among which text files and CMS NanoAOD files.
#  The pylhe module offers a very nice way to produce graphs from LHE files;
#  I shall leave in this macro the possibility of reading a plain text file,
#  the user shall ensure that they define appropriately its format.

import argparse
import pydot
import ROOT
import gzip, json

## @var particle_dict
#  pdgID-name dictionary; this file is produced by the makeJson script,
#  it is reasonable to expect that it does not need to be updated often...
particle_dict = {}

##
#  @return argparse object with user input via command-line options
def parsed_args():

    parser = argparse.ArgumentParser(
        description="""A script to create graphs from CMS NanoAOD files
                       or text files.
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
#  This is the workhorse function: decides what type of input is provided,
#  correspondingly selecting the correct read function, loops on the events
#  found in the input file, transformed into a list of dictionaries (each
#  dictionary correspond to a truth particle), sends individual events to
#  the processEvent function, prints the returned DOT graph into a file,
#  of the type defined by the user via a command-line option.
#
#  @param input_filename name of input file; its extension is used to define
#                        the data extraction method
#  @param output_pattern string used to define the name of the output files
#  @param extension define type of output file (PDF, PNG, SVG, ...)
#  @param max_events max number of graphs to produce, if enough events are
#                    available in the input file
def processFile(input_filename, output_pattern, extension, max_events):

    global particle_dict

    # Let us read the JSON file: I assume its name is fixed!
    with gzip.open('pdgnames.json.gz','rt', encoding='ascii') as json_file:
        particle_dict = json.load(json_file)

    # Depending on the extension of the input filename, we decide
    # how it should be read: NanoAOD? ROOT ntuple? CSV or TXT file?
    input_extension = input_filename.split('.')[-1]
    
    # Replace with "match-case" construct with python > 3.10
    if input_extension == "txt":
        readFile = readFile_txt # note: not yet written...
    elif input_extension == "root":
        readFile = readFile_root
    else:
        print("Uhm, undefined input file, giving up")
        return

    data = readFile(input_filename, max_events)

    # This is a convoluted way to check how many events are in the file
    # Let me leave it here for debugging purposes
    processed_events = max(data, key=lambda event:event['event'])['event'] + 1
    print (f"Processed {processed_events}",
           f"events; it had better be equal or smaller than {max_events}")

    for i in range(processed_events):

        # Filter data list of dictionaries to keep only the ones that
        # have the same event key (equal to i: the MC event number is
        # just a counter from 0 to N)
        event_data = list(filter(lambda x: x['event'] == i, data))

        # Let us now create the graph; note that the graph_from_dot_data
        # function returns a LIST of graphs; in our case, we know that
        # we are returning only one
        event_dot = processEvent(event_data)
        (event_graph,) = pydot.graph_from_dot_data(event_dot)
        
        # Now we have the graph in DOT language: save it in the selected format
        if extension == 'png':
            event_graph.write_png(f"{output_pattern}{i}.png")
        if extension == 'pdf':
            event_graph.write_pdf(f"{output_pattern}{i}.pdf")
        if extension == 'svg':
            event_graph.write_svg(f"{output_pattern}{i}.svg")
        if extension == 'dot':
            event_graph.write_raw(f"{output_pattern}{i}.dot")

    print ("Done with task")

##
#  @param input_filename text file containing events
#  @param max_events max number of graphs to produce, if enough events
#                    are available in the input file
#  @return list of all particles read in multiple events in the input file
def readFile_txt(input_filename, max_events):

    return [{"event":0, "particle":0, "pdg":22, "mother":-1,"status":3}]
#    with open(input_filename, 'r') as file:
#        for line in file:
#    return

##
#  The current implementation works with NanoAODv21. This is the function
#  where one defines the names of the columns in the ROOT tree corresponding
#  to truth MC information.
#
#  @param input_filename ROOT file containing events
#  @param max_events max number of graphs to produce, if enough events
#                    are available in the input file
#  @return list of all particles read in multiple events in the input file
def readFile_root(input_filename, max_events):

    infile = ROOT.TFile(input_filename,"read")
    # The line below assumes that the NanoAOD file contains a TTree
    # named "Events"
    tree = infile.Events

    entries = tree.GetEntriesFast()
    print ("Available entries in root tree: ", entries)

    n = 0
    data = []
    for event in tree:
        for particle in range(event.nGenPart):
            # Let me note that the NanoAOD file I used contained only a
            # handful of GenPart variables, which are the ones I am saving
            # here: GenPart_pdgId, GenPart_genPartIdxMother, GenPart_statusFlag
            # This is where things can go awry if the entries in the NanoAOD
            # have different names

            # n and particle are integers that happen to match (I hope) the
            # values in the "Row" and "Instance" columns when one scans the tree
            data.append({"event":n,
                         "particle":particle,
                         "pdg":event.GenPart_pdgId[particle],
                         "mother":event.GenPart_genPartIdxMother[particle],
                         "status":event.GenPart_statusFlags[particle]
                         })
        # Exit the loop if either processed max_events, or no more entries
        # are available in the tree
        n = n+1
        if n >= max_events or n >= entries:
            return data

    return data
        
## 
#  This function receives a list of particles found in a single event,
#  and produces a DOT graph object. This is where one may want to play
#  with the format of the graph (e.g., style and color of nodes and edges),
#  or the physics of what is being drawn (what to do with particles that
#  do not have a parent?)
#
#  @param data list of particles (in dictionary format) found in one event
#  @return graph corresponding to event decay chain, in DOT-string format
def processEvent(data):

    global particle_dict

    print(f"Event {data[0]['event']}")

    graph = pydot.Dot(f"Event {data[0]['event']}", graph_type="digraph")

    # create one node for each particle
    for particle in data:
        graph.add_node(pydot.Node(particle['particle'],
                                  shape="circle",
                                  label=particle_dict[str(particle['pdg'])]))

    # add edges between particles
    for particle in data:
        # Skip the particles without a valid mother index (i.e., >=0)
        if particle['mother'] == -1:
            continue
        graph.add_edge(pydot.Edge(particle['mother'], particle['particle']))

    return graph.to_string()

## 
#  @param args command line options
def main(args):

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
        main(parsed_args())
    except KeyboardInterrupt:
        pass
