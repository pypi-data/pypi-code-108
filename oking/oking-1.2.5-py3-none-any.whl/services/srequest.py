import requests
import json
import logging
import traceback
# from src import globals
import src
from src.services import slack
# from requests.auth import HTTPBasicAuth

logger = logging.getLogger()


def teste_json_fila(status):
    logger.debug("Buscando pedidos no status {}".format(status))

    with open('pedidos_fila.json', 'r', encoding="utf8") as jsnfile:
        data = jsnfile.read()
    obj = json.loads(data)
    return obj


def teste_json_pedido(ped_id):
    logger.debug("Buscando dados do pedido numero {}".format(ped_id))

    with open('pedido.json', 'r', encoding='utf8') as jsnfile:
        data = jsnfile.read()
    obj = json.loads(data)
    return obj


def get_oking(endpoint, retorno):
    return get(globals.url_oking + endpoint, retorno, None)


def get_cliente(endpoint, retorno):
    return get(globals.url_cliente + endpoint,
               retorno, globals.token_api)


def post_cliente(endpoint, body):
    return process_post(globals.url_cliente + endpoint, body)


def put_cliente(endpoint, body):
    return process_put(globals.url_cliente + endpoint, body)


def get(url, retorno, token):
    logger.debug("GET: {}".format(url))

    try:
        headers = {'Accept': 'application/json',
                   'access-token': token
                   }

        response = requests.get(url, headers=headers)  # ,timeout=5

        if response.status_code >= 200 and response.status_code <= 299:
            if retorno == 'json':
                return response.json()
            else:
                return response.text()
        else:
            slack.register_error('Retorno sem sucesso, status ' +
                                 str(response.status_code) + ' ' + response.text)
    except Exception as ex:
        logger.error(str(ex), exc_info=True)
        slack.register_error('Erro comunicando api: ' + traceback.format_exc())


def process_post(url, body):
    logger.debug("POST: {}".format(url))

    try:
        # auth = HTTPBasicAuth('teste@example.com', 'real_password')
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/html',
                   'access-token': src.token_api_okvendas}

        response = requests.post(url, json=body, headers=headers)

        if 200 <= response.status_code <= 299:
            return response.json(), response.status_code
        else:
            slack.register_error('Retorno sem sucesso - status ' +
                                 str(response.status_code) + ' ' + response.text)
            if response.content is not None and response.content != '':
                return response.json(), response.status_code

    except Exception as ex:
        logger.error(str(ex), exc_info=True)
        slack.register_error('Erro comunicando api: ' + traceback.format_exc())
        return None, response.status_code        


def process_put(url, body):
    logger.debug("PUT: {}".format(url))

    try:
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/html',
                   'access-token': globals.token_api}

        response = requests.put(url, json=body, headers=headers)

        if response.status_code >= 200 and response.status_code <= 299:
            return response.json()
        else:
            slack.register_error('Retorno sem sucesso - status ' +
                                 str(response.status_code) + ' ' + response.text)

    except Exception as ex:
        logger.error(str(ex), exc_info=True)
        slack.register_error('Erro comunicando api: ' + traceback.format_exc())
