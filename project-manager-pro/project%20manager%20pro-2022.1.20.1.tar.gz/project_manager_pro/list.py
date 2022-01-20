import json

from project_manager_pro._meta import cache_projects
from colorama import init, Style, Fore, Back

init(autoreset=True)


def _list(long):
    with open(cache_projects, 'r', encoding='utf-8') as file:
        projects = json.load(file)

    for type in projects:

        # make sorted array
        len_hash = 0
        len_name = 0

        sorted_projects = []

        for project in projects[type]:

            len_hash = max(len_hash, len(project['hash']))
            len_name = max(len_name, len(project['name']))

            sorted_projects.append([project['hash'], project['name']])

        sorted_projects = sorted(sorted_projects, key=lambda element: element[1])

        # print projects of type 'type'
        format_hash = '%-' + str(len_hash + 15) + 's'

        print(Style.BRIGHT + Fore.GREEN + type)

        for project in sorted_projects:
            project_hash = Style.BRIGHT + Fore.RED + str(project[0])
            project_name = Fore.BLUE + project[1]

            print(format_hash % project_hash, end='')
            print(project_name)

        print('')
