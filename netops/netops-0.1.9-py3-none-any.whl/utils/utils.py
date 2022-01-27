import json
import yaml
import os


def merge_dicts(dictionary):
    """ TODO translate to english 
    
    Recebe um dicionario de dicionarios e retorna um dicionario unico com chave valor, 
    onde valor nao e dicionario.
    
    Recebe:
            dictionary - dicionario de dicionarios.

    Retorna:
            merged_dict - dicionario com chave valor, onde valor nao e dicionario"""
    merged_dict = {}

    for key in dictionary:
        if type(dictionary[key]) is dict:
            merged_dict = {**merged_dict, **merge_dicts(dictionary[key])}
        else:
            merged_dict = {**merged_dict, **{key: dictionary[key]}}
    
    return merged_dict


def remove_item_list(list, item):
    """Recebe uma lista e um item a ser retirado da lista e retorna a lista sem o item.
    
    Recebe:
            list - lista

    Retorna:
            list - lista sem o item de entrada"""
    list.remove(item)
    return list


def print_json(input, file_path=None, mode='w'):
    """Recebe um dicionario de entrada (input var) e o caminho do arquivo JSON a ser gravado e printa
    o conteudo da entrada no arquivo caso exista. Em caso negativo printa em std_out.
    
    Recebe:
            input - dicionario a ser gravado no arquivo file_path caso exista
            file_path - caminho do arquivo a ser realizado o print do conteudo do dicionario de entrada"""

    if file_path is None:
        print(json.dumps(input, indent=4))
    else:
        print(
            json.dumps(input, indent=4), 
            file=open(file_path, mode)
        )

    return


def print_yaml(input, file_path=None):
    if file_path is None:
        print(yaml.dump(input))
    else:
        print(yaml.dump(input), file=open(file_path, "w"))

    return


def remove_empty_lines(filename):
    """Recebe o path de um arquivo e remove as linhas vazias
    
    Recebe:
            filename - path de um arquivo"""
    if not os.path.isfile(filename):
        print("{} does not exist ".format(filename))
        return
    with open(filename) as filehandle:
        lines = filehandle.readlines()

    with open(filename, 'w') as filehandle:
        lines = filter(lambda x: x.strip(), lines)
        filehandle.writelines(lines)  

    return