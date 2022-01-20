"""
Docker Dash CLI
"""
import argparse
import os
import subprocess
import sys


class ColorTag:
    RESET = '\x1b[0m'

    RED = '\x1b[5;31;40m'
    BLUE = '\x1b[5;34;40m'
    CYAN = '\x1b[5;36;40m'
    GRAY = '\x1b[5;37;40m'
    GREEN = '\x1b[5;32;40m'
    YELLOW = '\x1b[5;33;40m'

    ON_RED = '\x1b[5;30;41m'
    ON_BLUE = '\x1b[5;30;44m'
    ON_CYAN = '\x1b[5;30;46m'
    ON_GRAY = '\x1b[5;30;47m'
    ON_GREEN = '\x1b[5;30;42m'
    ON_YELLOW = '\x1b[5;30;43m'

    RED_ON_YELLOW = '\x1b[5;31;43m'
    BLUE_ON_YELLOW = '\x1b[3;34;43m'
    GRAY_ON_CYAN = '\x1b[3;37;46m'
    GRAY_ON_RED = '\x1b[3;37;41m'
    YELLOW_ON_RED = '\x1b[5;33;41m'
    YELLOW_ON_BLUE = '\x1b[5;33;44m'


class DDash:
    """
    `docker` and `docker-compose` cli tool, to specify and automatic apply with current work directory

    Setup following variable in you enviroment to make it permanently:

    + DDASH_TIMEOUT: Execute cli timeout [default is None(never timeout)]
    + DDASH_PROJECT_DELIMITER: Project delimiter for extracting prefix [default: '_'(underscore)]
    + DDASH_PROJECT_SPLIT_LIMIT: Project prefix word number for extracting prefix [default: 1]
    + DDASH_ROOT_PATH: Workspace [default: $HOME]
    + DDASH_SUB_PATH: Group directory combine with ROOT_PATH, `{PREFIX}` will be replace with porject prefix
    + DDASH_SATELLITE_SUFFIX: Satellite container name [default: service]
    + DDASH_COMPOSE_FILENAME: docker-compose filename [default: docker-compose.yml]
    + DDASH_DOCKER_EXEC_COMMAND: docker exec command [default: bash]
    """

    try:
        _TERMINAL_SIZE_WIDTH = os.get_terminal_size().columns
    except:
        _TERMINAL_SIZE_WIDTH = 90

    _DEFAULT_TABLE_FORMAT = 'table {{.ID}}\t{{.Names}}\t{{.Ports}}\t{{.Image}}'
    _TABLE_FORMAT = os.environ.get('DDASH_TABLE_FORMAT', _DEFAULT_TABLE_FORMAT)

    # default: None
    _TIMEOUT = os.environ.get('DDASH_TIMEOUT')
    # default: '_'
    _PROJECT_DELIMITER = os.environ.get('DDASH_PROJECT_DELIMITER', '_')
    # default: 1
    _PROJECT_SPLIT_LIMIT = int(os.environ.get('DDASH_PROJECT_SPLIT_LIMIT', 1))
    # default: "{$HOME}"
    _ROOT_PATH = os.path.expanduser(os.environ.get('DDASH_ROOT_PATH', '~'))
    # default: basename $PWD or Project {PREFIX}
    _SUB_PATH = os.environ.get('DDASH_SUB_PATH')
    # default: 'service'
    _SATELLITE_SUFFIX = os.environ.get('DDASH_SATELLITE_SUFFIX', 'service')
    # default: 'docker-comopse.yml'
    _COMPOSE_FILENAME = os.environ.get('DDASH_COMPOSE_FILENAME', 'docker-compose.yml')
    # default: 'docker-comopse.yml'
    _DOCKER_EXEC_COMMAND = os.environ.get('DDASH_DOCKER_EXEC_COMMAND', 'bash')

    @classmethod
    def _get_parser(cls):
        parser = argparse.ArgumentParser()
        action = parser.add_subparsers(description='List Subjects', dest='action')
        # ---------------- 檢視容器(List Running Container) ---------------- #
        ps = action.add_parser(
            'ps',
            help=('List running containers, format table and grep rows'),
        )
        ps.add_argument(
            'pattern',
            type=str,
            nargs='?',
            help='Combine grep command to searche pattern'
        )
        ps.add_argument(
            '-f', '--format',
            action='store',
            nargs='?',
            help=(
                f'Indicate or setup through `export DDASH_TABLE_FORMAT=\'YOUR_FORMAT\'` '
                f'[default: \'{cls._DEFAULT_TABLE_FORMAT}\']'
            ),
        )
        # ---------------- 啟動衛星服務(Launch Satellite Container) ---------------- #
        launch = action.add_parser(
            'launch',
            help=(
                'Launch satellite container through project {PREFIX} which is extract from `$PWD` or --project, '
                'combine {SUFFIX} to up a satellite container [default: {PREFIX}_service]'
            ),
        )
        launch.add_argument(
            'project',
            type=str,
            nargs='?',
            help='Indicate porject',
        )
        launch.add_argument(
            '--suffix',
            action='store',
            nargs='?',
            help='Indicate suffix of satellite container',
        )
        launch.add_argument(
            '--root',
            action='store',
            nargs='?',
            help='Indicate root dir or setup through `export DDASH_ROOT_PATH=\'YOUR_ROOT_PATH\'` [default: $HOME]',
        )
        launch.add_argument(
            '--sub',
            action='store',
            nargs='?',
            help='Indicate sub dir or setup through `export DDASH_SUB_PATH=\'YOUR_SUB_PATH\'`, use pattern \'{PREFIX}\' to apply with project prefix',
        )
        launch.add_argument(
            '--file',
            action='store',
            nargs='?',
            help='Indicate docker-compose filename or setup through `export DDASH_COMPOSE_FILENAME=\'YOUR_COMPOSE_FILENAME\'` [default: docker-compose.yml]',
        )
        launch.add_argument(
            '-a', '--attach',
            action='store_true',
            help='Indicate attach mode [default: False]',
        )
        # ---------------- 終止衛星服務(Terminate Satellite Container) ---------------- #
        terminate = action.add_parser(
            'terminate',
            help=(
                'Terminate satellite container through project {PREFIX} which is extract from `$PWD` or --project, '
                'combine {SUFFIX} to up a satellite container [default: {PREFIX}_service]'
            ),
        )
        terminate.add_argument(
            'project',
            type=str,
            nargs='?',
            help='Indicate porject',
        )
        terminate.add_argument(
            '--suffix',
            action='store',
            nargs='?',
            help='Indicate suffix of satellite container',
        )
        terminate.add_argument(
            '--root',
            action='store',
            nargs='?',
            help='Indicate root dir or setup through `export DDASH_ROOT_PATH=\'YOUR_ROOT_PATH\'` [default: $HOME]',
        )
        terminate.add_argument(
            '--sub',
            action='store',
            nargs='?',
            help='Indicate sub dir or setup through `export DDASH_SUB_PATH=\'YOUR_SUB_PATH\'`, use pattern \'{PREFIX}\' to apply with project prefix',
        )
        terminate.add_argument(
            '--file',
            action='store',
            nargs='?',
            help='Indicate docker-compose filename or setup through `export DDASH_COMPOSE_FILENAME=\'YOUR_COMPOSE_FILENAME\'` [default: docker-compose.yml]',
        )
        # ---------------- 啟動服務(Up Container) ---------------- #
        up = action.add_parser(
            'up',
            help=(
                'up container through project {PREFIX} which is extract from `$PWD` or --project, '
                'combine {SUFFIX} to up a satellite container [default: {PREFIX}_service]'
            ),
        )
        up.add_argument(
            'project',
            type=str,
            nargs='?',
            help='Indicate porject',
        )
        up.add_argument(
            '--root',
            action='store',
            nargs='?',
            help='Indicate root dir or setup through `export DDASH_ROOT_PATH=\'YOUR_ROOT_PATH\'` [default: $HOME]',
        )
        up.add_argument(
            '--sub',
            action='store',
            nargs='?',
            help='Indicate sub dir or setup through `export DDASH_SUB_PATH=\'YOUR_SUB_PATH\'`, use pattern \'{PREFIX}\' to apply with project prefix',
        )
        up.add_argument(
            '--file',
            action='store',
            nargs='?',
            help='Indicate docker-compose filename or setup through `export DDASH_COMPOSE_FILENAME=\'YOUR_COMPOSE_FILENAME\'` [default: docker-compose.yml]',
        )
        up.add_argument(
            '-a', '--attach',
            action='store_true',
            help='Indicate attach mode [default: False]',
        )
        # ---------------- 終止服務(Down Container) ---------------- #
        down = action.add_parser(
            'down',
            help=(
                'down container through project {PREFIX} which is extract from `$PWD` or --project, '
                'combine {SUFFIX} to up a satellite container [default: {PREFIX}_service]'
            ),
        )
        down.add_argument(
            'project',
            type=str,
            nargs='?',
            help='Indicate porject',
        )
        down.add_argument(
            '--root',
            action='store',
            nargs='?',
            help='Indicate root dir or setup through `export DDASH_ROOT_PATH=\'YOUR_ROOT_PATH\'` [default: $HOME]',
        )
        down.add_argument(
            '--sub',
            action='store',
            nargs='?',
            help='Indicate sub dir or setup through `export DDASH_SUB_PATH=\'YOUR_SUB_PATH\'`, use pattern \'{PREFIX}\' to apply with project prefix',
        )
        down.add_argument(
            '--file',
            action='store',
            nargs='?',
            help='Indicate docker-compose filename or setup through `export DDASH_COMPOSE_FILENAME=\'YOUR_COMPOSE_FILENAME\'` [default: docker-compose.yml]',
        )
        # ---------------- 執行服務(Exec Container) ---------------- #
        run = action.add_parser(
            'run',
            help=(
                'exec container with interactive tty mode through project {PREFIX} which is extract from `$PWD` or --project, '
                'combine {SUFFIX} to up a satellite container [default: {PREFIX}_service]'
            ),
        )
        run.add_argument(
            'project',
            type=str,
            nargs='?',
            help='Indicate porject',
        )
        run.add_argument(
            '-c', '--command',
            action='store',
            help='Indicate command or setup through `export DDASH_DOCKER_EXEC_COMMAND=\'YOUR_DOCKER_EXEC_COMMAND\'`',
        )
        return parser

    @classmethod
    def _print(cls, values, end='\n'):
        sys.stdout.write(f'{values}{end}')

    @classmethod
    def _show_doc(cls):
        cls._print(cls.__doc__)

    @classmethod
    def _stdout(cls, output, tag=None, end='\n'):
        header = str()
        if tag:
            badge = f' [{tag.upper()}] '
            header = f'{ColorTag.ON_CYAN}{badge:-^{cls._TERMINAL_SIZE_WIDTH}}{ColorTag.RESET}\n'
        cls._print(f'{header}{output}', end=end)

    @classmethod
    def _stderr(cls, output, tag=None, end='\n'):
        header = str()
        if tag:
            badge = f' [{tag.upper()}] '
            header = f'{ColorTag.ON_RED}{badge:-^{cls._TERMINAL_SIZE_WIDTH}}{ColorTag.RESET}\n'
        sys.stderr.write(
            f'{header}'
            f'{ColorTag.RED}{output}{ColorTag.RESET}{end}'
        )
        exit('Program has been terminated')

    @classmethod
    def _exec(cls, cmd):
        try:
            timeout = int(cls._TIMEOUT) if cls._TIMEOUT and cls._TIMEOUT.isdigit() else None
            output = subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT,
                shell=True,
                timeout=timeout,
                universal_newlines=True,
            )
        except subprocess.CalledProcessError as e:
            cls._stderr(output=e.output, tag='error')
        else:
            return output

    @classmethod
    def _ps(cls, args):
        format_ = args.format or cls._TABLE_FORMAT
        cmd = f'docker ps --format "{format_}"'
        if args.pattern:
            cmd = f'{cmd} | grep \'{args.pattern}\''
        stdout = cls._exec(cmd=cmd)
        cls._stdout(output=stdout)

    @classmethod
    def _extract_prefix(cls, project):
        if not isinstance(project, str) or not project:
            raise ValueError(f'Invalid value of _extract_prefix.project')
        data = project.split(cls._PROJECT_DELIMITER)[:cls._PROJECT_SPLIT_LIMIT]
        return f'{cls._PROJECT_DELIMITER}'.join(data)

    @classmethod
    def _get_satellite_project(cls, project, suffix):
        project = project or os.path.basename(os.getcwd())
        prefix = cls._extract_prefix(project=project)
        suffix = suffix or cls._SATELLITE_SUFFIX
        return f'{prefix}{cls._PROJECT_DELIMITER}{suffix}'

    @classmethod
    def _parse_sub_path(cls, pathname, project):
        results = list()
        pathname = pathname or cls._SUB_PATH
        home = os.path.expanduser('~')
        if '~' in pathname or home in pathname:
            cls._stderr(f'Detect invalid value ["~", "{home}"] from `DDASH_SUB_PATH` or `--sub`')
        if not pathname:
            return results
        prefix = cls._extract_prefix(project=project)
        for name in pathname.split('/'):
            temp = name.replace('{PREFIX}', prefix)
            results.append(temp)
        return results

    @classmethod
    def _launch(cls, args):
        satellite_project = cls._get_satellite_project(project=args.project, suffix=args.suffix)
        cls._print(
            f'{ColorTag.BLUE} {ColorTag.ON_BLUE} LAUNCH {ColorTag.YELLOW_ON_BLUE} {ColorTag.RESET}'
            f'{ColorTag.ON_YELLOW} {satellite_project} {ColorTag.YELLOW}{ColorTag.RESET}'
        )
        root_path = args.root or cls._ROOT_PATH
        sub_path = cls._parse_sub_path(pathname=args.sub, project=satellite_project)
        compose_filename = args.file or cls._COMPOSE_FILENAME
        satellite_project_pathname = os.path.join(root_path, *sub_path, satellite_project, compose_filename)
        cmd = f'docker-compose -f "{satellite_project_pathname}" up'
        if args.attach:
            subprocess.Popen(cmd, shell=True).wait()
        cmd = f'{cmd} -d'
        stdout = cls._exec(cmd=cmd)
        cls._stdout(output=stdout)

    @classmethod
    def _terminate(cls, args):
        satellite_project = cls._get_satellite_project(project=args.project, suffix=args.suffix)
        cls._print(
            f'{ColorTag.YELLOW}{ColorTag.ON_YELLOW} {satellite_project} {ColorTag.YELLOW_ON_RED} {ColorTag.RESET}'
            f'{ColorTag.ON_RED} CLOSE {ColorTag.RED}  {ColorTag.RESET}'
        )
        root_path = args.root or cls._ROOT_PATH
        sub_path = cls._parse_sub_path(pathname=args.sub, project=satellite_project)
        compose_filename = args.file or cls._COMPOSE_FILENAME
        satellite_project_pathname = os.path.join(root_path, *sub_path, satellite_project, compose_filename)
        cmd = f'docker-compose -f "{satellite_project_pathname}" down'
        stdout = cls._exec(cmd=cmd)
        cls._stdout(output=stdout)

    @classmethod
    def _up(cls, args):
        if not args.project:
            project = os.path.basename(os.getcwd())
            cmd = f'docker-compose up'
        else:
            project = args.project
            root_path = args.root or cls._ROOT_PATH
            sub_path = cls._parse_sub_path(pathname=args.sub, project=project)
            compose_filename = args.file or cls._COMPOSE_FILENAME
            project_pathname = os.path.join(root_path, *sub_path, project, compose_filename)
            cmd = f'docker-compose -f "{project_pathname}" up'
        cls._print(
            f'{ColorTag.GRAY}{ColorTag.ON_GRAY}   {project} {ColorTag.GRAY_ON_CYAN}  {ColorTag.RESET}'
            f'{ColorTag.ON_CYAN}{"UP":^10}{ColorTag.CYAN} {ColorTag.RESET}'
        )
        if args.attach:
            subprocess.Popen(cmd, shell=True).wait()
        cmd = f'{cmd} -d'
        stdout = cls._exec(cmd=cmd)
        cls._stdout(output=stdout)

    @classmethod
    def _down(cls, args):
        if not args.project:
            project = os.path.basename(os.getcwd())
            cmd = f'docker-compose down'
        else:
            project = args.project
            root_path = args.root or cls._ROOT_PATH
            sub_path = cls._parse_sub_path(pathname=args.sub, project=project)
            compose_filename = args.file or cls._COMPOSE_FILENAME
            project_pathname = os.path.join(root_path, *sub_path, project, compose_filename)
            cmd = f'docker-compose -f "{project_pathname}" down'
        cls._print(
            f'{ColorTag.GRAY}{ColorTag.ON_GRAY}   {project} {ColorTag.GRAY_ON_RED}  {ColorTag.RESET}'
            f'{ColorTag.ON_RED}{"DOWN":^10}{ColorTag.RED} {ColorTag.RESET}'
        )
        stdout = cls._exec(cmd=cmd)
        cls._stdout(output=stdout)

    @classmethod
    def _run(cls, args):
        project = args.project or os.path.basename(os.getcwd())
        command = args.command or cls._DOCKER_EXEC_COMMAND
        cmd = f'docker exec -it {project} {command}'
        os.system('clear')
        print (
            f'{"  CONTAINER ":^{cls._TERMINAL_SIZE_WIDTH}}\n'
            f'{ColorTag.BLUE} {ColorTag.ON_BLUE} EXEC {ColorTag.BLUE_ON_YELLOW} {ColorTag.RESET}'
            f'{ColorTag.ON_YELLOW}   {project} {ColorTag.YELLOW}  {ColorTag.RESET}'
        )
        subprocess.Popen(cmd, shell=True).wait()

    @classmethod
    def cli(cls):
        parser = cls._get_parser()
        if len(sys.argv) == 1:
            cls._show_doc()
            parser.print_help()
        args = parser.parse_args()
        if args.action == 'ps':
            cls._ps(args=args)
            parser.exit()
        if args.action == 'launch':
            cls._launch(args=args)
            parser.exit()
        if args.action == 'terminate':
            cls._terminate(args=args)
            parser.exit()
        if args.action == 'up':
            cls._up(args=args)
            parser.exit()
        if args.action == 'down':
            cls._down(args=args)
            parser.exit()
        if args.action == 'run':
            cls._run(args=args)
            parser.exit()


if __name__ == '__main__':
    DDash.cli()

