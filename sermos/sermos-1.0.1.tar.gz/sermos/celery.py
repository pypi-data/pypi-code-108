""" Configure and instantiate Celery
"""
import os

from sermos.constants import DEFAULT_RETRY_TASK_MAX_TTL, DEFAULT_MAX_RETRY

if os.environ.get('USE_GEVENT', "False").lower() == 'true':
    from gevent import monkey
    monkey.patch_all()

import random
import time

from celery_dyrygent.tasks import register_workflow_processor

import sys
import logging
from typing import List
from celery import Celery
from sermos.logging_config import setup_logging
from sermos.utils.module_utils import SermosModuleLoader
from sermos.utils.task_utils import PipelineGenerator, PipelineResult, \
    get_service_config_for_worker
from sermos.extensions import sermos_config, sermos_client_version
from sermos import __version__

logger = logging.getLogger('celery')
ENABLE_TOOLS = str(os.environ.get('ENABLE_TOOLS', 'false')).lower() == 'true'
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
OVERLOAD_ES = os.environ.get('ENV', 'production').lower() == 'production'
PIPELINE_CHORD_COMPRESSION = os.environ.get('PIPELINE_CHORD_COMPRESSION', None)

setup_logging(app_version=__version__,
              client_version=sermos_client_version,
              default_level=LOG_LEVEL,
              overload_elasticsearch=OVERLOAD_ES,
              establish_logging_config=True)


def pipeline_retry(event: dict):
    """ Handle pipeline retry and deadletter logic.
    """
    access_key = event.get('access_key', None)
    pipeline_id = event.get('pipeline_id', None)
    execution_id = event.get('execution_id', None)
    if pipeline_id is None or execution_id is None:
        logger.error(f"Unable to retry pipeline {pipeline_id} / "
                     f"execution {execution_id}.")
        return False

    # generate_chain() will return `None` if the pipeline has exceeded
    # max retry count or other erorrs happen.
    gen = PipelineGenerator(pipeline_id=pipeline_id,
                            access_key=access_key,
                            execution_id=execution_id,
                            queue=event.get('queue', None),
                            default_task_ttl=event.get('default_task_ttl',
                                                       None),
                            add_retry=event.get('add_retry', False),
                            chain_payload=event.get('chain_payload', None))

    if gen.good_to_go:
        chain = gen.generate_chain()
        if chain is not None:
            # Exponential backoff
            exponential_backoff = min((3 ** gen.pipeline_wrapper.retry_count) +
                                      (random.randint(0, 1000) / 1000),
                                      DEFAULT_RETRY_TASK_MAX_TTL)
            logger.debug(f"Exponential backoff sleep {exponential_backoff}")
            time.sleep(exponential_backoff)
            # Kick it off again.
            chain.apply_async()

    logger.warning(f"Pipeline retry was invoked for {pipeline_id} "
                   f"({execution_id})")
    return True


def task_chain_regulator(*args, **kwargs):
    """ Utility task to ensure celery properly waits between groups in a chain.

        For a chain(), if each element is a group() then celery does not
        properly adhere to the chain elements occurring sequentially. If you
        insert a task that is not a group() in between, though, then the
        chain operates as expected.
    """
    return True


def pipeline_success(event: dict):
    """ Utility task to ensure celery properly waits between groups in a chain.

        For a chain(), if each element is a group() then celery does not
        properly adhere to the chain elements occurring sequentially. If you
        insert a task that is not a group() in between, though, then the
        chain operates as expected.
    """
    pr = PipelineResult(event['execution_id'])
    pr.load()
    pr.save(status='success')


class GenerateCeleryTasks(SermosModuleLoader):
    """ Use the sermos.yaml configuration to turn customer methods into
        decorated celery tasks that are available for work/pipelines
    """
    def __init__(self, config: dict, celery_instance: Celery):
        super(GenerateCeleryTasks, self).__init__()
        self.config = config if config else {}
        self.celery = celery_instance

    def _get_default_tasks(self) -> List[dict]:
        """ Sermos provides default tasks that all workers should know about.
        """
        return [{
            'handler': 'sermos.celery.pipeline_retry'
        }, {
            'handler': 'sermos.celery.task_chain_regulator'
        }, {
            'handler': 'sermos.celery.pipeline_success'
        }]

    def generate(self):
        """ Loads methods based on sermos config file and decorates them as
            celery tasks.

            Customer's methods:
            --------------------------------
            def demo_task(*args, **kwargs):
                return True

            Turns into the equivallent of:
            --------------------------------
            @celery.task(queue='queue-name')
            def demo_task(*args, **kwargs):t
                return True
        """
        # Set in k8s deployment as an environment variable when Sermos Cloud
        # generates the final secrets.yaml file. The name comes from the user's
        # sermos.yaml file based on serviceConfig[].name. Each 'worker' will
        # have a single name and each individually registers tasks through its
        # registeredTasks list. This allows each worker to only attempt
        # bootstrapping those tasks that are relevant to the worker and not, for
        # example, attempt to import a package that's not used by this worker
        service = get_service_config_for_worker(self.config)
        if not service:
            return
        for task in service.get('registeredTasks', []):
            try:
                worker_path = task['handler']  # Required, no default

                tmp_handler = self.get_callable(worker_path)

                # Decorate the method as a celery task along with a default
                # queue if provided in config. Set ChainedTask as the base
                # which allows chained tasks to pass kwargs correctly.
                tmp_handler = self.celery.task(tmp_handler)
            except Exception as e:
                logger.warning(f"Unable to add a task to celery: {e}")
        # Sermos provides default tasks that all workers should know about, add
        # them here.
        for task in self._get_default_tasks():
            tmp_handler = self.get_callable(task['handler'])
            tmp_handler = self.celery.task(tmp_handler)


