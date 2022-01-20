'''
Provides an implementation of a job processor using the puzzle & play
varspool API which dispatches jobs from a specific queue based on a JSON
configuration.

The job processor can both be invoked by defining a Django management command
or directly calling the job loop. It requires a configuration
(:py:class:`papyru.varspool.config.VarspoolJobProcessorConfig`) and a
processing function. The processing function takes a
:py:class:`papyru.varspool.types.Job` and should return a
:py:class:`papyru.varspool.types.JobResult`.

Example:

  - via Management Command
    (:py:class:`papyru.varspool.command.VarspoolJobProcessorBaseCommand`)

    .. code-block:: python

      class Command(VarspoolJobProcessorBaseCommand):
          config = VarspoolJobProcessorConfig(config={...})

  - via directly calling the job loop
    (:py:func:`papyru.varspool.command.enter_job_loop`)

    .. code-block:: python

      enter_job_loop(
          VarspoolJobProcessorConfig(config={...}))
'''

from .command import (VarspoolJobProcessorBaseCommand, enter_job_loop,
                      handle_job, loop_until)
from .config import VarspoolJobProcessorConfig
from .types import Job, JobResult, JobStatus, JobStatusEntry, JobStatusHistory

__all__ = [
    # classes
    'VarspoolJobProcessorConfig',
    'VarspoolJobProcessorBaseCommand',

    # types
    'Job', 'JobResult', 'JobStatus', 'JobStatusEntry', 'JobStatusHistory',

    # functions
    'enter_job_loop', 'handle_job', 'loop_until',
]
