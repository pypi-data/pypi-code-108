import os
import os.path as osp
import re
import shutil
from datetime import datetime, timedelta
from glob import glob

from loguru import logger
from omegaconf import OmegaConf

from jamexp.utils import latest_time
from jamexp.wandb_clean import get_run_from_url


def extract_all_exp(folder: str = "outputs"):
    """extract whole hyd runs under folder

    :param folder: [description], defaults to "outputs"
    :type folder: str, optional
    :return: list of pathes
    """
    rtn_exps = []
    if not osp.exists(folder):
        logger.error(f"{folder} does not exists")
        exit(1)
    for cur_path in glob(f"{folder}/*/*/"):
        # TODO: remove me. Should be a global variable or more customized!
        if re.search(r"\d{4}-\d{2}-\d{2}/\d{2}-\d{2}-\d{2}/$", cur_path):
            rtn_exps.append(cur_path)
    return sorted(rtn_exps, reverse=True)


def time_from_folder(folder_str: str):
    """hyd folder name 2 its creation time

    :param folder_str: [description]
    :type folder_str: str
    :return: datetime
    """
    assert folder_str[-1] == "/"
    exp_path_time = folder_str[-20:]
    return datetime.strptime(exp_path_time, "%Y-%m-%d/%H-%M-%S/")


def clear_empty(folder: str = "outputs"):
    """clear empty hyd runs folder

    :param folder: [description], defaults to "outputs"
    :type folder: str, optional
    """
    for cur_path in glob(f"{folder}/*/"):
        if len(os.listdir(cur_path)) == 0:
            shutil.rmtree(str(cur_path), ignore_errors=True)


def filter_hyd_stale(folder: str = "outputs"):
    to_delete = []
    for run_f in extract_all_exp(folder):
        create_time = time_from_folder(run_f)
        end_time = latest_time(run_f)
        now = datetime.now()
        run2now = now - end_time
        duration = end_time - create_time
        time_thred = [[0, 10], [7, 60], [3, 180], [1, 600]]
        for thr_d, thr_s in time_thred:
            if run2now > timedelta(days=thr_d) and duration < timedelta(seconds=thr_s):
                wandb_run = run_from_meta(run_f)
                if wandb_run is not None:
                    logger.info(f"SHORT: {run_f}\t {wandb_run.url}")
                else:
                    logger.info(f"SHORT: {run_f}")
                to_delete.append(run_f)
                break
    return to_delete


def run_from_meta(run_f: str):
    meta_f = osp.join(run_f, "meta.yaml")
    if osp.exists(meta_f):
        conf = OmegaConf.load(meta_f)
        if "WEIGHT_URL" in conf:
            run = get_run_from_url(conf["WEIGHT_URL"])
            if run is not None:
                return run
    return None


def delete_run_from_folder(run_f: str):
    run = run_from_meta(run_f)
    if run is not None:
        run.delete()


def filter_hyd_wandb(folder: str = "outputs"):
    to_delete = []
    for run_f in extract_all_exp(folder):
        if run_from_meta(run_f) is None:
            to_delete.append(run_f)
    return to_delete
