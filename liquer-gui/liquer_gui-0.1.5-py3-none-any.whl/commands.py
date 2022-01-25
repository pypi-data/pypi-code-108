from liquer import *
from liquer.context import Context
from pathlib import Path
from liquer.store import web_mount_folder, get_store, get_web_store

def assets_path():
    return str((Path(__file__).parent/"assets").resolve())

def init():
    web_mount_folder("gui", assets_path())


