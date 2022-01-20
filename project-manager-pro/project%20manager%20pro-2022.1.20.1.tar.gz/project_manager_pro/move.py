import json
import os

from colorama import init, Style, Fore

from project_manager_pro._meta import cache_projects

init(autoreset=True)


def _move(name, destination):
    # load projects and get path to project with 'name'
    file = open(cache_projects, 'r', encoding='utf-8')
    projects = json.load(file)

    for type in projects:
        for project in projects[type]:
            if project['name'] == name or project['hash'] == name:

                destination_path = os.path.join(project['path'], '', '')

    print(Fore.RED + 'Project with \'' + name + '\' not found')