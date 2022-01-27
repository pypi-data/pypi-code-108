import logging
import traceback
from src.services import slack
from src.database.connection import Connection
from src.services import srequest
from src.entities.product import Product
import json

logger = logging.getLogger()


def sql_insere_estoque_semaforo():
    """
    Obter comando sql para inserir estoques de produtos na tabela semaforo
    """
    sql = None
    json_res = srequest.get_oking(endpoint_parametros + 'insere_estoque_produto_semaforo_job', 'json')
    if json_res is not None:
        sql = json_res['query']
    return sql


def sql_estoques_pendentes_atualizacao():
    """
    Obter comando sql para consultar os estoques pendentes de atualizacao
    """
    sql = None
    json_res = srequest.get_oking(endpoint_parametros + 'envia_estoque_produtos_job', 'json')
    if json_res is not None:
        sql = json_res['query']
    return sql


def sql_insere_preco_semaforo():
    sql = None
    json_res = srequest.get_oking(endpoint_parametros + 'insere_preco_produto_semaforo_job', 'json')
    if json_res is not None:
        sql = json_res['query']
    return sql


def sql_precos_pendentes_atualizacao():
    sql = None
    json_res = srequest.get_oking(endpoint_parametros + 'envia_preco_produtos_job', 'json')
    if json_res is not None:
        sql = json_res['query']
    return sql


def get_sql_criar_produtos_semaforo():
    """
    Obter comando sql para inserir os produtos do erp na tabela semaforo
    """
    insert = None
    response = srequest.get_oking(endpoint_parametros + 'envia_catalogo_produto_semaforo_job', 'json')
    if response is not None and response['query']:
        insert = response['query']
    return insert


def get_sql_criar_produtos():
    """
    Obter comando sql para consultar os produtos que estao na tabela semaforo aguardando sincronizacao
    """
    query = None
    response = srequest.get_oking(endpoint_parametros + 'envia_catalogo_produto_loja_job', 'json')
    if response is not None and response['query']:
        query = response['query']
    return query


def get_sql_atualizar_produtos_semaforo():
    """
    Obter comando sql para consultar os produtos que estao pendentes de atualizacao
    """
    query = None
    response = srequest.get_oking(endpoint_parametros + 'envia_atualizacao_catalogo_produto_job', 'json')
    if response is not None and response['query']:
        query = response['query']
    return query





def lista_produtos_preco_erp():
    produtos = None
    query = sql_precos_pendentes_atualizacao()

    if query is None:
        slack.register_warn("Query preço de produtos nao configurada!")
    else:
        try:
            conexao = Connection(globals.database_type)
            conn = conexao.get_conect()
            cursor = conn.cursor()  # Connected
            cursor.execute(query)
            rs = cursor.fetchall()
            if len(rs) > 0:
                produtos = preco_dict(rs)

            cursor.close()
            conn.close()
        except Exception as ex:
            err = "Erro executando: {}".format(query)
            slack.register_warn(err)
            logger.error(str(ex), exc_info=True)
            traceback.print_exc()

    return produtos


def produto_dict(produtos):
    lista = []
    for row in produtos:
        p = Product(**row)
        # ver como sera o retorno da view e usar row[1]
        lista.append(json.dumps(p))

    return lista





def preco_dict(produtos):
    lista = []
    for row in produtos:
        pdict = {
            'codigo_erp': row[0],
            'preco_atual': float(row[1]),
            'preco_lista': float(row[2]),
            'preco_custo': float(row[3]),
            'codigo_externo_campanha': '',
            'parceiro': 0}
        lista.append(pdict)

    return lista

# def lista_produtos_catalogo():
#     produtos = None  # nice
#     query = query_estoque_produtos()

#     if query is None:
#         slack.registerWarn("Query de produtos nao configurada!")
#     else:
#         try:
#             connection = Conexao(v_global.banco)
#             conn = connection.get_conect()
#             cursor = conn.cursor()
#             cursor.execute(query)
#             rs = cursor.fetchall()

#             if len(rs) > 0:
#                 produtos = produto_dict(rs)

#             cursor.close()
#             conn.close()
#         except Exception as ex:
#             err = "Erro executando: {}".format(query)
#             slack.registerWarn(err)
#             logger.error(str(ex), exc_info=True)
#             traceback.print_exc()

#     return produtos
