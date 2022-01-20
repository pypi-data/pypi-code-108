import os
import time

from polidoro_argument import Command
from string import Template

from polidoro_terminal import clear_to_end_of_line, up_lines, cursor, erase_lines

from polidoro_cli import CLI


class Git(object):
    @staticmethod
    def _get_git_projects():
        for project_dir in sorted(os.listdir()):
            if os.path.isdir(project_dir):
                os.chdir(project_dir)
                if os.path.exists('.git'):
                    yield project_dir
                os.chdir('..')

    @staticmethod
    @Command(
        help='Run "git COMMAND" in all git projects',
        aliases=['a']
    )
    def in_all(*_remainder):
        try:
            pids = {}
            cursor.hide()
            command = ' '.join(_remainder)
            projects = list(Git._get_git_projects())
            for folder in projects:
                os.chdir(folder)
                pid = CLI.execute(f'git {command}',
                                  show_cmd=False, capture_output=True, exit_on_fail=False, sync=False)
                os.chdir('..')
                pids[folder] = pid
            stop = False
            running_status = ''
            while not stop:
                stop = True
                status = CLI.get_processes_status()
                if running_status == '...':
                    running_status = ''
                else:
                    running_status += '.'
                for folder in projects:
                    clear_to_end_of_line()
                    is_alive = status[pids[folder]]
                    print(f'Running "git {command}" in "{folder}"' + (running_status if is_alive else ' ✓'))
                    stop &= not is_alive
                if not stop:
                    up_lines(len(projects))
                time.sleep(0.1)

            erase_lines(len(projects))
            _, returns = CLI.wait_processes_to_finish()
            for folder, pid in pids.items():
                ret = returns[pid]
                output = ret['outs'] + ret['errs']
                if output:
                    print(folder)
                    print(output)
        finally:
            cursor.show()

    @staticmethod
    @Command(
        help='Commit helper',
        aliases=['bc']
    )
    def build_commit(*args, **kwargs):
        template = '''$type($scope): $short'''

        types = dict(
            build='Build related changes',
            ci='CI related changes',
            chore='Build process or auxiliary tool changes',
            docs='Documentation only changes',
            feat='A new feature',
            fix='A bug fix',
            perf='A code change that improves performance',
            refactor='A code change that neither fixes a bug or adds a feature',
            revert='Reverting things',
            style='Markup, white-space, formatting, missing semi-colons...',
            test='Adding missing tests',
        )

        dict_types = {}
        for i, (_type, desc) in enumerate(types.items()):
            if i > 9:
                i = chr(ord('A') - 10 + i)
            print(f'{i} - {_type}: {desc}')
            dict_types[str(i)] = _type

        _type = input('Type: ')
        if _type is None:
            return

        _type = dict_types[_type.upper()]

        scope = input('Scope: ')
        if not scope:
            template = template.replace('($scope)', '')

        short = input('Short Description: ')

        long = input('Long Description: ')
        if long:
            template += '\n\n$long'

        commit_message = Template(template).safe_substitute(
            type=_type,
            scope=scope,
            short=short,
            long=long
        )

        CLI.execute(f'git commit -m "{commit_message}"')
