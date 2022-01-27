import os

from .configs import ( 
    get_configs,
    describe_dev_config
)
from .models import config_descr
from ..utils.paths import CONFIG_ROOT_DIR
from ..infra.infra import (
    get_infra_attribute,
    import_infra_data
)


def config_generate(infra_file_path, config_context):
    """
    TODO: write docstrings
    
    Gera a descricao das alteracoes de configuracao por dispositivos a partir do arquivo de 
    descricao da infraestrutura e do contexto de configuracao.
    
    Recebe:
            infra_file_path - nome do arquivo de descrivao de infraestrutura com extensao YAML,
            contendo as informacoes da infraestrutura associada a logica de negocio
            config_context - contexto de geracao de configuracao
            
    Retorna:
            dev_config_description - objeto dicionario (config.models.config_descr) contendo a 
            descricao das alteracoes de configuracao associadas a cada dispositivo"""
    infra, infra_dicts = import_infra_data(infra_file_path)
    
    dev_config_description = config_descr()

    config_root_dir = CONFIG_ROOT_DIR + config_context + '/'

    for dirpath, dirnames, filenames in os.walk(config_root_dir):
        config_file_path, unconfig_file_path = False, False
                
        for file in filenames:
            if file == 'configure.j2':
                config_file_path = os.path.join(dirpath, file)
            elif file == 'unconfigure.j2':
                unconfig_file_path = os.path.join(dirpath, file)

        # Checa a existencia dos arquivos, pois pode entrar em diretorio que nao ha arquivos de configuracao (caso de ma configuracao)    
        if config_file_path or unconfig_file_path:
            dir_template_struct = dirpath.split(config_root_dir)[-1].split('/')
            fabricante_buscado = dir_template_struct[-1]
            dir_template_struct.remove(fabricante_buscado)
            dir_template_struct_2 = list(dir_template_struct)
            nome_dispositivo = get_infra_attribute(infra_dicts, dir_template_struct, 'nome')
            fabricante_dispositivo = get_infra_attribute(infra_dicts, dir_template_struct_2, 'fabricante')
    
            # Sempre deve haver arquivo de configuracao e por isso checa se ha arquivo de desconfiguracao
            if unconfig_file_path:
                dev_unconfig_type, dev_unconfig, dev_config_type, dev_config = get_configs(
                    infra, 
                    unconfig_path = unconfig_file_path, 
                    config_path = config_file_path
                )
        
                dev_full_config = describe_dev_config(
                    device=nome_dispositivo,
                    platform=fabricante_dispositivo,
                    configs=[
                        (dev_unconfig_type, dev_unconfig),
                        (dev_config_type, dev_config)
                    ]
                )
            else:
                dev_config_type, dev_config = get_configs(
                    infra, 
                    config_path = config_file_path
                )
        
                dev_full_config = describe_dev_config(
                    device=nome_dispositivo,
                    platform=fabricante_dispositivo,
                    configs=[
                        (dev_config_type, dev_config)
                    ]
                )
            dev_config_description['sequential'].append(dev_full_config)

    #TODO ADICIONAR INFORMACOES DE DESCONEXAO FISICA

    return dev_config_description