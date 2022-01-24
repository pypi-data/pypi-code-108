"""Provides a command line interface for working with Open Mining Format.

This does the heavy lifting with the goal of making it simple to write-up
a script that handles both import and export. That script can then be used in
the Menu Customisation within the Maptek Workbench which does not support
running a library module as a script.

If the tkinter module is avaliable, the script is able to ask the user to
browse to a file to open or save to.

Examples
--------
Create a script with the bare essentials to provide a command line utility
that handles import and export.

```
from maptekomf.maptek.cli import main

if __name__ == '__main__':
    main()
```

Create a single command line utility that handles import and export.

```
from maptekomf.maptek.cli import define_parser

if __name__ == '__main__':
    arguments = define_parser().parse_args()
    arguments.command(arguments)
```
"""

###############################################################################
#
# (C) Copyright 2021, Maptek Pty Ltd. All rights reserved.
#
###############################################################################

import argparse
import logging
import os
import posixpath
import sys

try:
    import tkinter
    import tkinter.filedialog
    HAS_TK = True
except ImportError:
    # Some Python distributions may not have tkinter like the version from
    # NuGet. The script will still work without it but it just loses the
    # feature of being able to show a open dialog.
    HAS_TK = False


from mapteksdk.project import Project

from .importer import omf_to_project
from .exporter import objects_to_omf


DEFAULT_DESTINATION = '/scrapbook/omf/'


def define_parser():
    """Return an argument parser."""
    parser = argparse.ArgumentParser('Import/export OMF project')
    parser.set_defaults(command=lambda _: parser.print_help())
    parser.add_argument('--debug', action='store_true')
    subparsers = parser.add_subparsers(help='sub-command help')

    importer = subparsers.add_parser(
        'import',
        help='Import an OMF project into a Maptek project.')
    importer.set_defaults(command=_import_omf)
    importer.add_argument(
        "--destination",
        default=DEFAULT_DESTINATION,
        help="The path within the project to import the file to.",
    )

    importer.add_argument(
        '--overwrite', action='store_true',
        help='Overwrite any objects at the destination location if they '
        'already exist.')

    if HAS_TK:
        importer.add_argument(
            'omf_file', metavar='PATH', nargs='*',
            help='The OMF files to import. If no files are provided you '
                'will be prompted to select one using a file dialog.')
    else:
        importer.add_argument(
            'omf_file', metavar='PATH', nargs='+',
            help='The OMF files to import.')

    exporter = subparsers.add_parser(
        'export',
        help='Export objects from a Maptek project to an OMF project.')
    exporter.set_defaults(command=_export_omf)

    output_group = exporter.add_mutually_exclusive_group(required=False)

    output_group.add_argument(
        '-o', '--output',
        help='The path within the project to import the file to.'
              'The default name will be exported.omf if multiple paths are '
              'provided otherwise it will be the base name of the path.')

    if HAS_TK:
        output_group.add_argument(
            '--prompt-for-output', action='store_true',
            help='Prompt the user to provide where to save the output using '
            'a save dialog')

    exporter.add_argument(
        'object_paths', metavar='PATH', nargs='*',
        help='The paths to objects or containers to export. If no paths '
        'are given, it will use the active selection.')

    return parser


def _ask_for_files():
    """Ask the user for what OMF files to import.

    This allows this tool to be used in Maptek Workbench customisation such
    that it prompts the user for what files to import when the tool is run.

    This makes use of the tkinter module.
    """
    if not HAS_TK:
        raise ValueError('Unable to show open dialog as no tkinter module '
                         'was found.')

    root = tkinter.Tk()
    root.withdraw()
    return tkinter.filedialog.askopenfilenames(
        parent=root,
        title='Import OMF files',
        filetypes=[
            ('OMF project file', '*.omf'),
        ],
    )


def _ask_for_output_path(initial_filename: str = 'exported.omf'):
    """Ask the user where an OMF file should be saved to and what it should be
    called.

    This allows this tool to be used in Maptek Workbench customisation such
    that it prompts the user for where to save the file when the tool is run.

    This makes use of the tkinter module.
    """
    if not HAS_TK:
        raise ValueError('Unable to show save dialog as no tkinter module '
                         'was found.')

    root = tkinter.Tk()
    root.withdraw()
    return tkinter.filedialog.asksaveasfilename(
        parent=root,
        title='Export OMF file',
        initialfile=initial_filename,
        defaultextension='.omf',
        filetypes=[
            ('OMF project file', '*.omf'),
        ],
    )


