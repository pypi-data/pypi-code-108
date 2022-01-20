import json
import os

from colorama import init, Style, Fore

from project_manager_pro._meta import cache_commands, cache_projects

init(autoreset=True)


def _exec(alias, name):

    # loading command
    file = open(cache_commands, 'r', encoding='utf-8')
    commands = json.load(file)

    if alias in commands:
        command = commands[alias]
    else:
        print(Fore.RED + 'Command with alias \'' + alias + '\' not found')
        return

    # loading project
    file = open(cache_projects, 'r', encoding='utf-8')
    data = json.load(file)

    for type in data:
        for project in data[type]:
            if project['name'] == str(name) or str(project['hash']) == str(name):
                command = command.replace('$', project['path'])

                print(Fore.GREEN + 'run ' + Fore.CYAN + command)
                os.system(command)
                return


    print(Fore.RED + 'Project with name (hash) \'' + str(name) + '\' not found')
