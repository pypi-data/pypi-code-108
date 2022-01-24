"""Provides basic Workflow support for working with Open Mining Format.

The original design goal was to make it easy to write a script with a couple
of lines of code to write a script that can then be used in a workflow.

As a result this has not been designed for extensibility, i.e if you are
wishing to support what this does and more than by all means start with the
parser and then add extra options but you will need to write your own
function to handle handle the arguments.

The benefit of this module is it makes it easier to upgrade and improve
workflow functionality that uses it. It also means if a user needs to
write a script to bootstrap a workflow, they can write two to three line
script.

The drawback of this module is using it means its harder to customise and
modify.
"""

from maptekomf.maptek.importer import omf_to_project
from maptekomf.maptek.exporter import objects_to_omf

from mapteksdk.project import Project
from mapteksdk.workflows import WorkflowArgumentParser, WorkflowSelection

try:
    from mapteksdk.operations import write_report
except ImportError:
    # This handles an older version of the mapteksdk.
    from mapteksdk.pointstudio.operations import write_report

try:
    import tkinter
    import tkinter.filedialog
    HAS_TK = True
except ImportError:
    # Some Python distributions may not have tkinter like the version from
    # NuGet. The script will still work without it but it just loses the
    # feature of being able to show a open dialog.
    HAS_TK = False

import os.path
import posixpath


def parser_export_single_omf():
    """Provides a parser for exporting objects from a Maptek project to a
    single OMF file.

    This is designed specially for export_single_omf() if you wish to extend
    it you can call this function declare additional inputs and outputs but
    you will need to write your own function to perform the work.

    Returns
    -------
    WorkflowArgumentParser
        A parser that supports use in a workflow.

    Examples
    --------
    A minimum script for exporting objects from Maptek project in a Workflow.
    If you wish to extend this you need to write your own
    function to replace export_single_omf().

    ```
    from maptekomf.maptek.workflow import parser_export_single_omf
    from maptekomf.maptek.workflow import export_single_omf

    if __name__ == '__main__':
        parser = parser_export_single_omf()
        parser.parse_arguments()
        export_single_omf(parser)
    ```
    """

    # TODO: Consider making the selection optional such that it uses the
    # active selection in that case.

    parser = WorkflowArgumentParser(
        description='Export objects from a Maptek project to a single OMF '
                    '(Open Mining Format) file',
    )
    parser.declare_input_connector(
        'objects',
        WorkflowSelection,
        description="The objects to export to OMF",
    )

    parser.declare_input_connector(
        'destination',
        str,
        description="The path to write out the OMF file",
    )

    parser.declare_output_connector(
        'destination',
        str,
        description="The path where the OMF file was written to.",
    )

    return parser


def parser_import_single_omf():
    """Provides a parser for importing a single OMF file into a Maptek project.

    This is designed specially for import_single_omf() if you wish to extend
    it you can call this function declare additional inputs and outputs but
    you will need to write your own function to perform the work.

    Returns
    -------
    WorkflowArgumentParser
        A parser that supports use in a workflow.

    Examples
    --------
    A minimum script for importing a single OMF file into a Maptek project
    in a Workflow. If you wish to extend this you need to write your own
    function to replace handle_input_single_omf().

    ```
    from maptekomf.maptek.workflow import parser_import_single_omf
    from maptekomf.maptek.workflow import import_single_omf

    if __name__ == '__main__':
        parser = parser_import_single_omf()
        parser.parse_arguments()
        import_single_omf(parser)
    ```
    """

    parser = WorkflowArgumentParser(
        description='Import an OMF (Open Mining Format) file into a Maptek '
                    'Project',
    )
    parser.declare_input_connector(
        'source',
        str,
        description="the path to the OMF file to import.",
    )

    parser.declare_input_connector(
        'destination',
        str,
        description="the path in the project to import to",
        default='/scrapbook/omf/',
    )

    # The goal is support to kinds of destinations:
    # 1) The path is to a container that the project should be imported into
    #    and the project name appended.
    # 2) The path is the full path for where the objects will end up.
    parser.declare_input_connector(
        'no_project_name',
        bool,
        description="Do not add the name of the project to destination.\n"
                    "Use this option if the destination already contains a "
                    "a suitable name. If not set then the name of project "
                    "will be appended to the destination path.",
    )

    parser.declare_input_connector(
        'overwrite',
        bool,
        description="If there is already objects at the destination path than "
                    "they will be overwritten.",
    )

    # The omf_to_project() function could provide a list of the objects
    # imported which may be more useful.
    parser.declare_output_connector(
        'imported_project',
        WorkflowSelection,
        description="The container of the imported project.",
    )

    return parser


