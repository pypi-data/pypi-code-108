from typing import Callable

from papyru.validation import CerberusValidator


class VarspoolJobProcessorConfig:
    '''
    Configuration used by the base command scheduling varspool jobs.

    The configuration consists of the following keys:

    - queue_url: The URL to the varspool queue.
    - max_parallel_job_count: Maximum count of processes to start concurrently.
    - max_runtime_in_minutes: Duration in minutes for how long new jobs should
      be dispatched.
    - loop_cooldown_in_seconds (`Optional`): Indicates how long the job
      processor waits when there are no new jobs in the queue, when the queue
      is fully busy or when all jobs are dispatched.
      `Default`: 30.
    - failure_backoff_in_seconds (`Optional`): Indicates how many seconds the
      job processor should spend to wait when a failure occurred which makes
      the job processor unable to continue.
      `Default`: 600 (= 10 minutes).
    - job_handler: A function which actually does the hard work.
      It receives a `Job` object and should return a `JobResult` object.
    '''

    DEFAULT_LOOP_COOLDOWN_IN_SECONDS = 30
    DEFAULT_FAILURE_BACKOFF_IN_SECONDS = 600

    _CONFIG_SCHEMA = {
        'schema': {
            'queue_url': {
                'type': 'string',
                'required': True,
            },
            'max_parallel_job_count': {
                'type': 'integer',
                'required': True,
                'min': 1,
            },
            'max_runtime_in_minutes': {
                'type': 'integer',
                'required': True,
                'min': 0,
            },
            'loop_cooldown_in_seconds': {
                'type': 'integer',
                'min': 0,
            },
            'failure_backoff_in_seconds': {
                'type': 'integer',
                'min': 0,
            },
            'job_handler': {
                'required': True
            }
        }
    }

    def __init__(self, config: dict):
        CerberusValidator(self._CONFIG_SCHEMA).validate(config)

        self._queue_url = config['queue_url']
        self._max_parallel_job_count = config['max_parallel_job_count']
        self._max_runtime_in_minutes = config['max_runtime_in_minutes']
        self._loop_cooldown_in_seconds = config.get(
            'loop_cooldown_in_seconds',
            VarspoolJobProcessorConfig.DEFAULT_LOOP_COOLDOWN_IN_SECONDS)
        self._failure_backoff_in_seconds = config.get(
            'failure_backoff_in_seconds',
            VarspoolJobProcessorConfig.DEFAULT_FAILURE_BACKOFF_IN_SECONDS)
        self._job_handler = config['job_handler']

    @property
    def queue_url(self):
        return self._queue_url

    @property
    def max_parallel_job_count(self) -> int:
        return self._max_parallel_job_count

    @property
    def max_runtime_in_minutes(self) -> int:
        return self._max_runtime_in_minutes

    @property
    def loop_cooldown_in_seconds(self) -> int:
        return self._loop_cooldown_in_seconds

    @property
    def failure_backoff_in_seconds(self) -> int:
        return self._failure_backoff_in_seconds

    @property
    def job_handler(self) -> Callable:
        return self._job_handler
