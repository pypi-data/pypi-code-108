import os
import pathlib
import sys
import threading
from datetime import date, datetime
from typing import List
from urllib.parse import urlparse

import boto3
import botocore
import pandas as pd
from botocore.errorfactory import ClientError
from datefinder import DateFinder
from tqdm import tqdm


# pylint says this doesn't exist, but it does
try:
    from pandas._libs.tslibs.parsing import guess_datetime_format
except:
    from pandas.core.tools.datetimes import guess_datetime_format

from pyemr.utils.config import color_text, get_datetime_string, get_staging_dir


S3_CLIENT_TYPES = ["s3", "s3n", "s3a"]


def s3_path_exists(s3_path: str):
    """Checks path exists on s3.

    Args:
      s3_path: str:
      s3_path: str:
      s3_path: str:
      s3_path: str:
      s3_path: str:
      s3_path: str:
      s3_path: str:
      s3_path: str:

    Returns:
      bool: True if file exists.

    """

    if not is_valid_s3_path(s3_path):
        ValueError(f"Not a valid s3 path. Must start with any of {S3_CLIENT_TYPES}.")

    s3_client = boto3.client("s3")

    bucket = get_s3_bucket(s3_path)
    key = get_s3_key(s3_path)

    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError:
        # Not found
        return False


def download_file_from_s3(s3_path: str, local_path: str):
    """Download file to s3 with progress bar.

    Args:
      s3_path: str:
      local_path: str:
      s3_path: str:
      local_path: str:
      s3_path: str:
      local_path: str:
      s3_path: str:
      local_path: str:

    Returns:

    """
    s3_client = boto3.resource("s3")  # pylint: disable=C0103

    bucket = get_s3_bucket(s3_path)
    key = get_s3_key(s3_path)
    file_size = s3_client.meta.client.head_object(Bucket=bucket, Key=key)[
        "ContentLength"
    ]
    file_name = get_file_name(s3_path)

    bucket = s3_client.Bucket(bucket)

    def callback(bytes_transferred):
        """

        Args:
          bytes_transferred:

        Returns:

        """
        return pbar.update(bytes_transferred)

    with tqdm(
        total=file_size,
        unit="B",
        unit_scale=True,
        desc=f"Downloading '{file_name}'",
    ) as pbar:
        bucket.download_file(key, local_path, Callback=callback)


def get_file_name(path: str) -> str:
    """Parses path to get the file name.

    Args:
      path: str:
      path: str:
      path: str:
      path: str:

    Returns:

    """
    return os.path.basename(path)


def get_s3_bucket(s3_path: str):
    """Parses an s3 path to get the bucket.

    Args:
      s3_path: str:
      s3_path: str:
      s3_path: str:
      s3_path: str:

    Returns:

    """

    if is_valid_s3_path(s3_path):
        obj = urlparse(s3_path, allow_fragments=False)
        return obj.netloc

    raise ValueError("'{s3_path}' is not a valid s3 path.")


def get_s3_key(s3_path: str):
    """Parses an s3 path to get the blob path within the bucket.

    Args:
      s3_path: str:
      s3_path: str:
      s3_path: str:
      s3_path: str:

    Returns:

    """
    if is_valid_s3_path(s3_path):
        obj = urlparse(s3_path, allow_fragments=False)
        key = obj.path
        if key.startswith("/"):
            key = key[1:]
        return key

    raise ValueError("'{s3_path}' is not a valid s3 path.")


def upload_file_s3(local_path, out_dir=""):
    """Upload file to s3 staging directory with date.

    Args:
      local_path:
      out_dir: (Default value = "")

    Returns:

    """
    date_time = get_datetime_string()
    s3_path = upload_to_s3_stage(local_path, date_time, out_dir)
    return s3_path


def upload_to_s3(
    local_path,
    s3_path,
):
    """Upload a file to s3 with progress bar.

    Args:
      local_path:
      s3_path:

    Returns:

    """
    bucket = get_s3_bucket(s3_path)
    key = get_s3_key(s3_path)

    s3_client = boto3.resource("s3")  # pylint: disable=C0103

    # cprint(f"Uploading '{local_path}' to s3...")

    file_size = os.stat(local_path).st_size

    def callback(bytes_transferred):
        """

        Args:
          bytes_transferred:

        Returns:

        """
        return pbar.update(bytes_transferred)

    with tqdm(
        total=file_size,
        unit="B",
        unit_scale=True,
        desc=color_text(f"Uploading '{local_path}'"),
    ) as pbar:
        s3_client.meta.client.upload_file(
            Filename=local_path,
            Bucket=bucket,
            Key=key,
            Callback=callback,
        )


