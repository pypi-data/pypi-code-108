import copy
import os
import re
import sys
from argparse import SUPPRESS
from collections import defaultdict
from multiprocessing import Process, Pipe
from string import Template
from subprocess import Popen, PIPE

from polidoro_argument import Command
from polidoro_argument.polidoro_argument_parser import DEFAULT_COMMAND


class CLI:
    """
    Class to create CLI commands
    """
    _processes = []
    _parent_conn, _child_conn = Pipe()

    @staticmethod
    def create_file_commands(full_path):  # noqa: C901
        """
        Create commands reading from file
        """
        file = full_path.split('/')[-1]
        clazz_name = file.split('.')[0].title()
        clazz = getattr(sys.modules.get(clazz_name.lower(), None), clazz_name, None)
        if clazz is None:
            clazz = type(clazz_name, (object,), {})

        if not hasattr(clazz, 'help'):
            setattr(clazz, 'help', clazz.__qualname__ + ' CLI commands')

        local_vars = dict(vars={}, envs={})
        read_dict = False
        name = None
        command = ""
        with open(full_path, 'r', newline='') as file:
            for line in file.readlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    # set local variables defined in .cli file with `set VAR`
                    if line.startswith('set '):
                        local_var, _, value = line.replace('set ', '').partition('=')
                        if local_var == 'DEFAULT_COMMAND':
                            setattr(clazz, DEFAULT_COMMAND, value)
                            CLI._create_command(
                                DEFAULT_COMMAND,
                                value,
                                clazz,
                                help=SUPPRESS,
                                show_cmd=False,
                                **local_vars
                            )
                        else:
                            local_vars['vars'][local_var] = value
                    elif line.startswith('export '):
                        env_var, _, value = line.replace('export ', '').partition('=')
                        local_vars['envs'][env_var] = value
                        os.environ[env_var] = value
                    elif read_dict:
                        command += line
                        read_dict = CLI._create_evaluated_command(clazz, command, local_vars, name)
                    else:
                        name, _, command = line.partition('=')
                        if command.startswith('{'):
                            read_dict = CLI._create_evaluated_command(clazz, command, local_vars, name)
                        else:
                            final_command = []
                            for cmd in command.split(';'):
                                if hasattr(clazz, DEFAULT_COMMAND):
                                    cmd = f'{getattr(clazz, DEFAULT_COMMAND)} {cmd}'
                                final_command.append(cmd)
                            CLI._create_command(name, ';'.join(final_command), clazz, **local_vars)

    @staticmethod
    def _create_evaluated_command(clazz, command, local_vars, name):
        try:
            command_dict = eval(command)
            command = command_dict.pop('command')
            command_local_vars = copy.deepcopy(local_vars)
            command_local_vars['envs'].update(command_dict.pop('envs', {}))
            CLI._create_command(name, command, clazz, **command_dict, **command_local_vars)
            return False
        except SyntaxError:
            return True

    @staticmethod
    def _create_command(name, command, clazz, show_cmd=True, help=None,
                        messages=None,
                        **local_vars):
        run_cmd = getattr(clazz, 'get_cmd_method', CLI._get_cmd_method)(
            command,
            clazz,
            show_cmd=show_cmd,
            messages=messages,
            **local_vars)
        aliases = name.replace(' ', '').split(',')
        name = aliases.pop(0)
        # Parser full name
        setattr(run_cmd, '__qualname__', '%s.%s' % (clazz.__qualname__, name))
        # Command name
        setattr(run_cmd, '__name__', name)
        # Command class
        setattr(run_cmd, '__objclass__', clazz)
        if help is None:
            help = f'Run "{command}"'.replace('%', '%%')
        Command(help=help, aliases=aliases)(run_cmd)

    @staticmethod
    def _get_cmd_method(command, clazz, show_cmd=True, exit_on_fail=True, messages=None, **local_vars):  # noqa: C901
        if messages is None:
            messages = {}

        def print_if_has_message(message_key):
            if message_key in messages:
                print(messages[message_key])

        def run_cmd_method(*_remainder, docker=False):
            if docker is None:
                docker = True
            docker_class = getattr(sys.modules['docker'], 'Docker', None)
            interceptors = []
            substituted_command = Template(command).safe_substitute(**local_vars['vars'])
            interceptors_kwargs = {}
            if docker_class:
                if docker:
                    # If the argument --docker/-d in arguments, replace "$docker" (if exists) in command
                    interceptors.append(docker_class.command_interceptor)
                    substituted_command = Template(substituted_command).safe_substitute(
                        docker='docker-compose exec $service',
                    )
                    # Include environments variables to docker-compose call
                    interceptors_kwargs.update(local_vars['envs'])
                    if isinstance(docker, str):
                        interceptors_kwargs['service'] = docker
                else:
                    substituted_command = Template(substituted_command).safe_substitute(
                        docker=''
                    )

            if hasattr(clazz, 'command_interceptor'):
                interceptors.append(clazz.command_interceptor)

            for interceptor in interceptors:
                substituted_command, _remainder = interceptor(substituted_command, *_remainder, **interceptors_kwargs)

            if '$args' in substituted_command:
                substituted_command = Template(substituted_command).safe_substitute(args=' '.join(_remainder))
                _remainder = ()

            args_to_substitute = {}
            while '${arg' in substituted_command:
                arg_default_regex = r'\$\{(arg\d*:.*)\}'
                for arg_with_default in re.search(arg_default_regex, substituted_command).groups():
                    arg, default = arg_with_default.split(':')
                    args_to_substitute[arg] = default
                    substituted_command = re.sub(arg_default_regex, f'${arg}', substituted_command)
            arg_i = 0
            for arg in _remainder:
                arg_key = f'arg{arg_i}'
                if f'${arg_key}' in substituted_command:
                    args_to_substitute[arg_key] = arg
                else:
                    break
                arg_i += 1
            _remainder = tuple(list(_remainder)[arg_i:])
            substituted_command = Template(substituted_command).safe_substitute(**args_to_substitute)

            print_if_has_message('start')
            try:
                for cmd in substituted_command.split(';'):
                    cmd = cmd.replace('  ', ' ').strip()
                    compiled = compile_command(cmd, *_remainder)
                    run_command(compiled)
            except SystemExit as se:
                if se.code:
                    print_if_has_message('error')
                print_if_has_message('finish')

        def compile_command(cmd, *_remainder):
            cmd = cmd.strip()
            _for = re.search(r'(.*) for (\w+) in (.*)', cmd)
            if _for:
                for_cmd = _for.groups()[0]
                for_var = _for.groups()[1]
                for_in = _for.groups()[2]

                # Replacing for var for '%s'
                for_cmd = ' '.join(['$for_var' if c == for_var else c for c in for_cmd.split()] + list(_remainder))
                return eval('[Template(\'' + for_cmd + '\').safe_substitute(for_var=' + for_var + ') for ' +
                            for_var + ' in ' + for_in + ']')
            elif cmd.lower().startswith('run'):
                cmds = re.search('run(.*)in(.*)done', cmd).groups()
                return 'cd %s; %s; cd..' % (cmds[1], cmds[0])
            else:
                return ' '.join([cmd] + list(_remainder))

        def run_command(cmd):
            if isinstance(cmd, list):
                for c in cmd:
                    run_command(c)
            elif isinstance(cmd, str):
                if cmd.lower().startswith('cd'):
                    os.chdir(os.path.expanduser(cmd[2:].strip()))
                else:
                    CLI.execute(cmd, show_cmd=show_cmd, exit_on_fail=exit_on_fail)
            else:
                print_if_has_message('error')
                raise Exception

        # method without "docker" argument
        def run_docker_cmd_method(*_remainder):
            run_cmd_method(*_remainder)

        if clazz.__name__ == 'Docker':
            return run_docker_cmd_method
        else:
            setattr(run_cmd_method, 'arguments_aliases', {'docker': 'd'})
            return run_cmd_method

    @staticmethod
    def execute(command, exit_on_fail=True, capture_output=False, show_cmd=True, sync=True):
        """
        Run a shell command

        :param command: command as string
        :param exit_on_fail: If True, exit script if command fails
        :param capture_output: Return the command output AND not print in terminal
        :param show_cmd: Show command in terminal
        :param sync: If runs the command synchronously
        :return: subprocess.CompletedProcess
        """
        if show_cmd:
            print('+ %s' % command.strip())

        if capture_output:
            std = PIPE
        else:
            std = None

        p = CLI.start_process(command, std)
        if sync:
            error, returns = CLI.wait_processes_to_finish()
            ret = list(returns.values())[0]

            if exit_on_fail and error:
                exit(error)
            return ret['outs'], ret['errs']
        return p.pid

    @staticmethod
    def start_process(command, std):
        def async_run(conn, _command, _std):
            proc = Popen('exec ' + _command, shell=True, text=True, stdout=_std, stderr=_std)
            try:
                outs, errs = proc.communicate()
            except KeyboardInterrupt:
                proc.terminate()
                print('Waiting until process terminate')
                proc.wait()
                outs, errs = proc.communicate()
                proc.returncode = 1

            conn.send([os.getpid(), bool(proc.returncode), outs, errs])

        p = Process(target=async_run, args=(CLI._child_conn, command, std))
        CLI._processes.append(p)
        p.start()
        return p

    @staticmethod
    def wait_processes_to_finish():
        returns = defaultdict(dict)
        error = False
        while CLI._processes:
            p = CLI._processes.pop()
            p.join()
            p_pid, c_error, c_outs, c_errs = CLI._parent_conn.recv()
            returns[p_pid] = dict(error=c_error, outs=c_outs, errs=c_errs)
            error |= c_error

        return error, returns

    @staticmethod
    def get_processes_status():
        status = {}
        for p in CLI._processes:
            status[p.pid] = p.is_alive()
        return status


