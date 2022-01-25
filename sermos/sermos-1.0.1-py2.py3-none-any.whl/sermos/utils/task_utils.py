""" Utilities for running and managing tasks inside pipelines.
"""
import os
import logging
import uuid
from typing import List, Any, Union
from networkx.classes.digraph import DiGraph
from celery import chain, signature, chord

from sermos.constants import DEFAULT_TASK_TTL, \
    DEFAULT_REGULATOR_TASK, CHAIN_SUCCESS_MSG, CHAIN_FAILURE_MSG, \
    PIPELINE_RUN_WRAPPER_CACHE_KEY, DEFAULT_SUCCESS_TASK, DEFAULT_RESULT_TTL, \
    PIPELINE_RESULT_CACHE_KEY, DEFAULT_RETRY_TASK, DEFAULT_MAX_RETRY, \
    DEFAULT_RETRY_TASK_MAX_TTL
from sermos_tools import SermosTool
from sermos.utils.graph_utils import get_execution_graph, get_chainable_tasks
from sermos.utils.config_utils import retrieve_latest_pipeline_config, \
    load_json_config_from_redis, set_json_config_to_redis
from sermos.pipeline_config_schema import PipelineConfigValidator

logger = logging.getLogger(__name__)
WORKER_NAME = os.environ.get('WORKER_NAME', None)


def get_service_config_for_worker(sermos_config: dict,
                                  worker_name: str = None
                                  ) -> Union[dict, None]:
    """ For the current WORKER_NAME (which must be present in the environment
    of this worker instance for a valid deployment), return the worker's
    serviceConfig object.
    """
    if sermos_config is None:
        raise ValueError('Sermos config was not provided')
    if worker_name is None:
        worker_name = WORKER_NAME
    if worker_name is None:
        return None

    service_config = sermos_config.get('serviceConfig', [])
    for service in service_config:
        if service['serviceType'] == 'celery-worker' and service[
                'name'] == worker_name:
            return service

    raise ValueError('Could not find a service config for worker '
                     f'`{worker_name}`. Make sure you have added the service in'
                     f' your sermos.yaml with `name: {worker_name}` and '
                     '`type: celery-worker`.')


def get_task_signature(task_path: str,
                       queue: str,
                       access_key: str = None,
                       pipeline_id: str = None,
                       execution_id: str = None,
                       max_ttl: int = None,
                       immutable: bool = True,
                       task_config: dict = None,
                       custom_event_data: dict = None) -> signature:
    """ Generate a task signature with enforced event keyword
    """
    if task_config is None:
        task_config = dict()
    if custom_event_data is None:
        custom_event_data = dict()

    if queue is None:
        # Look for a pipeline task configuration, if one was provided then we
        # use queue specified on that task if it's specified.
        queue = task_config.get('queue', None)

        # If we still have None or 'default' (for backwards compability), raise
        # because we're not requiring that a queue is specified.
        if queue in (None, 'default'):
            raise ValueError('Must set queue for a worker or registeredTask.')

    if max_ttl is None:
        # First look on the pipeline configuration, if a max_ttl is specified,
        # then we're using that regardless.
        max_ttl = task_config.get('maxTtl', None)

        # If we still have None or 'default', set the default queue!
        if max_ttl in (None, 'default'):
            max_ttl = DEFAULT_TASK_TTL

    kwargs = {
        'event': {
            'access_key': access_key,
            'pipeline_id': pipeline_id,
            'execution_id': execution_id
        }
    }
    if custom_event_data is not None:
        kwargs['event'] = {**kwargs['event'], **custom_event_data}

    # TODO where do we inject the 'event' data from sermos yaml schema?

    sig = signature(
        task_path,
        args=(),
        kwargs=kwargs,
        immutable=immutable,
        task_id=str(uuid.uuid4()),
        options={
            'queue': queue,
            'expires': 86400,  # Expire after 1 day. TODO make tunable.
            'soft_time_limit': max_ttl,
            'time_limit': max_ttl + 10,  # Add 10s buffer for cleanup
        })
    return sig


