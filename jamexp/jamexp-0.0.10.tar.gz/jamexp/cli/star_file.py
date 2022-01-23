import os

import typer
from pyfzf.pyfzf import FzfPrompt


def fzf_select(folder: str):  # pylint: disable=inconsistent-return-statements
    fzf = FzfPrompt()
    sub_f = os.listdir(folder)
    try:
        return fzf.prompt(sub_f, "--multi")
    except Exception as error:  # pylint: disable=broad-except
        print("FZF error: {}".format(error))


def star_folder(folder: str):
    select_f = fzf_select(folder)
    for cur_f in select_f:
        full_f = os.path.join(folder, cur_f)
        if cur_f[:3] == "j*_":
            continue
        target_f = os.path.join(folder, f"j*_{cur_f}")
        os.rename(full_f, target_f)


def unstar_folder(folder: str):
    select_f = fzf_select(folder)
    for cur_f in select_f:
        full_f = os.path.join(folder, cur_f)
        if cur_f[:3] == "j*_":
            target_f = os.path.join(folder, cur_f[3:])
            os.rename(full_f, target_f)


def star_main(
    folder: str = ".runs", unstar: bool = typer.Option(False, "-d", help="delete stars")
):
    if unstar:
        unstar_folder(folder)
    else:
        star_folder(folder)


def main():
    typer.run(star_main)
