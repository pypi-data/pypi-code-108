import pytz
import boto3
from fnmatch import fnmatch
from pathlib import Path
from datetime import datetime


def get_latest_vintage_partition(bucket, path, date_pattern="%Y%m%d"):
    # Check to make sure there are files in there?
    s3 = boto3.client("s3")
    if path[-1] != "/":
        path += "/"
    partitions = [
        p["Prefix"]
        for p in s3.list_objects_v2(Bucket=bucket, Prefix=path, Delimiter="/")[
            "CommonPrefixes"
        ]
    ]
    vintages = [
        datetime.strptime(Path(p).parts[-1].split("=")[-1], date_pattern)
        for p in partitions
    ]
    max_vintage = max(vintages)
    return datetime.strftime(max_vintage, date_pattern)


def get_latest_file_in_folder_from_s3(bucket, path, pattern):
    s3 = boto3.client("s3")
    files = [
        f
        for f in s3.list_objects_v2(Bucket=bucket, Prefix=path)["Contents"]
        if (f["Size"] > 0) and (fnmatch(f["Key"], pattern))
    ]
    latest_dt = pytz.utc.localize(datetime.min)
    latest_key = None
    for f in files:
        if f["LastModified"] >= latest_dt:
            latest_dt = f["LastModified"]
            latest_key = f["Key"]

    if latest_key is None:
        raise IOError(f"No valid files in s3://{bucket}/{path}")

    return f"s3://{bucket}/{latest_key}"