class PipelineRunWrapper(SermosTool):
    """ A wrapper for a single "run" of a Pipeline.

        A 'run' is defined as a single execution of a pipeline, a pipeline
        consisting of one or more steps in a chain.

        When a pipeline's run is first executed, the execution id is generated
        as a uuid. Subsequent retries of this 'run' will be able to look up
        using that execution id.

        The primary purpose for the PipelineRunWrapper is to provide a cached
        representation of the full 'run' including retry count and any payload
        that should be accessible to any step in the chain. Remember, a pipeline
        is running asynchronously and, as such, each node in the graph operates
        independent the others, this allows for consistent coordination.
    """
    pipeline_id: str = None
    pipeline_config: dict = None  # Pipeline configuration in dictionary format
    dag_config: dict = None
    execution_id: str = None
    current_event: dict = None  # For single task when from_event(). NOT cached.
    cache_key: str = None  # Set on init
    max_ttl: int = 60  # Overloaded when pipeline_config provided and it's set
    max_retry: int = 3  # Overloaded when pipeline_config provided and it's set
    retry_count: int = 0
    chain_payload: dict = None  # Optional data to pass to each step in chain
    execution_graph: DiGraph = None
    good_to_go = False
    loading_message = None

    def __init__(self,
                 pipeline_id: str,
                 pipeline_config: dict = None,
                 execution_id: str = None,
                 max_ttl: int = 60,
                 max_retry: int = 3,
                 chain_payload: dict = None,
                 current_event: dict = None):
        super().__init__()
        self.pipeline_id = pipeline_id
        self.pipeline_config = pipeline_config

        self.max_ttl = max_ttl
        self.max_retry = max_retry

        # Execution IDs uniquely identify a single run of a given pipeline.
        # If None is provided, a random id is generated, which will be cached
        # and used downstream in the event of a retry. Initial invocations
        # should generally not set this value manually.
        self.execution_id = execution_id
        if self.execution_id is None:
            self.execution_id = str(uuid.uuid4())

        self.chain_payload = chain_payload\
            if chain_payload is not None else {}

        self.current_event = current_event\
            if current_event is not None else {}

        self.cache_key = PIPELINE_RUN_WRAPPER_CACHE_KEY.format(
            self.pipeline_id, self.execution_id)

        self.good_to_go = True

    @property
    def _cachable_keys(self):
        """ For caching purposes, only store json serializable values that are
        required for caching / loading from cache.

        Note: Several keys are pulled from the pipeline_config where they are
        camelCase and set on this as snake_case. This is done for convenience
        in the wrapper. Style convention switching is to keep with the naming
        convention of all yaml files following camelCase to conform with k8s
        and all local python variables being snake_case. This extraction of
        the yaml file variables to place onto the wrapper object is done
        during the .load() stage.
        """
        return ('pipeline_config', 'max_ttl', 'max_retry', 'retry_count',
                'chain_payload', 'pipeline_id')

    def _load_from_cache(self, is_retry=False):
        """ Attempt to load this PipelineRunWrapper from cache.
        """
        logger.debug(f"Attempting to load {self.cache_key} from cache")
        try:
            cached_wrapper = load_json_config_from_redis(self.cache_key)
            if cached_wrapper is not None:
                for key in self._cachable_keys:
                    setattr(self, key, cached_wrapper[key])

                msg = f"{self.cache_key} found in cache ..."
                self.loading_message = msg
                logger.debug(msg)
            else:
                raise ValueError(f"Unable to find {self.cache_key} ...")
        except Exception as e:
            if not is_retry:
                self.good_to_go = False
                self.loading_message = e
                logger.exception(e)

        if self.pipeline_config is None:
            raise ValueError("pipeline_config not set, invalid ...")

        return

    def save_to_cache(self):
        """ Save current state of PipelineRunWrapper to cache, json serialized.
            Re-set the key's TTL

            TODO: Lock this so no race condition on concurrent steps.
        """
        logger.debug(f"Saving {self.cache_key} to cache")
        cached_json = {}
        for key in self._cachable_keys:
            cached_json[key] = getattr(self, key)
        ttl = (self.max_ttl *
               len(self.pipeline_config['taskDefinitions'])) + 10
        set_json_config_to_redis(self.cache_key, cached_json, ttl)

    @classmethod
    def from_event(cls, event):
        """ Create instance of PipelineRunWrapper from pipeline event.

        Loads the cached PipelineRunWrapper instance, which is assumed to exist
        when loading from an event (which should only occur inside a pipeline
        node, which means the pipeline has been invoked/generated previously).

        Usage::

            pipeline_wrapper = PipelineRunWrapper.from_event(event)
            # pipeline_wrapper.load()  # TODO deprecate
        """
        wrapper = cls(pipeline_id=event.get('pipeline_id', None),
                      execution_id=event.get('execution_id', None),
                      current_event=event)
        wrapper.load()
        return wrapper

    def load(self,
             verify_retry_count: bool = True,
             allow_deadletter: bool = True,
             is_retry: bool = False):
        """ Loads PipelineRunWrapper from cache

            If verify_retry_count is True, this will deadletter the task wrapper
            immediately (if deadletter=True) if retry count is exceeded.
        """
        try:
            # Pipeline config is expected to be provided when first initializing
            # a pipeline run wrapper. On subsequent runs or when loading from
            # an event, the run wrapper can be loaded using only the pipeline
            # id and execution id, the pipeline config is then initialized from
            # the wrapper
            if self.pipeline_config is None or is_retry:
                self._load_from_cache(is_retry=is_retry)
            else:
                # If the pipeline_config is set before .load(), that means
                # this invocation is coming from an initial load, not cache.
                # We don't want to re-set pipeline_config and the retry_count
                # and chain_payload are not going to exist, as they are an
                # artifact of the caching process. We also explicitly skip
                # pipeline_id, max_retry, and max_ttl keys because those are
                # metadata keys in the pipeline_config and are camel case
                # (pipelineId/maxRetry/maxTtl), we set them on this wrapper
                # object purely for convenience and to provide logical defaults.
                for key in self._cachable_keys:
                    if key in ('pipeline_config', 'pipeline_id', 'max_retry',
                               'max_ttl', 'retry_count', 'chain_payload'):
                        continue
                    setattr(self, key, self.pipeline_config[key])

            # Validate pipeline config
            PipelineConfigValidator(config_dict=self.pipeline_config)

            # Initialize the actual pipeline configuration and execution graph
            self.dag_config = self.pipeline_config['dagAdjacency']
            self.execution_graph = get_execution_graph(self.pipeline_config)

            # Overload defaults if explicitly provided
            self.max_ttl = self.pipeline_config['metadata'].get(
                'maxTtl', self.max_ttl)
            self.max_retry = self.pipeline_config['metadata'].get(
                'maxRetry', self.max_retry)

            if is_retry:
                self.increment_retry()

            if verify_retry_count and self.retry_exceeded:
                msg = "Attempted to retry {}_{}; exceeded retry count."\
                    .format(self.pipeline_id, self.execution_id)
                logger.warning(msg)
                self.loading_message = msg
                if allow_deadletter:
                    self.deadletter()
                return

            self.save_to_cache()  # Always save back to cache
        except Exception as e:
            logger.exception(e)
            self.loading_message = e
            if allow_deadletter:
                self.deadletter()
            return

        self.loading_message = "Loaded Successfully."
        return

    def increment_retry(self, exceed_max: bool = False):
        """ Increment retry_count by 1

            `cache` determines whether this will re-cache object after increment
            `exceed_max` allows an instant kickout of this to deadletter.
        """
        if exceed_max:
            new_count = self.max_retry + 1
        else:
            new_count = self.retry_count + 1

        logger.debug(f"Incrementing Retry to {new_count}")
        self.retry_count = new_count
        self.save_to_cache()

    @property
    def retry_exceeded(self):
        """ Determine if retry_count has been exceeded.
        """
        logger.debug(f"Checking retry count: {self.retry_count} / "
                     f"{self.max_retry} / {self.retry_count > self.max_retry}")
        if self.retry_count >= self.max_retry:
            return True
        return False

    def deadletter(self):
        """ Add details of this PipelineTask to a deadletter queue.

            TODO:
            - add to a system for tracking failed pipeline runs
            - delete task wrapper and all tasks from cache
        """
        self.good_to_go = False
        pr = PipelineResult(
            self.execution_id,
            status='failed',
            result='Pipeline retried and failed {} times.'.format(
                self.retry_count))
        pr.save()
        self.increment_retry(
            exceed_max=True)  # Ensure this won't be retried...
        return


