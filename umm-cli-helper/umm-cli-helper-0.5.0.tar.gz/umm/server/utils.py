import os
import shutil

import yaml

from umm.server.command import Command
from umm.server.command_set import CommandSet


def parse_commands(pth: str):
    """
    Args:
        path: string path to commands.yaml
    Returns:
        CommandSet built from commands.yaml file
    """
    with open(pth) as f:
        comm_dict = yaml.full_load(f)
    commands = []
    for _, v in comm_dict["commands"].items():
        commands.append(Command(**v))

    return CommandSet(commands)


def setup_folder(root: str = None):
    root = root if root else os.path.expanduser("~")
    target_folder = os.path.join(root, ".umm")
    if not os.path.isdir(target_folder):
        shutil.copytree(
            os.path.join(os.path.dirname(__file__), "../resources/"), target_folder
        )
    return parse_commands(os.path.join(target_folder, "commands.yaml"))
