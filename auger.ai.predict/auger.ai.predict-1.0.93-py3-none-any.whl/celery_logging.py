import logging
import os

from celery import current_task
from celery.signals import after_setup_task_logger, after_setup_logger, task_prerun
from celery.utils.log import get_task_logger
from logstash import TCPLogstashHandler
from logstash_async.handler import LogstashFormatter

class MyTCPLogstashHandler(TCPLogstashHandler):
    def makePickle(self, record):
        data = self.formatter.format(record)

        if isinstance(data, str):
            data = str.encode(data)

        return data + b'\n'

class LogstashFormatterWithSessionID(LogstashFormatter):
    def format(self, record):
        task = current_task
        experiment_session_id = None

        if task and task.request:
            record.__dict__.update(task_id=task.request.id)

            args = task.request.args[0]
            if args:
                experiment_session_id = args.get('augerInfo', {}).get('experiment_session_id')

        if experiment_session_id:
            record.__dict__.update(experiment_session_id=experiment_session_id)
        else:
            record.__dict__.setdefault('experiment_session_id', '-')

        return super().format(record)

@after_setup_logger.connect
@after_setup_task_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    handler = MyTCPLogstashHandler(
        os.environ.get('LOGSTASH_HOST', 'logstash-logstash'),
        int(os.environ.get('LOGSTASH_PORT', '5000')),
    )
    handler.setFormatter(LogstashFormatterWithSessionID())
    logger.addHandler(handler)

    return logger

logger = get_task_logger(__name__)

@task_prerun.connect
def log_task_prerun(sender, task_id, task, *args, **kwargs):
    # When Celery logs "Received task:" there is no current_task yet and whe can't identify session id
    logging.info(f'Run task: {task.name}[{task_id}]')
