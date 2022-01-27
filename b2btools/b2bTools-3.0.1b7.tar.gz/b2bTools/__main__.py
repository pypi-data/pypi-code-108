# Example:
# python -m b2bTools -dynamics -agmata -file ./b2bTools/test/input/example_toy.fasta

import sys, os
import json
from .wrapper_source.wrapper_utils import *

def print_help_section():
    print("Help section:")
    print("Show help section: --help or -h")
    print("An input file in FASTA format is required: -file /path/to/file.fasta")
    print("An output file path is required: -output /path/to/output_file.json")
    print("At least one predictor should be present:")
    print("AgMata: -agmata or -aggregation")
    print("Dynamine: -dynamine or -dynamics")
    print("Disomine: -disomine or -disorder")
    print("EFoldMine: -efoldmine or -early_folding_events")
    print("An identifier is required: -identifier name")
    print("Full documentation available on https://pypi.org/project/b2bTools/")
    exit(0)

if __name__ == '__main__':
    _command, *parameters = sys.argv
    print("Bio2Byte Tools - Command Line Interface")

    tools = []
    fileName = None
    outputFileName = None
    identifier = None

    for index, param in enumerate(parameters):
        if param == "--help" or param == "-h":
          print_help_section()
        if param == "-file":
          fileName = parameters[index + 1]
        if param == "-output":
          outputFileName = parameters[index + 1]
        if param == "-identifier":
          identifier = parameters[index + 1]
        if param == "-dynamics" or param == "-{0}".format(constants.TOOL_DYNAMINE):
            tools.append(constants.TOOL_DYNAMINE)
        if param == "-aggregation" or param == "-{0}".format(constants.TOOL_AGMATA):
            tools.append(constants.TOOL_AGMATA)
        if param == "-early_folding_events" or param == "-{0}".format(constants.TOOL_EFOLDMINE):
            tools.append(constants.TOOL_EFOLDMINE)
        if param == "-disorder" or param == "-{0}".format(constants.TOOL_DISOMINE):
            tools.append(constants.TOOL_DISOMINE)

    if len(tools) == 0:
        exit("At least one predictor should be present: -agmata, -dynamine, -disomine, -efoldmine")
    if not fileName:
        exit("An input file is required: -file /path/to/file")
    if not outputFileName:
        exit("An output file path is required: -output /path/to/output_file.json")
    if not identifier:
        exit("An identifier is required: -identifier name")

    output_filepath = os.path.realpath(outputFileName)

    print("Ready to execute predictions with these arguments:\n{0}\n{1}\n{2}\n{3}\n{4}".format(fileName, outputFileName, output_filepath, identifier, tools))

    single_seq = SingleSeq(fileName).predict(tools)
    print("All predictions have been executed. Next step: exporting the results")
    json = single_seq.get_all_predictions_json(identifier)

    print("All predictions have been exported. Next step: saving json inside output path: {0}".format(output_filepath))

    with open(output_filepath, 'w', encoding="utf-8") as json_output_file:
        json_output_file.write(json)

    exit(0)