import sys
from omfit_classes import unix_os as os
import argparse

try:
    OMFITstartDir
except Exception:
    OMFITstartDir = os.getcwd()


def omfit_parse_args(input_list=None, show_omfit_launch_options=False):
    """
    Parse the arguments in input_list

    :param input_list: A list of strings, such as sys.argv, to be parsed for arguments passed to OMFIT

    :param show_omfit_launch_options: Display options that are parsed by omfit_launch.sh script or not

    :returns: The results of argparse.ArgumentParser(input_list).parse_args() with smart modifications to get paths correct
    """

    if input_list is None:
        input_list = sys.argv[1:]

    parser = argparse.ArgumentParser(description='OMFIT (One Modeling Framework for Integrated Tasks)')

    parser.add_argument('-s', '--setup', action='store_true', help='Helper setup for SSH authentication and dependencies')
    parser.add_argument('--purge', action='store_true', help='Purge all files in temporary OMFIT locations')
    parser.add_argument('--reset', action='store_true', help='Reset OMFIT SSH/MDS/SQL connections')
    parser.add_argument('--packages', action='store_true', help='List versions of OMFIT required packages')
    if show_omfit_launch_options:
        parser.add_argument('-cwd', '--cwd', action='store_true', help='use current working directory as $OMFIT_ROOT')
        parser.add_argument('-P', '--Python', action='store_true', help='Python major/minor release of executable to use (python[3, 3.x])')
    parser.add_argument('-g', '--scriptGui', action='store_true', help='Run the specified script in the GUI')
    parser.add_argument('-p', '--project', action='store', help='Open the specified project (`-1` for most recent project)')
    parser.add_argument('-m', '--module', action='store', nargs='*', help='Load the specified module(s)', metavar='REMOTE/BRANCH:MODULE')
    parser.add_argument(
        '-M', '--Module', action='store', nargs='*', help='Load the specified module(s) in developer mode', metavar='REMOTE/BRANCH:MODULE'
    )
    parser.add_argument('-c', '--command', action='store', nargs='*', help='Execute the specified Python command(s)')
    parser.add_argument('-b', '--bare', action='store_true', help='Do not start framework')
    parser.add_argument('scriptFile', nargs='?', help='Run the specified script (optional)', default=None)
    parser.add_argument('scriptArgs', nargs='*', help='Arguments passed to script (optional)')

    args = parser.parse_args(input_list)

    OMFITsrc = os.path.split(__file__)[0]

    # pre-process project path
    if args.project:

        if args.project.strip() != '-1':

            # prepend starting directory
            if args.project[0] != '/':
                args.project = os.path.sep.join([OMFITstartDir, args.project])

            # extract basename
            basename = os.path.split(args.project)[1]

            # check existence
            if not os.path.exists(args.project):
                raise IOError('Could not open project: %s.' % args.project)

            # update absolute path
            args.project = os.path.abspath(args.project)

    # pre-process script path
    if args.scriptFile:

        # prepend starting directory
        if args.scriptFile[0] != '/':
            args.scriptFile = os.path.sep.join([OMFITstartDir, args.scriptFile])

        # extract basename
        basename = os.path.split(args.scriptFile)[1]

        # check existence
        if not os.path.exists(args.scriptFile):
            if os.path.exists(os.sep.join([OMFITsrc, '..', 'scripts', os.path.splitext(basename)[0] + '.py'])):
                args.scriptFile = os.sep.join([OMFITsrc, '..', 'scripts', os.path.splitext(basename)[0] + '.py'])
            elif os.path.exists(os.sep.join([OMFITsrc, '..', 'regression', os.path.splitext(basename)[0] + '.py'])):
                args.scriptFile = os.sep.join([OMFITsrc, '..', 'regression', os.path.splitext(basename)[0] + '.py'])
            else:
                raise IOError('Could not open script: %s.' % args.scriptFile)

        # update absolute path
        args.scriptFile = os.path.abspath(args.scriptFile)

    return args


def nice_script_args(args):
    """
    Process script arguments
    """
    import shlex

    s = shlex.shlex(' '.join(args.scriptArgs), posix=False)
    s.whitespace_split = False
    s = list(s) + [None]

    kwargs = {}
    vaname = None
    for k, val in enumerate(s[:-1]):
        if val == '=':
            pass
        elif k == 0 or s[k + 1] == '=':
            varname = val
        else:
            if varname not in kwargs:
                kwargs[varname] = val
            else:
                kwargs[varname] = kwargs[varname] + val

    for varname in kwargs:
        try:
            kwargs[varname] = eval(kwargs[varname])
        except Exception:
            raise Exception(f'Problem with parsing command line argument: {varname}={kwargs[varname]}')
    return kwargs
