"""
Common methods shared between blocks, especially useful for directory handling
and block parameter/query input.
"""
import json
import os
from typing import Callable, Union, List
from contextlib import ContextDecorator
from pathlib import Path
from enum import Enum
import shutil
import base64
from datetime import datetime, timedelta

import rasterio as rio
from rasterio import warp
from shapely.geometry import box, mapping
from dateutil.parser import parse
from geojson import FeatureCollection, Feature

from .stac import STACQuery
from .logging import get_logger

logger = get_logger(__name__)


def ensure_data_directories_exist():
    """Creates required directories for any block input and output (`/tmp/input`,
    `tmp/output`, `/tmp/quicklooks`).
    """
    Path("/tmp/input/").mkdir(parents=True, exist_ok=True)
    Path("/tmp/output/").mkdir(parents=True, exist_ok=True)
    Path("/tmp/quicklooks/").mkdir(parents=True, exist_ok=True)


def setup_test_directories(
    test_dir: Union[str, Path], clean_subdirs: bool = True
) -> List[Path]:
    """Creates given test directory and empty subdirs "input", "output", "quicklooks".

    Args:
        test_dir: A directory to store temporary files (usually `/tmp` or `/tmp/e2e_test`)
        clean_subdirs: Remove all files in the subdirs "input", "output", "quicklooks".
    Returns:
        List of sub directories Paths depending onthe selection in sub_dirs.
    """
    test_dir = Path(test_dir)
    test_dir.mkdir(parents=True, exist_ok=True)

    subdirs = ["input", "output", "quicklooks"]
    subdir_paths = [test_dir / subdir for subdir in subdirs]
    for subdir_path in subdir_paths:
        if clean_subdirs:
            # Should not remove other files/dirs in test_dir, since often /tmp.
            subdir_path.mkdir(parents=True, exist_ok=True)
            try:
                shutil.rmtree(subdir_path)
            # Deleting subfolder sometimes does not work in temp, then remove all subfiles.
            except (PermissionError, OSError):
                files_to_delete = subdir_path.rglob("*.*")
                for file_path in files_to_delete:
                    file_path.unlink()
        subdir_path.mkdir(parents=True, exist_ok=True)

    return subdir_paths


class TestDirectoryContext(ContextDecorator):
    """Yields the test directory making sure folders exist and cleans up when
    context is closed.
    """

    def __init__(self, test_dir: Path):
        """
        Example:
            ```python
            with TestDirectoryContext(Path("/tmp")) as test_dir:
                block.process(dir=Path("/tmp"))
            ```

        Arguments:
            test_dir: A directory to store temporary files (usually `/tmp`
                or `/tmp/e2e_test`)
        """
        self.test_dir = test_dir

    def __enter__(self) -> Path:
        """Context entry point.

        Returns:
            Temporary test directory.
        """
        setup_test_directories(self.test_dir)
        return self.test_dir

    def __exit__(self, *exc):
        """Context exit point. Cleans up test subdirs."""
        setup_test_directories(test_dir=self.test_dir)
        return False


def load_query(validator: Callable = lambda x: True) -> STACQuery:
    """Get the query for the current task directly from the task parameters
    in `UP42_TASK_PARAMETERS` environment variable.

    Example:
        ```python
        def val(data: dict) -> bool:
            # Ensure bbox is defined.
            return "bbox" in data

        query = load_query(val)
        ```

    Arguments:
        validator: Callable that returns if the loaded query is valid.

    Returns:
        A `STACQuery` object initialized with the parameters if valid.
    """
    data: str = os.environ.get("UP42_TASK_PARAMETERS", "{}")
    logger.debug(f"Raw task parameters from UP42_TASK_PARAMETERS are: {data}")
    query_data = json.loads(data)

    return STACQuery.from_dict(query_data, validator)


def load_params() -> dict:
    """Get the parameters for the current task directly from the task
    parameters parameters in `UP42_TASK_PARAMETERS` environment variable.

    Returns:
        Dictionary of task parameters.
    """
    data: str = os.environ.get("UP42_TASK_PARAMETERS", "{}")
    logger.debug(f"Fetching parameters for this block: {data}")
    if data == "":
        data = "{}"
    return json.loads(data)


def load_metadata() -> FeatureCollection:
    """Get the geojson metadata input.

    Returns:
        Object defining input features for block.
    """
    ensure_data_directories_exist()
    if os.path.exists("/tmp/input/data.json"):
        with open("/tmp/input/data.json", encoding="utf-8") as fp:
            data = json.loads(fp.read())

        features = []
        for feature in data["features"]:
            features.append(Feature(**feature))

        return FeatureCollection(features)
    else:
        return FeatureCollection([])


