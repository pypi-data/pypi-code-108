import os
from typing import Any, Callable, List, Optional

import cronitor
import schedule
from schedule import every  # Use this to whitelist what we allow

from jetpack import utils
from jetpack.config import instrumentation, symbols
from jetpack.proto.runtime.v1alpha1 import remote_pb2

cronjob_suffix = os.environ.get("JETPACK_CRONJOB_SUFFIX", "-missing-suffix")


def repeat(repeat_pattern: schedule.Job) -> Callable[..., Any]:
    def wrapper(func: Callable[..., Any]) -> Any:
        name = symbols.get_symbol_table().register(func)
        name_with_suffix = name + cronjob_suffix
        cronitor_wrapped_func = cronitor.job(name_with_suffix)(func)
        instrumentation.get_tracer().cronjob_loaded(name, repeat_pattern)
        return schedule.repeat(repeat_pattern)(cronitor_wrapped_func)

    return wrapper


def get_jobs() -> List[remote_pb2.CronJob]:
    cron_jobs = []
    for job in schedule.get_jobs():

        if job.at_time is not None:
            target_time = job.at_time.isoformat()
        else:
            target_time = None

        target_day_of_week = remote_pb2.DayOfWeek.UNKNOWN_DAY
        if job.start_day is not None:
            target_day_of_week = remote_pb2.DayOfWeek.Value(job.start_day.upper())

        cron_jobs.append(
            remote_pb2.CronJob(
                qualified_symbol=utils.job_name(job),
                target_time=target_time,
                target_day_of_week=target_day_of_week,
                unit=remote_pb2.Unit.Value(job.unit.upper()),
                interval=job.interval,
            )
        )

    return cron_jobs


def pretty_print(self: remote_pb2.CronJob) -> str:
    s = f"Function: {self.qualified_symbol}"
    s += f"\nInterval: every {self.interval} {remote_pb2.Unit.Name(self.unit).lower()}"
    if self.target_time:
        s += f"\n at {self.target_time}"
    if self.target_day_of_week:
        s += f"\n on {remote_pb2.DayOfWeek.Name(self.target_day_of_week).capitalize()}"
    return s
