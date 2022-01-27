import datetime
from os.path import normpath, join

from fsos import fs_manager as fsm
from fsos.deco import os_failure_checker

"""
OS structure
{
    FSOS_BUCKET_KEY : {
        "Bucket_key" : {
            "Object_key" : {
                "path" : relative_file_path
                "meta" : meta_info
            }
        }
    },
    FSOS_VERSION_KEY : {
        version
    }
}
"""


@os_failure_checker
def _list_bucket(root_path: str) -> list:
    """get list of bucket in root fsos"""
    return list(fsm._get_db()[fsm.FSOS_BUCKET_KEY].keys())


@os_failure_checker
def _check_bucket(bucket_name: str, root_path: str) -> bool:
    """check bucket is exist in root fsos"""
    return bucket_name in fsm._get_db()[fsm.FSOS_BUCKET_KEY].keys()


@os_failure_checker
def _add_bucket(bucket_name: str, root_path: str) -> bool:
    """add bucket folder & fsos db"""
    fsm._get_db()[fsm.FSOS_BUCKET_KEY][bucket_name] = {}
    fsm._create_folder(root_path, bucket_name)
    return True


@os_failure_checker
def _remove_bucket(bucket_name: str, root_path: str) -> bool:
    """remove bucket folder & fsos db"""
    del fsm._get_db()[fsm.FSOS_BUCKET_KEY][bucket_name]
    fsm._remove_folder(root_path, bucket_name)
    return True


@os_failure_checker
def _copy_object(
    bucket_name: str,
    object_name: str,
    from_path: str,
    root_path: str,
    ignore_exist=False,
) -> bool:
    """copy file in fsos system"""
    fsm._get_db()[fsm.FSOS_BUCKET_KEY][bucket_name][object_name] = {
        "path": f"{bucket_name}/{object_name}",
        "meta": {},
        "created_time": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    fsm._copy_file(
        normpath(from_path), normpath(
            join(root_path, bucket_name, object_name))
    )
    return True


@os_failure_checker
def _add_object(
    bucket_name: str,
    object_name: str,
    object: bytes,
    root_path: str,
    ignore_exist=False,
) -> bool:
    """save byte in fsos system"""
    # TODO
    return True


@os_failure_checker
def _remove_object(bucket_name: str, object_name: str, root_path: str) -> bool:
    del fsm._get_db()[fsm.FSOS_BUCKET_KEY][bucket_name][object_name]
    fsm._remove_file(normpath(join(root_path, bucket_name, object_name)))
    return True


@os_failure_checker
def _update_object_meta(
    bucket_name: str, object_name: str, meta_info: dict, root_path: str
) -> bool:
    object_info = fsm._get_db()[fsm.FSOS_BUCKET_KEY][bucket_name][object_name]
    object_info["meta"] = meta_info
    return True


def _update_object(
    bucket_name: str, object_name: str, object: bytes, root_path: str
) -> bool:
    # TODO
    return True


@os_failure_checker
def _list_object(bucket_name: str, root_path: str) -> list:
    return list(fsm._get_db()[fsm.FSOS_BUCKET_KEY][bucket_name].keys())
