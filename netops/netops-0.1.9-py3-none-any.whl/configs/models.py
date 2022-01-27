def config_descr():
    """ TODO: write docstrings
    Retorna o Objeto de descricao de alteracoes de configuracoes sobre a infraestrutura, onde:
        * 'sequential': lista de Objetos config_dev, onde as configuracoes sao aplicadas somente ao final da ultima configuracao
        * 'parallel': lista de Objetos config_dev, onde as configuracoes sao aplicadas em todos os dispositivos de forma paralela"""
    obj = { 
        'sequential': [],
        'parallel': []
    }

    return obj


def config_dev():
    """ TODO: write docstrings
    Retorna o Objeto de descricao de alteracoes de configuracoes em um dispositivo, onde:
        * 'device_name' : nome do dispositivo que sofrera as alteracoes (deve ter o mesmo nome utilizado no gestor de inventario)
        * 'platform': fabricante do dispositivo
        * 'configuration': lista de Objetos config_data"""
    obj =  {
        'device_name': None,
        'platform': None,
        'configuration': []
    }

    return obj


def config_data():
    """ TODO: write docstrings
    Retorna o Objeto de descricao de dados de alteracoes de configuracoes, onde:
        * 'type': tipo da configuracao descrita, de acordo com as opcoes do objeto .choices.ConfigType
        * 'content': instrucoes de alteracao de configuracao
        * 'metadata': metadados diversos
        * 'metadata.commited': ultimo estado da configuracao aplicada, nok nao aplicada ainda"""
    obj = {
        "type": None,
        'content': None,
        "metadata": {
            "commited": "nok"
        }
    }

    return obj