def get_file_s3_path(local_file_path, date_time, suffix):
    """Get the staging directory path for a file.

    Args:
      file_name:
      datetime: (Default value = "latest")
      suffix: (Default value = "code")
      local_file_path:
      date_time:

    Returns:

    """
    file_name = local_file_path.split("/")[-1]
    staging_dir = get_staging_dir()
    if date_time == "latest":
        return f"{staging_dir}/{suffix}/latest/{file_name}"

    return f"{staging_dir}/{suffix}/datetime={date_time}/{file_name}"


def upload_to_s3_stage(in_path, date_time, suffix):
    """Upload an file to s3 staging directory.

    Args:
      in_path:
      datetime: (Default value = "latest")
      suffix: (Default value = "code")
      date_time:

    Returns:

    """

    s3_path = get_file_s3_path(in_path, date_time, suffix)
    upload_to_s3(in_path, s3_path)

    if date_time != "latest":
        s3_path_latest = get_file_s3_path(in_path, "latest", suffix)
        copy_on_s3(s3_path, s3_path_latest)
        return s3_path_latest

    return s3_path


def download_s3_file(s3_path, out_dir):
    """Download s3 file.

    Args:
      s3_path:
      out_dir:

    Returns:

    """

    bucket = get_s3_bucket(s3_path)
    key = get_s3_key(s3_path)
    file_name = key.split("/")[-1]
    s3_client = boto3.client("s3")
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    try:
        s3_client.download_file(bucket, key, f"{out_dir}/{file_name}")
    except botocore.exceptions.ClientError as err:
        if err.response["Error"]["Code"] == "404":
            raise ValueError(f"Object '{s3_path}' does not exists.")
        raise


def copy_on_s3(path, new_path):
    """Copy a blob on s3 to another s3 location

    Args:
      path:
      new_path:

    Returns:

    """
    s3_resource = boto3.resource("s3")  # pylint: disable=C0103

    bucket = get_s3_bucket(path)
    key = get_s3_key(path)

    new_bucket = get_s3_bucket(new_path)
    new_key = get_s3_key(new_path)

    copy_source = {"Bucket": bucket, "Key": key}

    bucket = s3_resource.Bucket(new_bucket)
    bucket.copy(copy_source, new_key)


# python3
class ProgressPercentage:
    """Progress Class
    Class for calculating and displaying download progress

    Args:

    Returns:

    """

    def __init__(self, client, bucket, filename):
        """Initialize
        initialize with: file name, file size and lock.
        Set seen_so_far to 0. Set progress bar length
        """
        self._filename = filename
        self._size = client.head_object(Bucket=bucket, Key=filename)["ContentLength"]
        self._seen_so_far = 0
        self._lock = threading.Lock()
        self.prog_bar_len = 80

    def __call__(self, bytes_amount):
        """Call
        When called, increments seen_so_far by bytes_amount,
        calculates percentage of seen_so_far/total file size
        and prints progress bar.
        """
        # To simplify we'll assume this is hooked up to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            ratio = round(
                (float(self._seen_so_far) / float(self._size))
                * (self.prog_bar_len - 6),
                1,
            )
            current_length = int(round(ratio))

            percentage = round(100 * ratio / (self.prog_bar_len - 6), 1)

            bars = "+" * current_length
            output = (
                bars
                + " " * (self.prog_bar_len - current_length - len(str(percentage)) - 1)
                + str(percentage)
                + "%"
            )

            if self._seen_so_far != self._size:
                sys.stdout.write(output + "\r")
            else:
                sys.stdout.write(output + "\n")
            sys.stdout.flush()


def download_s3_folder(s3_path, local_dir=None):
    """Download the contents of a folder directory

    Args:
      s3_folder: the folder path in the s3 bucket
      local_dir: a relative or absolute directory path in the local file system (Default value = None)
      s3_path:

    Returns:

    """
    bucket_name = get_s3_bucket(s3_path)
    s3_folder = get_s3_key(s3_path)

    s3_resource = boto3.resource("s3")

    bucket = s3_resource.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=s3_folder):

        target = (
            obj.key
            if local_dir is None
            else os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
        )

        if target.endswith("/."):
            target = target[:-2]

        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == "/":
            continue

        object_path = f"s3://{bucket_name}/{obj.key}"
        download_file_from_s3(object_path, target)


