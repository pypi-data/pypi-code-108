from os import environ
import click
import logging
from typing import List
from random import randint
import socket


def check_port_open(test_port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        return sock.connect_ex(("127.0.0.1", test_port)) != 0
    finally:
        sock.close()


def get_port() -> int:
    while True:
        port: int = randint(2000, 9000)
        if check_port_open(port):
            return port
        else:
            continue


def in_repl() -> bool:
    return len([env for env in environ.keys() if env.startswith("REPL_") or env.startswith("REPLIT_")]) > 0


def project_name() -> str:
    return environ["REPL_SLUG"]


def project_owner() -> str:
    return environ["REPL_OWNER"]


def namespace() -> str:
    return f"{project_owner()}/{project_name()}"


def instance_url() -> str:
    assert in_repl()
    return f"https://{project_name()}.{project_owner()}.repl.co"


def secho(text, file=None, nl=None, err=None, color=None, **styles):
    pass


def echo(text, file=None, nl=None, err=None, color=None, **styles):
    pass


def quiet_click() -> None:
    click.echo = echo
    click.secho = secho


def quiet_werkzeug() -> None:
    logging.getLogger("werkzeug").setLevel(logging.ERROR)


def quiet() -> None:
    quiet_click()
    quiet_werkzeug()


__all__: List[str] = [
    "check_port_open",
    "get_port",
    "in_repl",
    "project_name",
    "project_owner",
    "namespace",
    "instance_url",
    "quiet_click",
    "quiet_werkzeug",
    "quiet",
]