@Command(help='Create suggested aliases')
def create_aliases(*args):  # noqa: C901
    aliases = {k: f'cli {v}' for k, v in dict(
        dk='docker',
        dj='django',
        ex='elixir',
        rb='ruby',
        g='git',
        npm='npm',
        py='python',
        ssh='ssh',
        psql='postgres'
    ).items()}
    aliases_alias = dict()
    if args:
        aux_sub_aliases = {}

        sub_aliases = {}
        for cli, cli_alias in aliases.items():
            for sub_a in aux_sub_aliases.get(cli_alias.replace('cli ', ''), [])[:]:
                sub_aliases[f'{aliases_alias.get(cli, cli)}{sub_a}'] = f'{cli} {sub_a}'
        aliases.update(sub_aliases)

    bashrc_filename = os.path.expanduser('~/.bashrc')
    cli_aliases_filename = '~/.cli_aliases'
    with open(bashrc_filename, 'r') as bashrc_file:
        read = bashrc_file.read()
        if cli_aliases_filename not in read:
            with open(bashrc_filename, 'a+') as bashrc_file_write:
                print(f'Creating import "{cli_aliases_filename}" in {bashrc_filename}')
                bashrc_file_write.write(f'''
# include polidoro_cli_aliases if it exists
if [[ -f {cli_aliases_filename} ]]; then
    . {cli_aliases_filename}
fi
''')

    custom_aliases = {}
    already_created = []
    cli_aliases_filename = os.path.expanduser(cli_aliases_filename)
    if os.path.exists(cli_aliases_filename):
        with open(cli_aliases_filename, 'r') as cli_aliases_file:
            for line in cli_aliases_file.readlines():
                line = line.strip()
                if '=' in line:
                    alias, _, cmd = line.replace('alias ', '').partition('=')
                    if alias in aliases:
                        already_created.append(alias)
                    else:
                        custom_aliases[alias] = cmd.replace('\'', '')

    aliases.update(custom_aliases)
    created = False
    with open(cli_aliases_filename, 'w+') as cli_aliases_file:
        for alias, cmd in aliases.items():
            bash_alias = f'{alias}=\'{cmd}\''
            if alias not in already_created and alias not in custom_aliases:
                created = True
                print(f'Creating alias {bash_alias}')
            cli_aliases_file.write(f'alias {bash_alias}\n')
        if created:
            print('Run "source ~/.bashrc" to load the aliases')
