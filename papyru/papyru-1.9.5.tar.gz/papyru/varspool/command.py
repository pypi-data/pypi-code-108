import json
import signal
import traceback
from datetime import timedelta
from functools import wraps
from http import HTTPStatus
from multiprocessing import Pool
from os import environ, getpid
from sys import exit
from time import sleep
from typing import Callable, List, Optional
from urllib.parse import urljoin

import requests
from django.core.management.base import BaseCommand

from papyru.utils import limited_runtime, log
from papyru.varspool.config import VarspoolJobProcessorConfig
from papyru.varspool.types import (Job, JobResult, JobStatus, JobStatusEntry,
                                   JobStatusHistory)


class JobCounter:
    def __init__(self):
        self._counter = 0

    @property
    def active_jobs(self):
        return self._counter

    def inc(self):
        self._counter += 1

    def dec(self):
        self._counter -= 1

        if self._counter < 0:
            raise AssertionError("job counter must not be negative")


def loop_until(time_range: timedelta):
    '''
    Decorates a function which performs a single loop step.

    Calls the function as long as the according process has neither
    received SIGTERM nor the given time range has been exceeded.
    '''

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            state = {'received_sigterm': False}

            def handle_sigterm(*args, **kwargs):
                log('caught SIGTERM. will shutdown gracefully.')
                state['received_sigterm'] = True

            signal.signal(signal.SIGTERM, handle_sigterm)

            with limited_runtime(time_range) as has_runtime_left:
                while has_runtime_left() and not state['received_sigterm']:
                    func(*args, **kwargs)
        return wrapper
    return decorator


g_job_counter = JobCounter()


def _err_callback(ex: Exception):
    if isinstance(ex, CouldNotProcessJobException):
        log(ex.traceback, level='error')
        log('[ALERT] could not process job %d: %s' % (ex.job_id, ex.message),
            level='error')
    elif isinstance(ex, StatusUpdateConflict):
        log('[ALERT] could not finish job %d due to status conflict'
            % ex.job_id, level='error')
    else:
        log('[ALERT] internal error processing job due to %s: %s'
            % (type(ex).__name__, str(ex)),
            level='error')
    g_job_counter.dec()


def _succ_callback(job: Job):
    log('finished job %d with status %s.'
        % (job.id, job.status_history.items[-1].status))
    g_job_counter.dec()


def _get_num_of_jobs_to_fetch(max_parallel_job_count: int):
    return max_parallel_job_count - g_job_counter.active_jobs


def _fetch_jobs(queue_url: str, limit: int) -> List[Job]:
    endpoint = ('jobs?current_status=%s&limit=%d'
                % (str(JobStatus.OPEN), limit))

    resp = requests.get(urljoin('%s/' % queue_url, endpoint))
    resp.raise_for_status()

    return list(map(Job.from_dict, resp.json()['jobs']))


def _post_job_status(job: Job, new_status: JobStatusEntry) -> Job:
    previous_status = job.status_history.items[-1]

    resp = requests.post(
        job.status_history.location,
        data=json.dumps({
          'previous_status': {
              'checksum': str(previous_status.checksum),
          },
          **new_status.to_dict()}))

    if resp.status_code == HTTPStatus.CONFLICT:
        raise StatusUpdateConflict(job.id)
    elif resp.status_code != HTTPStatus.OK:
        raise CouldNotPersistJobStatusException(resp.status_code, resp.text)

    return Job(id=job.id,
               status_history=JobStatusHistory(
                   location=job.status_history.location,
                   items=list(map(JobStatusEntry.from_dict,
                                  resp.json()['items']))))


