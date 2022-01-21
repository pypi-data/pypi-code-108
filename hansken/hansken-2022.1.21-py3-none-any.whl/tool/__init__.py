# encoding=utf-8

from argparse import ArgumentParser, Namespace, SUPPRESS
from datetime import datetime, timezone, tzinfo
from getpass import getuser
import os
import shlex
import warnings

from dateutil.tz import gettz
from logbook import DEBUG, INFO, WARNING
from logbook import FileHandler, Logger, NullHandler, set_datetime_format, StderrHandler
from logbook.compat import redirected_logging, redirected_warnings
import requests

from hansken import __version__, envvars
from hansken.auth import HanskenAuthBase, resolve
from hansken.remote import Connection, MultiProjectContext, ProjectContext
from hansken.util import MultiContext

try:
    # ensure urllib3 is a module-level name for testability
    import urllib3
except ImportError:
    urllib3 = None


log = Logger(__name__)


def from_envvar(envvar, provided=None):
    if provided:
        return provided

    return os.environ.get(envvar, None)


def prompt_user():
    try:
        user = getuser()
        read = input('username [{}]: '.format(user))
        if read.strip():
            user = read
    except (KeyboardInterrupt, EOFError):
        user = None
    except Exception:  # documentation of getuser: "otherwise, an exception is raised"
        user = input('username: ')

    return user


# define a parent parser to define global options
parent = ArgumentParser(add_help=False)
parent.add_argument('-v', '--verbose', action='count', help='be verbose')
parent.add_argument('-l', '--log', metavar='FILE',
                    default=from_envvar(envvars.log),
                    help='log messages to FILE (use - for standard error, '
                         'log messages are hidden by default)')
parent.add_argument('-z', '--timezone', metavar='TZ', type=gettz, default=timezone.utc,
                    help='log messages with timestamps in timezone TZ (e.g. Europe/Amsterdam), '
                         'defaults to UTC')
# default endpoint and project to the value in env
parent.add_argument('-e', '--endpoint', default=from_envvar(envvars.endpoint),
                    help='connect to the Hansken REST endpoint at ENDPOINT '
                         '(defaults to environment variable {})'.format(envvars.endpoint))
parent.add_argument('--keystore', metavar='ENDPOINT',
                    default=from_envvar(envvars.keystore),
                    help='connect to the Hansken keystore REST endpoint at ENDPOINT '
                         '(defaults to environment variable {})'.format(envvars.keystore))
parent.add_argument('--preference', metavar='ENDPOINT',
                    default=from_envvar(envvars.preference),
                    help='connect to the Hansken preference REST endpoint at ENDPOINT '
                         '(defaults to environment variable {})'.format(envvars.preference))
parent.add_argument('--idp', metavar='IDP_ID',
                    default=from_envvar(envvars.idp),
                    help='select SAML identity provider named IDP_ID if available '
                         '(defaults to environment variable {})'.format(envvars.idp))
parent.add_argument('--idp-url', metavar='ENDPOINT',
                    default=from_envvar(envvars.idp_url),
                    help=SUPPRESS)
parent.add_argument('--idp-realm', metavar='REALM',
                    default=from_envvar(envvars.idp_realm),
                    help=SUPPRESS)
parent.add_argument('--sso-url', metavar='ENDPOINT',
                    default=from_envvar(envvars.sso_url),
                    help=SUPPRESS)
parent.add_argument('-u', '--user', '--username', dest='username', default=None,
                    help='specify a username (will otherwise be prompted for if needed)')
parent.add_argument('-U', '--prompt-username', action='store_const', const=prompt_user, dest='username',
                    help=SUPPRESS)
parent.add_argument('--password', dest='password', default=None,
                    help=SUPPRESS)
parent.add_argument('--connection-pool-size', type=int, default=None,
                    help='override default HTTP(S) connection pool size')
# add an argument to disable ssl/tls certificate verification
parent.add_argument('--no-verify', dest='verify', action='store_false', default=True,
                    help='disable certification verification for secure connections, use with caution')

