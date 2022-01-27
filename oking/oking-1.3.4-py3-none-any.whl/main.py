from time import sleep
import schedule
import logging
import src
from src.jobs import products_jobs
from src.api import oking

logger = logging.getLogger()
modules: list = [oking.Module(**m) for m in src.client_data.get('modulos')]
assert modules is not None, 'Nao foi possivel obter os modulos da integracao. Por favor, entre em contato com o suporte.'


# region Estoques

def instantiate_insert_stock_semaphore_job(job_config: dict) -> None:
    """
    Instancia o job de inserção/atualização de estoques na tabela de semáforo
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    # sproduto.insere_estoque_semaforo()


def instantiate_send_stock_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos estoques para a api okVendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    # sproduto.atualizar_estoques()


# endregion Estoques


# region Precos

def instantiate_insert_price_semaphore_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos estoques para a api okVendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    # sproduto.insere_preco_semaforo()


def instantiate_send_price_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos estoques para a api okVendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    # sproduto.atualizar_precos()


# endregion Precos


# region Produtos

def instantiate_insert_products_semaphore_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos estoques para a api okVendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    products_jobs.job_insert_products_semaphore(job_config)


def instantiate_update_products_semaphore_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos estoques para a api okVendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    products_jobs.job_update_products_semaphore(job_config)


def instantiate_send_products_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos estoques para a api okVendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')
    products_jobs.job_send_products(job_config)


# endregion Produtos


# region Pedidos

def instantiate_internalize_orders_job(job_config: dict) -> None:
    """
    Instancia o job de envio dos estoques para a api okVendas
    Args:
        job_config: Configuração do job obtida na api do oking
    """
    logger.info(job_config.get('job_name') + ' | Iniciando execucao')

# endregion Pedidos


def schedule_job(job_config: dict, time_unit: str, time: int) -> None:
    logger.info(f'Adicionando job {job_config.get("job_name")} ao schedule de {time} em {time} {time_unit}')
    if time_unit == 'M':  # Minutos
        func = get_job_from_name(job_config.get('job_name'))
        schedule.every(time).minutes.do(func, job_config)
    elif time_unit == 'H':  # Horas
        func = get_job_from_name(job_config.get('job_name'))
        schedule.every(time).hours.do(func, job_config)
    elif time_unit == 'D':  # Dias
        func = get_job_from_name(job_config.get('job_name'))
        schedule.every(time).days.do(func, job_config)


def get_job_from_name(job_name: str):
    if job_name == 'insere_estoque_produto_semaforo_job':
        return instantiate_insert_stock_semaphore_job
    elif job_name == 'envia_estoque_produtos_job':
        return instantiate_send_stock_job
    elif job_name == 'insere_preco_produto_semaforo_job':
        return instantiate_insert_price_semaphore_job
    elif job_name == 'envia_preco_produtos_job':
        return instantiate_send_price_job
    elif job_name == 'envia_catalogo_produto_semaforo_job':
        return instantiate_insert_products_semaphore_job
    elif job_name == 'envia_catalogo_produto_loja_job':
        return instantiate_send_products_job
    elif job_name == 'internaliza_pedidos_job':
        return instantiate_internalize_orders_job


for module in modules:
    schedule_job({
        'db_host': src.client_data.get('host'),
        'db_user': src.client_data.get('user'),
        'db_type': src.client_data.get('db_type'),
        'db_name': src.client_data.get('database'),
        'db_pwd': src.client_data.get('password'),
        'db_client': src.client_data.get('host'),
        'job_name': module.job_name,
        'sql': module.sql
    }, module.time_unit, module.time)


def start():
    while True:
        schedule.run_pending()
        sleep(5)


start()
