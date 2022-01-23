import os

import typer
from loguru import logger
from pyfzf.pyfzf import FzfPrompt

from jamexp.hyd.folder import extract_all_exp


def extract_dst_run(fname: str = ".runs"):
    rtn = []
    for sub_f in os.listdir(fname):
        if "j*_" in sub_f:
            sub_f = sub_f[3:]

        rtn.append(sub_f)
    return [item.replace("_", "/", 1) for item in rtn]


def pin_run(fname: str = "outputs", dst: str = ".runs"):
    dst_runs = extract_dst_run(dst)
    candidates = extract_all_exp(fname)
    unduplicate = []
    for item in candidates:
        for dst_item in dst_runs:
            if dst_item in item:
                break
        unduplicate.append(item)

    fzf = FzfPrompt()
    try:
        select = fzf.prompt(unduplicate, "--multi")
    except Exception as error:  # pylint: disable=broad-except
        print("FZF error: {}".format(error))

    for item in select:
        time_it = item.split("/")
        target = f"{time_it[-2]}_{time_it[-1]}"
        logger.info(f"{item} -> {dst}/{target}")
        os.symlink(item, f"{dst}/{target}")


def main():
    typer.run(pin_run)
