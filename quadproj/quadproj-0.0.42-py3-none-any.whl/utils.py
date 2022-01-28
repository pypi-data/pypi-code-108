from pathlib import Path
from os.path import join


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


def get_tmp_path():
    return join(get_project_root(), 'tmp')


def get_output_path():
    return join(get_project_root(), 'output')


def get_tmp_gif_path():
    return join(get_tmp_path(), 'gif')
