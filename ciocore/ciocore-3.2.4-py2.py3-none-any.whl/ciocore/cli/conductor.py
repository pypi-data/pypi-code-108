#!/usr/bin/env python
# Use absolute imports to avoid a "conductor" name clash (this module name vs conductor package).
from __future__ import absolute_import

import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ciocore import  downloader, uploader, loggeria, config

def parse_args():
    cfg = config.config().config

    # Create a parent parser. Arguments that are common across all subparsers can be added to this parser
    parent_parser = argparse.ArgumentParser(add_help=False)

    # create the main parser. Not sure why this parser is required, but got parsing tracebacks when excluding it (it gets confused about the arguments provided)
    parser = argparse.ArgumentParser(description="description")
    subparsers = parser.add_subparsers(title="actions")


    #############################
    # UPLOADER PARSER
    #############################
    uploader_parser_desciption = "parse uploader arguments"
    uploader_parser_help = ""

    uploader_parser = subparsers.add_parser("uploader", parents=[parent_parser],
                                            help=uploader_parser_help,
                                            description=uploader_parser_desciption,
                                            formatter_class=argparse.RawTextHelpFormatter)

    uploader_parser.add_argument("--database_filepath",
                                 help=("The filepath to the local md5 caching database. If no filepath "
                                       "is specified, the database will be created in a temp directory"))

    uploader_parser.add_argument("--location",
                                 help=('An optional string to indicate which location this uploader '
                                       'executable should register as. This option is only relevant '
                                       'for conductor accounts which submits jobs from different locations '
                                       '(e.g. differing geographic locations or office locations that have differing file systems).'
                                       ' Typically each location would have its own conductor uploader process running. This location '
                                       'string allows each uploader to target specific upload jobs (files to upload) that are appropriate '
                                       'for it. This is potentially useful as each location may have differing file systems '
                                       'available to it (e.g. uploader1 has /filesystem1 available to it, but uploader2 only '
                                       'has /filesystem2 available to it).  In this case uploader1 should only upload files '
                                       'that exist on /filesystem1 and uploader2 should only upload files that exist on /filesystem2. '
                                       'This is achieved by including a location argument (such as "location1" or "location2") '
                                       'when submitting jobs, as well as when launching this uploader command.'))

    uploader_parser.add_argument("--md5_caching",
                                 help=("Use cached md5s. This can dramatically improve the uploading "
                                       "times, as md5 checking can be very time consuming. Caching md5s "
                                       "allows subsequent uploads (of the same files) to skip the "
                                       "md5 generation process (if the files appear to not have been "
                                       "modified since the last time they were submitted). The cache is "
                                       "stored locally and uses a file's modification time and file size "
                                       "to intelligently guess whether the file has changed. Set this "
                                       "flag to False if there is concern that files may not be getting "
                                       "re-uploaded properly"),
                                 choices=[False, True],
                                 type=cast_to_bool,
                                 default=None)

    uploader_parser.add_argument("--log_level",
                                 choices=loggeria.LEVELS,
                                 help="The logging level to display")

    uploader_parser.add_argument("--log_dir",
                                 help=("When provided, will write a log file to "
                                       "the provided directory. This will be a "
                                       "rotating log, creating a new log file "
                                       "everyday, while storing the last 7 days "
                                       "of logs"))

    uploader_parser.add_argument("--thread_count",
                                 type=int,
                                 default=cfg["thread_count"],
                                 help=('The number of threads that should download simultaneously'))

    uploader_parser.set_defaults(func=run_uploader)

    #############################
    # DOWNLOADER PARSER
    #############################

    downloader_parser_desciption = "parse downloader arguments"
    downloader_parser_help = ""

    downloader_parser = subparsers.add_parser("downloader", parents=[parent_parser],
                                              help=downloader_parser_help,
                                              description=downloader_parser_desciption,
                                              formatter_class=argparse.RawTextHelpFormatter)

    downloader_parser.add_argument("--job_id",
                                   help=("The job id(s) to download. When specified "
                                         "will only download those jobs and terminate "
                                         "afterwards"),
                                   action='append')

    downloader_parser.add_argument("--task_id",
                                   help="Manually download output for specific tasks - use a comma-separated list of tasks if you wish")

    downloader_parser.add_argument("--output",
                                   help="Override for the output directory")

    downloader_parser.add_argument("--location",
                                   help=('An optional string to indicate which location this downloader '
                                         'executable should register as. This option is only relevant for '
                                         'conductor accounts which submits jobs from different locations '
                                         '(e.g. differing geographic locations or office locations that '
                                         'have differing file systems). Typically each location would '
                                         'have its own conductor downloader process running. This location '
                                         'argument allows each downloader to target specific jobs (to '
                                         'download upon job-completion) that match its appropriate location. '
                                         'Essentially this allows the location of which a job was submitted '
                                         'from to also be the destination in which to deliver completed '
                                         'renders to (which would typically be the desired behavior).'))

    downloader_parser.add_argument("--project",
                                   help=('An optional string to indicate which project that this downloader executable should register as.'))

    downloader_parser.add_argument("--log_level",
                                   choices=loggeria.LEVELS,
                                   default=cfg["log_level"],
                                   help="The logging level to display")

    downloader_parser.add_argument("--log_dir",
                                   help=("When provided, will write a log file to "
                                         "the provided directory. This will be a "
                                         "rotating log, creating a new log file "
                                         "everyday, while storing the last 7 days "
                                         "of logs"))

    downloader_parser.add_argument("--thread_count",
                                   type=int,
                                   default=cfg["thread_count"],
                                   help=('The number of threads that should download simultaneously'))

    downloader_parser.add_argument("--alt",
                                   help=('Run an alternative version of the downloader'),
                                   action='store_true')

    downloader_parser.set_defaults(func=run_downloader)

    return parser.parse_args()


def cast_to_bool(string):
    '''
    Ensure that the argument provided is either "True" or "False (or "true" or
    "false") and convert that argument to an actual bool value (True or False).
    '''
    string_lower = string.lower()
    if string_lower == "true":
        return True
    elif string_lower == "false":
        return False
    raise argparse.ArgumentTypeError('Argument must be True or False')

def run_uploader(args):
    uploader.run_uploader(args)


def run_downloader(args):
    '''
    Convert the argparse Namespace object to a dictionary and run the downloader
    with the given args.
    '''
    # Convert Namespace args object to args dict
    args_dict = vars(args)

    if args_dict.get("task_id") and not args_dict.get("job_id"):
        raise argparse.ArgumentTypeError('Must supply a job_id with task_id.')

    # New downloader broke in python 3. It was used only for linux and in
    # daemon mode, so for now we'll use the old downloader for everything.

    return downloader.run_downloader(args_dict)


def main():
    args = parse_args()
    args.func(args)


if __name__ == '__main__':
    main()

