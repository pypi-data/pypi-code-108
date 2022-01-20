# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
# ! /usr/bin/env python
"""Script to detect YANG model changes between 2 repositories."""
import argparse
import csv
from pprint import pprint as pp
from yscoverage.dataset import dataset_for_directory


def main():
    """Using parser aruguments, create a dataset with xpath as key."""
    parser = argparse.ArgumentParser(
        description="""
    Produces a list of xpaths with optional items associated to the paths
    to the output file or to stdout.

    Example usage:
    =====================================================================
    Create dataset for ietf-interfaces module, using YANG files in path
    /yang/ietf-standard/:

    ./dataset.py -p /yang/ietf-standard/ -m ietf-interfaces

    =====================================================================
    Create dataset for ietf-interfaces module, using YANG files in path
    /yang/ietf-standard/, and including nodetype and datatype in the data:

    ./xpathdata.py -p /yang/ietf-standard/ -m ietf-interfaces -d nodetype \\
    datatype
    =====================================================================
    """,
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-p', '--path', type=str, required=True,
                        help="Directory path to YANG models.")

    parser.add_argument('-m', '--model', type=str, required=True,
                        help="YANG model to retrieve data from.")

    parser.add_argument('-d', '--dataset-columns', type=str, nargs='+',
                        default=[], help="""
    The xpath is the key to a row and the columns are data associated
    to the xpath.
    """)

    parser.add_argument('-o', '--output-file', type=str,
                        help="""
    Full path plus filename for output, otherwise, prints to stdout.
    """)

    args = parser.parse_args()

    dataset = dataset_for_directory(args.path, args.model,
                                    args.dataset_columns)

    if args.output_file:
        with open(args.output_file, 'w') as fd:
            writer = csv.writer(fd)
            writer.writerow(dataset['header'])
            for row in dataset['data']:
                writer.writerow(row)
        print('Results in {0}'.format(args.output_file))
    else:
        pp(dataset['header'])
        pp(dataset['data'])


if __name__ == '__main__':
    main()
