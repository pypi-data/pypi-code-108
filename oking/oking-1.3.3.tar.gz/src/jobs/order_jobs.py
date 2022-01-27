import logging
from datetime import datetime
from time import sleep
from src.entities.log import Log
import src
import src.api.okvendas as api_okvendas
import src.database.connection as database
import src.database.utils as utils
from src.database import queries
from src.database.utils import DatabaseConfig
from src.entities.tracking import Tracking
from src.entities.invoice import Invoice
from src.entities.order import Order, Queue

logger = logging.getLogger()

default_limit = 50
queue_status = {
    'pending': 'PEDIDO',
    'paid': 'PEDIDO_PAGO',
    'shipped': 'ENCAMINHADO_ENTREGA',
    'delivered': 'ENTREGUE',
    'canceled': 'CANCELADO',
    'no_invoice': 'SEM_NOTA_FISCAL',
    'invoiced': 'FATURADO'
}


def define_job_start(job_config: dict) -> None:
    global current_job
    current_job = job_config.get('job_name')
    if current_job == 'internaliza_pedidos_job':  # Inicia o job a partir dos pedidos AgPagamento
        job_orders(job_config, True)
    else:  # Inicia o job a partir dos pedidos Confirmados
        job_orders(job_config)


def job_orders(job_config: dict, start_at_pending: bool = False) -> None:
    try:
        db_config = utils.get_database_config(job_config)
        if start_at_pending:
            process_order_queue(queue_status.get('pending'), db_config)

        process_order_queue(queue_status.get('paid'), db_config)

        process_order_queue(queue_status.get('canceled'), db_config)

        # process_order_queue(queue_status.get('invoiced'), db_config)

        process_order_queue(queue_status.get('shipped'), db_config)

        process_order_queue(queue_status.get('delivered'), db_config)

    except Exception as e:
        logger.error(current_job + f' | Erro ao inicializar job: {str(e)}')


def job_invoice_orders(job_config: dict):
    try:
        db_config = utils.get_database_config(job_config)
        if db_config.sql is None:
            logger.warning(job_config.get('job_name') + ' | Comando sql para baixar notas fiscais nao encontrado')
        else:
            invoices = query_invoices(db_config)
            for invoice in invoices:
                try:
                    invoice_sent = api_okvendas.post_invoices(src.client_data.get('url_api') + '/pedido/faturar', invoice, src.client_data.get('token_api'))
                    if invoice_sent is None:
                        logger.info(job_config.get('job_name') + f' | NF do pedido {invoice.id} enviada com sucesso para api okvendas')
                        continue
                    else:
                        logger.error(job_config.get('job_name') + f' | Falha ao enviar NF do pedido {invoice.id} para api okvendas: {invoice_sent.message}')
                except Exception as e:
                    logger.error(job_config.get('job_name') + f' | Falha ao enviar NF do pedido {invoice.id}: {str(e)}')
    except Exception as e:
        logger.error(job_config.get('job_name') + f' | Falha na execução do job: {str(e)}')


def job_send_erp_tracking(job_config: dict):
    try:
        db_config = utils.get_database_config(job_config)
        if db_config.sql is None:
            logger.warning(job_config.get('job_name') + ' | Comando sql para consultar rastreios nao encontrado')
        else:
            trackings = query_trackings(db_config)
            for tracking in trackings:
                try:
                    tracking_sent = api_okvendas.post_tracking(src.client_data.get('url_api') + '/pedido/encaminhar', tracking, src.client_data.get('token_api'))
                    if tracking_sent is None:
                        logger.info(job_config.get('job_name') + f' | Rastreio do pedido {tracking.id} enviada com sucesso para api okvendas')
                        continue
                    else:
                        logger.error(job_config.get('job_name') + f' | Falha ao enviar rastreio do pedido {tracking.id} para api okvendas: {tracking_sent.message}')
                except Exception as e:
                    logger.error(job_config.get('job_name') + f' | Falha ao enviar rastreio do pedido {tracking.id}: {str(e)}')
    except Exception as e:
        logger.error(job_config.get('job_name') + f' | Falha na execução do job: {str(e)}')


