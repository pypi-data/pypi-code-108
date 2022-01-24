import logging
import src.database.connection as database
from src.database import queries
from src.database.utils import DatabaseConfig
import src.database.utils as utils
from src.entities.product import Product
import src.api.okvendas as api_okvendas

logger = logging.getLogger()


def job_update_products_semaphore(job_config_dict: dict):
    try:
        db_config = utils.get_database_config(job_config_dict)
        if db_config.sql is None:
            logger.warning(job_config_dict.get('job_name') + ' | Comando sql para criar produtos nao encontrado')
            return

        db = database.Connection(db_config)
        connection = db.get_conect()
        cursor = connection.cursor()

        cursor.execute(db_config.sql)
        cursor.close()

        logger.info(job_config_dict.get('job_name') + f' | Produtos marcados para atualizar no banco semaforo: {cursor.rowcount}')
        connection.commit()
        connection.close()

    except Exception as e:
        logger.error(job_config_dict.get('job_name') + f' | Erro ao atualizar produtos no banco semaforo: {e}', exc_info=True)


def job_insert_products_semaphore(job_config_dict: dict):
    """
    Job que realiza a insercao dos produtos no banco semaforo
    Args:
        job_config_dict: Dicionario contendo configuracoes do job (obtidos na api oking)
    """
    try:
        db_config = utils.get_database_config(job_config_dict)
        if db_config.sql is None:
            logger.warning(job_config_dict.get('job_name') + ' | Comando sql para criar produtos nao encontrado')
            return

        # abre a connection com o banco
        db = database.Connection(db_config)
        connection = db.get_conect()
        cursor = connection.cursor()
        logger.info(job_config_dict.get('job_name') + f' | Conectado ao banco de dados {db_config.db_name}')

        try:
            insert_list = [insert for insert in db_config.sql.split(';') if insert != '']
            # executa o insert
            for i in insert_list:
                logger.info(job_config_dict.get('job_name') + f' | Executando comando sql {i}')
                cursor.execute(i)

            cursor.close()
            connection.commit()
            connection.close()
        except Exception as e:
            logger.error(job_config_dict.get('job_name') + f' | Erro ao inserir produtos no banco semaforo: {e}', exc_info=True)
            cursor.close()
            connection.close()

    except Exception as e:
        logger.error(job_config_dict.get('job_name') + f' | Erro ao durante a execucao do job: {e}', exc_info=True)


def job_send_products(job_config_dict: dict):
    """
    Job que realiza a leitura dos produtos contidos no banco semaforo e envia para a api okvendas
    Args:
        job_config_dict: Dicionario contendo configuracoes do job (obtidos na api oking)
    """
    try:
        db_config = utils.get_database_config(job_config_dict)
        if db_config.sql is None:
            logger.warning(job_config_dict.get('job_name') + ' | Comando sql para criar produtos nao encontrado')
            return

        produtos = query_products(db_config)
        if len(produtos) <= 0:
            logger.warning(job_config_dict.get('job_name') + ' | Nao existem produtos para criar no momento')
            return

        produtos_protocolar = []
        for prod in produtos:
            try:
                response = api_okvendas.post_produtos([prod])

                for res in response:
                    if res.status > 1:
                        logger.warning(job_config_dict.get('job_name') + f' | Erro ao gerar produto {res.codigo_erp} na api okvendas. Erro gerado na api: {res.message}')
                    else:
                        logger.info(job_config_dict.get('job_name') + f' | Produto {res.codigo_erp} criado com sucesso')
                        produtos_protocolar.append({'codigo_erp': prod.codigo_erp, 'codigo_erp_sku': prod.preco_estoque[0].codigo_erp_atributo})
            except Exception as e:
                logger.error(job_config_dict.get('job_name') + f' | Erro durante o envio de produtos: {e}', exc_info=True)

        protocol_products(produtos_protocolar, db_config)

    except Exception as e:
        logger.error(job_config_dict.get('job_name') + f' | Erro ao durante a execucao do job: {e}', exc_info=True)


def query_products(db_config: DatabaseConfig):
    """
    Consulta os produtos contidos no banco semaforo juntamente com os dados do banco do ERP
    Args:
        db_config: Configuracao do banco de dados

    Returns:
        Lista de produtos
    """
    # abre a connection com o banco
    db = database.Connection(db_config)
    connection = db.get_conect()
    # connection.start_transaction()
    cursor = connection.cursor()

    # obtem os dados do banco
    # logger.warning(query)
    cursor.execute(db_config.sql)
    columns = [col[0] for col in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]

    cursor.close()
    connection.close()

    produtos = []
    for result in results:
        produtos.append(Product(result))

    return produtos


def protocol_products(products: list, db_config: DatabaseConfig) -> None:
    """
    Protocola no banco semaforo os produtos que foram enviados para a api okvendas
    Args:
        products: Lista de produtos enviados para a api okvendas
        db_config: Configuracao do banco de dados
    """
    try:
        if len(products) > 0:
            db = database.Connection(db_config)
            connection = db.get_conect()
            cursor = connection.cursor()
            for prod in products:
                try:
                    dados_produto = [prod['codigo_erp'], prod['codigo_erp_sku']]
                    logger.info(f'Protocolando sku {dados_produto[1]}')
                    cursor.execute(queries.get_product_protocol_command(db_config.db_type), queries.get_command_parameter(db_config.db_type, dados_produto))
                    logger.info(f'Linhas afetadas {cursor.rowcount}')
                except Exception as e:
                    logger.error(f'Erro ao protocolar sku {prod["codigo_erp_sku"]}: {e}', exc_info=True)
            cursor.close()
            connection.commit()
            connection.close()
    except Exception as e:
        raise e
