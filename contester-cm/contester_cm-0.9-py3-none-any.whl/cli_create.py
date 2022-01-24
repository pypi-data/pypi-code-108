import os


ERROR_TASK_ALREADY_EXISTS = 1
ERROR_CATALOG_NOT_FOUND = 2
ERROR_STATICFILES_NOT_COPYED = 3


# копирование статического файла с именем file_name в каталог destination
# должно соблюдаться условие, что файл и каталог существуют
def copy_static_file(file_name, destination):

    full_path = os.path.join(os.path.dirname(__file__), 'static', file_name)
    print('Копипрование файла ' + full_path + ' в каталог ' + destination)

    # создание каталога для готовых файлов
    if not os.path.exists(full_path):
        print('ERROR copy_static_file: файл ' + full_path + ' не существует')
        return 1

    if not os.path.exists(destination):
        print('ERROR copy_static_file: каталог ' + destination + ' не существует')
        return 2

    with open(full_path, encoding="utf-8") as file:
        lines = file.readlines()

    file = open(os.path.join(destination, os.path.basename(full_path)), "w", encoding="utf-8")

    for line in lines:
        file.write(line)

    file.close()


def create_task(name):
    path = '.'

    task_catalog = os.path.join(path, name)
    tests_catalog = os.path.join(task_catalog, 'tests')
    inputs_catalog = os.path.join(tests_catalog, 'inputs')
    outputs_catalog = os.path.join(tests_catalog, 'outputs')

    print('Создание новой задачи ' + name + '...')

    if name in os.listdir(path):
        print('ERROR cll_create: задача с именем ' + name + ' уже существует')
        return ERROR_TASK_ALREADY_EXISTS

    # создание нового каталога
    print('1. Создание каталога ' + name + ': ', end='')

    if os.path.exists(path):
        os.mkdir(task_catalog)
        print('OK')
    else:
        print('ERROR cll_create: не найден каталог ' + path)
        return ERROR_CATALOG_NOT_FOUND

    # копирование файлов
    print('2. Копирование файлов:')

    os.mkdir(tests_catalog)
    os.mkdir(inputs_catalog)
    os.mkdir(outputs_catalog)

    if copy_static_file(file_name='checker.cpp', destination=task_catalog):
        return ERROR_STATICFILES_NOT_COPYED

    if copy_static_file(file_name='statement.md', destination=task_catalog):
        return ERROR_STATICFILES_NOT_COPYED

    if copy_static_file(file_name='info.ini', destination=task_catalog):
        return ERROR_STATICFILES_NOT_COPYED

    if copy_static_file(file_name=os.path.join('tests', 'inputs', 'input_1.txt'), destination=inputs_catalog):
        return ERROR_STATICFILES_NOT_COPYED

    if copy_static_file(file_name=os.path.join('tests', 'outputs', 'output_1.txt'), destination=outputs_catalog):
        return ERROR_STATICFILES_NOT_COPYED

    print('OK')

    return 0