# NB: add a hidden hdfs configuration option for operators, allowing a single argument file per Hansken instance
# (value for hdfs_url is ignored for most commands, can be overridden by -o/--output for upload command)
parent.add_argument('--hdfs-url', dest='hdfs_url', help=SUPPRESS)

# password and auth are not really arguments, but used in combo with user/idp/sso; make sure they're defined
parent.set_defaults(password=None, auth=None)


# define the actual parser to be used
# (defined as a local class to override result for and repr() in doc as default for arg)
class hansken_parser(ArgumentParser):  # noqa: N801
    def __repr__(self):
        return '<hansken.py default parser>'


hansken_parser = hansken_parser(fromfile_prefix_chars='@')
# define the version switch only on the global parser
hansken_parser.add_argument('--version', action='version', version=__version__)
# parse arguments like a shell when reading args from file
# (the default effectively only splits lines)
hansken_parser.convert_arg_line_to_args = lambda line: shlex.split(line, comments=True)

# enable subcommands, saving the name of the command in argument command
sub_commands = hansken_parser.add_subparsers(dest='command', metavar='COMMAND')
sub_commands.required = True  # 'fix' for required=True not being allowed in add_subparsers above


def create_parser(requires_project=False, **kwargs):
    warnings.warn('hansken.tool.create_parser has been renamed to hansken.tool.create_argument_parser',
                  DeprecationWarning)
    return create_argument_parser(requires_project=requires_project, **kwargs)


def create_argument_parser(requires_project=False, **kwargs):
    """
    Creates an `ArgumentParser` to be used with `.run` alongside
    ``with_context`` or ``with_admin``. This parser's main feature is to *not*
    add a ``-h/--help`` argument, which is attached to the main argument
    parser used by `.run`.

    :param requires_project: whether the parser should be fitted with a
        required positional argument ``project``
    :param kwargs: any `ArgumentParser` constructor arguments (see `argparse`
        documentation)
    :return: an `ArgumentParser` that won't clash with ``hansken.py``'s parent
        parser
    :rtype: `argparse.ArgumentParser`
    """
    # don't add help, returned parser will serve as a parent that will itself add help
    if kwargs.pop('add_help', False):
        raise ValueError('parser cannot specify -h/--help')

    parser = ArgumentParser(add_help=False, **kwargs)
    if requires_project:
        parser.add_argument('project', metavar='PROJECT',
                            help='attach to project with id PROJECT')
    return parser


def add_command(name, command, optional_project=True, **kwargs):
    """
    Adds a named command to be run when specified on the command line. Use the
    return value to add additional arguments for the newly added command.

    :param name: name of the command to add
    :param command: callable that runs the actual command, first positional
        argument to command is the `argparse.Namespace` object created by
        `argparse`.
    :param optional_project: whether to include a -p/--project option
    :param kwargs: any `ArgumentParser` constructor arguments (see `argparse`
        documentation)
    :return: an `ArgumentParser` for the newly added command
    :rtype: `argparse.ArgumentParser`
    """
    # add a new parser to sub commands, pass along the parent (enables command -e http://...) and any kwargs
    sub_parser = sub_commands.add_parser(name, parents=[parent], **kwargs)
    # set the callable as the actual command to be run
    sub_parser.set_defaults(run_command=command)

    if optional_project:
        # only add the optional -p/--project if sub command needs it
        sub_parser.add_argument('-p', '--project', default=from_envvar(envvars.project),
                                help='attach to project with id PROJECT '
                                     '(defaults to environment variable {})'.format(envvars.project))
    return sub_parser


