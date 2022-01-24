from typing import List
import traceback
import logging
from src import globals
from src.connection import Conexao
from src.services import srequest
from src.services import slack
from src.services import semail
from src.services import sql_erp
from src.entities.pedido import Pedido
from src.entities.pedido import Fila
from src.entities import pedido

logger = logging.getLogger()


def atualiza_pedidos_no_erp():
    url = globals.url_pedidos_fila.replace(":status", "PEDIDO")
    url_ped = globals.url_pedido.replace("/:id", "")

    jsn_pedidos = srequest.get_cliente(url, 'json')
    # jsn_pedidos = srequest.teste_json_fila("PEDIDO_PAGO")
    lista_pedidos = []
    p_size = 0
    procedure = True  # pegar no painel src

    if jsn_pedidos is not None:
        fila_array = jsn_pedidos['fila']
        p_size = len(fila_array)
        filas: List[Fila]

        if p_size > 0:
            logger.debug("Total de pedidos na fila: {}".format(p_size))
            filas = pedido.toListFilaDecoder(fila_array)

            for f in filas:
                # if f.pedido_id == 666098:
                # p_dados = srequest.teste_json_pedido(f.pedido_id)
                p_dados = srequest.get_cliente(
                    url_ped+'/' + str(f.pedido_id), 'json')
                p = Pedido(**p_dados)
                lista_pedidos.append(p)

            if procedure:
                executa_processa_pedido3(lista_pedidos)
            else:
                salvar_pedidos(lista_pedidos)

    if p_size == 0:
        logger.warn("Nao ha pedidos para Internalizar")


def salvar_pedidos_proc(pedidos: List[Pedido]):
    conexao = Conexao(globals.database_type)
    conn = conexao.get_conect()
    cursor = conn.cursor()

    mailErro = None
    logger.debug("Abriu connection insere pedidos via procedure")

    for ped in pedidos:
        sql = ped.get_comando_proc()
        try:
            cursor.execute(sql)
        except Exception as ex:
            logger.warn("Erro executando: {}".format(sql))
            logger.error(str(ex), exc_info=True)
            # print(str(ex))
            traceback.print_exc()  # stack trace
            mailErro = "Erro executando: "+sql + \
                "\n" + traceback.format_exc()

    cursor.close()
    conn.commit()
    conn.close()

    if mailErro is not None:
        slack.register_error(
            "Erro ao internalizar pedidos: "+mailErro)


def arquivo_processa_pedido3(pedidos: List[Pedido]):
    dados = ""

    for p in pedidos:
        dados = dados + p.get_dados_cliente() + \
            p.get_dados_pedido() + p.get_dados_lista_itens()

    myfile = open('pedidos_procedure.txt', 'w')
    try:
        myfile.write(dados)
    finally:
        myfile.close()


def executa_processa_pedido3(pedidos: List[Pedido]):
    proc_pedido = "STP_PROCESSA_PEDIDO3"

    conexao = Conexao(globals.database_type)
    conn = conexao.get_conect()
    cursor = conn.cursor()

    for ped in pedidos:
        try:
            logger.debug("Insere dados do cliente: ", ped.usuario.nome)
            args = ('C', ped.get_dados_cliente)
            cursor.callproc(proc_pedido, args)

            logger.debug("Insere dados do pedido: ", str(ped.id))
            args = ('P', ped.get_dados_pedido)
            cursor.callproc(proc_pedido, args)

            logger.debug("Insere dados itens pedido")
            args = ('I', ped.get_dados_lista_itens)
            cursor.callproc(proc_pedido, args)
        except Exception as ex:
            logger.warn("Erro executando STP_PROCESSA_PEDIDO3")
            logger.error(str(ex), exc_info=True)
            pass  # nao abortar

    cursor.close()
    conn.commit()
    conn.close()