class PipelineResult(SermosTool):
    """ Standard store for pipeline results.

        Helps keep standard way to store/retrieve results + status messages
        for pipelines.

        Can get fancier in the future by tracking retry count, pipeline
        execution time, etc.
    """
    def __init__(self,
                 execution_id: str,
                 status: str = None,
                 result: Any = None,
                 result_ttl: int = DEFAULT_RESULT_TTL):
        super().__init__()
        self.execution_id = execution_id
        if self.execution_id is None:
            raise ValueError("Must provide an execution_id!")
        self.status = status
        self.result = result
        self.results = result  # TODO Deprecate in future release, keep singular
        self.result_ttl = result_ttl
        self.cache_key =\
            PIPELINE_RESULT_CACHE_KEY.format(self.execution_id)

        self.valid_status_types = ('pending', 'success', 'failed',
                                   'unavailable')

        # Always validate status
        self._validate_status()

    def _validate_status(self):
        if self.status and self.status not in self.valid_status_types:
            raise ValueError("{} is not a valid status type ({})".format(
                self.status, self.valid_status_types))

    def save(self, status: str = None, result: Any = None):
        """ Save the result's current state.

            If status and/or result are not provided, then the existing instance
            state is used. You can override either by passing to this fn.

            Typical use case would be to initialize the PipelineResult with only
            the execution ID, then 'save_result()' and pass status/result.
        """
        if status is not None:
            self.status = status
        if result is not None:
            self.result = result
            self.results = result  # TODO Deprecate in future release
        set_json_config_to_redis(self.cache_key, self.to_dict(),
                                 self.result_ttl)

    def load(self):
        """ Load a pipeline result from cache.
        """
        results = load_json_config_from_redis(self.cache_key)
        if results is not None:
            for k in results:
                setattr(self, k, results[k])
        else:
            self.status = 'unavailable'
            self.result = None
            self.results = None  # TODO Deprecate in future release

    @classmethod
    def from_event(cls, event):
        """ Create initialized instance of PipelineResult from a pipeline event.

            Usage::

                pipeline_result = PipelineResult.from_event(event)
                pipeline_result.save(
                    result='my result value'
                )
        """
        pr = cls(execution_id=event.get('execution_id', None))
        pr.load()
        return pr

    def to_dict(self):
        """ Return serializable version of result for storage/retrieval.
        """
        return {
            'execution_id': self.execution_id,
            'status': self.status,
            'result': self.result,
            'results': self.result,  # TODO Deprecate in future release
            'result_ttl': self.result_ttl
        }


