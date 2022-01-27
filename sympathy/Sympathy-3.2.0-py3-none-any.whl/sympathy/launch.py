# This file is part of Sympathy for Data.
# Copyright (c) 2013-2018 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import argparse
import os
import sys
import signal
import functools
import contextlib
import compileall

WINDOWS = 'win32'
MACOS = 'darwin'
PATH = 'PATH'
PYTHONNOUSERSITE = 'PYTHONNOUSERSITE'
PYTHONHOME = 'PYTHONHOME'
PYTHONPATH = 'PYTHONPATH'

sy_launch = os.path.abspath(__file__)
sy_application_dir = os.path.dirname(sy_launch)
sy_python_executable = sys.executable


def _in_venv():
    try:
        return sys.prefix != sys.base_prefix
    except Exception:
        return False


class BaseParserDesc:

    @staticmethod
    def add_arguments(parser):
        pass


class ExternParserDesc(BaseParserDesc):
    def __init__(self, command, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cmd = command

    @property
    def description(self):
        return f"run {self._cmd} from sympathy's python environment"


class ViewerParserDesc:
    description = 'run the viewer for sydata files.'

    @staticmethod
    def add_arguments(parser):
        parser.add_argument(
            'filename', action='store', nargs='?', default=None,
            help='sydata file')


class LaunchParserDesc:
    description = 'internal use only'

    @staticmethod
    def add_arguments(parser):
        parser.add_argument('port', type=int)
        parser.add_argument('pid', type=int)
        parser.add_argument('session', type=str)


class ClearParserDesc:
    description = 'cleanup temporary files'

    @staticmethod
    def add_arguments(parser):
        parser.add_argument(
            '--caches',
            action='store_true', default=None,
            help='clear caches for Sympathy.')

        parser.add_argument(
            '--sessions',
            action='store_true', default=None,
            help='clear sessions for Sympathy.')


class InstallParserDesc:
    description = (
        'install Sympathy (start menu, file associations)')

    @staticmethod
    def add_arguments(parser):
        parser.add_argument(
            '--generate-all',
            action='store_true', default=None,
            help='generate parser files')

        parser.add_argument(
            '--compile',
            action='store_true', default=None,
            help='compile sympathy')

        parser.add_argument(
            '--compile-all',
            action='store_true', default=None,
            help='compile all site-package files')

        parser.add_argument(
            '--register',
            action='store_true', default=None,
            help='register desktop application and create shortcuts')

        parser.add_argument(
            '--set-preference',
            metavar=('OPT-NAME', 'OPT-VALUE'),
            nargs=2,
            action='store', default=None,
            help='set value of setting')

        parser.add_argument(
            '--all',
            action='store_true', default=None,
            help=(
                'perform full installation, includes all options if enabled '
                'or by default if no other options are provided'))


class DocParserDesc:
    description = 'generate documentation files'

    @staticmethod
    def add_arguments(parser):
        parser.add_argument(
            '--library-dir', action='store',
            help=(
                'path to library to generate docs for, if not specified '
                'generated documentation will be for the standard library '
                'and platform'))

        parser.add_argument(
            '--output-dir', action='store',
            help=(
                'choose folder in which to output generated docs, if not '
                'specified generated documentation will be put next to the '
                'chosen library'))

        parser.add_argument(
            '--exclude-code-links',
            action='store_true',
            help='disable generations of links to code')

        parser.add_argument(
            '-v', '--verbose', action='store_true',
            default=None, help='verbose output')


class UninstallParserDesc(BaseParserDesc):
    description = (
        'uninstall Sympathy (start menu, file associations)')


def top_parser():
    def add_subparser(subparsers, cmd, parser_desc):
        subparser = subparsers.add_parser(cmd, help=parser_desc.description)
        parser_desc.add_arguments(subparser)
        return subparser

    from sympathy.app import cli
    parser = argparse.ArgumentParser(description='Sympathy for Data')

    parser.add_argument(
        '-I', '--inifile', action='store', default=None,
        help=argparse.SUPPRESS)

    parser.add_argument(
        '--version', action='store_true', default=None,
        help='show Sympathy for Data version and exit')

    subparsers = parser.add_subparsers(
        dest='command', title='Commands', help='Command')
    add_subparser(subparsers, 'gui', cli.GuiParserDesc)
    add_subparser(subparsers, 'cli', cli.CliParserDesc)
    add_subparser(subparsers, 'viewer', ViewerParserDesc)
    add_subparser(subparsers, 'doc', DocParserDesc)
    install_parser = add_subparser(subparsers, 'install', InstallParserDesc)
    add_subparser(subparsers, 'uninstall', UninstallParserDesc)
    add_subparser(subparsers, 'clear', ClearParserDesc)

    launch_parser = add_subparser(subparsers, 'launch', LaunchParserDesc)
    launch_subparsers = launch_parser.add_subparsers(
        dest='launch_command', title='Commands', help='Command')
    add_subparser(launch_subparsers, 'gui', cli.GuiParserDesc)
    add_subparser(launch_subparsers, 'cli', cli.CliParserDesc)
    return parser


def setup_environment(environ):
    """Setup base environment required for importing sympathy."""
    environ = os.environ
    # Setting variables MPLBACKEND and QT_API for matplotlib, etc. This avoids
    # issues that can result from using undesirable default backends such as
    # tkinter and avoids having to do heavy matplotlib import in order to
    # configure this directly.
    environ['MPLBACKEND'] = 'Qt5Agg'
    environ['QT_API'] = 'pyside2'

    # We supply python's -I flag (isolated mode) in links, bat-files, etc.
    # created by our installers. It implies both both -E (ignore
    # python-specific environment variables such as PYTHONPATH) and -s (no user
    # site-packages).
    # Here we translate the flags -s and -E to equivalent modifications of
    # environment variables so that all child processes will inherit these
    # settings.
    if sys.flags.ignore_environment:
        for key in environ.keys():
            if key.startswith("PYTHON"):
                environ.pop(key)
    if sys.flags.no_user_site:
        environ[PYTHONNOUSERSITE] = 'x'

    if sys.platform == WINDOWS:
        python_home = os.path.abspath(sys.prefix)
        # The python home path is needed for when we bundle dll files there.
        # Other paths are added as a precaution, but are normally installed
        # via .pth-files.
        # TODO(erik): remove other paths in 4.0.0.
        paths = [
            ['Lib', 'site-packages', 'pywin32_system32'],
            ['Lib', 'site-packages', 'numpy', 'core'],
            ['Lib', 'site-packages', 'PySide2'],
            [],
        ]
        paths = [os.path.join(python_home, *path) for path in paths]
        path = environ.get(PATH)
        if path:
            paths = path.split(os.pathsep) + paths

        environ[PATH] = os.pathsep.join(paths)

    elif sys.platform == MACOS:
        if 'QT_MAC_WANTS_LAYER' not in os.environ:
            # Only set unless not already set to allow overriding behavior.
            # Work around bug which prevents Sympathy from starting.
            # Known to affect MacOS >= 10.16 (Big Sur).
            environ['QT_MAC_WANTS_LAYER'] = '1'


def run_cli(parsed):
    """Run cli."""
    sys.exit(run_sympathy(parsed))


def run_gui(parsed):
    """Run gui."""
    try:
        # Don't allow keyboard interrupt in the GUI application.
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    except AttributeError:
        pass
    sys.exit(run_sympathy(parsed))


def _install_common():
    from sympathy.app import version
    appname = version.application_name()
    syver = '{}.{}'.format(version.major, version.minor)
    sydata_ext = '.sydata'
    sydata_cls = 'Sympathy.Data'
    syx_ext = '.syx'
    syx_cls = 'Sympathy.Workflow'
    uinstkey = '{}-{}'.format(appname, syver)
    start_menu_root = r'Programs\{}\{}'.format(appname, syver)
    return (appname, syver, sydata_ext, sydata_cls, syx_ext, syx_cls, uinstkey,
            start_menu_root)


def run_doc(parsed):

    def generate_docs():
        """
        Trigger generation of documentation
        """
        if parsed.verbose:
            print('Generating documentation.')
        from sympathy.platform import os_support as oss
        args = []
        if parsed.library_dir:
            args.extend(('--docs-library-dir', parsed.library_dir))
        if parsed.output_dir:
            args.extend(('--docs-output-dir', parsed.output_dir))
        if parsed.exclude_code_links:
            args.append('--docs-exclude-code-links')

        kwargs = {}
        if parsed.verbose:
            kwargs['stdout'] = sys.stdout
            kwargs['stderr'] = sys.stderr

        proc = oss.Popen_no_console([
            sys.executable, __file__, 'cli', '--generate-docs'] + args,
            **kwargs)
        proc.communicate()
        if proc.returncode != 0 and not parsed.verbose:
            print("An error occurred when building documentation. "
                  "Use --verbose flag for more info.")
        sys.exit(proc.returncode)

    generate_docs()


def run_install(parsed):

    def generate_ply():
        """
        Trigger generation of lexer and parser files.
        """
        print('Generating files.')
        # Build type parser and lexer.
        import sympathy.platform.types  # NOQA

    def compile_sympathy():
        """
        Compile pyc-files for Sympathy.
        """
        dir = os.path.abspath(os.path.join(sy_application_dir, os.pardir))
        print('Compiling files in {}.'.format(dir))
        compileall.compile_dir(dir, quiet=True, force=True)

    def compile_all():
        dir = os.path.abspath(
            os.path.join(sy_application_dir, os.pardir, os.pardir))
        print('Compiling *.py files under {}... '
              '(this could take a few minutes.)'
              ''.format(dir))

        from sympathy.platform.os_support import encoded_file

        @contextlib.contextmanager
        def quiet():
            old_stderr = sys.stderr
            devnull = encoded_file(os.devnull, 'w')
            sys.stderr = devnull
            old_stdout = sys.stdout
            devnull = encoded_file(os.devnull, 'w')
            sys.stdout = devnull
            try:
                yield
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr

        with quiet():
            compileall.compile_dir(dir, quiet=True, force=True)

    def register():
        from sympathy.utils import prim

        if prim.is_linux():
            register_linux()
        elif prim.is_windows():
            register_windows()
        else:
            print("Don't know how to register on this platform.")

    def register_linux():
        from sympathy.platform import os_support as oss
        print('Registering application...')
        oss.create_desktop_entries()
        print('Registering file associations (syx and sydata)...')
        oss.create_mime_type_associations()
        print('Updating application and mime databases...')
        oss.update_mime_database()

    def register_windows():
        from sympathy.platform import os_support as oss
        from sympathy.utils import prim
        from sympathy.app import version

        (appname, syver, sydata_ext, sydata_cls, syx_ext, syx_cls, uinstkey,
         start_menu_root) = _install_common()

        launch = sy_launch
        py = sys.executable.replace('pythonw', 'python')
        pyw = py.replace('python', 'pythonw')
        uinstcli = '"{}" "{}" uninstall'.format(pyw, launch)

        print('Register file associations (syx, sydata).')

        oss.unregister_ext(sydata_ext, sydata_cls)
        oss.register_ext(sydata_ext, sydata_cls, 'Sympathy datafile',
                         '"{}" "{}" viewer "%1"'.format(pyw, launch))
        oss.unregister_ext(syx_ext, syx_cls)
        oss.register_ext(syx_ext, syx_cls, 'Sympathy workflow',
                         '"{}" "{}" gui "%1"'.format(pyw, launch),
                         prim.get_icon_path('syx.ico'))

        from sympathy.utils import prim

        print('Create start menu links.')

        oss.delete_start_menu_shortcuts(start_menu_root)
        oss.create_start_menu_shortcuts(
            start_menu_root,
            [
                ('{} {}.lnk'.format(appname, syver),
                 pyw,
                 '"{}" gui'.format(launch),
                 None,
                 prim.get_icon_path('application.ico')),

                ('{} {} - Viewer.lnk'.format(appname, syver),
                 pyw,
                 '"{}" viewer'.format(launch),
                 None,
                 prim.get_icon_path('application.ico'))])

        print('Register application in registry.')

        oss.unregister_app(uinstkey)
        oss.register_app(uinstkey, appname, syver, uinstcli, uinstcli,
                         version.application_copyright())

    install_all = parsed.all

    if install_all or parsed.generate_all:
        generate_ply()

    if install_all or parsed.compile:
        compile_sympathy()

    if install_all or parsed.compile_all:
        compile_all()

    if install_all or parsed.register:
        register()

    # Not included in install_all.
    if parsed.set_preference:
        k, v = parsed.set_preference
        from sympathy.app import settings
        if settings.permanent_types.get(k) == settings.to_bool and v in [
                'true', 'false']:
            settings.instance()[k] = v
        else:
            print('set-preference can only set permanent boolean settings. '
                  '{true, false}')


def run_uninstall(parsed):
    from sympathy.utils import prim
    from sympathy.platform import os_support as oss

    if prim.is_windows():
        (appname, syver, sydata_ext, sydata_cls, syx_ext, syx_cls, uinstkey,
         start_menu_root) = _install_common()

        print('Unregister file associations (syx, sydata).')
        oss.unregister_ext(sydata_ext, sydata_cls)
        oss.unregister_ext(syx_ext, syx_cls)

        print('Remove start menu links.')
        oss.delete_start_menu_shortcuts(start_menu_root)

        print('Unregister application in registry.')
        oss.unregister_app(uinstkey)

    elif prim.is_linux():
        print('Remove desktop entry.')
        oss.delete_desktop_entry()

        print('Remove mime-type association.')
        oss.delete_mime_type_association()

        print('Update application and mime databases')
        oss.update_mime_database()


def run_viewer(parsed):
    """Run viewer."""
    from sympathy.app import sy
    from sympathy.app import util
    from sympathy.platform import viewer

    # The viewer code is in platform and can therefore not import
    # sympathy.app.util.
    icon_path = util.icon_path('application.png')
    sy.run_function(functools.partial(viewer.run, parsed, icon_path))


def worker_environ():
    # Set execution environment.
    # SystemRoot is required for correct behavior on Windows.
    # LD_LIBRARY_PATH is required for correct behavior on Unix.
    environ = dict()
    for variable in ['LD_LIBRARY_PATH',
                     'DYLD_LIBRARY_PATH',
                     'PATH',
                     'LANG',
                     'SystemRoot',
                     'TEMP',
                     'TMP',
                     'TMPDIR',
                     'SYSTEMDRIVE',
                     'USERPROFILE',
                     'WINDIR',
                     'PYTHONNOUSERSITE',
                     'HOME',
    ]:
        if variable in os.environ:
            environ[variable] = os.environ[variable]

    return environ


def run_sympathy(parsed):
    from sympathy.platform import version_support as vs
    from sympathy.platform import os_support as oss
    from sympathy.app import settings
    from sympathy.app.tasks import task_manager2
    from sympathy.platform import crypto
    from sympathy.utils import log
    crypto.init()

    log.setup_log_levels(parsed.loglevel)
    log.get_logger('core').info('Sympathy for Data starting')

    if parsed.num_worker_processes:
        worker_processes = parsed.num_worker_processes
    else:
        worker_processes = settings.instance()['max_nbr_of_threads']

    nworkers = worker_processes or oss.limited_thread_count()
    worker_env = worker_environ()
    worker_env.update(crypto.env())
    platform_env = os.environ

    session_folder = vs.str_(settings.instance()['session_folder'],
                             vs.fs_encoding)

    platform_args = (['-m', 'sympathy',
                      'launch',
                      session_folder] + sys.argv[1:])

    log.get_logger('core.tasks').info('Launching Task Manager')
    return task_manager2.start(
        platform_args=platform_args,
        nworkers=nworkers,
        worker_environ=worker_env,
        platform_environ=platform_env,
        nocapture=parsed.nocapture,
        loglevel=parsed.loglevel,
        pipe=parsed.filename == '-' and parsed.command == 'cli')


def run_editor():
    """Run editor."""
    def execute():
        from sympathy.platform import editor as editor_api
        if editor_api.edit_file(filename=None) is False:
            print('Editor plugin is not installed.')

    from sympathy.app import sy
    sy.run_function(execute)


def run_ipython():
    """Run ipython."""
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            from IPython.frontend.terminal.ipapp import launch_new_instance
            return launch_new_instance()
        except ImportError:
            print('ipython is not installed')
            return 1


def run_pyflakes():
    """Run pyflakes."""
    from pyflakes.scripts.pyflakes import main as pyflakesmain

    def execute():
        try:
            pyflakesmain(sys.argv[-1:])
        except Exception:
            pyflakesmain()
    from sympathy.app import sy
    sy.run_function(execute)


def run_clear(parsed):
    from sympathy.app import sy
    import sympathy.app.application.application

    def clear():
        sessions = parsed.sessions
        storage = parsed.caches

        sympathy.app.application.application.clear(
            session=sessions, storage=storage)
    sy.run_function(clear)


def run_launch(parsed):
    """
    Extra step of executing python process through a file to get __file__ set
    Correctly. When launch via a string trouble arises when the __file__
    attribute is used.

    __file__ becomes relative in imported modules but it is not obvious to what
    if the working directory changes.

    Otherwise, this would have been done by run_sympathy directly.
    """
    from sympathy.app import sy, settings
    from sympathy.platform import feature
    from sympathy.platform import crypto
    settings.create_settings(parsed.inifile)
    session_folder = parsed.session
    settings.instance()['session_folder'] = session_folder
    settings.instance()['task_manager_port'] = parsed.port
    settings.instance()['task_manager_pid'] = parsed.pid
    crypto.init_from_env()

    features = feature.available_features()
    with contextlib.ExitStack() as stack:
        for f in features:
            stack.enter_context(f.manager())

        sy.run_binary(parsed)


def _valid_stream(stream):
    return stream is not None and stream.fileno() >= 0


_gui_apps = ['gui', 'viewer']


def run(parser, parsed, unhandled):
    """Run requested app."""
    internal_choices = [
        'cli', 'gui', 'viewer', 'doc', 'install', 'uninstall', 'clear', 'launch']

    # Wrapping of stdout/stderr.
    # Needs to happen early, before anything is written. Importing modules can
    # trigger output.
    stdout = None
    stderr = None

    cmd = parsed.command

    if not cmd:
        if parsed.version:
            from sympathy.app import version
            print('{name} ({edition}) version: {version}'.format(
                name=version.application_name(),
                edition=version.license_info()["edition"],
                version=version.version))
        else:
            parser.print_help()
        return

    if cmd in internal_choices and unhandled:
        parser.parse_args()

    from sympathy.platform.os_support import encoded_file

    if not cmd == 'launch':
        if not _valid_stream(sys.stdout):
            stdout = encoded_file(os.devnull, 'a')
            sys.stdout = stdout

        if not _valid_stream(sys.stderr):
            stderr = encoded_file(os.devnull, 'a')
            sys.stderr = stderr

    setup_environment(os.environ)

    if (cmd in ['cli', 'gui'] and
            sys.platform == WINDOWS):
        try:
            import colorama
        except ImportError:
            pass
        else:
            def wrap_tty(stream):
                if stream.isatty():
                    ansi_to_win32 = colorama.AnsiToWin32(stream)
                    stream = ansi_to_win32.stream
                return stream

            if _valid_stream(sys.stdout):
                sys.stdout = wrap_tty(sys.stdout)
            if _valid_stream(sys.stderr):
                sys.stderr = wrap_tty(sys.stderr)

    from sympathy.app import version
    from Qt import QtCore
    QtCore.QCoreApplication.setApplicationName(version.application_name())
    QtCore.QCoreApplication.setApplicationVersion(version.version)

    if cmd == 'launch':
        run_launch(parsed)
    else:
        # Internal commands
        if cmd in internal_choices:
            if cmd == 'cli':
                if not (parsed.filename or parsed.generate_docs):
                    parser.parse_args(sys.argv[1:2] + ['--help'])
                action = functools.partial(run_cli, parsed)
            elif cmd == 'gui':
                action = functools.partial(run_gui, parsed)
            elif cmd == 'viewer':
                action = functools.partial(run_viewer, parsed)
            elif cmd == 'doc':
                action = functools.partial(run_doc, parsed)
            elif cmd == 'install':
                action = functools.partial(run_install, parsed)
            elif cmd == 'uninstall':
                action = functools.partial(run_uninstall, parsed)
            elif cmd == 'clear':
                action = functools.partial(run_clear, parsed)
        else:
            del sys.argv[1]

        from sympathy.app import settings, util
        # Set the global settings inifile
        settings.create_settings(parsed.inifile)

        util.create_session_folder(timeout=10)
        session_folder = settings.instance()['session_folder']

        close_list = []

        try:
            # Writing missing pipes to files instead.

            if not _valid_stream(sys.stdin):
                stdin_filename = os.path.join(session_folder, 'stdin')
                sys.stdin = encoded_file(stdin_filename, 'w+')
                close_list.append(sys.stdin)

            if not _valid_stream(sys.stdout):
                stdout_filename = os.path.join(session_folder, 'stdout')
                sys.stdout = encoded_file(
                    stdout_filename, 'w')
                close_list.append(sys.stdout)

            if not _valid_stream(sys.stderr):
                stderr_filename = os.path.join(session_folder, 'stderr')
                sys.stderr = encoded_file(
                    stderr_filename, 'w')
                close_list.append(sys.stderr)

            action()
        finally:
            for f in reversed(close_list):
                f.close()


def _gui_error(exc_info):
    import traceback
    from Qt import QtWidgets
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    box = QtWidgets.QMessageBox(
        QtWidgets.QMessageBox.Critical,
        "Critical error",
        "An unexpected error occurred in the code "
        "used for startup and shutdown.")
    box.setDetailedText('\n'.join(traceback.format_exception(*exc_info)))
    box.show()
    app.exec_()


def main():
    from sympathy.platform.os_support import encode_stream
    encode_stream(sys.stdout)
    encode_stream(sys.stderr)
    try:
        app = sys.argv[1]
    except IndexError:
        app = None

    replacements = {
        'sy': 'cli',
        'syg': 'gui'
    }

    if app in replacements:
        app = replacements[app]
    if app:
        sys.argv[1] = app

    try:
        parser = top_parser()
        if app is None:
            parser.print_help()
            return
        parsed, unhandled = parser.parse_known_args()
    except SystemExit:
        raise
    except Exception:
        if app == 'gui':
            _gui_error(sys.exc_info())
        raise
    try:
        run(parser, parsed, unhandled)
    except SystemExit:
        raise
    except Exception:
        if app == 'gui' or app == 'launch' and parsed.launch_command == 'gui':
            _gui_error(sys.exc_info())
        raise


if __name__ == '__main__':
    main()