def salvar_pedidos(pedidos: List[Pedido]):
    conexao = Conexao(globals.database_type)
    conn = conexao.get_conect()
    cursor = conn.cursor()

    logger.debug("Abriu connection insere pedidos inserts")

    for ped in pedidos:
        try:
            if ped.novo_cliente:
                sql = ped.get_insert_endereco
                cursor.execute(sql)
                sql = ped.get_insert_cliente
                cursor.execute(sql)

            sql = ped.get_insert
            cursor.execute(sql)
            sql = ped.get_insert_itens
            cursor.execute(sql)
        except Exception as ex:
            logger.warn("Erro executando: {}".format(sql))
            logger.error(str(ex), exc_info=True)
            pass  # nao abortar

    cursor.close()
    conn.commit()
    conn.close()


def confirma_pagamento_pedidos_erp():
    url = globals.url_pedidos_fila.replace(":status", "PEDIDO_PAGO")
    url_ped = globals.url_pedido.replace("/:id", "")
    url_protocolar = globals.url_pedidos_fila.replace("/:status", "")

    jsn_pedidos = srequest.get_cliente(url, 'json')
    # jsn_pedidos = srequest.teste_json_fila("PEDIDO_PAGO")
    lista_pedidos = []
    p_size = 0

    if jsn_pedidos is not None:
        fila_array = jsn_pedidos['fila']
        p_size = len(fila_array)
        filas: List[Fila]

        if p_size > 0:
            logger.debug("Total de pedidos na fila: {}".format(p_size))
            filas = pedido.toListFilaDecoder(fila_array)

            for f in filas:
                p_dados = srequest.get_cliente(
                    url_ped+'/' + str(f.pedido_id), 'json')
                p = Pedido(**p_dados)
                lista_pedidos.append(p)

            size_ped = len(lista_pedidos)

            if size_ped > 0:
                atualizados = atualizar_pedidos(lista_pedidos)
                size_at = len(atualizados)

                if size_at > 0:
                    logger.debug(
                        "Protocolando pedidos pagos: {}".format(size_at))
                    for p_id in atualizados:
                        srequest.put_cliente(url_protocolar, p_id)


def atualiza_pedidos_cancelado_no_erp():
    url = globals.url_pedidos_fila.replace(":status", "CANCELADO")
    url_ped = globals.url_pedido.replace("/:id", "")
    url_protocolar = globals.url_pedidos_fila.replace("/:status", "")

    jsn_pedidos = srequest.get_cliente(url, 'json')
    lista_pedidos = []
    p_size = 0

    if jsn_pedidos is not None:
        fila_array = jsn_pedidos['fila']
        p_size = len(fila_array)
        filas: List[Fila]

        if p_size > 0:
            logger.debug("Total de pedidos na fila: {}".format(p_size))
            filas = pedido.toListFilaDecoder(fila_array)

            for f in filas:
                p_dados = srequest.get_cliente(
                    url_ped+'/' + str(f.pedido_id), 'json')
                p = Pedido(**p_dados)
                lista_pedidos.append(p)

            size_ped = len(lista_pedidos)

            if size_ped > 0:
                atualizados = atualizar_pedidos(lista_pedidos)
                size_at = len(atualizados)

                if size_at > 0:
                    logger.debug(
                        "Protocolando pedidos cancelados: {}".format(size_at))
                    for p_id in atualizados:
                        srequest.put_cliente(url_protocolar, p_id)


def atualizar_pedidos(pedidos: List[Pedido]):
    atualizados = []
    nao_atualizado = []

    conexao = Conexao(globals.database_type)
    conn = conexao.get_conect()
    cursor = conn.cursor()

    for ped in pedidos:
        try:
            sql = ped.get_insert
            cursor.execute(sql)
            atualizados.append(ped.id)
        except Exception as ex:
            nao_atualizado.append(ped.id)
            logger.warn("Erro executando: {}".format(sql))
            logger.error(str(ex), exc_info=True)
            pass  # nao abortar

    cursor.close()
    conn.commit()
    conn.close()

    if len(nao_atualizado) > 0:
        msg = "".join(nao_atualizado)
        semail.enviar(msg, "Pedidos nao atualizado status!")

    return atualizados


