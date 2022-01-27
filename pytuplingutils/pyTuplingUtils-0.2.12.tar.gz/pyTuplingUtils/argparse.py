#!/usr/bin/env python3
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Wed Jan 26, 2022 at 03:08 PM -0500

import sys
from argparse import Action, ArgumentParser


###########################
# Argument parser actions #
###########################

class DataRangeAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            setattr(namespace, self.dest, [])
            return

        if len(values) % 2 != 0:
            print('Odd number of min, max pairs!')
            sys.exit(255)

        values = [float(v) for v in values]
        min_max_pairs = self.divide_list_in_chunk(values)
        setattr(namespace, self.dest, min_max_pairs)

    @staticmethod
    def divide_list_in_chunk(lst, chunk_size=2):
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


class DataPairAction(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            setattr(namespace, self.dest, [])

        try:
            val_min, val_max = [float(i) for i in values]
            setattr(namespace, self.dest, [val_min, val_max])
        except ValueError:
            print('Invalid value for pair: {}'.format(values))


##############################
# Bare-bone argument parsers #
##############################

def single_ntuple_parser_no_output(descr, parser=None):
    parser = ArgumentParser(description=descr) if parser is None else parser

    parser.add_argument('-n', '--ref',
                        required=True,
                        help='''
path to reference ntuple.''')

    parser.add_argument('-t', '--ref-tree',
                        required=True,
                        help='''
tree name for the reference ntuple.''')

    parser.add_argument('--bins',
                        type=int,
                        default=25,
                        help='''
specify binning.''')

    return parser


def double_ntuple_parser_no_output(descr, parser=None):
    parser = single_ntuple_parser_no_output(descr) if parser is None else parser

    parser.add_argument('-N', '--comp',
                        required=True,
                        help='''
path to comparison ntuple.''')

    parser.add_argument('-T', '--comp-tree',
                        required=True,
                        help='''
tree name for the comparison ntuple.''')

    return parser


def single_branch_parser_no_output(descr, parser=None):
    parser = ArgumentParser(description=descr) if parser is None else parser

    parser.add_argument('-n', '--ref',
                        required=True,
                        action='append',
                        help='''
paths to reference ntuple-tree combos.''')

    parser.add_argument('-b', '--ref-branch',
                        required=True,
                        action='append',
                        nargs='+',
                        help='''
branch names in reference trees.''')

    parser.add_argument('--bins',
                        type=int,
                        default=25,
                        help='''
specify binning.''')

    return parser


def diff_branch_parser_no_output(descr, parser=None):
    parser = single_branch_parser_no_output(descr) if parser is None else parser

    parser.add_argument('-N', '--comp',
                        required=True,
                        action='append',
                        help='''
paths to comparison ntuple-tree combos.''')

    parser.add_argument('-B', '--comp-branch',
                        required=True,
                        action='append',
                        nargs='+',
                        help='''
branch names in comparison trees.''')

    return parser


###########
# Helpers #
###########

def split_ntp_tree(ntp_tree):
    ntp, tree = ntp_tree.split('.root/')
    ntp += '.root'
    return ntp, tree
