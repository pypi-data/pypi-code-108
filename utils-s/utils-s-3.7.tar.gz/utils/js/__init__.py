import json


def write_new_js(data, file_name):
    with open('{}.json'.format(file_name), 'w+') as file:
        file.seek(0)
        json.dump(data, file, indent=4)


def open_load_file(file_name):
    file = open('{}.json'.format(file_name), 'r+')
    return json.load(file), file


def update_dict(data, file_name):
    with open('{}.json'.format(file_name), 'r+') as file:
        JsF = json.load(file)
        JsF.update(data)

        file.seek(0)
        json.dump(JsF, file, indent=4)
        file.close()


def dump_js_to_file(file, Js):
    file.seek(0)
    json.dump(Js, file, indent=4)


def append_to_list(list_key, file_name, list_data_append):
    s = open_load_file(file_name)

    Js = s[0]
    file = s[1]

    Js[list_key].append(list_data_append)
    dump_js_to_file(file=file, Js=Js)


def get_values_list(file_name, key=None):
    s = open_load_file(file_name)
    Js = s[0]

    if key is not None:
        return Js[key]
    else:
        return Js


def waste():
    pass
