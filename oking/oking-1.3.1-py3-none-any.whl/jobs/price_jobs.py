from datetime import datetime
import logging
import src.database.connection as database
import src.database.utils as utils
from src.database.utils import DatabaseConfig
import src.api.okvendas as api_okvendas
from src.entities.price import Price
from src.entities.response import PriceResponse
from src.database import queries
import src
import time
from src.entities.log import Log

logger = logging.getLogger()


def job_insert_prices_semaphore(job_config_dict: dict):
    """
    Job para preços no banco semáforo
    Args:
        job_config_dict: Configuração do job
    """
    db_config = utils.get_database_config(job_config_dict)
    if db_config.sql is None:
        logger.warning(job_config_dict.get('job_name') + ' | Comando sql para inserir precos no semaforo nao encontrado')
    else:
        db = database.Connection(db_config)
        conn = db.get_conect()
        cursor = conn.cursor()

        try:
            logger.info(job_config_dict.get('job_name') + ' | Inserindo precos no banco semaforo')
            logger.info(db_config.sql)
            cursor.execute(db_config.sql)
            logger.info(job_config_dict.get('job_name') + f' | {cursor.rowcount} precos inseridos no banco semaforo')
        except Exception as ex:
            logger.error(job_config_dict.get('job_name') + ' | Erro ' + str(ex), exc_info=True)

        cursor.close()
        conn.commit()
        conn.close()


def job_send_prices(job_config_dict: dict):
    """
    Job para realizar a atualização de preços
    Args:
        job_config_dict: Configuração do job
    """
    try:
        db_config = utils.get_database_config(job_config_dict)
        if db_config.sql is None:
            logger.warning(job_config_dict.get('job_name') + ' | Comando sql para inserir precos no semaforo nao encontrado')
        else:
            prices_to_protocol = []
            prices = query_prices(db_config)
            if prices is not None and len(prices) > 0:
                logger.info(job_config_dict.get('job_name') + f' | Produtos para atualizar preco {len(prices)}')

                for price in prices:
                    try:
                        time.sleep(0.5)
                        response = api_okvendas.post_prices(src.client_data.get('url_api') + '/catalogo/preco', price, src.client_data.get('token_api'))
                        if response.status == 1:
                            prices_to_protocol.append(price)
                        else:
                            logger.warning(job_config_dict.get('job_name') + f' | Nao foi possivel atualizar o preco do sku {price.codigo_erp}. Erro recebido da Api: {response.message}')
                            api_okvendas.post_log(Log(job_config_dict.get('job_name') + f' | Erro ao atualizar preço do sku {price.codigo_erp}: {response.message}', datetime.now().isoformat(), price.codigo_erp, 'PRECO'))
                    except Exception as e:
                        logger.warning(job_config_dict.get('job_name') + f' | Falha ao atualizar preco do sku {price.codigo_erp}: {str(e)}')

                protocol_prices(db_config, prices_to_protocol)

            else:
                logger.warning(job_config_dict.get('job_name') + ' | Nao existem precos a serem enviados no momento')
    except Exception as e:
        logger.error(job_config_dict.get('job_name') + f' | Erro durante execucao do job: {e}')


def query_prices(db_config: DatabaseConfig) -> list[Price]:
    """
    Consulta os precos para atualizar no banco de dados
    Args:
        db_config: Configuracao do banco de dados

    Returns:
        Lista de preços para atualizar
    """
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    try:
        cursor.execute(db_config.sql)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        results = list(dict(zip(columns, row)) for row in rows)
        cursor.close()
        conn.close()
        if len(results) > 0:
            prices = [Price(**p) for p in results]
            return prices

    except Exception as ex:
        logger.error(f' Erro ao consultar precos no banco semaforo:  {ex}')

    return []


def protocol_prices(db_config: DatabaseConfig, prices: list[Price]) -> None:
    """
    Protocola os preços no banco semáforo
    Args:
        db_config: Configuração do banco de dados
        prices: Lista de skus para protocolar
    """
    db = database.Connection(db_config)
    conn = db.get_conect()
    cursor = conn.cursor()
    sql = queries.get_price_protocol_command(db_config.db_type)
    for p in prices:
        try:
            cursor.execute(sql, queries.get_command_parameter(db_config.db_type, [p.preco_atual, p.preco_lista, p.preco_custo, p.codigo_erp]))
        except Exception as e:
            logger.warning(f'Erro ao protocolar preco do sku {p}: {e}')

    cursor.close()
    conn.commit()
    conn.close()
