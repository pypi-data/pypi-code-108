from datetime import datetime as dt
from multiprocessing import Queue
from pathlib import Path
import sys
from threading import Thread
import time
import traceback
from typing import Optional, Tuple, Union
from urllib.parse import urlparse

from .utils import (
    _get_or_create_resource_archive,
    make_name_by_path,
)
from ..config import AnylearnConfig
from ..interfaces import Mirror
from ..interfaces.resource import (
    Algorithm,
    Resource,
    ResourceState,
    ResourceUploader,
    ResourceVisibility,
    SyncResourceUploader,
)
from ..utils import logger
from ..utils.errors import (
    AnyLearnException,
    AnyLearnMissingParamException,
    AnyLearnNotSupportedException,
    AnylearnRequiredLocalCommitException,
)


DEFAULT_TRAIN_PARAMS = "[{\"name\":\"dataset\",\"type\":\"dataset\",\"suggest\":1}]"
DEFAULT_EVAL_PARAMS = "[{\"name\":\"dataset\",\"type\":\"dataset\",\"suggest\":1},\
                        {\"name\":\"model_path\",\"alias\":\"\",\"description\":\"\",\"type\":\"model\",\"suggest\":1}]"


def sync_algorithm(
    id: Optional[str]=None,
    name: Optional[str]=None,
    dir_path: Optional[Union[str, Path]]=None,
    archive_path: Optional[str]=None, # deprecated in 0.11.11, remove in 0.12.3
    entrypoint_training: Optional[str]=None,
    output_training: Optional[str]=None,
    entrypoint_evaluation: Optional[str]=None, # deprecated in 0.11.11, remove in 0.12.3
    output_evaluation: Optional[str]=None, # deprecated in 0.11.11, remove in 0.12.3
    mirror_name: Optional[str]="QUICKSTART",
    uploader: Optional[ResourceUploader]=None,
    polling: Union[float, int]=5,
    force: bool=False,
) -> Tuple[Algorithm, str]:
    if id:
        return _sync_remote_algorithm(
            id=id,
            entrypoint_training=entrypoint_training,
            output_training=output_training,
            entrypoint_evaluation=entrypoint_evaluation,
            output_evaluation=output_evaluation,
            image_name=mirror_name,
        )
    else:
        deprecated = {
            'archive_path': archive_path,
            'entrypoint_evaluation': entrypoint_evaluation,
            'output_evaluation': output_evaluation,
        }
        for k, v in deprecated.items():
            if v:
                logger.warning(
                    f"Parameter `{k}` is deprecated since 0.11.11 "
                    "and will be removed in 0.12.3."
                )
        return _sync_local_algorithm(
            name=name,
            dir_path=dir_path,
            entrypoint_training=entrypoint_training,
            output_training=output_training,
            image_name=mirror_name,
            uploader=uploader,
            polling=polling,
            force=force,
        )


def _sync_remote_algorithm(
    id: str,
    entrypoint_training: Optional[str]=None,
    output_training: Optional[str]=None,
    entrypoint_evaluation: Optional[str]=None,
    output_evaluation: Optional[str]=None,
    image_name: Optional[str]='QUICKSTART',
) -> Tuple[Algorithm, Optional[str]]:
    algo = Algorithm(id=id, load_detail=True)
    algo.mirror_id =_get_quickstart_mirror(image_name).id
    if entrypoint_training is not None:
        algo.entrypoint_training = entrypoint_training
    if output_training is not None:
        algo.output_training = output_training
    # Eval things is temporarily deactivated, ignored here
    algo.save()
    algo.get_detail()
    return algo, None


def _sync_local_algorithm(
    name: str,
    dir_path: Union[str, Path],
    entrypoint_training: str,
    output_training: str,
    image_name: str="QUICKSTART",
    uploader: Optional[ResourceUploader]=None,
    polling: Union[float, int]=5,
    force: bool=False
) -> Tuple[Algorithm, Optional[str]]:
    # Required params
    if not all([dir_path, entrypoint_training, output_training]):
        raise AnyLearnMissingParamException((
            "Parameters "
            "`dir_path`, `entrypoint_training` and `output_training` "
            "are required"
        ))
    if not name:
        name = make_name_by_path(dir_path)
    _check_local_algorithm(dir_path)
    algo = _get_or_create_algorithm(
        name=name,
        dir_path=dir_path,
        entrypoint_training=entrypoint_training,
        output_training=output_training,
        image_name=image_name,
    )
    if AnylearnConfig.git_ready and algo.git_address:
        current_sha = _sync_algorithm_repo(
            algorithm=algo,
            dir_path=dir_path,
            force=force,
        )
        logger.info("Waiting algorithm to be ready...")
        algo.sync_finish(checkout_sha=current_sha)
    else:
        _upload_algorithm(
            algorithm=algo,
            dir_path=dir_path,
            uploader=uploader,
            polling=polling,
        )
        current_sha = None
    return algo, current_sha


def _check_local_algorithm(dir_path: str) -> None:
    logger.info(f"Verifying local algorithm in '{dir_path}'")
    dir_path = Path(dir_path)
    # Check directory
    if not all([
        dir_path.exists(),
        dir_path.is_dir(),
    ]):
        raise AnyLearnException(
            "Parameter `dir_path` must be an existing directory"
        )
    # Check requirements.txt
    if not (dir_path / "requirements.txt").exists():
        raise AnyLearnException(("Missing 'requirements.txt' "
                                 "in algorithm directory"))


