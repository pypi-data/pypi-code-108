import os, subprocess, datetime
from typing import Any, Dict, Iterable, List, Tuple, Union, Callable
import json_minify
import json
from collections import OrderedDict
import boto3
from pathlib import Path


S3_INSTANCE = boto3.resource("s3")

MODE = "LOCAL"

GV = {
    "snapShotDate": datetime.datetime.today().strftime("%d/%m/%Y"),
    "scoringDate": datetime.datetime.today().strftime("%d/%m/%Y"),
    "RunDate": datetime.datetime.today().strftime("%d/%m/%Y"),
    "todayDate": datetime.datetime.today().strftime("%d/%m/%Y"),
    "time": "1",
}

SEPERATOR = "=" * 70

BAKWAS = """from pyspark.context import SparkContext
from pyspark.sql import HiveContext
import os, subprocess
from pathlib import Path
from datetime import datetime
sqlContext = HiveContext(sc)


def create_view_from_file(name,path,file_type="baba",*args,**kwrgs):
    if file_type=="json":    df=spark.read.json(path)
    elif file_type=="csv":   df=spark.read.options(header='True', inferSchema='True',delimiter=kwrgs.get('delimiter',',')).csv(path)
    else:               df=spark.read.load(path)
    df.registerTempTable(name)
    return df

def create_view_from_sql(name,sql):
    df=sqlContext.sql(sql)
    df.registerTempTable(name)
    return df
    
def create_view_from_table(name,table):
    df=sqlContext.table(table)
    df.registerTempTable(name)
    return df

def get_key_for_time_by(data, frmt, regex):
    founded = re.findall(regex, data)
    return tuple(map(lambda x: datetime.strptime(x, frmt), founded))
    
def _get_latest_path_with_time(clean_path, frmt, regex):
    raw_times =  os.popen(f"aws s3 ls {clean_path}").read().split('\\n')
    iter_times = map(lambda x: x.strip().split(' ')[-1], raw_times)
    times = list((filter(lambda x: x, iter_times)))
    time = max(times, key=lambda d: get_key_for_time_by(d, frmt, regex))
    return os.path.join(clean_path, time)
    
def get_latest_dir_path(path, dateFormatInPath=[]):
    path=path.strip()
    _, rest_path = path.split('://')
    path = "s3" + "://" + Path(rest_path).__str__() + "/"
    n = len(dateFormatInPath) if (type(dateFormatInPath)==list or type(dateFormatInPath)==tuple) else dateFormatInPath
    if n > 0:    path = _get_latest_path_with_time(path, '%Y-%m-%d', r'\d{4}-\d{2}-\d{2}')
    if n > 1:    path = _get_latest_path_with_time(path, '%H', r'\d{2}')
    return path
"""


def get_latest_path_s3(
    base_path, bucket_name, key: Callable = None, *args, **kwargs
) -> str:
    # returns latest file, compared by "key". by-default it is last date.
    s3_bucket = S3_INSTANCE.Bucket(bucket_name)
    result = max(
        s3_bucket.objects.filter(Prefix=base_path),
        key=lambda x: key(x) if key else x.last_modified,
        default="",
    )
    return (
        "s3://" + bucket_name + "/" + result.key.rsplit("/", 1)[0] + "/"
        if result
        else ""
    )


def get_all_files_s3(
    base_path: str, bucket_name: str, extension=None, key=None, *args, **kwargs
) -> Iterable[Tuple[str, str]]:
    """
    returns generator of all absolute (dir_path, file_path) in s3 bucket at given prefix
    """
    my_bucket = S3_INSTANCE.Bucket(bucket_name)
    if key:
        for obj in filter(lambda x: key(x), my_bucket.objects.filter(Prefix=base_path)):
            file_path = "s3://" + bucket_name + "/" + obj.key
            yield (file_path.rsplit("/", 1)[0] + "/", file_path)
    elif extension:
        for obj in filter(
            lambda x: x.key.endswith(extension),
            my_bucket.objects.filter(Prefix=base_path),
        ):
            file_path = "s3://" + bucket_name + "/" + obj.key
            yield (file_path.rsplit("/", 1)[0] + "/", file_path)
    else:
        for obj in my_bucket.objects.filter(Prefix=base_path):
            file_path = "s3://" + bucket_name + "/" + obj.key
            yield (file_path.rsplit("/", 1)[0] + "/", file_path)


def get_files_by_ext_local(path: str, extention: str) -> Iterable[Tuple[str, str]]:
    for dirpath, _, filenames in os.walk(path):
        for file in filenames:
            if file.endswith(extention):
                yield (dirpath, dirpath + "/" + file)


