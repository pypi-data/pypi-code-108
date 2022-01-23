import os
import subprocess
from signal import SIGKILL

import gpustat
import typer
from loguru import logger
from pyfzf.pyfzf import FzfPrompt


def get_pname(pid):
    with subprocess.Popen(
        ["ps -o cmd= {}".format(pid)], stdout=subprocess.PIPE, shell=True
    ) as proc:
        return str(proc.communicate()[0])


def get_gpu_proc_info():
    query = gpustat.new_query()
    proc_info = {}
    for i_th, cur_gpu in enumerate(query):
        if len(cur_gpu.processes) > 0:
            pinfos = [
                {
                    "pid": cur_p["pid"],
                    "pname": get_pname(cur_p["pid"]),
                    "user": cur_p["username"],
                    "mem": cur_p["gpu_memory_usage"],
                }
                for cur_p in cur_gpu.processes
            ]
            proc_info[i_th] = pinfos
    return proc_info


def kill_all_proc(
    is_debug: bool = typer.Option(False, "--v", help="only show info, not kill proc"),
):
    proc_info = get_gpu_proc_info()
    for i_th, cur_all_pinfo in proc_info.items():
        for cur_pinfo in cur_all_pinfo:
            logger.info(
                f"GPU {i_th:02d}  {cur_pinfo['user']: <10}   {cur_pinfo['pname']}"
            )

    for i_th, cur_all_pinfo in proc_info.items():
        for cur_pinfo in cur_all_pinfo:
            if cur_pinfo["user"] == os.getlogin():
                if not is_debug:
                    os.kill(cur_pinfo["pid"], SIGKILL)
                logger.warning(f"Kill {cur_pinfo['pname']}")


def fzf_kill_proc(
    is_debug: bool = typer.Option(False, "--v", help="only show info, not kill proc"),
):
    proc_info = get_gpu_proc_info()
    info = {}
    for i_th, cur_all_pinfo in proc_info.items():
        for cur_pinfo in cur_all_pinfo:
            if cur_pinfo["user"] == os.getlogin():
                info[f"GPU {i_th:02d} {cur_pinfo['pname']}"] = cur_pinfo["pid"]
    try:
        fzf = FzfPrompt()
        select = fzf.prompt(list(info.keys()), "-m")
    except Exception as error:  # pylint: disable=broad-except
        raise RuntimeError(  # pylint: disable=raise-missing-from
            "FZF error: {}".format(error)
        )
    for cur_p in select:
        logger.warning(f"KILL   {cur_p}")
    if not is_debug:
        for cur_p in select:
            os.kill(info[cur_p], SIGKILL)


def cudakill():
    typer.run(kill_all_proc)


def cudakillfzf():
    typer.run(fzf_kill_proc)