def _get_or_create_algorithm(name: str,
                             dir_path: Union[str, Path],
                             entrypoint_training: str,
                             output_training: str,
                             image_name: str="QUICKSTART") -> Algorithm:
    # Algo name or dir name
    if not name:
        logger.warning(
            "Algorithm `name` is not set, using directory basename"
        )
        name = dir_path.name
    image = _get_quickstart_mirror(image_name)
    algo = _get_algorithm_by_name(name)
    if algo:
        logger.warning(f"Algorithm named '{name}' already exists.")
    else:
        logger.info(f"Creating new algorithm '{name}'")
        algo =_create_new_algorithm(name)
    # Set execution metadata
    algo.mirror_id = image.id
    algo.entrypoint_training = entrypoint_training
    algo.output_training = output_training
    # Existing/new algo needs respectively create/update towards remote
    algo.save()
    algo.get_detail()
    return algo


def _get_algorithm_by_name(name) -> Optional[Algorithm]:
    try:
        return Algorithm.get_user_custom_algorithm_by_name(name=name)
    except:
        return None


def _create_new_algorithm(name: str) -> Algorithm:
    algo = Algorithm(
        name=name,
        description="SDK_QUICKSTART",
        visibility=ResourceVisibility.PRIVATE,
        filename=f"{name}.zip", # legacy
        is_zipfile=True, # legacy
        train_params=DEFAULT_TRAIN_PARAMS,
        evaluate_params=DEFAULT_EVAL_PARAMS,
        follows_anylearn_norm=False,
    )
    return algo


def _get_quickstart_mirror(name: str) -> Mirror:
    mirrors = Mirror.get_list()
    try:
        return next(m for m in mirrors if m.name == name)
    except:
        raise AnyLearnNotSupportedException((
            f"Container for `{name}` is not supported by "
            "the connected backend."
        ))

def _sync_algorithm_repo(algorithm: Algorithm,
                         dir_path: str,
                         force: bool=False) -> None:
    if AnylearnConfig.git_ready:
        from git import Repo
        from .git_progress_printer import GitProgressPrinter
    logger.info(f"Synchronizing algorithm repo to {algorithm.git_address}")
    repo = Repo.init(dir_path)
    # Origin
    try:
        origin = repo.remotes.anylearn
        origin.set_url(_auth_git_url(algorithm.git_address))
    except AttributeError:
        origin = repo.create_remote(
            'anylearn',
            _auth_git_url(algorithm.git_address),
        )
    # Try fetching
    if origin.exists():
        logger.debug("Fetching")
        origin.fetch()
    else:
        logger.debug("Skipped `git fetch`")
    # add & commit & push
    logger.debug("Staging")
    repo.git.add(A=True)
    try:
        # Check staged changes
        empty_stage = not repo.index.diff(repo.tree())
    except ValueError:
        # Non published repo occurs ValueError
        empty_stage = False
    if not empty_stage:
        if not force:
            raise AnylearnRequiredLocalCommitException
        logger.warning(
            f"Forced auto-committing changes in '{dir_path}'"
        )
        logger.debug("Commiting")
        repo.index.commit(_commit_msg())
    push_args = {'all': True}
    if force:
        push_args['force'] = True
    logger.debug("Pushing")
    origin.push(progress=GitProgressPrinter(), **push_args)
    # Reset remote URL without credentials
    origin.set_url(algorithm.git_address)
    return repo.head.commit.hexsha


def _auth_git_url(url):
    p = urlparse(url)
    root = p.netloc.split('@')[-1]
    auth = f"{AnylearnConfig.username}:{AnylearnConfig.password}"
    return p._replace(netloc=f"{auth}@{root}").geturl()


def _commit_msg():
    return (
        "Anylearn auto-commit "
        f"{dt.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )


def _upload_algorithm(algorithm: Algorithm,
                      dir_path: str,
                      uploader: Optional[ResourceUploader]=None,
                      polling: Union[float, int]=5):
    if not uploader:
        uploader = SyncResourceUploader()
    archive = _get_or_create_resource_archive(
        name=algorithm.name,
        dir_path=dir_path,
    )
    q = Queue()
    t_algorithm = Thread(
        target=__do_upload,
        args=[q],
        kwargs={
            'resource_id': algorithm.id,
            'file_path': archive,
            'uploader': uploader,
        }
    )
    logger.info(f"Uploading algorithm {algorithm.name}...")
    t_algorithm.start()
    err = q.get()
    t_algorithm.join()
    Path(archive).unlink()
    if err:
        ex_type, ex_value, tb_str = err
        message = f"{str(ex_value)} (in subprocess)\n{tb_str}"
        raise ex_type(message)
    __wait_algorithm_ready(algorithm, polling)
    logger.info("Successfully uploaded algorithm")


def __do_upload(q: Queue, *args, **kwargs):
    try:
        Resource.upload_file(*args, **kwargs)
        err = None
    except:
        ex_type, ex_value, tb = sys.exc_info()
        err = ex_type, ex_value, ''.join(traceback.format_tb(tb))
    q.put(err)


def __wait_algorithm_ready(algorithm: Algorithm, polling: Union[float, int]=5):
    algorithm.state = None
    finished = [ResourceState.ERROR, ResourceState.READY]
    while algorithm.state not in finished:
        time.sleep(polling)
        algorithm.get_detail()
    if algorithm.state == ResourceState.ERROR:
        raise AnyLearnException("An error occured when uploading algorithm")
    logger.info("Algorithm is ready")