def process_order_queue(status: str, db_config: DatabaseConfig) -> None:
    try:
        logger.info(current_job + f' | Consultando fila de pedidos no status {status}')
        queue = api_okvendas.get_order_queue(
            url=src.client_data.get('url_api') + '/pedido/fila/{0}',
            token=src.client_data.get('token_api'),
            status=status,
            limit=default_limit)

        qty = 0
        for q_order in queue:
            try:
                sleep(0.5)
                qty = qty + 1
                print()
                logger.info(current_job + f' | Iniciando processamento ({qty} de {len(queue)}) pedido {q_order.order_id}')
                order = api_okvendas.get_order(
                    url=src.client_data.get('url_api') + '/pedido/{0}',
                    token=src.client_data.get('token_api'),
                    order_id=q_order.order_id)

                if order.erp_code is not None and order.erp_code != '':
                    if check_order_existence(db_config, order.order_id):
                        logger.info(current_job + ' | Pedido ja integrado com o ERP, chamando procedure de atualizacao...')
                        if call_update_order_procedure(db_config, order):
                            logger.info(current_job + ' | Pedido atualizado com sucesso')
                            protocol_order(db_config=db_config, order=order, queue_order=q_order, order_erp_id='', client_erp_id='')
                    else:
                        logger.warning(current_job + f' | Pedido {order.order_id} nao existe no banco semaforo porem ja foi integrado previamente. Protocolando pedido...')
                        protocol_non_existent_order(q_order)

                else:
                    if check_order_existence(db_config, order.order_id):
                        logger.info(current_job + ' | Pedido já existente no banco semáforo, porem nao integrado com erp. Chamando procedures')
                        sp_success, client_erp_id, order_erp_id = call_order_procedures(db_config, q_order.order_id)
                        if sp_success:
                            logger.info(current_job + ' | Chamadas das procedures executadas com sucesso, protocolando pedido...')
                            protocol_order(db_config=db_config, order=order, queue_order=q_order, order_erp_id=order_erp_id, client_erp_id=client_erp_id)
                    else:
                        logger.info(current_job + ' | Inserindo novo pedido no banco semaforo')
                        inserted = insert_temp_order(order, db_config)
                        if inserted:
                            logger.info(current_job + ' | Pedido inserido com sucesso, chamando procedures...')
                            sp_success, client_erp_id, order_erp_id = call_order_procedures(db_config, q_order.order_id)
                            if sp_success:
                                logger.info(current_job + ' | Chamadas das procedures executadas com sucesso, protocolando pedido...')
                                protocol_order(db_config=db_config, order=order, queue_order=q_order, order_erp_id=order_erp_id, client_erp_id=client_erp_id)

            except Exception as e:
                logger.error(current_job + f' | Erro no processamento do pedido {q_order.order_id}: {str(e)}')
                api_okvendas.post_log(Log(current_job + f' | Erro no processamento do pedido {q_order.order_id}: {str(e)}', datetime.now().isoformat(), str(q_order.order_id), 'PEDIDO'))
    except Exception as e:
        logger.error(current_job + f' | Erro ao inicializar job de processamento de pedidos: {str(e)}')
        api_okvendas.post_log(Log(current_job + f' | Erro ao inicializar job de processamento de pedidos do status {status}: {str(e)}', datetime.now().isoformat(), status, 'PEDIDO'))