def configure_celery(celery: Celery):
    """ Configure Sermos-compatible Celery instance. Primarily this means
    compatibility with Pipelines and Scheduled Tasks through injecting the
    event kwarg. Also sets prebaked defaults that can be overloaded by user.
    """
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', REDIS_URL)
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', REDIS_URL)
    TaskBase = celery.Task

    class ChainedTask(TaskBase):
        """ A Celery Task that is used as the _base_ for all dynamically
        generated tasks (by GenerateCeleryTasks().generate()). This injects
        `event` into every task's signature, which allows pipelines to pass
        event information easily through a chain.
        """
        abstract = True
        autoretry_for = (Exception,)
        max_retries = DEFAULT_MAX_RETRY
        retry_backoff = True
        retry_jitter = True

        def __call__(self, *args, **kwargs):
            """ Allow the return value of one task to update the kwargs of a
                subsequent task if it's a dictionary. Important to the function
                of a pipeline to allow event information to flow easily.
            """
            # Inject app context
            if len(args) == 1 and isinstance(args[0], dict):
                kwargs.update(args[0])
                args = ()

            # Event holds information used in PipelineRunWrapper and
            # other areas.
            if 'event' not in kwargs.keys():
                kwargs['event'] = {}
            # This is a special worker from dyrygent that orchestrates our
            # pipelines.  It provides a patch in fix for celery's poor
            # implementation of Canvas work-flows
            if self.__name__ == 'workflow_processor':
                kwargs.pop('event', None)
            return super(ChainedTask, self).__call__(*args, **kwargs)

    celery.Task = ChainedTask

    # Configure the broker and tasks
    celery.conf.broker_url = CELERY_BROKER_URL

    # Use our custom database scheduler for dynamic celery beat updates.
    celery.conf.beat_scheduler =\
        'sermos.celery_beat:SermosScheduler'

    # Reasonable defaults, override as necessary
    celery.conf.worker_redirect_stdouts = True
    celery.conf.worker_redirect_stdouts_level = LOG_LEVEL
    celery.conf.worker_hijack_root_logger = False

    if PIPELINE_CHORD_COMPRESSION:
      celery.conf.task_compression = PIPELINE_CHORD_COMPRESSION

    # NOTE: The broker URL may not be the best result backend. For example,
    # When using Rabbit as the broker (recommended), you should use Redis
    # as the result backend, as Rabbit has horrible support as backend.
    celery.conf.result_backend = CELERY_RESULT_BACKEND
    celery.conf.task_ignore_result = False  # Must not ignore for Chords
    celery.conf.task_acks_late = False  # Check per worker
    celery.conf.result_expires = int(
        os.environ.get('CELERY_RESULT_EXPIRES', 10800))  # 3 hours by default
    celery.conf.broker_pool_limit = int(os.environ.get('BROKER_POOL_LIMIT',
                                                       10))
    celery.conf.worker_max_tasks_per_child = int(
        os.environ.get('MAX_TASKS_PER_CHILD', 100))
    celery.conf.task_soft_time_limit =\
        int(os.environ.get('TASK_TIMEOUT_SECONDS', 3600))
    celery.conf.task_time_limit =\
        int(os.environ.get('TASK_TIMEOUT_SECONDS', 3600)) + 10  # Cleanup buffer
    celery.conf.task_serializer = 'json'
    celery.conf.result_serializer = 'json'
    celery.conf.accept_content = ['json']
    # Required config options for some brokers we use frequently.
    transport_options = {}
    celery.conf.broker_transport_options = transport_options

    # Sermos generally has long-running tasks (relatively speaking), so
    # limit number of jobs a worker can reserve. This may not be true for
    # all tasks, so configure this on a per application basis. In the event
    # mutltiple task kinds exist in an application (short and long), see
    # http://docs.celeryproject.org/en/latest/userguide/optimizing.html#optimizing-prefetch-limit
    # for some guidance on combining multiple workers and routing tasks.
    # TODO make configurable from env
    celery.conf.worker_prefetch_multiplier = 1

    # Add our application's workers & any other tasks to be made
    # available
    register_workflow_processor(celery)
    try:
        GenerateCeleryTasks(sermos_config, celery).generate()
    except Exception as e:
        logger.error(f"Unable to dynamically generate celery tasks: {e}")
        sys.exit(1)

    return celery