def handle_job(job: Job,
               processing_fn: Callable) -> Job:
    '''
    A wrapper for a function processing a job.

    This wrapper function does all the bureaucratic stuff which needs to be
    done around the hard work. It notifies varspool that the job has been
    started and sends the result status after the job has been finished.
    '''

    log('processing job %d.' % job.id)

    try:
        # tell varspool the job has been started and provide some debug
        # information
        job = _post_job_status(
            job,
            JobStatusEntry(
                status=JobStatus.IN_PROGRESS,
                data={
                    'pod': (
                        environ.get(
                            'HOSTNAME',
                            'could not determine pod.')),
                    'worker-pid': getpid(),
                }))

    except StatusUpdateConflict:
        log('job %d is already in progress. skipping.' % job.id)
        return job
    except Exception:
        raise CouldNotProcessJobException(
            job.id,
            'failed telling varspool the job is in progress',
            traceback.format_exc())

    try:
        result = processing_fn(job)

    except Exception as ex:
        formatted_traceback = traceback.format_exc()
        formatted_exc = ('uncaught error (%s): %s'
                         % (type(ex).__name__, str(ex)))

        log(formatted_traceback, level='error')
        log('[ALERT] %s' % formatted_exc, level='error')

        result = JobResult(status=JobStatus.FAILED,
                           data={
                               'reason': formatted_exc,
                               'traceback': formatted_traceback,
                           })

    log('processed job %d. updating varspool.' % job.id)

    try:
        # update varspool with the fallback failure result or the processing
        # result
        job = _post_job_status(job, result.to_status_entry())

    except StatusUpdateConflict:
        raise
    except Exception:
        raise CouldNotProcessJobException(
            job.id,
            'failed to persist job status. result was: %s' % result,
            traceback.format_exc())

    return job


def enter_job_loop(config: VarspoolJobProcessorConfig):
    '''
    Main job loop launching a process pool and asynchronously calling
    job processing functions.
    '''

    try:
        log('checking config...')

        if not isinstance(config, VarspoolJobProcessorConfig):
            raise RuntimeError(
                'could not start job loop due to invalid config.')

        log('- queue url: %s' % config.queue_url)

        with Pool(processes=config.max_parallel_job_count) as pool:
            @loop_until(
                time_range=timedelta(minutes=config.max_runtime_in_minutes))
            def wrapper():
                log('fetching jobs...')

                if (g_job_counter.active_jobs
                        >= config.max_parallel_job_count):
                    log('too many active jobs. waiting for a free slot.')
                    sleep(config.loop_cooldown_in_seconds)
                    return

                try:
                    jobs = _fetch_jobs(config.queue_url,
                                       _get_num_of_jobs_to_fetch(
                                           config.max_parallel_job_count))
                except Exception as exc:
                    raise FetchJobException('%s: %s' % (type(exc).__name__,
                                                        str(exc)))

                if len(jobs) == 0:
                    log('no jobs to process. waiting...')
                    sleep(config.loop_cooldown_in_seconds)
                    return

                for job in jobs:
                    log('dispatching job %d.' % job.id)
                    g_job_counter.inc()

                    pool.apply_async(func=handle_job,
                                     args=(job,
                                           config.job_handler),
                                     callback=_succ_callback,
                                     error_callback=_err_callback)
                    log('dispatched job %d.' % job.id)
            wrapper()

            # time is over or SIGTERM has been fired to the job processor.
            # make sure no running jobs will be killed.
            while g_job_counter.active_jobs > 0:
                log('waiting for jobs to finish. (%d left)'
                    % g_job_counter.active_jobs)
                sleep(config.loop_cooldown_in_seconds)

    except Exception as ex:
        log(traceback.format_exc(), level='error')
        log('[ALERT] critical error occurred: %s (%s). '
            'awaiting end of failure backoff...'
            % (type(ex).__name__, str(ex)),
            level='error')

        sleep(config.failure_backoff_in_seconds
              if hasattr(config, 'failure_backoff_in_seconds')
              else (VarspoolJobProcessorConfig
                    .DEFAULT_FAILURE_BACKOFF_IN_SECONDS))
        exit(1)


class VarspoolJobProcessorBaseCommand(BaseCommand):
    config: VarspoolJobProcessorConfig = None

    def handle(self, *args, **kwargs):
        log('varspool job processor started.')

        log('entering job loop.')
        enter_job_loop(self.config)
        log('goodbye.')


class FetchJobException(Exception):
    pass


class StatusUpdateConflict(Exception):
    def __init__(self, job_id: int):
        self.job_id = job_id


class CouldNotPersistJobStatusException(Exception):
    def __init__(self, status_code: int, text: str):
        self.status_code = status_code
        self.text = text


class CouldNotProcessJobException(Exception):
    def __init__(self,
                 job_id: int, message: str, traceback: Optional[str] = None):
        self.job_id = job_id
        self.message = message
        self.traceback = traceback
