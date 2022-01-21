import os
import requests
import shutil
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tempfile import gettempdir
from tqdm import tqdm
from math import pow, isnan, isinf
import re
import sys
from typing_extensions import Literal, TypedDict
from typing import Any, Dict, List, Optional, Union, Type, Tuple
import uuid
import datetime
from google.resumable_media.requests import ResumableUpload
from google.resumable_media.common import InvalidResponse, DataCorruption

retry_strategy = Retry(  # type: ignore
    total=4,
    backoff_factor=1,
    status_forcelist=[404, 429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "PUT", "POST", "DELETE", "OPTIONS", "TRACE"],
    raise_on_status=False,
)
retry_adapter = HTTPAdapter(max_retries=retry_strategy)
requests_retry = requests.Session()
requests_retry.mount("https://", retry_adapter)
requests_retry.mount("http://", retry_adapter)
tempdir_ttl_days = 1

MAX_FRAMES_PER_BATCH = 1000
MAX_CHUNK_SIZE = int(pow(2, 23))  # 8 MiB
DEFAULT_SAMPLING_THRESHOLD = 0.5

DUMMY_FRAME_EMBEDDING = [0.0, 0.0, 0.0]
DEFAULT_SENSOR_ID = "DEFAULT"


def _upload_local_files(
    file_names: List[str],
    get_upload_path: str,
    headers: Dict[str, Any],
    upload_prefix: str,
    upload_suffix: str,
    delete_after_upload: bool = True,
) -> List[str]:
    """This uploads a set of files with a reader, and then deletes it.

    Args:
        file_names (str): The local file_names (files to be uploaded)
        get_upload_path (str): The URL that generates upload URLs
        headers (Dict[str, Any]): Headers for the get_upload_path request
        upload_prefix (str): Prefix for the filepath (once uploaded)
        upload_suffix (str): Suffix for the filepath (once uploaded)
        delete_after_upload (bool): Whether to delete the file after upload

    Return:
        A list of download URLs for the uploaded files
    """
    xml_api_headers = {
        "x-goog-resumable": "start",
        "content-type": "application/octet-stream",
    }

    download_urls: List[str] = []
    if len(file_names) == 0:
        return download_urls

    all_files_bytes = sum([os.path.getsize(file_name) for file_name in file_names])
    with tqdm(
        total=all_files_bytes,
        file=sys.stdout,
        unit="B",
        unit_scale=True,
        desc="Upload Progress",
    ) as pbar:  # type: tqdm[Any]
        for count, file_name in enumerate(file_names, start=1):
            upload_filename = (
                f"{upload_prefix}_batch_{str(count).zfill(6)}{upload_suffix}"
            )

            params = {
                "upload_filename": upload_filename,
                "resumable_upload": "true",
            }
            upload_url_resp = requests_retry.get(
                get_upload_path, headers=headers, params=params
            )
            raise_resp_exception_error(upload_url_resp)
            urls = upload_url_resp.json()
            put_url = urls["put_url"]
            download_url = urls["download_url"]
            download_urls.append(download_url)

            pbar.write(
                f"Uploading file {str(count).zfill(len(str(len(file_names))))}/{str(len(file_names))}"
            )

            upload = ResumableUpload(put_url, MAX_CHUNK_SIZE, headers=xml_api_headers)

            with open(file_name, "rb") as content_reader:
                upload.initiate(
                    requests_retry, content_reader, {}, "application/octet-stream"
                )
                last_upload_bytes = 0
                while not upload.finished:
                    try:
                        upload.transmit_next_chunk(requests_retry)
                    except (InvalidResponse, DataCorruption):
                        if upload.invalid:
                            upload.recover(requests_retry)
                        continue
                    except ConnectionError:
                        upload.recover(requests_retry)
                        continue
                    pbar.update(upload.bytes_uploaded - last_upload_bytes)
                    last_upload_bytes = upload.bytes_uploaded

            if delete_after_upload:
                os.remove(file_name)

    return download_urls


def _cleanup_temp_dirs(root_dir: str) -> None:
    sessions = os.listdir(root_dir)
    for session in sessions:
        session_dir = os.path.join(root_dir, session)
        lock_dir = os.path.join(session_dir, "lock")
        # clear session cache if no lockfile or past TTL
        if not os.path.exists(lock_dir):
            if os.path.isdir(session_dir):
                shutil.rmtree(session_dir)
            else:
                os.remove(session_dir)
        else:
            lockfiles = os.listdir(lock_dir)
            if len(lockfiles) == 0:
                shutil.rmtree(session_dir)
            else:
                date = os.path.splitext(lockfiles[0])[0]
                if int(date) < int(datetime.datetime.today().timestamp()):
                    shutil.rmtree(session_dir)