def get_files_by_ext(
    path: str, extention: str, *args, **kwargs
) -> Iterable[Tuple[str, str]]:
    if MODE == "LOCAL":
        return get_files_by_ext_local(path, extention)
    elif MODE == "S3":
        bucket_name, prefix_path = get_bucket_and_prefix_path(path)
        return get_all_files_s3(prefix_path, bucket_name, extention, *args, **kwargs)


def get_short_path(full_path: str) -> str:
    index = 0
    if "postprocessing" in full_path.lower():
        index = full_path.find("postprocessing")
    elif "preprocessing" in full_path.lower():
        index = full_path.find("preprocessing")
    return full_path[index:]


def get_latest_dir_path_local(
    path: str, dateFormatInPath: Union[int, List[str]] = []
) -> str:
    path = path.strip()
    if path.startswith("s3a://"):
        path = path.replace("s3a", "s3")
    elif path.startswith("s3n://"):
        path = path.replace("s3n", "s3")
    if path[-1] != "/":
        path += "/"
    n = (
        len(dateFormatInPath)
        if (type(dateFormatInPath) == list or type(dateFormatInPath) == tuple)
        else dateFormatInPath
    )
    if n > 0:
        raw_dates = subprocess.getstatusoutput(f"aws s3 ls {path} | sort -r")[1]
        date = list(map(lambda x: x.replace("PRE", "").strip(), raw_dates.split("\n")))[
            0
        ]  # sorted till date
        path = os.path.join(path, date)
    if n > 1:
        raw_hours = subprocess.getstatusoutput(f"aws s3 ls {path} | sort -r")[1]
        hour = list(map(lambda x: x.replace("PRE", "").strip(), raw_hours.split("\n")))[
            0
        ]  # sorted till hours
        path = os.path.join(path, hour)
    return path


def get_latest_dir_path(
    path: str,
    dateFormatInPath: Union[int, List[str]] = [],
    *args,
    **kwarg,
) -> str:
    if MODE == "LOCAL":
        return get_latest_dir_path_local(path, dateFormatInPath)
    elif MODE == "S3":
        bucket_name, prefix_path = get_bucket_and_prefix_path(path)
        return get_latest_path_s3(prefix_path, bucket_name, *args, **kwarg)


def get_string_with_substituted_global_variables(
    s: str, global_variables: Dict[str, Any]
) -> str:
    for key, value in global_variables.items():
        tmp = "#{" + str(key) + "}"
        s = s.replace(tmp, str(value))
    return s


def does_path_exists(path: str) -> bool:
    if MODE == "LOCAL":
        return os.path.exists(path)
    elif MODE == "S3":
        bucket_name, prefix_path = get_bucket_and_prefix_path(path)
        prefix_path = prefix_path.rstrip("/")
        resp = boto3.client("s3").list_objects(
            Bucket=bucket_name, Prefix=prefix_path, Delimiter="/", MaxKeys=1
        )
        return any(
            (
                "CommonPrefixes" in resp,  # mathching dir path
                "Contents" in resp
                and resp["Contents"]
                and resp["Contents"][0]["Key"] == prefix_path,  # mathching file path
            )
        )


def read_file_from_s3(bucket_name: str, prefix_path: str) -> str:
    bucket = S3_INSTANCE.Bucket(bucket_name)
    obj = list(bucket.objects.filter(Prefix=prefix_path))[0]
    data = obj.get()["Body"].read()
    return data.decode("utf-8")


def read_file_from_local(path: str) -> str:
    with open(path, "r") as f:
        data = f.read()
        return data


def read_file(path: str) -> str:
    if MODE == "LOCAL":
        return read_file_from_local(path)
    elif MODE == "S3":
        bucket_name, prefix_path = get_bucket_and_prefix_path(path)
        return read_file_from_s3(bucket_name=bucket_name, prefix_path=prefix_path)


def get_global_variables(path: str) -> Dict[str, Any]:
    data = read_file(path)
    data = json_minify.json_minify(data)
    data = json.loads(data, object_pairs_hook=OrderedDict)
    gv = data["GlobalVariables"]
    gv.update(GV)
    return gv


def get_bucket_and_prefix_path(path: str) -> Tuple[str, str]:
    _, raw_path = path.split("://")
    bucket_name, raw_prefix_path = raw_path.split("/", 1)
    return bucket_name, raw_prefix_path.strip("/")

def prettify_path(path: str) -> str:
    if MODE == "LOCAL":
        return str(Path(path))
    elif MODE == "S3":
        return path