from datetime import datetime
import logging
import src.api.okvendas as api_okvendas
from src.entities.log import Log

logger = logging.getLogger()


def send_execution_notification(job_config: dict) -> None:
    logger.info(job_config.get('job_name') + ' | Notificando execucao api okvendas')
    api_okvendas.post_log(Log(f'Oking em execucao desde {job_config.get("execution_start_time")} com {job_config.get("job_qty")} jobs para o cliente {job_config.get("integration_id")}', datetime.now().isoformat(), '', 'NOTIFICACAO'))
