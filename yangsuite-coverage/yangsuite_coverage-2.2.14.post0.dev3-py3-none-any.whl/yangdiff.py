# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
# ! /usr/bin/env python
"""Script to detect YANG model changes between 2 repositories."""
import argparse
import csv
from collections import OrderedDict
from pprint import pprint as pp
from yscoverage.dataset import (
    dataset_for_yangset, dataset_for_directory, YSYangDatasetException
)

from yangsuite.logs import get_logger

log = get_logger(__name__)


def getdiff(from_dataset, to_dataset):
    """Return differences of 2 model datasets.

    Args:
      from_dataset (dict): dataset with older version.
        The last addon in the dataset **must** be 'nodetype'
      to_dataset (dict): dataset with newer version
        The last addon in the dataset **must** be 'nodetype'
    Raises:
      yscoverage.dataset.YSYangDatasetException
    Returns:
      dict: with keys 'header' (list of header titles) and 'data' (list of
        data entries, each of the form ``[operation, xpath, *addons]``.
        For example::

          {
            'header': ['?', 'xpath', 'datatype', 'nodetype', ...],
            'data': [
              ['+', '/foo/bar', ...],      # added in newer version
              ['-', '/x/y', ...],          # deleted from newer version
              ['<', '/bat', 'int32', ...], # changed, this is the old version
              ['>', '/bat', 'int64', ...], # changed, this is the new version
            ]
          }
    """
    def is_data_node(entry):
        return entry[-1] not in [
            'case',
            'choice',
            'grouping',
            'identity',
            'typedef',
            'input',
            'output',
        ]

    if from_dataset['header'] != to_dataset['header']:
        raise YSYangDatasetException("Datasets contain mismatched addons")
    header = from_dataset['header']
    if header[-1] != "nodetype":
        raise YSYangDatasetException('Dataset MUST have "nodetype" as its '
                                     'final column')
    from_data = filter(is_data_node, from_dataset['data'])
    to_data = filter(is_data_node, to_dataset['data'])

    # Drop the trailing 'nodetype' from each entry - if user wants it, they
    # need to have requested it themselves as part of 'addons'.
    header = header[:-1]
    from_data = [entry[:-1] for entry in from_data]
    to_data = [entry[:-1] for entry in to_data]

    # https://wiki.python.org/moin/TimeComplexity
    #
    # We have several requirements for this algorithm:
    # 1) Need to preserve order of entries for consistent output, so we
    #    need something with list-like semantics (a set alone won't suffice)
    # 2) To detect insertions and deletions (the majority of diffs) we need
    #    quick membership checks (entry in data)
    # 3) More generally, to detect *changes* we need quick lookup by XPath too.
    #
    # We end up using an OrderedDict keyed by XPath, allowing us to meet all
    # of the above requirements with a single data structure.

    from_data = OrderedDict([[entry[0], entry] for entry in from_data])
    to_data = OrderedDict([[entry[0], entry] for entry in to_data])

    result = {
        'header': ['?'] + header,
        'data': [],
    }

    delta = []

    log.info("Beginning diffset calculation")

    while from_data or to_data:
        from_path, from_entry = (from_data.popitem(False) if from_data
                                 else (None, None))
        to_path, to_entry = (to_data.popitem(False) if to_data
                             else (None, None))

        if from_entry == to_entry:
            # Unchanged - carry on
            continue
        elif not from_entry:
            # Only to_data remains
            delta.append(['+'] + to_entry)
            continue
        elif not to_entry:
            # Only from_data remains
            delta.append(['-'] + from_entry)
            continue
        elif from_path == to_path:
            # Same xpath, but some other part doesn't match. A change!
            delta.append(['<'] + from_entry)
            delta.append(['>'] + to_entry)
            continue

        # If we make it here, then we have two distinct entries with different
        # xpath values. We need to figure out what to do with both of them.

        # The first question - does either (or both) xpath exist elsewhere in
        # the dataset?
        secondary_from_entry = from_data.get(to_path, None)
        secondary_to_entry = to_data.get(from_path, None)

        if not secondary_to_entry:
            # A genuine deletion for from_entry
            delta.append(['-'] + from_entry)
        else:
            # A reordering of existing elements
            if from_entry != secondary_to_entry:
                delta.append(['<'] + from_entry)
                delta.append(['>'] + secondary_to_entry)
            del to_data[secondary_to_entry[0]]

        if not secondary_from_entry:
            # A genuine addition of to_entry
            delta.append(['+'] + to_entry)
        else:
            # A reordering of existing elements
            if secondary_from_entry != to_entry:
                delta.append(['<'] + secondary_from_entry)
                delta.append(['>'] + to_entry)
            del from_data[secondary_from_entry[0]]

    log.info("Diffset calculation completed")

    result['data'] = delta
    return result