def set_command(command, parents=None, **kwargs):
    """
    Overwrite the default functionality of the ``hansken.py`` command line
    interface. Note that this method should be called only once, either from
    user code, passing the resulting `ArgumentParser` to `.run` or by `.run`
    itself when used with one of the *with_\\** keyword arguments.

    :param command: a `callable` to be called with a single positional
        argument of type `argparse.Namespace` after parsing arguments
    :param parents: a sequence of parent parsers to use aside from the always
        inserted parent parser defining the global configuration options
    :param kwargs: any `ArgumentParser` constructor arguments (see `argparse`
        documentation)
    :return: an `ArgumentParser` for the new command
    :rtype: `argparse.ArgumentParser`
    """
    if hasattr(set_command, 'called') and set_command.called:
        raise ValueError('cannot set main command more than once')

    if not callable(command):
        raise ValueError('command must be callable')

    # 'copy' behaviour of global parser to the new one
    fromfile_chars = kwargs.pop('fromfile_prefix_chars', '@')
    fromfile_splitter = kwargs.pop('convert_arg_line_to_args', hansken_parser.convert_arg_line_to_args)

    # add the global parent to any parents provided by the caller
    parents = list(parents or [])
    parents.append(parent)
    # define a new default nameless command (the empty name will make --help appear as if there's no sub command)
    sub_parser = sub_commands.add_parser('', parents=parents, fromfile_prefix_chars=fromfile_chars, **kwargs)
    sub_parser.convert_arg_line_to_args = fromfile_splitter
    sub_parser.set_defaults(command='', run_command=command)

    # mark this function as called, subsequent calls produce confusing behaviour and should fail
    setattr(set_command, 'called', True)
    # provide the sub parser to the caller, let them add additional arguments
    return sub_parser


def resolve_logging(args):
    """
    Creates `logbook.Handler` instances from available parameters.

    :param args: an `argparse.Namespace` object with parsed commandline
        arguments
    :return: a context manager within which logging is configured from the
        provided command line arguments
    """
    levels = [WARNING, INFO, DEBUG]
    verbosity = args.verbose
    if verbosity not in levels:
        # make sure verbosity is an int (default None)
        verbosity = max(0, min(verbosity or 0, len(levels) - 1))
        verbosity = levels[verbosity]

    if args.log:
        tz = args.timezone
        if not isinstance(tz, tzinfo):
            # should timezone be provided through run, argument won't have been passed to gettz
            tz = gettz(tz)

        def utc_dt():
            return datetime.now(tz=tz)

        # force logbook to use tz-aware timestamps, log in requested timezone (default UTC)
        set_datetime_format(utc_dt)

        # when logging is actively used, also steal both logging.* and warnings.warn calls
        # bind the logbook handlers application-wide
        if args.log == '-':
            return MultiContext(redirected_logging(),
                                redirected_warnings(),
                                StderrHandler(level=verbosity).applicationbound())
        elif args.log:
            return MultiContext(redirected_logging(),
                                redirected_warnings(),
                                FileHandler(args.log, level=verbosity).applicationbound())
    else:
        # no dest, no real handler
        return NullHandler().applicationbound()


def resolve_auth(args):
    """
    Creates a HanskenAuthBase instance from available parameters.

    - endpoint + idp        -> select named IDP from REST API, probe for
                               implementation to use
    - idp_url + sso_url     -> OpenAM auth with Kerberos SSO
    - idp_url + user + pass -> OpenAM auth using REST login
    - user + pass           -> SAML proxy auth using REST login
    - otherwise             -> None

    :param args: an argparse.Namespace object with parsed commandline arguments
    :return: a HanskenAuthBase instance if args contained parameters that
             enable one of the options, None otherwise
    """
    return resolve(args.username, args.password,
                   base_url=args.endpoint, idp_id=args.idp,
                   idp_url=args.idp_url, idp_realm=args.idp_realm, sso_url=args.sso_url,
                   verify=args.verify)


def _disable_insecure_request_warning():
    try:
        # attempt to disable repeated verbose warnings when certificate verification is explicitly turned off
        # (remove when hansken.py depends on requests>=2.16.0)
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        return True
    except Exception:  # nosec
        pass

    try:
        # newer installations will fail the above on the 'packages' module being absent, fall back to the 'new way'
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return True
    except Exception:  # nosec
        pass

    # disabling the warning failed
    return False


