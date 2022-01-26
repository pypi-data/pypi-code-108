import time
import typing as T
from numbers import Real
from copy import deepcopy
from dbt.contracts.results import TimingInfo


def rename_keys(d: T.Dict, keys: T.Dict) -> T.Dict:
    dc = deepcopy(d)
    for k in keys.keys():
        if k in dc.keys():
            dc[keys[k]] = dc.pop(k)

    return dc


def omit_keys(d: T.Dict, keys: T.List) -> T.Dict:
    return {k: v for k, v in d.items() if k not in keys}


def freshness_age_to_unit(age: T.Union[Real, float], unit: str) -> float:
    age = float(age)
    if unit == 'hour':
        return round(age / 3600, 0)

    if unit == 'minute':
        return round(age / 60, 1)

    if unit == 'day':
        return round(age / 86400, 0)

    return round(age, 2)


def get_execution_datetime(timing: T.List[TimingInfo]) -> float:
    unix = None
    for obj in timing:
        if obj.name == 'execute' and obj.completed_at is not None:
            unix = time.mktime(obj.completed_at.timetuple())
    return unix


def get_full_db_id(db: str, schema: str, table: str, capitalize: bool = True) -> str:
    db_id = f'{db}.{schema}.{table}'
    if capitalize:
        return db_id.upper()
    return db_id


def get_elapsed_milliseconds_since(time_started: float) -> float:
    return (time.time() - time_started) * 1000