def protocol_order(db_config: DatabaseConfig, order: Order, queue_order: Queue, order_erp_id: str = '', client_erp_id: str = '') -> None:
    db = database.Connection(db_config)
    try:
        if order_erp_id != '':
            logger.info(current_job + f' | Protocolando pedido com codigo_referencia {order_erp_id}')
            updated_order_code = api_okvendas.put_order_erp_code(src.client_data.get('url_api') + '/pedido/integradoERP',
                                                                 src.client_data.get('token_api'),
                                                                 order.order_id,
                                                                 order_erp_id)
            if updated_order_code:
                logger.info(current_job + ' | Codigo Erp do pedido atualizado via api OkVendas')
            else:
                logger.warning(current_job + ' | Falha ao atualizar o Codigo Erp do pedido via api OkVendas')

        if client_erp_id != '':
            logger.info(current_job + f' | Protocolando cliente com codigo_referencia {client_erp_id}')
            updated_client_code = api_okvendas.put_client_erp_code(src.client_data.get('url_api') + '/cliente/codigo',
                                                                   src.client_data.get('token_api'),
                                                                   {
                                                                       'cpf_cnpj': order.user.cpf if order.user.cpf is not None or order.user.cpf != '' else order.user.cnpj,
                                                                       'codigo_cliente': client_erp_id
                                                                   })
            if updated_client_code:
                logger.info(current_job + ' | Codigo Erp do cliente atualizado via api OkVendas')
            else:
                logger.warning(current_job + ' | Falha ao atualizar o Codigo Erp do cliente via api OkVendas')

        # print(queue_order)
        logger.info(current_job + f' | Removendo pedido da fila pelo protocolo {queue_order.protocol}')
        protocoled_order = api_okvendas.put_protocol_orders([queue_order.protocol])
        if protocoled_order:
            logger.info(current_job + ' | Pedido protocolado via api OkVendas')
        else:
            logger.warning(current_job + ' | Falha ao protocolar pedido via api OkVendas')

        logger.info(current_job + ' | Protocolando pedido no banco semaforo')
        conn = db.get_conect()
        cursor = conn.cursor()
        cursor.execute(queries.get_order_protocol_command(db_config.db_type), queries.get_command_parameter(db_config.db_type, [order_erp_id, order.order_id]))
        cursor.close()
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(current_job + f' | Erro ao protocolar pedidos: {e}')
        api_okvendas.post_log(Log(current_job + f' | Erro ao protocolar pedido {queue_order.order_id}: {str(e)}', datetime.now().isoformat(), str(queue_order.order_id), 'PEDIDO'))


def protocol_non_existent_order(queue_order: Queue) -> None:
    try:
        protocoled_order = api_okvendas.put_protocol_orders([queue_order.protocol])
        if protocoled_order:
            logger.info(current_job + f' | Pedido {queue_order.order_id} protocolado via api OkVendas')
        else:
            logger.warning(current_job + f' | Falha ao protocolar pedido {queue_order.order_id} via api OkVendas')
    except Exception as ex:
        logger.error(current_job + f' | Erro ao protocolar pedido {queue_order.order_id}: {str(ex)}')
        api_okvendas.post_log(Log(current_job + f' | Erro ao protocolar pedido {queue_order.order_id}: {str(ex)}', datetime.now().isoformat(), str(queue_order.order_id), 'PEDIDO'))


