import os
import sys
from typing import List, Optional

from datetime_matcher import DatetimeMatcher

from zhaostephen.rebrn._internal.cli.main_parser import parse_args
from zhaostephen.rebrn._internal.exceptions import CliInvalidArgumentError
from zhaostephen.rebrn._internal.table_printer import print_table_by_columns

PROGRAM_NAME = "rebrn"


def main(argv: Optional[List[str]] = None) -> int:
    program_name = (
        PROGRAM_NAME if os.path.basename(sys.argv[0]) == "__main__.py" else "rebrn"
    )
    if argv is None:
        argv = sys.argv[1:]

    # Parse args
    try:
        args = parse_args(program_name, argv)
    except CliInvalidArgumentError as err:
        sys.stderr.write("{}".format(err))
        sys.exit(1)

    # Get list of files in directory
    pre_rename_files = list(
        file
        for file in os.listdir(str(args.in_dir_path))
        if (args.in_dir_path / file).is_file()
    )

    # Create a DatetimeMatcher to match regex with datetime formatting
    dtmatcher = DatetimeMatcher()

    # Generate new file names
    final_pre_rename_files = []
    final_post_rename_files = []
    for pre_rename_file in pre_rename_files:
        post_rename_file = dtmatcher.sub(
            args.search_pattern, args.replacement_pattern, pre_rename_file
        )
        if pre_rename_file != post_rename_file:
            final_pre_rename_files.append(pre_rename_file)
            final_post_rename_files.append(post_rename_file)

    # Get final length of files
    num_final_files = len(final_pre_rename_files)

    # Generate mapping
    files_oldtonew = dict(
        (final_pre_rename_files[i], final_post_rename_files[i])
        for i in range(num_final_files)
    )

    # Make display table
    table_data = [
        final_pre_rename_files,
        ["-->" for i in range(num_final_files)],
        final_post_rename_files,
    ]

    # Early exit if no files to be renamed
    if num_final_files == 0:
        print("No renames to be done!")
        print("Exiting...")
        sys.exit(0)

    # Display all files and pending rename results
    print("Pending renames to be done: ")
    print_table_by_columns(table_data)

    # Confirm renaming operation
    is_input_invalid = True
    while is_input_invalid:
        confirm = input("Continue with file renaming? (y/n) ")
        if confirm == "n":
            print("Rename cancelled.")
            print("Exiting...")
            sys.exit(0)
        if confirm == "y":
            is_input_invalid = False

    # Do renaming operation
    print("Processing rename...")
    for filename in final_pre_rename_files:
        try:
            os.rename(
                str(args.in_dir_path / filename),
                str(args.in_dir_path / files_oldtonew[filename]),
            )
        except Exception:
            print("An error occurred when trying to rename {}".format(filename))

    print("Rename done.")
    print("Exiting...")
    sys.exit(0)
