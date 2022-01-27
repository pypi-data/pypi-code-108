import logging
from datetime import datetime
from os import path
from src.api import oking
import sys
import src.api.okvendas as api_okvendas
from src.entities.log import Log

global is_connected_oracle_client, client_data, start_time

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s][%(asctime)s] %(message)s',
                    datefmt='%Y-%m-%d %I:%M:%S')
logger = logging.getLogger()


def print_version():
    f = open(path.abspath('version.txt'), 'r')
    v = f.read()
    print(v)
    f.close()
    exit(0)


def get_token_from_params(args: list) -> (str, bool):
    if len(args) >= 2:
        if args[1] == '--version':
            print_version()

        if len(args) >= 3 and args[2] == '--dev':
            return args[1], True

        return args[1], False
    else:
        logger.error('Informe o token da integracao como parametro')
        exit(1)


token_oking, is_dev = get_token_from_params(sys.argv)

start_time = datetime.now().isoformat()
logger.info('Iniciando oking __init__')
logger.info(f'Ambiente: {"Dev" if is_dev else "Prod"}')
if not is_dev:
    # Consultar dados da integracao do cliente (modulos, tempo de execucao, dados api okvendas)
    client_data = oking.get(f'https://appbuilder.openk.com.br/api/consulta/integracao_oking/filtros?token={token_oking}', None)
    api_okvendas.post_log(Log(f'Oking inicializando {client_data["integracao_id"]}', datetime.now().isoformat(), '', 'INICIALIZACAO'))
else:
    # Consultar dados da integracao do cliente em ambiente node-red local
    client_data = oking.get(f'http://127.0.0.1:1880/api/consulta/integracao_oking/filtros', None)
    api_okvendas.post_log(Log(f'Oking inicializando cliente id {client_data["integracao_id"]}', datetime.now().isoformat(), '', 'INICIALIZACAO'))


if client_data is not None:
    assert client_data['integracao_id'] is not None, 'Id da integracao nao informado (Api Oking)'
    assert client_data['db_type'] is not None, 'Tipo do banco de dados nao informado (Api Oking)'
    assert client_data['host'] is not None, 'Host do banco de dados nao informado (Api Oking)'
    assert client_data['database'] is not None, 'Nome do banco de dados nao informado (Api Oking)'
    assert client_data['user'] is not None, 'Usuario do banco de dados nao informado (Api Oking)'
    assert client_data['password'] is not None, 'Senha do banco de dados nao informado (Api Oking)'
    assert client_data['url_api'] is not None, 'Url da api okvendas nao informado (Api Oking)'
    assert client_data['token_api'] is not None, 'Token da api okvendas nao informado (Api Oking)'
    is_connected_oracle_client = False
else:
    logger.warning(f'Cliente nao configurado no painel oking para o token: {token_oking}')