def insert_temp_order(order: Order, db_config: DatabaseConfig) -> bool:
    step = ''
    db = database.Connection(db_config)
    conn = db.get_conect()
    try:
        step = 'conexao'
        cursor = conn.cursor()

        if order.user.erp_code is not None and order.user.erp_code != '':
            cursor.execute(queries.get_query_client_erp(db_config.db_type), queries.get_command_parameter(db_config.db_type, [order.user.erp_code]))
            existent_client = cursor.fetchone()
            if existent_client is None:
                # insere cliente
                step = 'insere cliente'
                logger.info(f'\tPedido {order.order_id}: Inserindo cliente')
                cursor.execute(queries.get_insert_client_command(db_config.db_type), queries.get_command_parameter(db_config.db_type, [
                    order.user.name or order.user.company_name,
                    order.user.company_name or order.user.name,
                    order.user.cpf,
                    order.user.cnpj,
                    order.user.email,
                    order.user.residential_phone,
                    order.user.mobile_phone,
                    order.user.address.zipcode,
                    order.user.address.address_type,
                    order.user.address.address_line,
                    order.user.address.number,
                    order.user.address.complement,
                    order.user.address.neighbourhood or " ",
                    order.user.address.city,
                    order.user.address.state,
                    order.user.address.reference]))
            else:
                # update no cliente existente
                step = 'update cliente'
                logger.info(f'\tPedido {order.order_id}: Atualizando cliente existente')
                cursor.execute(queries.get_update_client_sql(db_config.db_type), queries.get_command_parameter(db_config.db_type, [
                    order.user.name,
                    order.user.company_name or order.user.name,
                    order.user.cpf,
                    order.user.cnpj,
                    order.user.email,
                    order.user.residential_phone,
                    order.user.mobile_phone,
                    order.user.address.zipcode,
                    order.user.address.address_type,
                    order.user.address.address_line,
                    order.user.address.number,
                    order.user.address.complement,
                    order.user.address.neighbourhood,
                    order.user.address.city,
                    order.user.address.state,
                    order.user.address.reference,
                    order.user.erp_code]))

            if cursor.rowcount > 0:
                logger.info(current_job + f' | Cliente inserido/atualizado para o pedido {order.order_id}')
                cursor.execute(queries.get_query_client(db_config.db_type), queries.get_command_parameter(db_config.db_type, [order.user.email]))
                client_id = cursor.fetchone()
                if client_id is None:
                    cursor.close()
                    raise Exception('Nao foi possivel obter o cliente inserido do banco de dados')
            else:
                cursor.close()
                raise Exception('O cliente nao foi inserido')

        # insere pedido
        step = 'insere pedido'
        logger.info(f'\tPedido {order.order_id}: Inserindo cabecalho pedido')
        cursor.execute(queries.get_insert_order_command(db_config.db_type), queries.get_command_parameter(db_config.db_type, [
            order.order_id,
            order.order_code,
            str(datetime.strptime(order.date.replace('T', ' '), '%Y-%m-%d %H:%M:%S') if order.date is not None else ''),
            order.status,
            client_id[0],
            order.total_amount,
            order.total_discount,
            order.freight_amount,
            order.additional_payment_amount,
            str(datetime.strptime(order.paid_date.replace('T', ' '), '%Y-%m-%d %H:%M:%S') if order.paid_date is not None else ''),
            order.payment_type,
            order.flag,
            order.parcels,
            order.erp_payment_condition,
            order.tracking_code,
            str(datetime.strptime(order.delivery_forecast.replace('T', ' '), '%Y-%m-%d %H:%M:%S') if order.delivery_forecast is not None else ''),
            order.carrier,
            order.shipping_mode,
            order.channel_id]))

        if cursor.rowcount > 0:
            logger.info(current_job + f' | Pedido {order.order_id} inserido')
            cursor.execute(queries.get_query_order(db_config.db_type), queries.get_command_parameter(db_config.db_type, [order.order_id]))
            order_id = cursor.fetchone()
            if order_id is None:
                cursor.close()
                raise Exception('Nao foi possivel obter o pedido inserido no banco de dados')
        else:
            cursor.close()
            raise Exception('O cliente nao foi inserido')

        # insere itens
        step = 'insere itens'
        logger.info(f'\tPedido {order.order_id}: Inserindo itens do pedido')
        for item in order.items:
            cursor.execute(queries.get_insert_order_items_command(db_config.db_type), queries.get_command_parameter(db_config.db_type, [
                order.order_id,
                item.sku,
                item.erp_code,
                item.quantity,
                item.ean,
                item.value,
                item.discount,
                item.freight_value]))

        cursor.close()
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(current_job + f' | Passo {step} - Erro durante a inserção dos dados do pedido {order.order_id}: {str(e)}')
        api_okvendas.post_log(Log(current_job + f' | Passo {step} - Erro durante a inserção dos dados do pedido {order.order_id}: {str(e)}', datetime.now().isoformat(), str(order.order_id), 'PEDIDO'))
        conn.rollback()
        conn.close()
        return False