def envia_notafiscal_pedidos():
    # Fluxo 1
    # url = v_global.url_pedidos_fila.replace(":status", "SEM_NOTA_FISCAL")

    # Fluxo 2
    notas = sql_erp.lista_notas_emitidas()
    p_size = len(notas) if notas is not None else 0

    if p_size > 0:
        logger.debug("Enviando notas emitidas: {}".format(p_size))
        pedidosJson = srequest.post_cliente(
            globals.url_pedido_faturar, notas)
        protocolar_notafiscal_pedidos(pedidosJson)
    else:
        logger.warn("Sem notas fiscais emitidas para envio!")


def protocolar_notafiscal_pedidos(pedidosJson):
    msg_erro = "OKING >> update_notafiscal_pedido >> " + \
               globals.cliente + " >> Erro comando sql"

    sql_protocolar = sql_erp.update_notafiscal_pedido()

    if sql_protocolar is not None:
        conexao = Conexao(globals.database_type)
        conn = conexao.get_conect()
        cursor = conn.cursor()

        for p in pedidosJson:
            if p['Status'] == 1:
                pedId = p['Identifiers'][0]

                try:
                    sql = sql_protocolar.replace(
                        "?pedido", pedId)
                    cursor.execute(sql)
                except Exception as ex:
                    logger.error(str(ex), exc_info=True)
                    slack.register_error(msg_erro + str(ex))


def envia_rastreio_pedidos():
    pedidos = sql_erp.lista_rastreio_pedidos()
    p_size = len(pedidos) if pedidos is not None else 0

    if p_size > 0:
        logger.debug("Enviando rastreio de pedidos: {}".format(p_size))
        pedidosJson = srequest.post_cliente(
            globals.url_pedido_rastreio, pedidos)
        protocolar_rastreio_pedidos(pedidosJson)
    else:
        logger.warn("Sem dados de rastreio pedido para enviar!")


def protocolar_rastreio_pedidos(pedidosJson):
    msg_erro = "OKING >> update_rastreio_pedido >> " + \
               globals.cliente + " >> Erro comando sql"

    sql_protocolar = sql_erp.update_rastreio_pedido()

    if sql_protocolar is not None:
        conexao = Conexao(globals.database_type)
        conn = conexao.get_conect()
        cursor = conn.cursor()

        for p in pedidosJson:
            if p['Status'] == 1:
                pedId = p['Identifiers'][0]

                try:
                    sql = sql_protocolar.replace(
                        "?pedido", pedId)
                    cursor.execute(sql)
                except Exception as ex:
                    logger.error(str(ex), exc_info=True)
                    slack.register_error(msg_erro + str(ex))


def envia_pedidos_entregues():
    pedidos = sql_erp.lista_entrega_pedidos()
    p_size = len(pedidos) if pedidos is not None else 0

    if p_size > 0:
        logger.debug("Enviando pedidos entregues: {}".format(p_size))
        pedidosJson = srequest.post_cliente(
            globals.url_pedido_entregue, pedidos)
        protocolar_pedidos_entregues(pedidosJson)
    else:
        logger.warn("Sem dados pedidos entregues para enviar!")


def protocolar_pedidos_entregues(pedidosJson):
    msg_erro = "OKING >> update_entrega_pedidos >> " + \
               globals.cliente + " >> Erro comando sql"

    sql_protocolar = sql_erp.update_entrega_pedidos()

    if sql_protocolar is not None:
        conexao = Conexao(globals.database_type)
        conn = conexao.get_conect()
        cursor = conn.cursor()

        for p in pedidosJson:
            if p['Status'] == 1:
                pedId = p['Identifiers'][0]

                try:
                    sql = sql_protocolar.replace(
                        "?pedido", pedId)
                    cursor.execute(sql)
                except Exception as ex:
                    logger.error(str(ex), exc_info=True)
                    slack.register_error(msg_erro + str(ex))
