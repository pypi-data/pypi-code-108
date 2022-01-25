import json
from jsonpath_ng import parse

from whizbang.domain.models.json_serializable import JsonSerializable


def import_local_json(file_path: str):
    file = open(file_path)
    j_object = json.load(file)
    file.close()
    return j_object


def export_local_json(file_path: str, t_object: JsonSerializable) -> None:
    file = open(file_path, 'w+')
    file.write(t_object.to_json())
    file.close()


def export_json_dict(file_path: str, t_object: dict) -> None:
    file = open(file_path, 'w+')
    file.write(json.dumps(t_object))
    file.close()


def __check_add_dollar_sign(expression_string: str):
    if expression_string[:2] == '$.':
        return expression_string
    return f'$.{expression_string}'


def __jsonpath_find(json_data: dict, expression_string: str):
    expression_string = __check_add_dollar_sign(expression_string)
    jsonpath_expression = parse(expression_string)
    match = jsonpath_expression.find(json_data)

    if match.__len__() == 0:
        return None
    return match[0].value


def jsonpath_parse(json_data: dict, expression_string: str):
    match = __jsonpath_find(json_data, expression_string)
    return match


def jsonpath_parse_string(json_string: str, expression_string: str):
    json_data = json.loads(json_string)
    match = __jsonpath_find(json_data, expression_string)
    return match


def jsonpath_set(json_data: dict, expression_string: str, new_value: any) -> dict:
    expression_string = __check_add_dollar_sign(expression_string)
    jsonpath_expression = parse(expression_string)
    # not sure if this is needed
    # jsonpath_expression.find(json_data)
    jsonpath_expression.update(json_data, new_value)
    return json_data


def update_json_values(new_values: dict, existing_dictionary: dict):
    for key in new_values:
        jsonpath_set(json_data=existing_dictionary, expression_string=key, new_value=new_values[key])
