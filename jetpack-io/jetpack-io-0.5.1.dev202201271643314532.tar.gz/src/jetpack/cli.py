import asyncio
import sys
from typing import Any, List, Optional

from google.protobuf import json_format
import redis
import schedule

from jetpack import utils
from jetpack._task.jetpack_function import JetpackFunction
from jetpack.cmd import is_using_new_cli
from jetpack.config import symbols
from jetpack.config.symbols import Symbol
from jetpack.models.runtime import cronjob_pb2, describe_pb2, job_pb2

# TODO: Change types of both `app` and return type. Return type is DescribeOutput
# but because that protocol buffer is still outside of /proto we are not generating
# type information for it.


# TODO(Landau): Use a framework? Like https://click.palletsprojects.com/en/7.x/
def handle(app: Any = None) -> None:
    run(app=app, cli_args=sys.argv)


# TODO(Landau): Use a framework? Like https://click.palletsprojects.com/en/7.x/
def run(app: Any = None, cli_args: List[str] = []) -> None:

    # When using new cli, we don't do anything here.
    if is_using_new_cli():
        return

    # TODO: refactor this method into a separate method for each command.
    print(f"Running jetpack with args: {cli_args}")

    # Early return if just one argument is provided (e.g. 'uwsgi').
    if len(cli_args) <= 1:
        return

    """
    Execute a job: `python jetpack_main.py job exec_id qualified_job_symbol [base_64_args]`
    """
    if cli_args[1] == "job" and (len(cli_args) == 4 or len(cli_args) == 5):
        exec_id = cli_args[2]
        target_job_name = cli_args[3]
        params = cli_args[4] if len(cli_args) == 5 else ""
        # Find the OnDemand job, if there is one.
        func = symbols.get_symbol_table()[Symbol(target_job_name)]
        asyncio.run(JetpackFunction(func).exec(exec_id, params))
        return

    """
    DEPRECATED: we now use `job` to run cronjobs.
    This will be removed soon

    Execute a cronjob: `python jetpack_main.py cronjob cronjob_name`
    For legacy reasons, `run` is an alias for `cronjob`. We intend to remove this alias eventually.
    """
    if (cli_args[1] == "run" or cli_args[1] == "cronjob") and len(cli_args) == 3:
        target_job_name = cli_args[2]
        for job in schedule.get_jobs():
            if utils.job_name(job) == target_job_name:
                job.job_func()
                return

        raise JobNotFoundError(f'Target cronjob "{target_job_name}" not found')

    """
    Get all jobs `python jetpack_main.py describe`
    """
    if cli_args[1] == "describe" and len(cli_args) == 2:
        print(json_format.MessageToJson(describe_output(app)))
        return

    """
    Get all jobs `python jetpack_main.py describe-to-redis`
    """
    if cli_args[1] == "describe-to-redis" and len(cli_args) == 4:
        host = cli_args[2]
        key = cli_args[3]
        r = redis.Redis(host=host, port=6379, db=0)
        r.set(key, json_format.MessageToJson(describe_output(app)))
        return


def describe_output(app: Any) -> Any:
    # Should these be the same? The concepts are really similar.
    cron_jobs = []
    jobs = []
    for job in schedule.get_jobs():

        if job.at_time is not None:
            target_time = job.at_time.isoformat()
        else:
            target_time = None

        target_day_of_week: Optional[int] = None
        if job.start_day is not None:
            target_day_of_week = cronjob_pb2.DayOfWeek.Value(job.start_day.upper())

        cron_jobs.append(
            cronjob_pb2.CronJob(
                function=utils.job_name(job),
                target_time=target_time,
                target_day_of_week=target_day_of_week,
                unit=cronjob_pb2.Unit.Value(job.unit.upper()),
                interval=job.interval,
            )
        )

    for symbol in symbols.get_symbol_table().defined_symbols():
        # Note that cronjobs are also jobs and will be added to this list.
        jobs.append(
            job_pb2.Job(
                qualified_symbol=symbol,
            )
        )

    try:
        enum_name = app.__class__.__name__.upper() if app is not None else "NONE"
        framework = describe_pb2.Framework.Value(enum_name)
    except ValueError:
        framework = describe_pb2.Framework.Value("UNKNOWN")

    return describe_pb2.DescribeOutput(
        cron_jobs=cron_jobs,
        jobs=jobs,
        framework=framework,
    )


class JobNotFoundError(Exception):
    pass
