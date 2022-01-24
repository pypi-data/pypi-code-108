import os
import shutil

tests_catalog = 'tests'
inputs_catalog = os.path.join(tests_catalog, 'inputs')
outputs_catalog = os.path.join(tests_catalog, 'outputs')


# проверить наличие каталогов для тестов
def check_catalogs():
    if os.path.exists(tests_catalog) and os.path.exists(inputs_catalog) and os.path.exists(outputs_catalog):
        return True

    return False


# количество уже существующих тестов input
def amount_inputs_already_exists():
    inputs = len(os.listdir(inputs_catalog))

    return inputs


# количество уже существующих тестов output
def amount_outputs_already_exists():
    outputs = len(os.listdir(outputs_catalog))

    return outputs


# удалить все тесты
def cleartests():
    if os.path.exists('tests'):
        shutil.rmtree('tests')
        print('Все тесты успешно удалены.')
    else:
        print('Не найден каталог с тестами.')
        return 1

    os.mkdir(tests_catalog)
    os.mkdir(inputs_catalog)
    os.mkdir(outputs_catalog)


# добавить amount тестов
def addtest(amount):
    if not check_catalogs():
        print('ERROR addtest: не найден один из каталогов для файлов тестов')
        return 1

    already = max(amount_outputs_already_exists(), amount_inputs_already_exists())

    for i in range(already + 1, already + amount + 1, 1):
        with open(os.path.join(inputs_catalog, 'input_' + str(i) + '.txt'), 'w', encoding='utf-8') as file:
            file.write('')

        with open(os.path.join(outputs_catalog, 'output_' + str(i) + '.txt'), 'w', encoding='utf-8') as file:
            file.write('')

    print('Добавлено ' + str(amount) + ' тестов.')
