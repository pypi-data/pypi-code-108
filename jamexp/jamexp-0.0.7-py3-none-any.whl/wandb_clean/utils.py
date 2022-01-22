import datetime
import os.path as osp
import shutil
import socket

import wandb
from loguru import logger

# https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
TIME_PARTTERN = "%Y-%m-%dT%H:%M:%S"


def extract_time(run):
    """extract run info

    :param run: [description]
    :type run: [type]
    :return: duration, run2now
    :rtype: datetime.timedelta
    """
    create_time_str = run.createdAt
    last_time_str = run.heartbeatAt
    start_time = datetime.datetime.strptime(create_time_str, TIME_PARTTERN)
    end_time = datetime.datetime.strptime(last_time_str, TIME_PARTTERN)
    now_time = datetime.datetime.now()
    duration = end_time - start_time
    run2now = now_time - end_time
    return duration, run2now


def delete_run(run, delete=True, is_all=False):
    """delete a wandb run on server

    :param run: wandb run object
    :type run: wandb.run
    :param delete: delete local run if exists and delete remote run, defaults to True
    :type delete: bool, optional
    :param is_all: delete runs not run on this machine, defaults to False
    :type is_all: bool, optional
    """
    # FIXME: should be a better approach to get hostname
    delete_info = f"{run.name}\t{run.url}\n"
    if not is_all and run.config["host"] != socket.gethostname():
        delete_info += f"\t{run.config['host']}! not no this machine!\n"
        logger.info(delete_info)
    else:
        cfg = run.config
        if "run_path" in cfg:
            if osp.exists(cfg["run_path"]):
                if delete:
                    shutil.rmtree(cfg["run_path"], ignore_errors=True)
                delete_info += f"\t Delete local run path: {cfg['run_path']}"
        logger.info(delete_info)
        if delete:
            run.delete()


def get_run_from_url(url: str):
    segs = url.split("/")
    entity = segs[-4]
    proj = segs[-3]
    run_id = segs[-1]
    wandb_id = "/".join([entity, proj, run_id])
    api = wandb.Api()
    try:
        run = api.run(wandb_id)
    except Exception as e:  # pylint: disable=broad-except
        run = None
        logger.critical(f"ERROR: {url}, \t{e}")
    return run


def delete_run_from_url(url: str):
    run = get_run_from_url(url)
    if run is not None:
        run.delete()