def _create_lock_file(temp_dir: str) -> None:
    """Creates lockfile at <TEMP_DIR>/lock/<EXPIRE_DATE>.lock"""
    lock_dir = os.path.join(temp_dir, "lock")
    os.makedirs(lock_dir)
    expire_date = datetime.datetime.today() + datetime.timedelta(days=tempdir_ttl_days)
    lock_file = os.path.join(lock_dir, str(int(expire_date.timestamp())) + ".lock")
    f = open(lock_file, "w")
    f.close()


def create_root_temp_directory() -> str:
    current_temp_directory = os.getenv("AQUARIUM_TEMP_DIR")

    if not current_temp_directory:
        current_temp_directory = gettempdir()
    else:
        current_temp_directory = os.path.expanduser(current_temp_directory)
        if not os.path.isdir(current_temp_directory):
            raise Exception("Temp dir {} must exist".format(current_temp_directory))

    disk_cache_dir = "aquarium_learning_disk_cache"
    if os.name != "nt":
        try:
            import pwd

            disk_cache_dir = disk_cache_dir + "_" + pwd.getpwuid(os.getuid()).pw_name
        except:
            pass
    root_temp_path = os.path.join(current_temp_directory, disk_cache_dir)
    os.makedirs(root_temp_path, exist_ok=True)
    _cleanup_temp_dirs(root_temp_path)

    return root_temp_path


ROOT_TEMP_FILE_PATH = create_root_temp_directory()


def create_temp_directory() -> str:
    temp_path = os.path.join(ROOT_TEMP_FILE_PATH, str(uuid.uuid4()))
    os.makedirs(temp_path)

    _create_lock_file(temp_path)

    return temp_path


def mark_temp_directory_complete(temp_dir: str) -> None:
    lock_dir = os.path.join(temp_dir, "lock")
    if os.path.exists(lock_dir):
        shutil.rmtree(lock_dir)


def _is_one_gb_available() -> bool:
    """Returns true if there is more than 1 GB available on the current filesystem"""
    return shutil.disk_usage("/").free > pow(1024, 3)  # 1 GB


def assert_valid_name(name: str) -> None:
    is_valid = re.match(r"^[A-Za-z0-9_]+$", name)
    if not is_valid:
        raise Exception(
            "Name {} must only contain alphanumeric and underscore characters".format(
                name
            )
        )


def raise_resp_exception_error(resp: requests.Response) -> None:
    if not resp.ok:
        message = None
        try:
            r_body = resp.json()
            message = r_body.get("message") or r_body.get("msg")
        except:
            # If we failed for whatever reason (parsing body, etc.)
            # Just return the code
            raise Exception(
                "HTTP Error received: {}".format(str(resp.status_code))
            ) from None

        if message:
            raise Exception("Error: {}".format(message))
        else:
            raise Exception(
                "HTTP Error received: {}".format(str(resp.status_code))
            ) from None


def determine_latest_version() -> Optional[str]:
    from bs4 import BeautifulSoup
    from http import HTTPStatus
    import requests
    import re

    PACKAGE_REPO_URL = "https://aquarium-not-pypi.web.app/{}".format(__package__)
    SEM_VER_MATCHER = re.compile(
        f"{__package__}-(.*)\.tar\.gz"  # noqa: W605 (invalid escape seq)
    )

    r = requests.get(PACKAGE_REPO_URL)
    if r.status_code == HTTPStatus.OK:
        # Python package repos have a standard layout:
        # https://packaging.python.org/guides/hosting-your-own-index/
        versions = BeautifulSoup(r.text, "html.parser").find_all("a")
        if len(versions) > 0:
            version_match = SEM_VER_MATCHER.match(versions[-1]["href"])
            if version_match is not None:
                return version_match.group(1)
    return None


def check_if_update_needed() -> None:
    from importlib_metadata import version
    from termcolor import colored

    current_version = version(__package__)
    latest_version = determine_latest_version()

    if latest_version != None and current_version != latest_version:
        print(
            colored(
                f"aquariumlearning: Please upgrade from version {current_version} to latest version {latest_version}.",
                "yellow",
            )
        )


def add_object_user_attrs(
    attrs: Dict[str, Any], user_attrs: Optional[Dict[str, Any]]
) -> None:
    if user_attrs is not None:
        for k, v in user_attrs.items():
            if "user__" not in k:
                k = "user__" + k
            attrs[k] = v


def is_valid_float(num: Any) -> bool:
    return isinstance(num, float) and not isnan(num) and not isinf(num)


def is_valid_int(num: Any) -> bool:
    return isinstance(num, int)


def is_valid_number(num: Any) -> bool:
    return is_valid_int(num) or is_valid_float(num)


def assert_and_get_valid_iso_date(date_string: str) -> str:
    try:
        date_string_fixed = date_string.replace("Z", "+00:00")
        datetime.datetime.fromisoformat(date_string_fixed)
        return date_string_fixed
    except:
        raise Exception(
            f'Date: "{date_string}" not given in valid iso formatted string'
        )


