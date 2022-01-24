import logging
from src.entities.product import Product
from src.services import semaforo
from src.services import srequest
from src.services import slack
from src.database.connection import Connection
import src.api.okvendas as api_okvendas
import src.database.queries as queries




def atualizar_precos():
    produtos = semaforo.lista_produtos_preco_erp()
    p_size = len(produtos) if produtos is not None else 0

    if p_size > 0:
        logger.debug("Total de produtos atualizar preco: {}".format(p_size))
        jsn_prods = srequest.post_cliente(globals.url_preco, produtos)
        # Identifiers, Status, Message, Protocolo

        mensagens = []

        if jsn_prods is not None:
            logger.debug('Atualizando preco produtos no semaforo')
            conexao = Connection(globals.database_type)
            conn = conexao.get_conect()
            cursor = conn.cursor()

            sql_protocolar_precos = 'update openk_semaforo.preco_produto set data_sincronizacao = now() where codigo_erp_variacao = %s;'
            for p in jsn_prods:
                if p['Status'] == 1:
                    cod_erp = p['Identifiers'][0]
                    try:
                        cursor.execute(sql_protocolar_precos, (cod_erp))
                    except Exception as ex:
                        logger.error(str(ex), exc_info=True)
                        slack.register_error(
                            "OKING >> atualiza_preco_loja >> " +
                            globals.cliente + " >> " +
                            " Erro sql " + str(ex))
                else:
                    mensagens.append(p['Message'])

            cursor.close()
            conn.commit()
            conn.close()
            logger.debug('Atualizado precos produto semaforo FIM')
    else:
        logger.warn("Nao ha produtos para atualizar preco")


def insere_preco_semaforo():
    insert_carga = semaforo.sql_insere_preco_semaforo()

    if insert_carga is None:
        slack.register_warn(
            "SQL insert preco produtos nao configurado no Oking")
    else:
        conexao = Connection(globals.database_type)
        conn = conexao.get_conect()
        cursor = conn.cursor()

        try:
            cursor.execute(insert_carga)
            cursor.close()
            conn.commit()
        except Exception as ex:
            slack.register_error("Erro executando: {}".format(insert_carga))
            logger.error(str(ex), exc_info=True)

        conn.close()


    