"""Provides an entry point to use the vulcanomf module as a program to
import data from an omf project (file) into a Maptek Vulcan project or
to export data to a Maptek Vulcan project.

This can be called like so:

>>> python -m vulcanomf omf_file_1.omf omf_file_2.omf -o output_directory

"""
###############################################################################
#
# (C) Copyright 2021, Maptek Pty Ltd. All rights reserved.
#
###############################################################################

import argparse

def import_omf_command(args):
  """Command for importing OMF files into a Maptek Vulcan project.

  This is called when this script is started with the 'import'
  subcommand.

  Parameters
  ----------
  args : namespace
    Namespace containing the arguments passed to the script.

  """
  # This import is done during this method to avoid importing the
  # Vulcan Python SDK unless it will be used.
  # This way it won't be imported if the user passes --help
  # to this module.
  from .importer import omf_to_vulcan_project

  for input_file in args.omf_paths:
    print(f"Importing: {input_file}")
    try:
      results = omf_to_vulcan_project(input_file,
                                      args.output,
                                      overwrite=args.overwrite,)
      print(results)
    except Exception as error:
      # This shouldn't happen because omf_to_vulcan_project should not
      # raise an error. But just in case, keep going.
      print(f"Failed to Import: {input_file}. Due to the following error:")
      print(type(error).__qualname__, error)
    print("-" * 10)

def export_omf_command(args):
  """Command for exporting files from a Maptek Vulcan Project to OMF.

  This is called when this script is started with the 'export'
  subcommand.

  Parameters
  ----------
  args : namespace
    Namespace containing the arguments passed to the script.

  """
  from .exporter import vulcan_files_to_omf_file

  try:
    input_paths = args.input_paths
    count = vulcan_files_to_omf_file(input_paths, args.output)

    if count == 0:
      print("No exportable objects found.")
    elif count == 1:
      print(f"Exported '{input_paths[0]}' to '{args.output}'")
    else:
      print(f"Exported {count} objects to '{args.output}'")
  except Exception as error:
    print(f"Failed to export objects due to the following error:")
    print(type(error).__qualname__, error)


def _define_import_parser_arguments(subparser):
  """Defines the arguments for the import parser.

  Parameters
  ----------
  subparser : ArgumentParser
    Argument parser to define the import arguments in.

  """
  subparser.add_argument(
    "omf_paths",
    type=str,
    nargs="+",
    help="Path to OMF file(s) to import.")
  subparser.add_argument(
    "--output",
    "-o",
    type=str,
    help="Path to vulcan project directory to place imported files in.",
    default=".")
  overwrite_help = ("If this argument is specified, existing files and "
                    "objects will be overwritten by the import rather "
                    "than raising an error.")
  subparser.add_argument(
    "--overwrite",
    action='store_true',
    default=False,
    help=overwrite_help)

  subparser.set_defaults(command=import_omf_command)


def _define_export_parser_arguments(subparser):
  """Defines the arguments on the export parser.

  Parameters
  ----------
  subparser : ArgumentParser
    Argument parser to define the export arguments in.
  """
  subparser.add_argument(
    "input_paths",
    type=str,
    nargs="+",
    help="Path to Vulcan file(s) to export to OMF. If any is a directory, "
         "all supported files in the directory will be exported.")
  subparser.add_argument(
    "--output",
    "-o",
    type=str,
    help="Path to omf file to place imported files in.",
    default="export.omf")

  subparser.set_defaults(command=export_omf_command)

if __name__ == "__main__":
  parser_description = ("Import or export OMF (Open Mining Format) version 1 "
                        "files into or from Maptek Vulcan.")
  parser = argparse.ArgumentParser(
    prog="vulcanomf",
    description=parser_description)

  subparsers = parser.add_subparsers(title="Commands")

  # Define the import parser.
  import_parser = subparsers.add_parser(
    "import",
    help="Import OMF files into Maptek Vulcan.",
    description="Import OMF files into Maptek Vulcan.")
  _define_import_parser_arguments(import_parser)

  # Define the export parser
  export_parser = subparsers.add_parser(
    "export",
    help="Export Maptek Vulcan files to OMF.")
  _define_export_parser_arguments(export_parser)

  args = parser.parse_args()
  args.command(args)