def call_order_procedures(db_config: DatabaseConfig, order_id: int) -> (bool, str, str):
    client_erp_id = ''
    order_erp_id = ''
    success = True
    db = database.Connection(db_config)
    conn = db.get_conect()
    try:
        cursor = conn.cursor()
        logger.info(current_job + f' | Executando procedure de cliente')
        client_out_value = cursor.var(str)
        cursor.callproc('OPENK_SEMAFORO.SP_PROCESSA_CLIENTE', [order_id, client_out_value])
        client_erp_id = client_out_value.getvalue()
        if client_erp_id is not None:
            logger.info(current_job + f' | Cliente ERP criado com sucesso {client_erp_id}. Commitando transacao...')
            conn.commit()
            order_out_value = cursor.var(str)
            logger.info(current_job + f' | Executando procedure de pedido')
            # type(client_erp_id)
            cursor.callproc('OPENK_SEMAFORO.SP_PROCESSA_PEDIDO', [order_id, int(client_erp_id), order_out_value])
            order_erp_id = order_out_value.getvalue()
            if order_erp_id is not None:
                logger.info(current_job + f' | Pedido ERP criado com sucesso {order_erp_id}')
            else:
                success = False
                logger.warning(current_job + f' | Nao foi possivel obter o id do pedido do ERP (retorno da procedure)')
        else:
            success = False
            logger.warning(current_job + f' | Nao foi possivel obter o id do cliente do ERP (retorno da procedure)')

        cursor.close()
        if success:
            conn.commit()
        else:
            conn.rollback()
        conn.close()
        return success, client_erp_id, order_erp_id
    except Exception as e:
        logger.error(current_job + f' | Erro: {e}')
        api_okvendas.post_log(Log(current_job + f' | Erro no método de chamada da procedure de internalização do pedido {order_id}: {str(e)}', datetime.now().isoformat(), str(order_id), 'PEDIDO'))
        conn.rollback()
        conn.close()


def call_update_order_procedure(db_config: DatabaseConfig, order: Order) -> bool:
    success = True
    db = database.Connection(db_config)
    conn = db.get_conect()
    try:
        cursor = conn.cursor()
        order_updated = cursor.var(int)
        cursor.callproc('OPENK_SEMAFORO.SP_ATUALIZA_PEDIDO', [order.order_id, order.status, order_updated])
        updated = order_updated.getvalue()
        if updated is None or updated <= 0:
            success = False
            logger.warning(current_job + f' | Nao foi possivel atualizar o pedido informado')

        cursor.close()
        if success:
            conn.commit()
        else:
            conn.rollback()
        conn.close()
        return success
    except Exception as e:
        logger.error(current_job + f' | Erro: {e}')
        api_okvendas.post_log(Log(current_job + f' | Erro no método de chamada da procedure de atualização do pedido {order.order_id}: {str(e)}', datetime.now().isoformat(), str(order.order_id), 'PEDIDO'))
        conn.rollback()
        conn.close()


def check_order_existence(db_config: DatabaseConfig, order_id: int) -> bool:
    db = database.Connection(db_config)
    conn = db.get_conect()
    try:
        cursor = conn.cursor()
        cursor.execute(queries.get_query_order(db_config.db_type), queries.get_command_parameter(db_config.db_type, [order_id]))
        existent_order = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return existent_order is not None and existent_order > 0
    except Exception as e:
        conn.close()
        return False


def query_invoices(db_config: DatabaseConfig) -> list[Invoice]:
    """
    Consulta as notas fiscais a serem enviadas na api do okvendas
    Args:
        db_config: Configuracao do banco de dados

    Returns:
        Lista de notas fiscais para enviar
    """
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    invoices = list[Invoice]
    try:
        cursor.execute(db_config.sql.replace(';', ''))
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        cursor.close()
        conn.close()
        if len(results) > 0:
            invoices = [Invoice(**p) for p in results]

    except Exception as ex:
        logger.error(f' Erro ao consultar notas fiscais no banco:  {ex}')

    return invoices


def query_trackings(db_config: DatabaseConfig) -> list[Tracking]:
    """
    Consulta os rastreios a serem enviados na api do okvendas
    Args:
        db_config: Configuracao do banco de dados

    Returns:
        Lista de notas fiscais para enviar
    """
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    trackings = list[Tracking]
    try:
        cursor.execute(db_config.sql.replace(';', ''))
        rows = cursor.fetchall()
        columns = [col[0].lower() for col in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        cursor.close()
        conn.close()
        if len(results) > 0:
            trackings = [Tracking(**p) for p in results]

    except Exception as ex:
        logger.error(f' Erro ao consultar rastreios no banco: {ex}')

    return trackings

