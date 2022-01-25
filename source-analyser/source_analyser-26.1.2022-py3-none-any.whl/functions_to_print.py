from pyspark.context import SparkContext
from pyspark.sql import HiveContext
import os
from pathlib import Path
from datetime import datetime
import re

sqlContext = HiveContext(sc)


def create_view_from_file(name, path, file_type=None, *args, **kwrgs):
    if file_type == "json":
        df = spark.read.json(path)
    elif file_type == "csv":
        df = spark.read.options(
            header="True", inferSchema="True", delimiter=kwrgs.get("delimiter", ",")
        ).csv(path)
    else:
        df = spark.read.load(path)
    df.registerTempTable(name)
    return df


def create_view_from_sql(name, sql):
    df = sqlContext.sql(sql)
    df.registerTempTable(name)
    return df


def create_view_from_table(name, table):
    df = sqlContext.table(table)
    df.registerTempTable(name)
    return df


def get_key_for_time_by(data, frmt, regex):
    founded = re.findall(regex, data)
    return tuple(map(lambda x: datetime.strptime(x, frmt), founded))


def _get_latest_path_with_time(clean_path, frmt, regex):
    raw_times = os.popen(f"aws s3 ls {clean_path}").read().split("\\n")
    iter_times = map(lambda x: x.strip().split(" ")[-1], raw_times)
    times = list((filter(lambda x: x, iter_times)))
    time = max(times, key=lambda d: get_key_for_time_by(d, frmt, regex))
    return os.path.join(clean_path, time)


def get_latest_dir_path(path, dateFormatInPath=[]):
    path = path.strip()
    _, rest_path = path.split("://")
    path = "s3" + "://" + Path(rest_path).__str__() + "/"
    n = (
        len(dateFormatInPath)
        if (type(dateFormatInPath) == list or type(dateFormatInPath) == tuple)
        else dateFormatInPath
    )
    if n > 0:
        path = _get_latest_path_with_time(path, "%Y-%m-%d", r"\d{4}-\d{2}-\d{2}")
    if n > 1:
        path = _get_latest_path_with_time(path, "%H", r"\d{2}")
    return path
