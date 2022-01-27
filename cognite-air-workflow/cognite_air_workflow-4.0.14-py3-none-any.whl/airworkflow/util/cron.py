from datetime import datetime
from pathlib import Path
from typing import Dict

from croniter import croniter
from croniter.croniter import CroniterBadCronError


def transform_minutes(minutes: str) -> str:
    return f"*/{minutes} * * * *"


def transform_hours(hours: str) -> str:
    return f"0 */{hours} * * *"


def validate_cron_expr(expr: str, path: Path) -> None:
    base = datetime(2000, 1, 1)
    try:
        croniter(expr, base)
    except CroniterBadCronError as e:
        raise ValueError(f"Malformed file, {path} \n {e}")


def cron_update(config: Dict) -> None:
    schedule = config["schedule"]
    if "cronExpression" in schedule:
        cron = schedule["cronExpression"]
    elif "runEveryHour" in schedule:
        cron = transform_hours(schedule["runEveryHour"])
    elif "runEveryMinute" in schedule:
        cron = transform_minutes(schedule["runEveryMinute"])
    else:
        raise ValueError(
            "Expected the schedule section of the configuration file to contain one of the following:"
            " 'cronExpression', 'runEveryHour', 'runEveryMin'"
        )

    config["schedule"].update({"cronExpression": cron})
    if "runEveryHour" in schedule:
        config["schedule"].pop("runEveryHour")
    if "runEveryMinute" in schedule:
        config["schedule"].pop("runEveryMinute")


def validate_and_update_cron(config: Dict, path: Path) -> None:
    if "cronExpression" in config["schedule"]:
        validate_cron_expr(config["schedule"]["cronExpression"], path)

    cron_update(config)