def run(args=None, using_parser=hansken_parser, with_connection=None, with_context=None,
        with_multi_context=None, error='raise', with_admin=None, **defaults):
    """
    Run the command line tool, either as the command line interface defined by
    ``hansken.py`` itself, or running user code, piggybacking on all the
    command line argument parsing and resolving done by ``hansken.py``.

    .. note::

        `.run` parses the command line by default. If user code does its own
        command line parsing, either pass applicable *args* to `.run` or use
        `.set_command`, passing the resulting `argparse.ArgumentParser` to
        `.run` as *using_parser* after adding additional user arguments.

    .. note::

        By default, `.run` calls `exit` on the `argparse.ArgumentParser` in
        case of an error raised from whatever command is called (this includes
        user-provided commands). This call results in a CLI-like error message
        containing the exception message of the error that was caught. As the
        call to `exit` raises a `SystemExit`, any user code *after* the call
        to `.run` will not be executed. When the *error* argument to `.run` is
        set to ``'raise'`` or the arguments parser sets verbose mode, `exit`
        is *not* called, the exception is reraised instead.

    :param args: arguments to the tool, a `list` of `str`, or `None`, in which
        case *args* will be read from the command line
    :param using_parser: the `argparse.ArgumentParser` to be used, either the
        parser that processes the command line interface defined by
        ``hansken.py`` itself or one that is the result of `.set_command`
    :param with_connection: a user-defined `callable` to be run with a
        `.Connection` instance, passed as keyword argument ``connection``
    :param with_context: a user-defined `callable` to be run with a
        `.ProjectContext` instance, passed as keyword argument ``context``
    :param with_multi_context: a user-defined `callable` to be run with a
        `.MultiProjectContext` instance, passed as keyword argument ``context``
    :param error: how to deal with an error raised from the selected command
        runner, defaults to propagating errors to the caller of `.run`, set to
        ``'exit'`` to call ``using_parser.exit()`` with a non-zero return code
        and failure message
    :param defaults: named arguments to be used as defaults when parsing the
        command line, matching the destinations of defined arguments (e.g.
        ``project='a-project-uuid'``)
    :return: the return value of the command that was ultimately called (when
        `.run` was called with either *with_context* or *with_admin*, the
        return value of that callable will be returned by `.run`)
    """
    def has_project(parser):
        # try to determine whether parser has already defined either default or argument for a project
        if parser.get_default('project'):
            return True

        return any(action.dest == 'project' for action in parser._actions)

    # run with either connection or context, not both
    if (with_context, with_connection, with_admin).count(None) < 2:
        raise ValueError('use either with_context=<my_func> or with_connection=<my_func>, not both')

    # check whether the parser being used is a custom one
    custom_parser = using_parser is not hansken_parser

    # user requests to be called with a context, overwrite our main command (…)
    if with_context:
        def run(args):
            # (…) with something that creates a ProjectContext from the env/command line (…)
            context = ProjectContext(args.endpoint, args.project, args.keystore, args.preference,
                                     auth=args.auth, connection_pool_size=args.connection_pool_size,
                                     verify=args.verify)

            kwargs = {'context': context}
            if custom_parser:
                # (optionally add the parsed args to the passed arguments)
                kwargs.update(args=args)

            # (…) and calls the user's function with that context
            return with_context(**kwargs)

        # set the parser to be used to the one resulting in the user's function being called
        # add the custom parser as one of the parents of the resulting one to incorporate parsed user args
        using_parser = set_command(run, parents=[using_parser] if custom_parser else None)
        if not defaults.get('project') and not has_project(using_parser):
            # user did not supply an explicit project id to run(), we'll require it form the command line
            using_parser.add_argument('project', metavar='PROJECT',
                                      help='attach to project with id PROJECT')

    if with_multi_context:
        def run(args):
            # (…) with something that creates a MultiProjectContext from the env/command line (…)
            context = MultiProjectContext(args.endpoint, args.project, args.keystore, args.preference,
                                          auth=args.auth, connection_pool_size=args.connection_pool_size,
                                          verify=args.verify)

            kwargs = {'context': context}
            if custom_parser:
                # (optionally add the parsed args to the passed arguments)
                kwargs.update(args=args)

            # (…) and calls the user's function with that context
            return with_multi_context(**kwargs)

        # set the parser to be used to the one resulting in the user's function being called
        # add the custom parser as one of the parents of the resulting one to incorporate parsed user args
        using_parser = set_command(run, parents=[using_parser] if custom_parser else None)
        if not defaults.get('project') and not has_project(using_parser):
            # user did not supply an explicit project id to run(), we'll require it form the command line
            using_parser.add_argument('project', metavar='PROJECT', nargs='+',
                                      help='attach to project with id PROJECT')

    connection_kwarg = 'connection'
    if with_admin:
        warnings.warn('hansken.tool.run(with_admin=…) has been deprecated, use hansken.tool.run(with_connection=…) '
                      'instead', DeprecationWarning)
        connection_kwarg = 'admin'

    connection_callable = with_connection or with_admin
    # user requests to be called with connection, overwrite our main command (…)
    if connection_callable:
        def run(args):
            # (…) with something that creates a Connection from the env/command line (…)
            connection = Connection(args.endpoint, args.keystore, args.preference,
                                    auth=args.auth, connection_pool_size=args.connection_pool_size,
                                    verify=args.verify)

            kwargs = {connection_kwarg: connection}
            if custom_parser:
                # (optionally add the parsed args to the passed arguments)
                kwargs.update(args=args)

            # (…) and calls the user's function with that connection
            return connection_callable(**kwargs)
        # set the parser to be used to the one resulting in the user's function being called
        # add the custom parser as one of the parents of the resulting one to incorporate parsed user args
        using_parser = set_command(run, parents=[using_parser] if custom_parser else None)

    # parse args (defaults to sys.argv[1:]) using hansken_parser or something resulting in a user function being
    # called, exiting here if not satisfiable
    # pre-create the Namespace where arguments are stored, initialized to user defaults
    args = using_parser.parse_args(args, Namespace(**defaults))

    # create a log handler from parsed arguments, use it while running command
    with resolve_logging(args):
        # when certificate validation is disabled, attempt to disable the insecure warning (…)
        if not args.verify and not _disable_insecure_request_warning():
            # (…) but log when that fails
            log.warn('failed to disable InsecureRequestWarning in 3rd party package')

        if not isinstance(args.auth, HanskenAuthBase):
            # allow auth to be 'turned off' if explicitly set to False
            args.auth = None if args.auth is False else resolve_auth(args)

        try:
            # run action with the parsed arguments
            return args.run_command(args)
        except Exception as e:
            if error == 'exit' and not args.verbose:
                # calls to run with_* will likely have an empty command string, fall back to the parser's prog
                command = args.command or using_parser.prog
                command = command.strip()

                using_parser.exit(1, '\n{} failed: {}\n'.format(command, str(e)))
            else:
                # error == 'raise' or verbose mode, propagate error
                raise


# force adding commands from command sub-modules
# (note that a from ... import ... can't be used here as that would cause a circular import)
import hansken.tool.command_backup  # noqa: E402,F401,I100,I202
import hansken.tool.command_extract  # noqa: E402,F401
import hansken.tool.command_grant  # noqa: E402,F401
import hansken.tool.command_mount  # noqa: E402,F401
import hansken.tool.command_quickstart  # noqa: E402,F401
import hansken.tool.command_shell  # noqa: E402,F401
import hansken.tool.command_stats  # noqa: E402,F401
import hansken.tool.command_tasks  # noqa: E402,F401
import hansken.tool.command_tools  # noqa: E402,F401
import hansken.tool.command_upload  # noqa: E402,F401
import hansken.tool.command_versions  # noqa: E402,F401
