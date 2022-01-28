import yaml

from ..utils.template_rendering import J2Template
from .models import (
    config_dev,
    config_data
)

def get_dev_config(infra, config_path):
    """Obtem as configuracoes a serem executadas em um dispositivo baseado no template de configuracao de entrada (config_path).
    
    Recebe:
            infra = Dicionario que contem as informacoes relativas a infraestrutura para ativacao do novo circuito
            config_path = Path do template de configuracao do dispositivo
    Retorna:
            (
                config_type = Tipo de configuracao do dispositivo
                config_data = Dados de configuracao do dispositivo
            )"""
    template_configure = J2Template(config_path)
    config_data = yaml.load(
        template_configure.template.render(**infra),
        Loader=yaml.loader.SafeLoader
    )
    config_data = config_data.splitlines()
    config_type = config_data[0].split('{')[1].split('}')[0].replace(' ', '')
    config_data.pop(0)
    new_config_data = []
    for item in config_data:
        if item == '':
            continue
        else:
            new_config_data.append(item)
    if config_type == 'procedural':
        config_data = new_config_data
    elif config_type == 'json-rpc':
        config_data = ' '.join(new_config_data)

    return config_type, config_data


def get_configs(infra, unconfig_path=None, config_path=None):
    """
	TODO: translate to English

    Obtem as configuracoes a serem executadas nos dispositivos baseado nos templates de configuracao.
    
    Recebe:
            infra = Dicionario que contem as informacoes relativas a infraestrutura para ativacao do novo circuito
            unconfig_path = Path do template de desconfiguracao do dispositivo
            config_path = Path do template de configuracao do dispositivo
    Retorna:
            (
                unconfig_type = Tipo de desconfiguracao do dispositivo,
                unconfig_data = Dados de desconfiguracao do dispositivo,
                config_type = Tipo de configuracao do dispositivo,
                config_data = Dados de configuracao do dispositivo
            )"""
    if unconfig_path is not None:
        unconfig_type, unconfig_data = get_dev_config(infra, unconfig_path)
    
    if config_path is not None:
        config_type, config_data = get_dev_config(infra, config_path)

    if unconfig_path is not None and config_path is not None:
        return unconfig_type, unconfig_data, config_type, config_data
    elif config_path is not None:
        return config_type, config_data
    elif unconfig_path is not None:
        return unconfig_type, unconfig_data


def describe_dev_config(device=None, platform=None, configs=None):
    """
    TODO: translate to English

    Descreve os procedimentos de alteracao de configuracao por dispositivo.
    
    Recebe:
        device: nome do dispositivo, conforme utilizado pelo gestor de inventario
        platform: nome do fabricante do dispositivo
        configs: lista de tuplas contendo as configuracoes do tipo (.choices.ConfigType, config steps)
        
    Retorna:
        dev_config: Objeto .models.config_dev"""

    dev_config = config_dev()
    dev_config['device_name'] = device
    dev_config['platform'] = platform

    for configuration in configs:
        data_config = config_data()
        data_config['type'] = configuration[0]
        data_config['content'] = configuration[1]

        dev_config['configuration'].append(data_config)

    return dev_config