def save_metadata(result: FeatureCollection):
    """Save the geojson metadata output.

    Arguments:
        result: Output feature collection.
    """
    ensure_data_directories_exist()
    with open("/tmp/output/data.json", "w", encoding="utf-8") as fp:
        fp.write(json.dumps(result))


def update_extents(feat_coll: FeatureCollection) -> FeatureCollection:
    """
    Updates all geometry extents to reflect actual images

    Arguments:
        feat_coll: geojson Feature Collection

    Returns: A FeatureCollection where image extents reflect actual images
    """
    for feature in feat_coll.features:
        with rio.open(
            os.path.join("/tmp/output", feature.properties["up42.data_path"])
        ) as img_file:
            img_bounds = img_file.bounds
        bounds_trans = warp.transform_bounds(
            img_file.crs, {"init": "epsg:4326"}, *img_bounds
        )

        geom = box(*bounds_trans)
        feature["geometry"] = mapping(geom)
        feature["bbox"] = geom.bounds

    return feat_coll


class BlockModes(Enum):
    """
    Types of block modes: DRY_RUN or DEFAULT.

    Important:
        Find out more about job modes/block modes in our
        [documentation](https://docs.up42.com/reference/block-envvars.html#up42-job-mode).
    """

    DRY_RUN = "DRY_RUN"
    DEFAULT = "DEFAULT"


def get_block_mode() -> str:
    """Gets the task mode from environment variables. If no task mode is set,
    DEFAULT mode will be returned.

    Important:
        Find out more about job modes/block modes in our
        [documentation](https://docs.up42.com/reference/block-envvars.html#up42-job-mode).

    Returns:
        Block mode.
    """
    value = os.environ.get("UP42_JOB_MODE", BlockModes.DEFAULT.value)
    if value not in [mode.value for mode in BlockModes]:
        value = "DEFAULT"
    return value


def get_block_info() -> dict:
    """Gets the Block Info variable as a dictionary.

    Returns:
        Block info as a dict.
    """
    value_str = str(os.environ.get("UP42_BLOCK_INFO"))
    value_dict = json.loads(value_str)

    return value_dict


def get_job_info() -> dict:
    """Gets the Job Info variable as a dictionary.

    Returns:
        Job info as a dict.
    """
    value_str = str(os.environ.get("UP42_JOB_INFO", "{}"))
    value_dict = json.loads(value_str)

    return value_dict


def encode_str_base64(string: str) -> str:
    """
    A function that encodes strings in base64. The primary use case is passing complex environment variables into
    docker containers. In cases where these env variables are complex json objects including a number of different
    special characters the process of getting them unharmed into a docker container sometimes fails. Encoding them
    in base64 is a save method to solve this problem.

    Arguments:
        string: A, potentially complex, non-encoded string
    Returns:
        A base64-encoded string
    """
    return base64.b64encode(string.encode("ascii")).decode("ascii")


def decode_str_base64(string: str) -> str:
    """
    Inverter function for encode_str_base64

    Arguments:
        string: A base64-encoded string
    Returns:
        A decoded string
    """

    str_encoded_byte = bytes(string, "utf-8")
    str_decoded_byte = base64.b64decode(str_encoded_byte)
    return str_decoded_byte.decode("utf-8")


def get_timeperiod(
    duration: int = 365,
    start: int = -365,
    start_date: str = None,
    end_date: str = None,
) -> str:
    """
    Generates time period string from any combinations of duration(days) & start(days),
    duration(days) & start_date or start_date & end_date parameters. Defaults to 1 year till today.

    Most relevant for selecting timeperiods for testing of rolling archives.

    Args:
        duration: Time period duration in days.
        start: Time period start from today in days.
        start_date: Time period start date, format string YYYY-MM-DD.
        end_date: Time period end date, format string YYYY-MM-DD.

    Returns:
        time period string with variable time and fixed clock time, in the format
        "2019-07-01T00:00:00+00:00/2029-07-10T23:59:59+00:00"
    """
    if start_date is not None and end_date is not None:
        start_date = parse(start_date).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_date = parse(end_date).replace(hour=0, minute=0, second=0, microsecond=0)
    elif start_date is not None and duration is not None:
        start_date = parse(start_date).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_date = start_date + timedelta(days=+duration)
    elif duration is not None and start is not None:
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = today + timedelta(days=+start)
        end_date = start_date + timedelta(days=+duration)
    else:
        raise ValueError(
            "Only the combinations `1. duration(months) & start(months), "
            "2. duration(months) & start_date or 3. start_date & end_date` are allowed."
        )

    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    time = f"{start_date}T00:00:00+00:00/{end_date}T23:59:59+00:00"
    return time
