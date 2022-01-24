import json
import logging
from typing import Optional

import jsonpickle
import requests

import src
from src.entities.invoice import Invoice
from src.entities.log import Log
from src.entities.order import Queue, Order
from src.entities.price import Price
from src.entities.response import CatalogoResponse, PriceResponse, InvoiceResponse, TrackingResponse
from src.entities.tracking import Tracking

logger = logging.getLogger()


def obj_dict(obj):
    return obj.__dict__


def object_list_to_dict(obj_list: list):
    lista = []
    for obj in obj_list:
        lista.append(obj.toJSON())
    return lista


def post_produtos(produtos: list):
    try:
        url = f'{src.client_data.get("url_api")}/catalogo/produtos'

        json_produtos = jsonpickle.encode(produtos, unpicklable=False)
        logger.info(f'Enviando produto para api okvendas {json_produtos}')
        response = requests.post(url, json=json.loads(json_produtos), headers={
            'Content-type': 'application/json',
            'Accept': 'text/html',
            'access-token': src.client_data.get('token_api')})

        obj = jsonpickle.decode(response.content)
        result = []
        if 200 <= response.status_code <= 299:
            for res in obj:
                result.append(CatalogoResponse(**res))
        else:
            if type(obj) is list:
                for res in obj:
                    result.append(CatalogoResponse(**res))
            else:
                result.append(CatalogoResponse(**obj))

        return result
    except Exception as e:
        logger.error(f'Erro ao enviar produto para api okvendas {e}', exc_info=True)


def send_stocks(url, body, token):
    logger.debug("POST: {}".format(url))
    try:
        # auth = HTTPBasicAuth('teste@example.com', 'real_password')
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/html',
                   'access-token': token}

        logger.info(body)
        json_stock = jsonpickle.encode(body, unpicklable=False)
        response = requests.put(url, json=json.loads(json_stock), headers=headers)

        if response.ok:
            return response.json(), response.status_code
        else:
            if response.content is not None and response.content != '':
                return response.json(), response.status_code

    except Exception as ex:
        logger.error(str(ex))
        return None, response.status_code


def post_prices(url, price: Price, token) -> PriceResponse:
    try:
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/html',
                   'access-token': token}

        json_prices = jsonpickle.encode(price, unpicklable=False)
        logger.info(f'{url} - {json_prices}')
        response = requests.put(url, json=json.loads(json_prices), headers=headers)

        obj = jsonpickle.decode(response.content)
        return PriceResponse(**obj)

    except Exception as ex:
        logger.error(str(ex))
        return PriceResponse([price.codigo_erp], 3, str(ex), '', '')


def get_order_queue(url: str, token: str, status: str, limit: int) -> list[Queue]:
    queue = []
    try:
        response = requests.get(url.format(status), headers={'Accept': 'application/json', 'access-token': token}, params={'limit': limit})
        if response.ok:
            obj = jsonpickle.decode(response.content)
            for o in obj['fila']:
                queue.append(Queue(**o))
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
    except Exception as ex:
        logger.error(f'Erro ao realizar GET na api okvendas {url}' + str(ex), exc_info=True)

    return queue


def get_order(url: str, token: str, order_id: int) -> Order:
    order = None
    try:
        response = requests.get(url.format(order_id), headers={'Accept': 'application/json', 'access-token': token})
        if response.ok:
            obj = jsonpickle.decode(response.content)
            order = Order(**obj)
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
    except Exception as ex:
        logger.error(f'Erro ao realizar GET na api okvendas {url} - {str(ex)}')
        raise

    return order


def put_order_erp_code(url: str, token: str, order_id: int, order_erp_id: str) -> bool:
    try:
        response = requests.put(url, headers={'Accept': 'application/json', 'access-token': token}, params={'id': order_id, 'codigo_erp': order_erp_id})
        if response.ok:
            return True
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
            return False
    except Exception as ex:
        logger.error(f'Erro ao realizar GET na api okvendas {url}' + str(ex), exc_info=True)
        return False


