import yaml
from ..utils.utils import (
    remove_item_list, 
    merge_dicts
)


def get_infra_attribute(infra_dict, keys, search_str_in_key):
    """ TODO: write docstrings
    Obtem um atributo da infraestrutura a partir das chaves que caracterizam de onde 
    se trata esse atributo e uma string que filtra o tipo de atributo buscado.
    
    Recebe:
            infra_dict - dicionario que descreve a infraestrutura
            keys - lista de chaves que caracterizam de onde vem o atributo
            search_str_in_key - string para filtra a chave do atributo buscado

    Retorna:
            attribute - atributo da infraestrutura buscado"""
    key = keys[0]
    new_keys = remove_item_list(keys, key)
    if new_keys == []:
        for dict_key in infra_dict[key]:
            if search_str_in_key in dict_key:
                attribute = infra_dict[key][dict_key]
                return attribute
    else:
        attribute = get_infra_attribute(infra_dict[key], new_keys, search_str_in_key)
        return attribute


def import_infra_data(infra_file_path):
    """ TODO: write docstrings
    Recebe o caminho do arquivo de descricao da infraestrutura e retorna os objetos
    que descrevem a infraestrutura.
    
    Recebe:
            infra_file_path - nome do arquivo de descrivao de infraestrutura com extensao YAML,
            contendo as informacoes da infraestrutura associada a logica de negocio

    Retorna:
            infra_dicts - dicionario de dicionarios com a estrutura importada conforme arquivo de descricao
            infra - dicionario contendo chaves univocas, mas que descrevem integralmente a infraestrura"""
    arquivo_yaml = open(infra_file_path)
    infra_dicts = yaml.load(arquivo_yaml, Loader=yaml.CLoader)
    arquivo_yaml.close()
    
    infra = merge_dicts(infra_dicts)
    
    return infra, infra_dicts