def list_date_patters_decending_priority():
    """Generates a series of date patterns that are used to search"""
    todays_date = date.today()
    current_year = todays_date.year
    for suffix in ["-01", "-01-01", ""]:
        for prefix in ["datetime=", "dt=", "timestamp=", ""]:
            for year in range(current_year, 2012, -1):
                yield f"{prefix}{year}{suffix}", f"{prefix}{current_year}{suffix}"


def s3_ls_sorted(s3_directory):
    """List s3 blob paths in order of recency.

    Args:
      s3_directory:

    Returns:

    """
    s3_client = boto3.client("s3")
    bucket = get_s3_bucket(s3_directory)
    key = get_s3_key(s3_directory)
    objs = s3_client.list_objects_v2(Bucket=bucket, Prefix=key)
    if "Contents" not in objs:
        return []

    objs = objs["Contents"]

    def get_last_modified(obj):
        """

        Args:
          obj:

        Returns:

        """
        return int(obj["LastModified"].strftime("%s"))

    return [obj["Key"] for obj in sorted(objs, key=get_last_modified)]


def s3_ls_most_recent_absolute(s3_directory):
    """List s3 blob absolute paths in order of recency.

    Args:
      s3_directory:

    Returns:

    """
    bucket = get_s3_bucket(s3_directory)
    ls_sorted = s3_ls_sorted(s3_directory)
    if len(ls_sorted) > 0:
        last_added = ls_sorted[0]
        return f"s3://{bucket}/{last_added}"

    raise ValueError("Path '{s3_directory}' is empty or doesn't exists.")


def s3_ls_most_recent_parquet_absolute(s3_directory):
    """

    Args:
      s3_directory:

    Returns:

    """
    bucket = get_s3_bucket(s3_directory)
    ls_sorted = s3_ls_sorted(s3_directory)
    for path in ls_sorted:
        if path.endswith(".parquet") or path.endswith(".csv") or path.endswith(".json"):
            return f"s3://{bucket}/{path}"

    for path in ls_sorted:
        if "part" in path:
            return f"s3://{bucket}/{path}"

    for path in ls_sorted:
        if not path.endswith("_SUCCESS"):
            return f"s3://{bucket}/{path}"

    return None


def s3_list_most_recent(s3_directory):
    """

    Args:
      s3_directory:

    Returns:

    """
    last_added = s3_ls_most_recent_absolute(s3_directory)
    return os.path.relpath(last_added, s3_directory)


def s3_get_most_recent_parquet(s3_directory):
    """

    Args:
      s3_directory:

    Returns:

    """
    last_added = s3_ls_most_recent_parquet_absolute(s3_directory)
    return os.path.relpath(last_added, s3_directory)


def get_possible_more_recent_paths(path: str, n_days=30) -> List[str]:
    """

    Args:
      path: str:
      n_days: (Default value = 30)
      path: str:
      path: str:
      path: str:
      path: str:
      path: str:
      path: str:
      path: str:

    Returns:

    """

    past_n_days = pd.date_range(
        datetime.today(),
        periods=n_days // 3,
        freq="-1D",
    ).tolist()

    past_n_days += pd.date_range(
        min(past_n_days),
        periods=n_days // 2,
        freq="-5D",
    ).tolist()

    past_n_days += pd.date_range(
        min(past_n_days),
        periods=n_days // 3,
        freq="-10D",
    ).tolist()

    date_finder = DateFinder()
    dates = date_finder.extract_date_strings(path)
    for date_string, _, _ in dates:
        date_format = guess_datetime_format(date_string)
        if date_format:
            for date in past_n_days:
                new_recent_path = path.split(date_string)[0] + date.strftime(
                    date_format,
                )
                yield new_recent_path


def s3_ls_smart_most_recent_absolute(s3_directory):
    """

    Args:
      s3_directory:

    Returns:

    """

    s3_directory = s3_directory.strip("/")
    latest_part_path = s3_ls_most_recent_parquet_absolute(s3_directory)

    for new_path_preffix in get_possible_more_recent_paths(latest_part_path):
        tmp = s3_ls_most_recent_parquet_absolute(new_path_preffix)
        if tmp:
            latest_part_path = tmp
            break

    if latest_part_path.endswith("/."):
        latest_part_path = latest_part_path[:-2]

    return latest_part_path


def s3_ls_smart_most_recent(s3_directory):
    """

    Args:
      s3_directory:

    Returns:

    """
    last_added = s3_ls_smart_most_recent_absolute(s3_directory)
    return os.path.relpath(last_added, s3_directory)


def is_valid_s3_path(path):
    """Checks if path has s3 prefix.

    Args:
      path:

    Returns:

    """
    for client_type in S3_CLIENT_TYPES:
        if path.startswith(f"{client_type}://"):
            return True

    return False
