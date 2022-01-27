import requests as req
import jsonpickle
import logging

logger = logging.getLogger()


class Module:
    def __init__(self, job: str, comando_sql: str, unidade_tempo: str, tempo_execucao: int):
        self.job_name = job
        self.sql = comando_sql
        self.time_unit = unidade_tempo
        self.time = tempo_execucao


def get(url: str, params: dict = None):
    response = req.get(url, params)
    if str(response.status_code).startswith('2'):
        return jsonpickle.decode(response.content)
    else:
        logger.error(f'Erro ao executar GET: {url} | Code: {response.status_code} | {response.content}')

    return None
