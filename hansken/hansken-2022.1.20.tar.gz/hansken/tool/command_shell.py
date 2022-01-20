# encoding=utf-8

from argparse import SUPPRESS
import warnings

from logbook import Logger

from hansken import __version__
from hansken.remote import Connection, ProjectContext
from hansken.tool import add_command


log = Logger(__name__)


try:
    from IPython import embed

    def shell(endpoint=None, project=None, keystore=None, preference=None, auth=None,
              verify=True, admin=False,
              **shell_locals):
        """
        Spawns an interactive shell. If an endpoint and project id are provided
        through args, a `ProjectContext <hansken.remote.ProjectContext>` instance
        is created attached to project at endpoint and exposed as local variable
        ``context``.

        :param endpoint: HTTP endpoint to a Hansken gatekeeper
        :param project: project identifier to create a context for
        :param keystore: HTTP endpoint to a Hansken keystore
        :param preference: HTTP endpoint to Hansken preference service
        :param auth: `HanskenAuthBase <hansken.auth.HanskenAuthBase>` instance to
            handle authentication, or `None`
        :param shell_locals: keyword arguments to expose as locals in the spawned
            shell
        """
        # construct multiline header
        header = ['Hansken interactive shell (client API version {})'.format(__version__)]

        if endpoint and 'connection' not in shell_locals:
            # provide a connection if not already provided as kwarg
            connection = Connection(endpoint, keystore, preference, auth=auth, verify=verify)
            shell_locals['connection'] = connection
        if admin:
            warnings.warn('use of admin in a shell has been deprecated, use connection',
                          DeprecationWarning)
        if project and 'connection' in shell_locals and 'context' not in shell_locals:
            # provide a project context if not already provided as kwarg (always created from pre-created Connection)
            context = ProjectContext(shell_locals['connection'], project)
            shell_locals['context'] = context

        # determine column width for shell locals dump
        maxlen = max(len(key) for key in shell_locals) if shell_locals else 0
        # add header lines for all shell locals, sorted by name
        header.extend('{name:<{len}} -> {value}'.format(name=name, len=maxlen, value=value)
                      for name, value in sorted(shell_locals.items()))
        # included to end banner with an empty line, like ipython itself
        header.append('')
        # start interactive session
        embed(banner2='\n'.join(header),  # print our info after the default ipython banner (including python version)
              user_ns=shell_locals,    # expose explicit locals created in shell_locals
              colors='neutral')  # work around an ipython colors bug (https://github.com/ipython/ipython/issues/11523)

    ipython_available = True
except ImportError as e:
    log.debug('shell command not available', e)
    ipython_available = False

    def shell(*args, **kwargs):
        shell_parser.error("command requires ipython, install hansken.py with the 'shell' extra or "
                           "install package 'ipython' manually")


help_text = 'spawn an interactive python shell'
if not ipython_available:
    help_text += ' (requires ipython to be installed)'


# define a command shell (ignore the return value, shell doesn't take additional arguments)
shell_parser = add_command('shell',
                           lambda args: shell(endpoint=args.endpoint,
                                              project=args.project,
                                              keystore=args.keystore,
                                              preference=args.preference,
                                              auth=args.auth,
                                              verify=args.verify,
                                              admin=args.admin),
                           help=help_text)
shell_parser.add_argument('-a', '--admin', dest='admin', action='store_true', default=False,
                          help=SUPPRESS)
