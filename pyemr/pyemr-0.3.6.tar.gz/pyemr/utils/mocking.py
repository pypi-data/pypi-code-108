""" """
import code
import os
from pathlib import Path
from unittest.mock import patch

from pyemr.utils.config import cinput, cprint, get_mock_s3_path, set_spark_home
from pyemr.utils.s3 import (
    S3_CLIENT_TYPES, download_s3_folder, is_valid_s3_path,
    s3_ls_smart_most_recent_absolute,
)


set_spark_home()


YES_RESPONSES = ["yes", "Yes", "y", "Y", True, "True"]
NO_RESPONSES = ["No", "no", "N", "n", "False", "false", "F", "f", False]


def local_path_exists_and_not_empty(path):
    """Checks if a local path exists and is not empty.

    Args:
      path:

    Returns:

    """

    if os.path.isfile(path):
        return True

    if os.path.isdir(path):
        if any(os.scandir(path)):
            return True
        else:
            print(f"'{path}' is empty.")

    return False


def download_3s_path_to_local_patch(s3_path):
    """Downloads an s3 path and creates a local patch.

    Args:
      s3_path:

    Returns:

    """
    local_path = mock_s3_folder(s3_path)
    return local_path


def mock_part_s3_folder(s3_dir):
    """

    Args:
      s3_dir:

    Returns:

    """

    local_mock_path = get_patch_local_path(s3_dir)
    s3_sample_path = s3_ls_smart_most_recent_absolute(s3_dir)
    cprint("Creating local mock...", "WARNING")
    response = cinput("Download part? ", s3_sample_path)

    # check if response is an s3 path
    if is_valid_s3_path(response):
        s3_sample_path = response
        response = "y"

    if response in YES_RESPONSES:
        local_mock_path = download_3s_path_to_local_patch(s3_sample_path)
        cprint("DONE", "OKGREEN")
        if not local_path_exists_and_not_empty(local_mock_path):
            ValueError(f"Patch faild: '{local_mock_path}' is empty or not exist. ")
        return local_mock_path
    elif response in NO_RESPONSES:
        cprint("You chose not to mock the file. No data to load.")
        return None
    else:
        raise ValueError(
            "Response not recognised. Must be 'y','n' or 's3://some/path'.",
        )


def get_mock_path_if_exists_else_prompt(s3_dir):
    """

    Args:
      s3_dir:

    Returns:

    """

    local_mock_path = get_patch_local_path(s3_dir)

    if local_path_exists_and_not_empty(local_mock_path):
        return local_mock_path

    local_mock_path = mock_part_s3_folder(s3_dir)

    return local_mock_path


def mock_s3_folder(s3_path):
    """

    Args:
      s3_path:

    Returns:

    """
    local_path = get_patch_local_path(s3_path)
    download_s3_folder(s3_path, local_path)
    return local_path


def get_patch_local_path(path):
    """

    Args:
      path:

    Returns:

    """

    if not is_valid_s3_path(path):
        ValueError(f"Not a valid s3 path. Must start with any of {S3_CLIENT_TYPES}.")

    mock_dir = get_mock_s3_path()
    Path(mock_dir).mkdir(parents=True, exist_ok=True)
    path = path.replace("s3:/", mock_dir)
    return path


def pyspark_read_wrapper(original_method):
    """

    Args:
      original_method:

    Returns:

    """

    def pyspark_read_wrapped_method(self, path, *args, **kwargs):
        """

        Args:
          path:
          *args:
          **kwargs:

        Returns:

        """
        local_path = get_mock_path_if_exists_else_prompt(path)
        if not local_path:
            raise ValueError(f"No '{local_path}' in 3s mocked dir.")
        cprint(f"Reading mock path '{local_path}'")
        return original_method(self, local_path, *args, **kwargs)

    return pyspark_read_wrapped_method


def write_wrapper(original_method):
    """

    Args:
      original_method:

    Returns:

    """

    def write_wrapped_method(self, path, *args, **kwargs):
        """

        Args:
          path:
          *args:
          **kwargs:

        Returns:

        """
        local_path = get_patch_local_path(path)
        cprint(f"Writing mock path '{local_path}'")
        return original_method(self, local_path, *args, **kwargs)

    return write_wrapped_method


def patch_pyspark(original_method):
    """

    Args:
      original_method:

    Returns:

    """
    from pyspark.sql.readwriter import DataFrameReader, DataFrameWriter

    @patch.object(
        DataFrameReader,
        "parquet",
        pyspark_read_wrapper(DataFrameReader.parquet),
    )
    @patch.object(DataFrameReader, "csv", pyspark_read_wrapper(DataFrameReader.csv))
    @patch.object(DataFrameReader, "load", pyspark_read_wrapper(DataFrameReader.load))
    @patch.object(DataFrameReader, "json", pyspark_read_wrapper(DataFrameReader.json))
    @patch.object(DataFrameWriter, "parquet", write_wrapper(DataFrameWriter.parquet))
    @patch.object(DataFrameWriter, "csv", write_wrapper(DataFrameWriter.csv))
    @patch.object(DataFrameWriter, "save", write_wrapper(DataFrameWriter.save))
    @patch.object(DataFrameWriter, "json", write_wrapper(DataFrameWriter.json))
    def wrapped_method(*args, **kwargs):
        """

        Args:
          *args:
          **kwargs:

        Returns:

        """
        return original_method(*args, **kwargs)

    return wrapped_method


@patch_pyspark
def launch_python_mock_on_sys():
    """

    Args:
      script:
      *args:
      **kwargs:

    Returns:

    """
    init_spark()
    code.interact(local=locals())


def init_spark():
    """Sets spark home, and spark configs."""

    os.environ["PYARROW_IGNORE_TIMEZONE"] = "1"
    import warnings

    from pyspark.sql import SparkSession

    warnings.filterwarnings("ignore")
    spark = SparkSession.builder.master("local").appName("foo").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")
    spark.conf.set("spark.rapids.sql.enabled", False)
    spark.conf.set("spark.sql.parquet.datetimeRebaseModeInWrite", "LEGACY")


@patch_pyspark
def launch_kernelapp():
    """Launches a python kernel. Adds patching to pyspark read.."""
    # append site packages to python path

    from ipykernel import kernelapp as app

    init_spark()
    app.launch_new_instance()
