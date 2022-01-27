import logging
import traceback
from src.connection import Conexao
from src.services import slack
from src.services import srequest
from src import globals

logger = logging.getLogger()


# Rastreio de entrega
def query_rastreio_pedido():
    sql = None
    json_res = srequest.get_oking(
        '/consulta/query_rastreio_pedido', 'json')
    if json_res is not None:
        sql = json_res['query']

    return sql


def update_rastreio_pedido():
    sql = None
    json_res = srequest.get_oking(
        '/consulta/sql_update_rastreio_pedido', 'json')
    if json_res is not None:
        sql = json_res['query']
    return sql


def dict_rastreio_pedido(pedidos):
    lista = []
    for row in pedidos:
        dict = {
            'id': float(row[0]),
            'codigoRastreio': row[1],
            'linkRastreio': row[2],
            'data_previsao_entrega': row[3],
            'observacao': row[4],
            'codigo_erp': row[5],
            'codigo_sku': row[6],
            'cnpj_transportadora': row[7],
            'transportadora': row[8],
            'codigo_transportadora': row[9],
            'tipo_servico': row[10],
            'quantidade': float(row[11]),
            'codigo_carga': row[12]
        }
        lista.append(dict)


def query_entrega_pedidos():
    sql = None
    json_res = srequest.get_oking(
        '/consulta/query_entrega_pedidos', 'json')
    if json_res is not None:
        sql = json_res['query']

    return sql


def update_entrega_pedidos():
    sql = None
    json_res = srequest.get_oking(
        '/consulta/sql_update_entrega_pedidos', 'json')
    if json_res is not None:
        sql = json_res['query']
    return sql


def dict_entrega_pedidos(pedidos):
    lista = []
    for row in pedidos:
        dict = {
            'id': float(row[0]),
            'codigoRastreio': row[1],
            'linkRastreio': row[2],
            'data_previsao_entrega': row[3],
            'observacao': row[4],
            'data_Entrega': row[5]
        }
        lista.append(dict)


# Nota Fiscal
def query_notafiscal_pedido():
    sql = None
    json_res = srequest.get_oking(
        '/consulta/query_notafiscal_emitidas', 'json')
    if json_res is not None:
        sql = json_res['query']

    return sql


def update_notafiscal_pedido():
    sql = None
    json_res = srequest.get_oking(
        '/consulta/sql_update_notafiscal_pedido', 'json')
    if json_res is not None:
        sql = json_res['query']
    return sql


def dict_notafiscal_pedido(notas):
    lista = []
    for row in notas:
        nota_dict = {
            'id': float(row[0]),
            'numero_nota': row[1],
            'numero_serie': row[2],
            'chave_acesso': row[3],
            'valor_total_nota': float(row[4]),
            'data_emissao': row[5],
            'quantidade_volume': float(row[6]),
            'link_danfe': row[7],
            'link_xml': row[8],
            'xml': row[9]
        }
        lista.append(nota_dict)

    return lista


def lista_notas_emitidas():
    notas_fiscais = None
    query = query_notafiscal_pedido()

    if query is None:
        slack.register_warn("Query de notas fiscais emitidas nao configurada!")
    else:
        try:
            conexao = Conexao(globals.database_type)
            conn = conexao.get_conect()
            cursor = conn.cursor()
            cursor.execute(query)

            rs = cursor.fetchall()
            if len(rs) > 0:
                notas_fiscais = dict_notafiscal_pedido(rs)

            cursor.close()
            conn.close()
        except Exception as ex:
            err = "Erro executando: {}".format(query)
            slack.register_warn(err)
            logger.error(str(ex), exc_info=True)
            traceback.print_exc()

    return notas_fiscais


def lista_rastreio_pedidos():
    dados_rastreios = None
    query = query_rastreio_pedido()

    if query is None:
        slack.register_warn("Query rastreio de pedidos nao configurada!")
    else:
        try:
            conexao = Conexao(globals.database_type)
            conn = conexao.get_conect()
            cursor = conn.cursor()
            cursor.execute(query)

            rs = cursor.fetchall()
            if len(rs) > 0:
                dados_rastreios = dict_rastreio_pedido(rs)

            cursor.close()
            conn.close()
        except Exception as ex:
            err = "Erro executando: {}".format(query)
            slack.register_warn(err)
            logger.error(str(ex), exc_info=True)
            traceback.print_exc()

    return dados_rastreios


def lista_entrega_pedidos():
    pedidos = None
    query = query_entrega_pedidos()

    if query is None:
        slack.register_warn("Query entrega de pedidos nao configurada!")
    else:
        try:
            conexao = Conexao(globals.database_type)
            conn = conexao.get_conect()
            cursor = conn.cursor()
            cursor.execute(query)

            rs = cursor.fetchall()
            if len(rs) > 0:
                pedidos = dict_entrega_pedidos(rs)

            cursor.close()
            conn.close()
        except Exception as ex:
            err = "Erro executando: {}".format(query)
            slack.register_warn(err)
            logger.error(str(ex), exc_info=True)
            traceback.print_exc()

    return pedidos