def put_client_erp_code(url: str, token: str, body: dict) -> bool:
    try:
        data = jsonpickle.encode(body, unpicklable=False)
        response = requests.put(url, data=json.loads(data), headers={'Accept': 'application/json', 'access-token': token})
        if response.ok:
            return True
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
            return False
    except Exception as ex:
        logger.error(f'Erro ao realizar GET na api okvendas {url}' + str(ex), exc_info=True)
        return False


def put_protocol_orders(protocolos: list[str]) -> bool:
    url = src.client_data.get('url_api') + f'/pedido/fila'
    try:
        json_protocolos = jsonpickle.encode(protocolos)
        response = requests.put(url, json=json.loads(json_protocolos), headers={'Accept': 'application/json', 'access-token': src.client_data.get('token_api')})
        if response.ok:
            return True
        else:
            logger.warning(f'Retorno sem sucesso {response.status_code} - {response.url}')
            return False
    except Exception as ex:
        logger.error(f'Erro ao protocolar pedidos na api okvendas {url}' + str(ex), exc_info=True)
        return False


def post_invoices(url: str, invoice: Invoice, token) -> Optional[InvoiceResponse]:
    """
    Enviar NF de um pedido para api okvendas
    Args:
        url: Url da api okvendas
        invoice: Objeto com os dados da NF
        token: Token de acesso da api okvendas

    Returns:
    None se o envio for sucesso. Caso falhe, um objeto contendo status e descrição do erro
    """
    try:
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': token}

        json_invoice = jsonpickle.encode(invoice, unpicklable=False)
        logger.info(f'{url} - {json_invoice}')
        response = requests.post(url, json=json.loads(json_invoice), headers=headers)
        if response.ok:
            return None
        else:
            err = jsonpickle.decode(str(response.text))
            invoice_response = InvoiceResponse(**err)
            if '_okvendas' in invoice_response.message or '_openkuget' in invoice_response.message:
                invoice_response.message = 'Erro interno no servidor. Entre em contato com o suporte'
            return invoice_response

    except Exception as ex:
        return InvoiceResponse(3, str(ex))


def post_tracking(url: str, tracking: Tracking, token) -> Optional[TrackingResponse]:
    """
    Enviar rastreio de um pedido para api okvendas
    Args:
        url: Url da api okvendas
        tracking: Objeto com os dados do rastreio
        token: Token de acesso da api okvendas

    Returns:
    None se o envio for sucesso. Caso falhe, um objeto contendo status e descrição do erro
    """
    try:
        headers = {'Content-type': 'application/json',
                   'Accept': 'application/json',
                   'access-token': token}

        json_tracking = jsonpickle.encode(tracking, unpicklable=False)
        logger.info(f'{url} - {json_tracking}')
        response = requests.post(url, json=json.loads(json_tracking), headers=headers)
        if response.ok:
            return None
        else:
            err = jsonpickle.decode(str(response.text))
            tracking_response = TrackingResponse(**err)
            if '_okvendas' in tracking_response.message or '_openkuget' in tracking_response.message:
                tracking_response.message = 'Erro interno no servidor. Entre em contato com o suporte'
            return tracking_response

    except Exception as ex:
        return TrackingResponse(3, str(ex))


def post_log(log: Log) -> bool:
    try:
        if not src.is_dev:
            url = f'{src.client_data.get("url_api")}/log/logIntegracao'
            headers = {
                'Content-type': 'application/json',
                'Accept': 'application/json',
                'access-token': src.client_data.get('token_api')
            }

            body = list([Log])
            body.append(log)
            json_log = jsonpickle.encode(body, unpicklable=False)
            response = requests.post(url, json=json.loads(json_log), headers=headers)
            if response.ok:
                return True

            return False
        else:
            return True
    except Exception:
        return False
