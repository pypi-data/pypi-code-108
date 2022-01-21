import pathlib
import json
import csv
import math
import re

import logging
logger = logging.getLogger(__name__)

from . import blockseparator

def run(input_,
        outputdir,
        cascadedir_form='casc{Cascade:05d}-gr{Group:05d}-num{Number:05d}',
        config_dump_text_blocks=True,
        config_cascade_table_output='BOTH',
        config_ignore_block_parse_error=False,
        config_block_file_form='00.{blockname:s}.txt',
        config_debug_parser=False):
    '''Dumper operates,
        1. read input file and split into blocks using blockseparator.BlockSeparator
        2. blocks are parsed in detail and dumped as .json or .csv files
            optionally, blocks are dumped as-is text file for debugging

    input_ is file stream to parse
    outputdir is string or pathlib.Path object to save output data.
      If outputdir does not exist, try to create it.
    cascadedir_form is formattable string to save data for each cascade
    config_dump_text_blocks: if True, 'as-is' text block is saved, otherwise skipped if it is not needed.
    config_cascade_table_output: chooses whether large output data generated at each cascade
        is written in one file ('BUNDLE'), in each cascade dir('SEPARATE'),  or both('BOTH')
    config_ignore_block_parse_error: if True, continue even an error occurs during parsing each block.
    config_block_file_form is fileformat to output parsed block text'''

    context = blockseparator.Context(
            outputdir,
            cascadedir_form,
            config_dump_text_blocks,
            config_cascade_table_output,
            config_ignore_block_parse_error,
            config_block_file_form,
            config_debug_parser=False)

    for _ in blockseparator.BlockSeparator(input_, context):
        pass

    context.close_bundled_files_explicitly()
    


if __name__ == '__main__':
    import sys
    import argparse

    from .. import smart_argparse

    argparser = argparse.ArgumentParser(formatter_class=smart_argparse.SmartHelpFormatter)
    argparser.add_argument('input', type=argparse.FileType('rt'), help="Input file. '-' for stdin")
    argparser.add_argument(
        'output', type=str, default=None, nargs='?',
        help='output data directory to output parsed data. '
        'If ommitted, INPUT.post is set for INPUT.lst data file. '
        'If input is stdin, this option should be given.')
    argparser.add_argument(
        '--cascade-directory-format', type=str,
        default='casc{Cascade:05d}-gr{Group:05d}-num{Number:05d}',
        help='directory form to store data for each cascade, which is created under '
        'OUTPUT directory (default: %(default)s)')
    argparser.add_argument(
        '--skip-verbose-textblock-output', action='store_true', default=False,
        help='skip output of verbose text block')
    argparser.add_argument(
            '-l', '--logging', dest='loglevel',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            help='choose logging level (default : %(default)s)',
            default='INFO')
    argparser.add_argument(
            '--cascade-table-output', choices=['BUNDLE', 'SEPARATE', 'BOTH'],
            default='BUNDLE',
            help='R|Select output form for large cascade data tables (ex. description_of_cascade{_all}.csv) '
            '(default: %(default)s)\n'
            '  SEPARATE: output as <root>/<each cascade>/xxx.csv\n'
            '  BUNDLE: output as <root>/xxx_all.csv\n'
            '  BOTH: SEPARATE and BUNDLE')
    argparser.add_argument(
            '--abort-on-block-parse-error',
            help='abort when an error occurs during parsing each block',
            action='store_true',
            default=False)

    args = argparser.parse_args()

    # set logging & debug level
    logging.basicConfig(level=logging.getLevelName(args.loglevel))

    # test output directory
    if args.output is None:
        if args.input.name == '<stdin>':
            print('Error: input is stdin, but no output name is provided.')
            sys.exit(1)
        else:
            # generate output name
            args.output = re.sub('\.lst$', '.post', args.input.name)
    if args.output == args.input.name:
        print('Error: same input ({}) and output ({}) name'.format(args.input.name,
                                                                   args.output))
        sys.exit(2)

    try:
        run(args.input,
            args.output,
            cascadedir_form=args.cascade_directory_format,
            config_dump_text_blocks=not args.skip_verbose_textblock_output,
            config_cascade_table_output=args.cascade_table_output,
            config_ignore_block_parse_error=args.ignore_block_parse_error)
    except Exception as e:
        logging.critical(str(e), stack_info=True)