def split_user_attrs(attrs: Dict[str, Any]) -> Dict[str, Any]:
    user_attrs = {}
    for k, v in attrs.items():
        if "user__" in k:
            user_attrs[k] = v

    return user_attrs


def maybe_parse_json_vals(dict: Dict[str, Any]) -> Dict[str, Any]:
    new_dict = {}
    for k, v in dict.items():
        try:
            new_value = json.loads(v)
            new_dict[k] = new_value
        except:
            new_dict[k] = v
    return new_dict


# TODO: Is there a way to just infer these from the constant initialized dictionary literal?
USER_METADATA_PRIMITIVE = Union[str, int, float, bool]
USER_METADATA_PRIMITIVE_TYPES = Literal["str", "int", "float", "bool"]
USER_METADATA_SEQUENCE = Union[
    List[str],
    List[int],
    List[float],
    List[bool],
    Tuple[str],
    Tuple[int],
    Tuple[float],
    Tuple[bool],
]
USER_METADATA_MODE_TYPES = Literal["list", "scalar"]

SUPPORTED_USER_METADATA_TYPES = Union[USER_METADATA_PRIMITIVE, USER_METADATA_SEQUENCE]

TYPE_PRIMITIVE_TO_STRING_MAP: Dict[
    Type[USER_METADATA_PRIMITIVE], USER_METADATA_PRIMITIVE_TYPES
] = {
    str: "str",
    int: "int",
    float: "float",
    bool: "bool",
}

POLYGON_VERTICES_KEYS = Literal["vertices"]
POSITION_KEYS = Literal["x", "y", "z"]
ORIENTATION_KEYS = Literal["w", "x", "y", "z"]
KEYPOINT_KEYS = Literal["x", "y", "name"]

ALL_POSITION_KEYS: List[POSITION_KEYS] = ["x", "y", "z"]
ALL_ORIENTATION_KEYS: List[ORIENTATION_KEYS] = ["x", "y", "z", "w"]

CAMERA_MODELS = Literal["brown_conrady", "fisheye"]

ALL_CAMERA_MODELS: List[CAMERA_MODELS] = ["brown_conrady", "fisheye"]

# We work directly with dicts because it's tossed directly into a json.dumps()
# Should we make a python wrapper class for all of these?
# These are mostly internal use.
LabelType = Literal[
    "BBOX_2D",
    "LINE_SEGMENT_2D",
    "TEXT_TOKEN",
    "CUBOID_3D",
    "KEYPOINTS_2D",
    "POLYGON_LIST_2D",
    "SEMANTIC_LABEL_URL_2D",
    "SEMANTIC_LABEL_ASSET_2D",
    "INSTANCE_LABEL_URL_2D",
    "INSTANCE_LABEL_ASSET_2D",
    "INSTANCE_LABEL_2D",
    "CLASSIFICATION_2D",
    "CLASSIFICATION_3D",
]

UpdateType = Literal["ADD", "MODIFY", "DELETE"]

# TODO: Type these.
# Python can't really capture partial shapes of dictionaries, so we probably
# want to shift to making these native python classes with a serialization method.

GtLabelAttrs = Dict[str, Any]
InferenceAttrs = Dict[str, Any]
LabelAttrs = Dict[str, Any]


class BaseLabelEntryDict(TypedDict):
    uuid: str
    linked_labels: List[Any]
    label_type: LabelType
    label: str
    label_coordinate_frame: str
    attributes: LabelAttrs


LabelAssetType = Literal["SEMSEG_MASK", "INSTANCE_SEG_MASK"]


class BaseLabelAssetDict(TypedDict):
    uuid: str
    asset_type: LabelAssetType
    value: Any


class GtLabelEntryDict(BaseLabelEntryDict):
    pass


class InferenceEntryDict(BaseLabelEntryDict):
    pass


EmbeddingVec = List[Union[int, float]]


class CropEmbeddingDict(TypedDict):
    uuid: str
    embedding: EmbeddingVec
    model_id: str
    date_generated: str


class FrameEmbeddingDict(TypedDict):
    task_id: str
    model_id: str
    date_generated: str
    embedding: EmbeddingVec


class LabelFrameSummary(TypedDict):
    frame_id: str
    label_counts: Dict[LabelType, int]


class InferenceFrameSummary(LabelFrameSummary):
    custom_metrics_names: List[str]


ElementType = Union[Literal["crop"], Literal["frame"]]
PrimaryTask = Union[
    Literal["2D_SEMSEG"],
    Literal["2D_INSTANCE_SEGMENTATION"],
    Literal["CLASSIFICATION"],
    Literal["MULTI_LABEL_CLASSIFICATION"],
]

ResizeMode = Literal["fill"]
