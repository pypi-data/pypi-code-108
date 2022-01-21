#!/usr/bin/env python

import sys
import re
import argparse
import traceback

import logging

import marlowe_ui.smart_argparse as smart_argparse
import marlowe_ui.postprocess.dumper as old_dumper
import marlowe_ui.postprocess_lark.dumper as dumper

def main():
    argparser = argparse.ArgumentParser(formatter_class=smart_argparse.SmartHelpFormatter)
    argparser.add_argument('input', type=argparse.FileType('rt'), help="Input file. '-' for stdin")
    argparser.add_argument(
            'output', type=str, default=None, nargs='?',
            help='output data directory to output parsed data. '
            'If ommitted, INPUT.post is set INPUT.lst for data file. '
            'If input is stdin, this option should be given.')
    argparser.add_argument(
            '--cascade-directory-format', type=str,
            default='casc{Cascade:05d}-gr{Group:05d}-num{Number:05d}',
            help='directory form to store data for each cascade, which is created under '
            'OUTPUT directory (default: %(default)s)')
    argparser.add_argument(
            '-l', '--logging', dest='loglevel',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            help='choose logging level (default : %(default)s)',
            default='INFO')

    argparser.add_argument(
            '--old-inline-parser', action='store_true', default=False,
            help='use old inline parser')

    # the following options are valid only for new-inline-parser
    argparser.add_argument(
            '--skip-verbose-textblock-output', action='store_true', default=False,
            help='skip output of verbose text block (ignored if --old-inline-parser is set)')
    argparser.add_argument(
            '--cascade-table-output', choices=['BUNDLE', 'SEPARATE', 'BOTH'],
            default='BUNDLE',
            help='R|Select output form for large cascade data tables (ex. description_of_cascade{_all}.csv) '
            '(default: %(default)s)\n'
            '(ignored if --old-inline-parser is set)\n'
            '  BUNDLE: output as <root>/xxx_all.csv\n'
            '  SEPARATE: output as <root>/CASCADE_DIRECTORY_FORMAT/xxx.csv\n'
            '  BOTH: BUNDLE and SEPARATE')
    argparser.add_argument(
            '--ignore-block-parse-error',
            help='ignore errors during parsing each text block',
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
        if args.old_inline_parser:
            p = old_dumper.Parser(
                    outputdir=args.output, cascade_dir_form=args.cascade_directory_format)

            p.parse(args.input)
        else:
            dumper.run(args.input,
                args.output,
                cascadedir_form=args.cascade_directory_format,
                config_dump_text_blocks=not args.skip_verbose_textblock_output,
                config_cascade_table_output=args.cascade_table_output,
                config_ignore_block_parse_error=args.ignore_block_parse_error)

    except Exception as e:
        logging.critical(str(e), exc_info=True)

if __name__ == '__main__':
    main()