def parser_import_multiple_omf():
    """Provides a parser for importing a multiple OMF file into a Maptek
    project.

    This is designed specially for import_multiple_omf() if you wish to extend
    it you can call this function declare additional inputs and outputs but
    you will need to write your own function to perform the work.

    Returns
    -------
    WorkflowArgumentParser
        A parser that supports use in a workflow.

    Examples
    --------
    A minimum script for importing a single OMF file into a Maptek project
    in a Workflow. If you wish to extend this you need to write your own
    function to replace handle_input_single_omf().

    ```
    from maptekomf.maptek.workflow import parser_import_multiple_omf
    from maptekomf.maptek.workflow import import_multiple_omf

    if __name__ == '__main__':
        parser = parser_import_multiple_omf()
        parser.parse_arguments()
        import_multiple_omf(parser)
    ```
    """

    parser = WorkflowArgumentParser(
        description='Import an OMF (Open Mining Format) files into a Maptek '
                    'Project',
    )
    parser.declare_input_connector(
        'paths',
        list,
        description="the paths of OMF files to import.",
        default=[],
    )

    parser.declare_input_connector(
        'destination',
        str,
        description="The path to a container in the project to import each "
                    "OMF file into.",
        default='/scrapbook/omf/',
    )

    parser.declare_input_connector(
        'overwrite',
        bool,
        description="If there is already objects at the destination path than "
                    "they will be overwritten.",
    )

    return parser

def _ask_for_files():
    """Ask the user for what OMF files to import.

    This makes use of the tkinter module. This provides a fallback if the
    Workflow does not provide any paths.
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


def export_single_omf(parser: WorkflowArgumentParser = None):
    """Provides the ability to export from a Maptek project into a single OMF
    file via a Workflow with a single function call.

    This takes care of defining the WorkflowArgumentParser (if no
    existing parser is given), connecting to the project and performing
    the import.

    Parameters
    ----------
    parser
        Optionally a workflow argument parser.
        If None then parser_export_single_omf() will be used which is the
        parser designed to support all the of this function.
    Examples
    --------
    A minimum script for export from a Maptek project into  a single OMF file
    in a Workflow.
    ```
    from maptekomf.maptek.workflow import export_single_omf

    if __name__ == '__main__':
        export_single_omf()
    """

    parser = parser or parser_export_single_omf()
    parser.parse_arguments()

    with Project() as project:

        objects_to_omf(project, parser['objects'], parser['destination'])

        write_report('OMF Export',
                     f'Exported {len(parser["objects"])} objects to '
                     f'{repr(parser["destination"])}')

        parser.set_output('destination', parser['destination'])


def import_single_omf(parser: WorkflowArgumentParser = None):
    """Provides the ability to import a single OMF file into a Maptek project
    via a Workflow with a single function call.

    This takes care of defining the WorkflowArgumentParser (if no
    existing parser is given), connecting to the project and performing
    the import.


    Parameters
    ----------
    parser
        Optionally a workflow argument parser.
        If None then parser_import_single_omf() will be used which is the
        parser designed to support all the of this function.
    Examples
    --------
    A minimum script for importing a single OMF file into a Maptek project
    in a Workflow.
    ```
    from maptekomf.maptek.workflow import import_single_omf

    if __name__ == '__main__':
        import_single_omf()
    """

    parser = parser or parser_import_single_omf()
    parser.parse_arguments()

    with Project() as project:
        filename = os.path.basename(parser['source'])
        if parser['no_project_name']:
            destination = parser['destination']
        else:
            # The filename typically ends up being better description of the
            # name of the project than the name stored inside the project.
            name = os.path.splitext(filename)[0]
            destination = posixpath.join(parser['destination'], name)

        omf_to_project(parser['source'], project, destination,
                       overwrite=parser['overwrite'])

        write_report('OMF Import', f'Imported {filename} to {destination}')

        parser.set_output('imported_project', [destination])


def import_multiple_omf(parser: WorkflowArgumentParser = None):
    """Provides the ability to multiple OMF files into a Maptek project via a
    Workflow with a single function call.

    This takes care of defining the WorkflowArgumentParser (if no
    existing parser is given), connecting to the project and performing
    the import.

    The list of paths is optional, if not provided and Tkinter is available the
    user will be shown a browse dialog.

    Parameters
    ----------
    parser
        Optionally a workflow argument parser.
        If None then parser_import_single_omf() will be used which is the
        parser designed to support all the of this function.
    Examples
    --------
    A minimum script for importing a multiple OMF files into a Maptek project
    in a Workflow.
    ```
    from maptekomf.maptek.workflow import import_multiple_omf

    if __name__ == '__main__':
        import_multiple_omf()
    """

    parser = parser or parser_import_multiple_omf()
    parser.parse_arguments()

    if not parser['paths'] and HAS_TK:
        parser['paths'].extend(_ask_for_files())

    with Project() as project:
        for path in parser['paths']:
            # The filename typically ends up being better description of the
            # name of the project than the name stored inside the project.
            name = os.path.splitext(os.path.basename(path))[0]
            destination = posixpath.join(parser['destination'], name)
            omf_to_project(path, project, destination,
                           overwrite=parser['overwrite'])