def main():
    """Diff model between 2 YANG Sets."""
    parser = argparse.ArgumentParser(
        description="""
    Differences between a YANG model in one YANG Set compared to the same
    YANG Model in another YANG Set.  If you are comparing updated models,
    the base set would be the YANG set with the older model.

    Writes list of xpaths with optional items associated to the paths
    to the output file or to stdout.

    Example usage:
    =====================================================================
    Compares xpaths of Cisco-IOS-XE-native from YANG set csr57-nomibs to
    miott-csr-no-mib:

    yangdiff -u admin -m Cisco-IOS-XE-native --from-set csr57-nomibs \\
        --to-set miott-csr-no-mib
    =====================================================================
    Compares xpaths with nodetype, datatype, and module from YANG set
    csr57-nomibs to miott-csr-no-mib and outputs it to dataset.txt:

    yangdiff -u admin -m Cisco-IOS-XE-native --from-set csr57-nomibs \\
        --to-set miott-csr-no-mib -d nodetype datatype module -o dataset.txt
    =====================================================================
    Compares xpaths with nodetype, datatype, and module from YANG set
    csr57-nomibs to YANG files in /yang directory and outputs to dataset.txt:

    yangdiff -u admin -m Cisco-IOS-XE-native --from-set csr57-nomibs \\
        --to-directory /yang -d nodetype datatype module -o dataset.txt
    =====================================================================
    """,
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-m', '--model', type=str, required=True,
                        help="YANG model to compare between versions.")

    parser.add_argument('-u', '--user', type=str,
                        help="YANG Suite user owning YANG sets. "
                        "Only required if using --from-set / --to-set")

    from_group = parser.add_mutually_exclusive_group(required=True)

    from_group.add_argument('--from-set', type=str, metavar="SETNAME",
                            help="YANG set to compare from "
                            "(typically, older version).")
    from_group.add_argument('--from-directory', type=str, metavar="PATH",
                            help="YANG file directory to compare from "
                            "(typically, older version).")

    to_group = parser.add_mutually_exclusive_group(required=True)

    to_group.add_argument('--to-set', type=str, metavar="SETNAME",
                          help="YANG set to compare to "
                          "(typically, newer version).")
    to_group.add_argument('--to-directory', type=str, metavar="PATH",
                          help="YANG file directory to compare to "
                          "(typically, newer version).")

    parser.add_argument('-d', '--dataset-columns', type=str, nargs='+',
                        default=[], metavar="COLUMN",
                        help="Additional data to compare and report on")

    parser.add_argument('-o', '--output-file', type=str,
                        help="Full path plus filename for output; "
                        "otherwise, prints to stdout.")

    args = parser.parse_args()

    addons = args.dataset_columns + ['nodetype']

    if args.from_directory:
        from_dataset = dataset_for_directory(args.from_directory,
                                             args.model,
                                             addons)
    else:
        from_dataset = dataset_for_yangset(args.user, args.from_set,
                                           args.model,
                                           addons)

    if args.to_directory:
        to_dataset = dataset_for_directory(args.to_directory,
                                           args.model,
                                           addons)
    else:
        to_dataset = dataset_for_yangset(args.user, args.to_set,
                                         args.model,
                                         addons)

    dscmp = getdiff(from_dataset, to_dataset)

    if args.output_file:
        with open(args.output_file, 'w') as fd:
            writer = csv.writer(fd)
            writer.writerow(dscmp['header'])
            for row in dscmp['data']:
                writer.writerow(row)
        print('Results in {0}'.format(args.output_file))
    else:
        pp(dscmp['header'])
        pp(dscmp['data'])


if __name__ == '__main__':
    main()
