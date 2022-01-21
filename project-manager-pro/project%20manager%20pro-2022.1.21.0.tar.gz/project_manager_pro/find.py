import os
import json

from colorama import init, Style, Fore, Back

from project_manager_pro.hash_b import hash_4

from project_manager_pro._meta import cache_projects, cache_types

init(autoreset=True)


def _find(path):

    # dict of projects by type ('active', 'template' etc)
    data = {}

    # список каталогов, в которых хранятся проекты - далее они называются разделы
    # основная идея в том, что проекты делятся на активные, неактивные, временные, шаблоны и т.д..
    # это определяется тем, в каком разделе лежит проект
    catalogs = os.listdir(path)

    catalogs = sorted(catalogs, key=lambda element: element)

    # список разделов с путями к ним
    types = {}

    # обработка проектов в разделах
    for catalog in catalogs:

        types[catalog] = os.path.join(path, catalog)

        print(Fore.GREEN + 'In the catalog \'' + os.path.join(path, catalog) + '\':')

        if catalog not in data:
            data[catalog] = []

        # список проектов в разделе
        projects = os.listdir(os.path.join(path, catalog))

        if len(projects) == 0:
            print(Fore.RED + 'projects not found')

        for project in projects:
            print(Fore.CYAN + project)

            # make hash
            temp_hash = str(hash_4(project + catalog))

            while len(temp_hash) < 4:
                temp_hash = '0' + temp_hash

            data[catalog].append({
                'name': project,
                'hash': temp_hash,
                'path': os.path.join(path, catalog, project),
            })

    # save data
    with open(cache_projects, 'w', encoding='utf-8') as file:
        file.write(json.dumps(data, ensure_ascii=False))

    with open(cache_types, 'w', encoding='utf-8') as file:
        file.write(json.dumps(types, ensure_ascii=False))

    if len(data) == 0:
        print(Fore.RED + 'Projects was not found')
