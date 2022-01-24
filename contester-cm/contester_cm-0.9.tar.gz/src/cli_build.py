import os
import shutil

from .loader_md import load_md
from .prepare_md import prepare_md
from .make_html import make_html
from .make_xml import get_xml


def build_task(name):
    print('Формирование zip-архива задачи ' + name)

    # пути к файлам и каталогам задачи
    root = name
    statement_file = os.path.join(root, 'statement.md')
    info_file = os.path.join(root, 'info.ini')
    checker_file = os.path.join(root, 'checker.cpp')
    tests_catalog = os.path.join(root, 'tests')
    inputs_catalog = os.path.join(tests_catalog, 'inputs')
    outputs_catalog = os.path.join(tests_catalog, 'outputs')

    paths = [root, statement_file, info_file, checker_file, tests_catalog]
    for path in paths:
        if not os.path.exists(path):
            print('ERROR build_task: файл или каталог ' + path + ' не существует\n')
            return 1

    print('1. Загрузка statement.md: ', end='')
    md_data = load_md(statement_file=statement_file)
    print('OK')

    if md_data:

        print('2. Обработка statement.md: ', end='')
        prep_md = prepare_md(md_data)
        data = prep_md[0]
        tests = prep_md[1]
        print('OK')

        print('3. Подготовка информации для htm и xml файлов: ', end='')
        html = make_html(data=data, tests=tests)
        xml = get_xml(info_file=info_file)
        print('OK')

        print('4. Сохранение файлов: ', end='')
        destination_catalog = 'dist'
        if not os.path.exists(destination_catalog):
            os.mkdir(destination_catalog)

        dist_task_catalog = os.path.join(destination_catalog, name)
        dist_tests_catalog = os.path.join(dist_task_catalog, 'tests')

        if os.path.exists(dist_task_catalog):
            print('\nZip-файл задачи ' + name + ' уже существует. Он будет перезаписан.')
            shutil.rmtree(dist_task_catalog)
        os.mkdir(dist_task_catalog)

        # сохранение основных файлов
        with open(os.path.join(dist_task_catalog, 'statement.htm'), 'w', encoding='cp1251') as file:
            file.write(html)
        with open(os.path.join(dist_task_catalog, 'info.xml'), 'w', encoding='cp1251') as file:
            file.write(xml)
        shutil.copyfile(checker_file, os.path.join(dist_task_catalog, 'checker.cpp'))

        # сохранение тестов
        os.mkdir(dist_tests_catalog)
        for file in os.listdir(inputs_catalog):
            shutil.copyfile(os.path.join(inputs_catalog, file), os.path.join(dist_tests_catalog, os.path.basename(file)))

        for file in os.listdir(outputs_catalog):
            shutil.copyfile(os.path.join(outputs_catalog, file), os.path.join(dist_tests_catalog, os.path.basename(file)))
        print('OK')

        # сохранение копии исходных файлов
        print('5. Сохранении копии файлов задачи: ', end='')
        shutil.make_archive(name, 'zip', name)
        shutil.move(name + '.zip', dist_task_catalog)
        print('OK')

        # подготовка архива
        print('6. Подготовка zip-архива задачи: ', end='')
        shutil.make_archive(os.path.join('dist', name), 'zip', dist_task_catalog)
        shutil.rmtree(dist_task_catalog)
        print('OK')

    else:
        print('ERROR build_task: не удалось загрузить файл с описанием условий задачи - ' + statement_file)
        return 1

    return 0


def build(tasks):
    for task in tasks:
        build_task(task)
