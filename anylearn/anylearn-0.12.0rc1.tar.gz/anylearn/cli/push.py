import click
from requests import HTTPError
from typing import Optional, Union

from anylearn.applications.algorithm_manager import sync_algorithm
from anylearn.applications.dataset_manager import sync_dataset
from anylearn.cli.anylearn_cli_config import AnylearnCliConfig
from anylearn.cli.utils import (
    check_config,
    check_connection,
    cmd_confirm_or_abort,
    cmd_error,
    cmd_info,
    cmd_success,
    cmd_warning,
    get_cmd_command,
)
from anylearn.interfaces import Algorithm, Dataset, Project
from anylearn.interfaces.resource import (
    AsyncResourceUploader,
    SyncResourceUploader,
)
from anylearn.utils.errors import AnylearnRequiredLocalCommitException


_option_force = click.option(
    '-f', '--force',
    is_flag=True,
    default=False,
    help="Skip prompt and force actions."
)


_option_async_upload = click.option(
    '--async-upload',
    is_flag=True,
    default=False,
    help="Upload in asynchronous mode."
)


@click.group("push")
def commands():
    """
    Push local project or algorithm(s) or dataset(s) to remote Anylearn.
    """
    pass


@commands.command()
@_option_force
@_option_async_upload
@check_config()
@check_connection()
@get_cmd_command()
def all(force: bool=False, async_upload: bool=False):
    """
    Create/update local project, all algorithms and all datasets
    to remote Anylearn.
    """
    config = AnylearnCliConfig.load()
    # Project
    cmd_info(msg=f"Pushing project {config.project.name}...")
    config.project = _push_project(project=config.project, force=force)
    cmd_success(msg="PUSHED")
    AnylearnCliConfig.update(config)

    # All algorithms
    for name in config.algorithms.keys():
        try:
            cmd_info(msg=f"Pushing algorithm {name}...")
            algorithm = _push_1_algorithm(
                algorithm=config.algorithms[name],
                dir=config.path['algorithm'][name],
                image=config.images[name],
                force=force,
            )
            config.algorithms[name] = algorithm
            AnylearnCliConfig.update(config)
            cmd_success(msg="PUSHED")
        except KeyError:
            cmd_warning(msg=(
                f"Algorithm named {name} or its path config does not exist, "
                "ignored."
            ))
            continue
    # All datasets
    for name in config.datasets.keys():
        try:
            cmd_info(msg=f"Pushing dataset {name}...")
            dataset = _push_1_dataset(
                dataset=config.datasets[name],
                dir=config.path['dataset'][name],
                force=force,
            )
            config.datasets[name] = dataset
            AnylearnCliConfig.update(config)
            cmd_success(msg="PUSHED")
        except KeyError:
            cmd_warning(msg=(
                f"Dataset named {name} or its path config does not exist, "
                "ignored."
            ))
            continue
    cmd_success(msg="DONE")


@commands.command()
@_option_force
@check_config()
@check_connection()
@get_cmd_command()
def project(force: bool=False):
    """
    Create/update local project to remote Anylearn.
    """
    config = AnylearnCliConfig.load()
    config.project = _push_project(project=config.project, force=force)
    AnylearnCliConfig.update(config)
    cmd_success(msg="PUSHED")


def _push_project(project: Project, force: bool=False) -> Project:
    if project.id:
        try:
            remote_project = Project(project.id, load_detail=True)
            if remote_project == project:
                cmd_info(msg="Already up-to-date.")
                return project
            cmd_warning(msg=(
                "Remote project "
                "("
                f"id={remote_project.id}, "
                f"name={remote_project.name}"
                ") will be overridden."
            ))
            if not force:
                cmd_confirm_or_abort()
        except HTTPError:
            cmd_warning(msg=(
                "Remote project "
                "("
                f"id={project.id}, "
                f"name={project.name}"
                ") is unaccessible. "
                "A new project will be created."
            ))
            if not force:
                cmd_confirm_or_abort()
            project.id = None
    project.save()
    project.get_detail()
    return project


@commands.command()
@click.argument('name')
@_option_force
@_option_async_upload
@check_config()
@check_connection()
@get_cmd_command()
def algorithm(name :str, force: bool=False, async_upload: bool=False):
    """
    Create/update and/or upload local algorithm to remote Anylearn.
    """
    config = AnylearnCliConfig.load()
    try:
        algo = config.algorithms[name]
        dir = config.path['algorithm'][name]
        img = config.images[name]
    except KeyError:
        cmd_error(msg=(
            f"Algorithm named {name} or its path config does not exist."
        ))
        raise click.Abort
    uploader = AsyncResourceUploader() if async_upload else SyncResourceUploader()
    algo = _push_1_algorithm(
        algorithm=algo,
        dir=dir,
        image=img,
        force=force,
    )
    config.algorithms[name] = algo
    AnylearnCliConfig.update(config)
    cmd_success(msg="PUSHED")