class PipelineGenerator(object):
    """ Allows an API endpoint to generate a functional pipeline based on the
        requested pipeline id. Allows API to then issue the tasks asynchronously
        to initiate the pipeline. Thereafter, celery will monitor status and
        handle success/failure modes so the API web worker can return
        immediately.

        The primary purpose is to unpack the pipeline config, create the
        requisite cached entities to track pipeline progress, and apply the
        chained pipeline tasks asynchronously so Celery can take over.

        Usage:
            gen = PipelineGenerator(pipeline_id)
            chain = gen.generate_chain()
            chain.on_error(custom_error_task.s())  # Optional add error handling
            chain.delay()
    """
    def __init__(self,
                 pipeline_id: str,
                 access_key: str = None,
                 execution_id: str = None,
                 queue: str = None,
                 default_task_ttl: int = None,
                 regulator_queue: str = None,
                 regulator_task: str = None,
                 success_queue: str = None,
                 success_task: str = None,
                 retry_task: str = None,
                 add_retry: bool = True,
                 default_max_retry: int = None,
                 chain_payload: dict = None):
        super().__init__()
        self.pipeline_id = pipeline_id
        self.access_key = access_key

        pipeline_config_api_resp = retrieve_latest_pipeline_config(
            pipeline_id=self.pipeline_id, access_key=self.access_key)

        if pipeline_config_api_resp is None:
            raise ValueError("Unable to load Pipeline Configuration for "
                             f"pipeline id: {self.pipeline_id} ...")

        # The only part of the API response used for any 'pipeline config'
        # is the `config` key. The API nests it under `config` to preserve
        # ability to add additional detail at a later date.
        self.pipeline_config = pipeline_config_api_resp.get('config', {})
        schema_version = pipeline_config_api_resp.get('schemaVersion')
        PipelineConfigValidator(config_dict=self.pipeline_config,
                                schema_version=schema_version)

        self.execution_id = execution_id  # UUID string
        self.good_to_go = False  # Indicates initialization/loading success
        self.loading_message = None  # Allows access to success/error messages
        self.is_retry = False if self.execution_id is None else True
        self.add_retry = add_retry
        self.retry_task = retry_task\
            if retry_task is not None else DEFAULT_RETRY_TASK

        self.default_max_retry = default_max_retry \
            if default_max_retry is not None else \
            self.pipeline_config['metadata'].get('maxRetry', DEFAULT_MAX_RETRY)

        # Queue on which to place tasks by default and default TTL per task
        # These can be overridden in PipelineConfig.config['taskDefinitions']
        self.queue = queue \
            if queue is not None \
            else self.pipeline_config['metadata']['queue']
        self.default_task_ttl = default_task_ttl \
            if default_task_ttl is not None else \
            self.pipeline_config['metadata'].get('maxTtl', DEFAULT_TASK_TTL)

        # See docstring in self._get_regulator()
        self.regulator_queue = regulator_queue \
            if regulator_queue is not None \
            else self.pipeline_config['metadata']['queue']
        self.regulator_task = regulator_task\
            if regulator_task is not None else DEFAULT_REGULATOR_TASK

        # See docstring in self._get_success_task()
        self.success_queue = success_queue \
            if success_queue is not None \
            else self.pipeline_config['metadata']['queue']
        self.success_task = success_task\
            if success_task is not None else DEFAULT_SUCCESS_TASK

        # Optional data to pass to each step in chain
        self.chain_payload = chain_payload\
            if chain_payload is not None else {}

        self.pipeline_wrapper = None  # Allows access to the PipelineRunWrapper
        self.chain = None  # Must be intentionally built with generate_chain()

        try:
            # Generate our wrapper for this pipeline_id / execution_id
            self.pipeline_wrapper = PipelineRunWrapper(
                pipeline_id=self.pipeline_id,
                pipeline_config=self.pipeline_config,
                execution_id=self.execution_id,
                max_ttl=self.default_task_ttl,
                max_retry=self.default_max_retry,
                chain_payload=self.chain_payload)

            # Loads pipeline config from remote or cache if it's already there
            # `is_retry` will be True for any PipelineGenerator instantiated
            # with an execution_id. This flag helps the wrapper increment the
            # retry count and determine if this should be deadlettered.
            # This step also saves the valid/initialized run wrapper to cache.
            self.pipeline_wrapper.load(is_retry=self.is_retry)

            # Set all variables that were established from the run wrapper
            # initialization. Notably, default_task_ttl can be overloaded
            # if the pipeline config has an explicit maxTtl set in metadata.
            self.good_to_go = self.pipeline_wrapper.good_to_go
            self.loading_message = self.pipeline_wrapper.loading_message
            self.execution_id = self.pipeline_wrapper.execution_id

        except Exception as e:
            fail_msg = "Failed to load Pipeline for id {} ... {}".format(
                self.pipeline_id, e)
            self.loading_message = fail_msg
            logger.error(fail_msg)
            raise e

    def _get_regulator(self):
        """ Create a chain regulator celery task signature.

            For a chain(), if each element is a group() then celery does not
            properly adhere to the chain elements occurring sequentially. If you
            insert a task that is not a group() in between, though, then the
            chain operates as expected.
        """
        return signature(self.regulator_task,
                         queue=self.regulator_queue,
                         immutable=True)

    def _get_success_task(self):
        """ A final 'success' task that's added to the end of every pipeline.

            This stores the 'success' state in the cached result. Users can
            set other values by using TaskRunner().save_result()
        """
        return get_task_signature(task_path=self.success_task,
                                  queue=self.success_queue,
                                  pipeline_id=self.pipeline_id,
                                  execution_id=self.execution_id)

    def _get_retry_task(self):
        """ The retry task will re-invoke a chain.
        """
        return get_task_signature(task_path=self.retry_task,
                                  queue=self.queue,
                                  access_key=self.access_key,
                                  pipeline_id=self.pipeline_id,
                                  execution_id=self.execution_id,
                                  max_ttl=DEFAULT_RETRY_TASK_MAX_TTL,
                                  custom_event_data={
                                      'queue': self.queue,
                                      'default_task_ttl':
                                      self.default_task_ttl,
                                      'add_retry': self.add_retry,
                                      'chain_payload': self.chain_payload
                                  })

    def _get_signature(self, node):
        """ Create a celery task signature based on a graph node.
        """
        metadata = self.pipeline_config['metadata']
        node_config = self.pipeline_config['taskDefinitions'][node]

        # Node config takes precedence, pipeline metadata as default
        queue = node_config.get('queue', metadata['queue'])
        max_ttl = node_config.get('maxTtl', metadata.get('maxTtl', None))

        # Ensures task signatures include requisite information to retrieve
        # PipelineRunWrapper from cache using the pipeline id, and execution id.
        # We set immutable=True to ensure each client task can be defined
        # with this specific signature (event)
        # http://docs.celeryproject.org/en/master/userguide/canvas.html#immutability
        return get_task_signature(task_path=node_config.get('handler'),
                                  queue=queue,
                                  access_key=self.access_key,
                                  pipeline_id=self.pipeline_id,
                                  execution_id=self.execution_id,
                                  max_ttl=max_ttl,
                                  immutable=True,
                                  task_config=node_config)

    def generate_chain(self):
        """ Generate the full pipeline chain.
        """
        logger.debug(f'Starting Pipeline {self.pipeline_id}')

        if not self.good_to_go:
            logger.info("Chain deemed to be not good to go.")
            if self.loading_message is None:
                self.loading_message = CHAIN_FAILURE_MSG
            return None

        try:
            # Create the task chain such that all concurrent tasks are grouped
            # and all high level node groups are run serially
            G = self.pipeline_wrapper.execution_graph

            total_tasks = 0
            pipeline_chain = []
            chainable_tasks = get_chainable_tasks(G, None, [])

            # Current chord+chain solution based on
            # https://stackoverflow.com/questions/15123772/celery-chaining-groups-and-subtasks-out-of-order-execution
            # Look also at last comment from Nov 7, 2017 here
            # https://github.com/celery/celery/issues/3597
            # Big outstanding bug in Celery related to failures in chords that
            # results in really nasty log output. See
            # https://github.com/celery/celery/issues/4834
            for i, node_group in enumerate(chainable_tasks):
                total_tasks += len(node_group)
                this_group = []
                for node in node_group:
                    node_signature = self._get_signature(node)
                    this_group.append(node_signature)

                if len(this_group) <= 1:
                    this_group.append(self._get_regulator())

                the_chord = chord(header=this_group,
                                  body=self._get_regulator())

                pipeline_chain.append(the_chord)

            # Add a 'finished/success' task to the end of all pipelines
            pipeline_chain.append(
                chord(header=self._get_success_task(),
                      body=self._get_regulator()))

            the_chain = chain(*pipeline_chain)

            # Add retry
            if self.add_retry:
                the_chain.link_error(self._get_retry_task())

            self.loading_message = CHAIN_SUCCESS_MSG

            self.chain = the_chain
        except Exception as e:
            self.loading_message = CHAIN_FAILURE_MSG + " {}".format(e)
            logger.exception(e)
            the_chain = None

        self.chain = the_chain

        return the_chain