def _import_omf(arguments):
    """Handle the import command."""
    logger = logging.getLogger('maptekomf')
    if arguments.debug:
        logger.setLevel(logging.DEBUG)

    if not arguments.omf_file and HAS_TK:
        arguments.omf_file.extend(_ask_for_files())

    with Project() as project:
        for source in arguments.omf_file:
            # If the default destination is used add the project's name.
            if arguments.destination == DEFAULT_DESTINATION:
                name = os.path.splitext(os.path.basename(source))[0]
                assert DEFAULT_DESTINATION.endswith('/')
                destination = arguments.destination + name
            else:
                destination = arguments.destination

            # For OMF 1.0.1, this doesn't rely on the omf.OMFReader raising an
            # IOError due to a bug that causes another exception to be raised.
            if not os.path.exists(source):
                print(f'Failed to import {source} because the file does not '
                      'exist.')
                continue
            elif not os.path.isfile(source):
                print(f'Failed to import {source} because it is not an OMF '
                     'file.')
                continue

            logger.info('Importing %s to %s in project.', source, destination)
            results = omf_to_project(source, project, destination,
                                     overwrite=arguments.overwrite)

            # Report the results.
            if results:
                success_count = sum(result.success for result in results)
                if success_count == 1:
                    print(f'Imported one object from {source}')
                elif success_count:
                    print(f'Imported {success_count} objects from {source}')
                else:
                    print(f'Imported {source}')

            for result in results:
                if result.error and result.fatal:
                    print(f'Failed to import {result.source_name} due to the '
                          f'following error: {result.error}.')
                    print('No further objects were imported.')
                elif result.error:
                    print(f'Failed to import {result.source_name} due to the '
                          f'following error: {result.error}.')
                else:
                    print(f'Imported {result.source_name} to '
                          f'{result.destination_path}')


def _export_omf(arguments):
    """Handle the export command.

    Each object will be exported into the same OMF project/file.
    """
    logger = logging.getLogger('maptekomf')
    if arguments.debug:
        logger.setLevel(logging.DEBUG)

    with Project() as project:
        if arguments.object_paths:
            objects_to_export = arguments.object_paths
        else:
            # An alternative would be to make this opt-in via a
            # --use-selection argument.
            logger.info('No paths provided - using the current object '
                        'selection.')
            objects_to_export = project.get_selected()

            # Determine the paths for each selected object to log.
            #
            # Alternatively, this could simply say 'Exporting selection to
            # <path>'
            arguments.object_paths.extend(
                object_to_export.path for object_to_export in objects_to_export
            )

            if not objects_to_export:
                logger.error('No objects were selected. Nothing to export.')
                sys.exit(1)

        if not arguments.output:
            if len(arguments.object_paths) == 1:
                # Use the name of the container/object as the name of the file
                # if no output path is given.
                name = posixpath.basename(arguments.object_paths[0])
                if not name:
                    # Account for if the container is given with trailing
                    # slash.
                    name = posixpath.basename(
                        posixpath.dirname(arguments.object_paths[0]))

                if name:
                    arguments.output = name + '.omf'
                else:
                    arguments.output = 'exported.omf'
            else:
                arguments.output = 'exported.omf'

        if arguments.prompt_for_output:
            arguments.output = _ask_for_output_path(arguments.output)

        results = objects_to_omf(project, objects_to_export, arguments.output)

        # Report the results.
        if results:
            success_count = sum(result.success for result in results)
            if success_count == 1:
                print(f'Exported one object to "{arguments.output}"')
            elif success_count:
                print(f'Exported {success_count} objects to '
                      f'"{arguments.output}"')
            else:
                print(f'Failed to export any objects.')

        for result in results:
            if result.error:
                print(f'* Failed to export "{result.source_path}."\n'
                      f'  {result.error}')
            else:
                print(f'* Exported "{result.source_path}".')


def main():
    """Main entry point for a command line interface tool for importing and
    exporting OMF files.
    """
    parsed_arguments = define_parser().parse_args()
    parsed_arguments.command(parsed_arguments)


if __name__ == '__main__':
    # By providing a main here, this enables:
    #     python -m maptekomf.maptek.cli import myproject.omf
    #     python -m maptekomf.maptek.cli export /scrapbook/pit/ --output exported.omf
    main()
