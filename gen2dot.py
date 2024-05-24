#!/usr/bin/python3

## @package gen2dot
#
# A script to create figures from CMS NanoAOD files.

#import matplotlib
import argparse
import pydot
import ROOT

def parsed_args():

    parser = argparse.ArgumentParser(
        description="""A script to create figures from CMS NanoAOD files.
                       The input files may be gzipped.
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

## processFile
#  @param input_filename Used to define the data extraction method
#  @param output_filename Used to define the output type; if missing, assume interactive view of events
#  @param max_events Defaults to 999 for interactive view
def processFile(input_filename, output_pattern, extension, max_events):

    # If there is no output_filename, we will show the graphs interactively
    # I cannot imagine anyone wanting to look at more than 1000 graphs...
    if not output_pattern:
        max_events = 999
    
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

    # This is a convolute way to check how many events are in the file
    # Let me leave it here for debugging purposes
    print (f"Processed {max(data, key=lambda event:event['event'])['event']}",
           f" events; it had better be equal to {max_events}")

    for i in range(max_events):

        # Filter data list of dictionaries to keep only the ones that
        # have the same event key (equal to i: the MC event number is
        # just a counter from 0 to N)
        event_data = list(filter(lambda x: x['event'] == i, data))

        # Let us now create the graph; note that the graph_from_dot_data
        # function returns a LIST of graphs; in our case, we know that
        # we are returning only one
        event_dot = processEvent(event_data)
        event_graph = pydot.graph_from_dot_data(event_dot)[0]
        
        # Now we have the graph in DOT language: if output_filename is empty,
        # we will show it interactively (push button to move to next file -
        # max_events reset to 999)
        if extension == 'png':
            event_graph.write_png(f"{output_pattern}{i}.png")
        if extension == 'pdf':
            event_graph.write_pdf(f"{output_pattern}{i}.pdf")
        if extension == 'svg':
            event_graph.write_svg(f"{output_pattern}{i}.svg")
        if extension == 'dot':
            event_graph.write_raw(f"{output_pattern}{i}.dot")

#def readFile_txt(input_filename):
#
#    with open(input_filename, 'r') as file:
#        for line in file:
#    return

def readFile_root(input_filename, max_events):

    infile = ROOT.TFile(input_filename,"read")
    # The line below assumes that the NanoAOD file contains a TTree
    # named "Events"
    tree = infile.Events

    entries = tree.GetEntriesFast()
    print ("Entries: ", entries)

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
            #print (n, " ", particle, " ",
            #       event.GenPart_pdgId[particle], " ",
            #       event.GenPart_genPartIdxMother[particle])
        n = n+1
        if n > max_events:
            return data

    return data
        
def processEvent(data):

    print(f"Event {data[0]['event']}")

    graph = pydot.Dot(f"Event {data[0]['event']}", graph_type="digraph")

    # create one node for each particle
    for particle in data:
        graph.add_node(pydot.Node(particle['particle'],
                                  shape="circle",
                                  label=particle['pdg']))

    # add edges between particles
    for particle in data:
        # Skip the particles without a valid mother index (i.e., >=0)
        if particle['mother'] == -1:
            continue
        graph.add_edge(pydot.Edge(particle['mother'], particle['particle']))

    return graph.to_string()

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
