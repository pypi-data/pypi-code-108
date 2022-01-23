import datetime
import logging
from telegram.ext import JobQueue, Job
from nerddiary.bot.context import JobContext, ChatJobContext

from typing import Callable, Any

logger = logging.getLogger("nerddiary.bot.job")


def remove_jobs(job_queue: JobQueue, job_context: JobContext) -> None:
    """Remove all jobs matching this context from queue but not from the chat context."""

    job_key = job_context.job_key
    current_jobs = job_queue.get_jobs_by_name(job_key)
    if current_jobs:
        for job in current_jobs:
            job.schedule_removal()


def dispose_chat_job(job_queue: JobQueue, job_context: ChatJobContext) -> None:
    """Remove all jobs matching this context from queue and chat context."""

    job_key = job_context.job_key

    remove_jobs(job_queue=job_queue, job_context=job_context)

    if job_key in job_context.chat_context.jobs:
        del job_context.chat_context.jobs[job_key]


def run_once(
    callback: Callable[..., Any],
    job_queue: JobQueue | None,
    job_context: JobContext,
    when: float | datetime.timedelta | datetime.datetime | datetime.time,
) -> Job | None:
    if job_queue:
        return job_queue.run_once(
            callback=callback,
            when=when,
            context=job_context,
            name=job_context.job_key,
        )
    else:
        return None


def run_daily(
    callback: Callable[..., Any],
    job_queue: JobQueue | None,
    job_context: JobContext,
    time: datetime.time,
) -> Job | None:
    if job_queue:
        return job_queue.run_daily(
            callback=callback,
            time=time,
            context=job_context,
            name=job_context.job_key,
        )
    else:
        return None