def _push_1_algorithm(
    algorithm: Algorithm,
    dir: Optional[str]=None,
    image: Optional[str]='QUICKSTART',
    force: bool=False,
    uploader=None,
    polling=5,
) -> Algorithm:
    if dir:
        return __push_local_algorithm(
            algorithm=algorithm,
            dir=dir,
            image=image,
            force=force,
        )
    else:
        return __push_remote_algorithm(
            algorithm=algorithm,
            force=force,
        )


def __push_local_algorithm(
    algorithm: Algorithm,
    dir: str,
    image: str,
    force: bool=False,
):
    try:
        algo, _ = sync_algorithm(
            name=algorithm.name,
            dir_path=dir,
            entrypoint_training=algorithm.entrypoint_training,
            output_training=algorithm.output_training,
            mirror_name=image,
            force=False,
        )
        return algo
    except AnylearnRequiredLocalCommitException as e:
        cmd_warning(msg=(
            f"Algorithm dir {dir} is not clean, commit required. "
            "Anylearn can make an auto-commit in this case "
            "(or you can cancel the operation and "
            "commit your changes yourself)."
        ))
        if not force:
            cmd_confirm_or_abort()
        algo, _ = sync_algorithm(
            name=algorithm.name,
            dir_path=dir,
            entrypoint_training=algorithm.entrypoint_training,
            output_training=algorithm.output_training,
            mirror_name=image,
            force=True,
        )
        return algo


def __push_remote_algorithm(algorithm: Algorithm, force: bool=False):
    try:
        remote_algo = Algorithm(id=algorithm.id, load_detail=True)
        if remote_algo == algorithm:
            cmd_info(msg="Metadata already up-to-date.")
        else:
            cmd_warning(msg=(
                "Remote algorithm "
                "("
                f"id={remote_algo.id}, "
                f"name={remote_algo.name}"
                ") will be overridden."
            ))
            if not force:
                cmd_confirm_or_abort()
            algorithm.save()
    except HTTPError:
        cmd_error(msg=(
            "Remote algorithm "
            "("
            f"id={algorithm.id}, "
            f"name={algorithm.name}"
            ") is unaccessible."
        ))
        raise click.Abort
    return algorithm


@commands.command()
@click.argument('name')
@_option_force
@_option_async_upload
@check_config()
@check_connection()
@get_cmd_command()
def dataset(name :str, force: bool=False, async_upload: bool=False):
    """
    Create/update and/or upload local dataset to remote Anylearn.
    """
    config = AnylearnCliConfig.load()
    try:
        dset = config.datasets[name]
        dir = config.path['dataset'][name]
    except KeyError:
        cmd_error(msg=(
            f"Dataset named {name} or its path config does not exist."
        ))
        raise click.Abort
    uploader = AsyncResourceUploader() if async_upload else SyncResourceUploader()
    dset = _push_1_dataset(
        dataset=dset,
        dir=dir,
        force=force,
        uploader=uploader,
    )
    if dset:
        config.datasets[name] = dset
        AnylearnCliConfig.update(config)
        cmd_success(msg="PUSHED")


def _push_1_dataset(
    dataset: Dataset,
    dir: Optional[str]=None,
    force: bool=False,
    uploader=None,
    polling=5,
) -> Dataset:
    if dataset.id:
        return __push_remote_dataset(
            dataset=dataset,
            force=force,
        )
    else:
        return __push_local_dataset(
            dataset=dataset,
            dir=dir,
            uploader=uploader,
            polling=polling,
        )


def __push_local_dataset(
    dataset: Dataset,
    dir: Optional[str]=None,
    uploader=None,
    polling=5,
):
    return sync_dataset(
        id=dataset.id,
        name=dataset.name,
        dir_path=dir,
        uploader=uploader,
        polling=polling,
    )


def __push_remote_dataset(dataset: Dataset, force: bool=False):
    try:
        remote_dset = Dataset(id=dataset.id, load_detail=True)
        if remote_dset == dataset:
            cmd_info(msg="Metadata already up-to-date.")
        else:
            cmd_warning(msg=(
                "Remote dataset "
                "("
                f"id={remote_dset.id}, "
                f"name={remote_dset.name}"
                ") will be overridden."
            ))
            if not force:
                cmd_confirm_or_abort()
            dataset.save()
    except HTTPError:
        cmd_error(msg=(
            "Remote dataset "
            "("
            f"id={dataset.id}, "
            f"name={dataset.name}"
            ") is unaccessible."
        ))
        raise click.Abort
    return dataset
