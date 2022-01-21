from functools import wraps
import sys
import time
import os
from pathlib import Path

import click

from anylearn.config import init_sdk
from anylearn.cli.anylearn_cli_config import AnylearnCliConfig


def cmd_error(msg: str):
    update_history_record(f"                      [ERROR] {msg}")
    click.echo(click.style(f"[ERROR] {msg}", fg="red"))


def cmd_warning(msg: str):
    click.echo(click.style(f"[WARNING] {msg}", fg="yellow"))


def cmd_success(msg: str):
    update_history_record(f"                      [SUCCESS] {msg}")
    click.echo(click.style(f"[SUCCESS] {msg}", fg="green"))


def cmd_info(msg: str):
    click.echo(msg)


def cmd_confirm_or_abort():
    # No confirm = abort, so no need for any conditions
    click.confirm("Are you sure you want to proceed?", abort=True)


def check_config():
    def wrapper(fn):
        """

        :param fn: 

        """

        @wraps(fn)
        def decorator(*args, **kwargs):
            config_path = AnylearnCliConfig.get_config_path()
            if not config_path.exists():
                msg = "Anylearn project does not exist in current directory. "
                cmd_error(msg)
                raise click.Abort()
            return fn(*args, **kwargs)

        return decorator

    return wrapper


def do_login(show_success=False):
    config = AnylearnCliConfig.load()
    remote = {
        'host': (
            config.remote['host']
            if 'host' in config.remote and config.remote['host']
            else click.prompt(click.style("Anylearn host", fg="yellow"))
        ),
        'username': (
            config.remote['username']
            if 'username' in config.remote and config.remote['username']
            else click.prompt(click.style("Anylearn username", fg="yellow"))
        ),
        'password': (
            config.remote['password']
            if 'password' in config.remote and config.remote['password']
            else click.prompt(click.style("Anylearn password", fg="yellow"), hide_input=True)
        ),
    }
    try:
        init_sdk(remote['host'], remote['username'], remote['password'])
        config.remote = remote
        AnylearnCliConfig.update(config)
        if show_success:
            cmd_success(msg="Logged into Anylearn remote.")
    except:
        config.remote = {
            'host': None,
            'username': None,
            'password': None,
        }
        AnylearnCliConfig.update(config)
        cmd_error(msg="Failed to establish connection to Anylearn remote.")
        raise click.Abort()


def do_logout():
    config = AnylearnCliConfig.load()
    config.remote = {
        'host': None,
        'username': None,
        'password': None,
    }
    AnylearnCliConfig.update(config)
    cmd_success(msg="Logged out from Anylearn remote.")


def check_connection():
    def wrapper(fn):
        """

        :param fn: 

        """

        @wraps(fn)
        def decorator(*args, **kwargs):
            do_login()
            return fn(*args, **kwargs)

        return decorator

    return wrapper


def get_cmd_command():
    def wrapper(fn):
        """

        :param fn: 

        """

        @wraps(fn)
        def decorator(*args, **kwargs):
            cmd = sys.argv
            dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            command = f"[{dt}] anyctl"
            for i in range(len(cmd)):
                command += (f"{cmd[i]} ") if i else " "
            update_history_record(command=command)
            return fn(*args, **kwargs)

        return decorator

    return wrapper


def get_history_file_path():
    cwd = Path(os.getcwd())
    file_path = cwd / 'cmd_history.txt'
    file_path.touch(exist_ok=True)
    return file_path

def update_history_record(command: str):
    with open(get_history_file_path(), 'a') as f:
        f.write(f"\r{command}")


option_force = click.option(
    '-f', '--force',
    is_flag=True,
    default=False,
    help="Skip prompt and force actions."
)
