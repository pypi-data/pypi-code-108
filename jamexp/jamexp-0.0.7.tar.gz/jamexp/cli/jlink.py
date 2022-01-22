import os
import shutil

import typer
from loguru import logger
from pyfzf.pyfzf import FzfPrompt


def create_link(
    fname: str,
    is_delete: bool = typer.Option(False, "--d", help="delete dst if exists"),
    is_debug: bool = typer.Option(False, "--v", help="only show info, not create link"),
):
    """
    create softlink to another disk, mostly for data disk
    """
    cwd = os.getcwd()
    if cwd.startswith(f"/home/{os.getlogin()}"):
        path_split = cwd.split("/")
        path_relative_home = path_split[3:]
        dst = os.path.join(cwd, fname)
        if os.path.exists(dst):
            logger.warning(f"{dst} already exists")
            if is_delete:
                if os.path.islink(dst):
                    os.unlink(dst)
                else:
                    shutil.rmtree(dst, ignore_errors=True)
            else:
                exit(0)
        local_dist = [os.path.expanduser("~/dpdata"), os.path.expanduser("~/dpruns")]
        src_dist = [
            os.path.join("/", fdir, os.getlogin())
            for fdir in os.listdir("/")
            if "hd" in fdir or "hhd" in fdir or "ssd" in fdir or "scratch" in fdir
        ]
        src_dist.extend(local_dist)
        try:
            select = os.environ["DATA_DISK"]
        except Exception as error:  # pylint: disable=broad-except
            logger.warning("Env DATA_DISK not SET, use FZF")
            try:
                fzf = FzfPrompt()
                select = fzf.prompt(src_dist)
                logger.warning(f"src select disk: {select[0]}")
            except Exception as error:  # pylint: disable=broad-except
                raise RuntimeError("FZF error: {}".format(error))

        final_src = [os.path.join(select[0], *path_relative_home, fname)] + local_dist
        try:
            fzf = FzfPrompt()
            src = fzf.prompt(final_src)[0]
        except Exception as error:  # pylint: disable=broad-except
            raise RuntimeError("FZF error: {}".format(error))

        logger.info(f"{src} ====> {dst}")
        logger.info(f"ln -sfn {src} {dst}")
        if not is_debug:
            os.makedirs(src, exist_ok=True)
            os.symlink(src, dst)


def delete_link(
    fname: str,
    is_delete: bool = typer.Option(False, "--d", help="delete src folder"),
):
    """
    delete link
    """
    cwd = os.getcwd()
    dst = os.path.join(cwd, fname)
    if os.path.exists(dst):
        if os.path.islink(dst):
            src = os.readlink(dst)
            if is_delete:
                logger.warning(f" Deleting SRC: {src} ==> {dst}")
            else:
                logger.warning(f" Deleting link: {src} ==> {dst}")
            shutil.rmtree(dst, ignore_errors=True)
            if is_delete:
                shutil.rmtree(src, ignore_errors=True)
        else:
            logger.warning(f"{dst} is not a link")


def link():
    typer.run(create_link)


def unlink():
    typer.run(delete_link)
