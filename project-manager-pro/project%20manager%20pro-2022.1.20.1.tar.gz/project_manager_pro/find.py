import os
import json

from colorama import init, Style, Fore, Back

from project_manager_pro.hash_b import hash_4

from project_manager_pro._meta import cache_projects

init(autoreset=True)


def _find(path):

    # dict of projects by type ('active', 'template' etc)
    data = {}

    catalogs = os.listdir(path)

    catalogs = sorted(catalogs, key=lambda element: element)

    # find projects
    for catalog in catalogs:

        print(Fore.GREEN + 'Find in \'' + os.path.join(path, catalog) + '\':')

        if catalog not in data:
            data[catalog] = []

        projects = os.listdir(os.path.join(path, catalog))

        for project in projects:
            print('project \'' + Fore.CYAN + project + Style.RESET_ALL + '\' was found')

            # make hash
            temp_hash = str(hash_4(project + catalog))

            while len(temp_hash) < 4:
                temp_hash = '0' + temp_hash

            data[catalog].append({
                'name': project,
                'hash': temp_hash,
                'path': os.path.join(path, catalog, project)
            })

    # save data
    with open(cache_projects, 'w', encoding='utf-8') as file:
        file.write(json.dumps(data, ensure_ascii=False))

    if len(data) == 0:
        print(Fore.RED + 'Projects was not found')
