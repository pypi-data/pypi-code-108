import subprocess
from typing import List

import click
import requests
from pygments import console

from umm.cli.client import add_request, confirm_request, umm_request
from umm.server.__main__ import main


@click.command()
@click.option("--start", "-s", is_flag=True)
@click.option("--stop", is_flag=True)
@click.option("--add", is_flag=True)
@click.argument("tags", nargs=-1)
def umm(start: bool, stop: bool, add: bool, tags: List[str]):
    """
    Args:
        start:
        add:
        tags:
    Returns:
        None
    """
    if add:
        msg = "input command"
        msg = console.colorize("blue", msg)
        command = click.prompt(msg)

        msg = "input tags [/-separated list]"
        msg = console.colorize("blue", msg)
        tags = click.prompt(msg)
        print(add_request(command, tags.split("/")))
        return
    if start:
        print("umm server starting")
        main()
        return
    if stop:
        print("umm server stopping")
        import psutil

        from umm.utils.config import parse_config

        config = parse_config()

        # find and kill pid(s)
        pids = set()
        for proc in psutil.process_iter():
            if "python" in proc.name().lower():
                if proc.connections():
                    conns = proc.connections()
                    for conn in conns:
                        if conn.laddr.port == config.port:
                            pids.add(proc.pid)
        for pid in pids:
            subprocess.run(["kill", f"{pid}"])

        # if no pids were found
        if not pids:
            print("Could not find running server")

        return

    try:
        candidates = umm_request(tags)
    except requests.exceptions.ConnectionError:
        raise ConnectionError("can't connect to umm.server try `umm --start`")

    if len(candidates["commands"]) == 0:
        print("no candidate commands found")
        return

    for command in candidates["commands"]:
        msg = f"{command['command']} [y/n/c/p/q]?"
        msg = console.colorize("green", msg)
        action_str = click.prompt(msg, default="y")

        while action_str not in ["y", "n", "c", "p", "q"]:
            print("invalid input. use [y/n/c/p/q]")
            action_str = click.prompt(msg, default="y")

        # continue and exit conditions
        if action_str == "q":
            return
        elif action_str != "n":
            break

    # no candidate command selected found
    if action_str == "n":
        print("no command selected")
        return

    # if command has prompts
    prompts = command.get("prompts", [])
    in_data = []
    for prompt in prompts:
        in_data.append(click.prompt(f"{prompt} = ?"))

    # build command
    command_str = command["command"]
    for i, value in enumerate(in_data):
        command_str = command_str.replace(f"${i+1}", value)

    # get action
    command_actions = {
        "y": ([command_str], {"shell": True}),
        "c": ([f"echo '{command_str}' |pbcopy"], {"shell": True}),
        "p": ([f"echo '{command_str}'"], {"shell": True}),
    }

    cmd, kwargs = command_actions[action_str]
    subprocess.run(cmd, **kwargs)
    _ = confirm_request(command["id"])
