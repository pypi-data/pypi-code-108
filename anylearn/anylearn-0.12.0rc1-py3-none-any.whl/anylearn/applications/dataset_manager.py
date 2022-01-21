from multiprocessing import Queue
from pathlib import Path
import sys
from threading import Thread
import time
import traceback
from typing import Optional, Union

from .utils import (
    _get_archive_checksum,
    _get_or_create_resource_archive,
    make_name_by_path,
)
from ..interfaces.resource import (
    Dataset,
    Resource,
    ResourceState,
    ResourceUploader,
    ResourceVisibility,
    SyncResourceUploader,
)
from ..storage.db import DB
from ..utils import logger
from ..utils.errors import (
    AnyLearnException,
    AnyLearnMissingParamException,
)


def sync_dataset(
    id: Optional[str]=None,
    name: Optional[str]=None,
    dir_path: Optional[Union[str, Path]]=None,
    archive_path: Optional[str]=None,
    uploader: Optional[ResourceUploader]=None,
    polling: Union[float, int]=5,
) -> Dataset:
    try:
        return Dataset(id=id, load_detail=True)
    except:
        dset, archive, upload = _sync_local_dataset(
            name=name,
            dir_path=dir_path,
            archive_path=archive_path,
        )
        if archive and upload:
            _upload_dataset(
                dataset=dset,
                archive=archive,
                uploader=uploader,
                polling=polling,
            )
        return dset


def _sync_local_dataset(
    name: Optional[str]=None,
    dir_path: Optional[Union[str, Path]]=None,
    archive_path: Optional[str]=None,
):
    if not any([dir_path, archive_path]):
        raise AnyLearnMissingParamException((
            "None of ['dir_path', 'archive_path'] "
            "is specified."
        ))
    if not name:
        name = make_name_by_path(dir_path or archive_path)
    archive_path = _get_or_create_resource_archive(
        name=name,
        dir_path=dir_path,
        archive_path=archive_path
    )
    checksum = _get_archive_checksum(archive_path)
    dset, upload = _get_or_create_raw_dataset(name=name, checksum=checksum)
    return dset, archive_path, upload


def _get_or_create_raw_dataset(name, checksum):
    to_upload = False
    dset = _get_dataset_by_checksum(checksum)
    if not dset:
        to_upload = True
        dset = _create_new_dataset(name)
    return dset, to_upload


def _get_dataset_by_checksum(checksum) -> Optional[Dataset]:
    local_id = DB().find_local_dataset_by_checksum(checksum=checksum)
    if not local_id:
        return None
    try:
        return Dataset(id=local_id, load_detail=True)
    except:
        logger.warning(
            f"Local dataset ({local_id}) "
            "has been deleted remotely, "
            "forced to re-registering dataset."
        )
        DB().delete_local_dataset(id=local_id)
        return None


def _create_new_dataset(name) -> Dataset:
    dset = Dataset(
        name=name,
        description="SDK_QUICKSTART",
        visibility=ResourceVisibility.PRIVATE,
        filename=f"{name}.zip",
        is_zipfile=True,
    )
    dset.save()
    return dset


def _upload_dataset(dataset: Dataset,
                    archive: str,
                    uploader: Optional[ResourceUploader]=None,
                    polling: Union[float, int]=5):
    if not uploader:
        uploader = SyncResourceUploader()
    q = Queue()
    t_dataset = Thread(
        target=__do_upload,
        args=[q],
        kwargs={
            'resource_id': dataset.id,
            'file_path': archive,
            'uploader': uploader,
        }
    )
    logger.info(f"Uploading dataset {dataset.name}...")
    t_dataset.start()
    err = q.get()
    t_dataset.join()
    if err:
        ex_type, ex_value, tb_str = err
        message = f"{str(ex_value)} (in subprocess)\n{tb_str}"
        raise ex_type(message)
    finished = [ResourceState.ERROR, ResourceState.READY]
    while dataset.state not in finished:
        time.sleep(polling)
        dataset.get_detail()
    if dataset.state == ResourceState.ERROR:
        raise AnyLearnException("Error occured when uploading dataset")
    logger.info("Successfully uploaded dataset")


def __do_upload(q: Queue, *args, **kwargs):
    try:
        Resource.upload_file(*args, **kwargs)
        err = None
    except:
        ex_type, ex_value, tb = sys.exc_info()
        err = ex_type, ex_value, ''.join(traceback.format_tb(tb))
    q.put(err)
