import logging
import time

from packer.file_handling import FSHandler
from packer.task_status import Status
from ..tasks import BaseDataTask, app

logger = logging.getLogger(__name__)


def compute_addition(x: int, y: int):
    """
    This function contains the actual logic that is necessary to run the job.
    """
    return x + y


@app.task(bind=True, base=BaseDataTask)
def add(self: BaseDataTask, x: int, y: int, sleep: int = 10) -> None:
    """
    Example task that does basic additions of two integers.

    :param self: first argument is always required for bind to BaseDataTask.
    :param x: should be in job_parameters.
    :param y: should be in job_parameters.
    :param sleep: don't start for this many seconds (default 10).
    """

    if sleep:
        for i in range(sleep, 0, -1):
            msg = f'Task will be ready in {i} seconds'
            self.update_status(Status.RUNNING, msg)
            time.sleep(1)

    value = compute_addition(x, y)
    logger.info('Calculated value: {}'.format(value))

    with FSHandler(self.task_id).writer as writer:
        writer.write(value.to_bytes(2, byteorder='big'))

    logger.info(f'Stored to disk.')