class TaskRunner(SermosTool):
    """ Run tasks in Sermos
    """
    @classmethod
    def save_result(cls):
        """ Save a task result
        """
        # TODO Implement

    @classmethod
    def publish_work(cls,
                     task_path: str,
                     task_payload: dict,
                     queue: str = None,
                     max_ttl: int = None):
        """ Uniform way to issue a task to another celery worker.

            Args:
                task_path (str): Full path to task intended to run. e.g.
                    sermos_company_client.workers.my_work.task_name
                task_payload (dict): A dictionary containing whatever payload
                    the receiving task expects. This is merged into the `event`
                    argument for the receiving task such that any top level
                    keys in your `task_payload` are found at event['the_key']
                queue (str): The queue on which to place this task.
                    Ensure there are workers available to accept work on
                    that queue.
                max_ttl (int): Optional. Max time to live for the issued task.
                    If not specified, system default is used.
        """
        try:
            # TODO consider whether to add access key/deployment id here
            worker = get_task_signature(task_path=task_path,
                                        queue=queue,
                                        max_ttl=max_ttl,
                                        custom_event_data=task_payload)
            worker.delay()
        except Exception as e:
            logger.error(f"Failed to publish work ... {e}")
            return False

        return True

    @classmethod
    def publish_work_in_batches(cls,
                                task_path: str,
                                task_payload_list: List[dict],
                                queue: str,
                                grouping_key: str = 'tasks',
                                max_per_task: int = 5,
                                max_ttl: int = None):
        """ Uniform way to issue tasks to celery in 'batches'.

            This allows work to be spread over multiple workers, each worker is
            able to consume one or more messages in a single task.

            Args:
                task_path (str): Full path to task intended to run. e.g.
                    sermos_company_client.workers.my_work.task_name
                task_payload_list (list): A list of dictionaries containing
                    whatever payload the receiving task expects. This is broken
                    into batches according to `max_per_task` and nested under
                    the `grouping_key` in the `event` argument for the receiving
                    task such that payload dicts are found at event['grouping_key']
                queue (str): The queue on which to place this task.
                    Ensure there are workers available to accept work on
                    that queue.
                grouping_key (str): Default: tasks. Sets the key name under the
                    receiving task's `event` where the payload items are found.
                max_per_task (int): Default: 5. Maximum number of tasks from the
                    `task_payload_list` that will be bundled under the `grouping_key`
                    and issued as a single task to the receiving worker.
                max_ttl (int): Optional. Max time to live for the issued task.
                    If not specified, system default is used.
        """
        try:
            if len(task_payload_list) > 0:
                for idx in range(len(task_payload_list)):
                    if idx % max_per_task == 0:
                        custom_event_data = {
                            grouping_key:
                            task_payload_list[idx:idx + max_per_task]
                        }
                        # TODO consider whether to add access key/deployment id here
                        worker = get_task_signature(
                            task_path=task_path,
                            queue=queue,
                            max_ttl=max_ttl,
                            custom_event_data=custom_event_data)
                        worker.delay()
        except Exception as e:
            logger.error(f"Failed to publish work in batches ... {e}")
            return False

        return True
