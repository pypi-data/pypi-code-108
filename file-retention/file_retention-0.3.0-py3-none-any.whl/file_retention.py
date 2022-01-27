#!/usr/bin/env python3

# import glob
import os
from os.path import expanduser
from datetime import date, timedelta
import click
import logging
from .functions import (
    create_yaml,
    get_files,
    create_dict,
    read_yaml,
    delete_files,
    today,
    output_yaml_file,
    trace,
    send_mail,
    setup,
)

home = expanduser("~")
logging.basicConfig(
    filename=f"{home}/file_retention.log",
    level=logging.INFO,
    format="%(asctime)s  - %(levelname)s - %(funcName)s - %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)


@click.group("cli")
def cli():
    """Delete files from a directory based on a specific date \n
    First of all, run:\n
        $ python3 -m file_retention install\n
    How to use:\n
        $ python3 -m file_retention snapshot /tmp/create_files/ -e txt\n
        $ python3 -m file_retention delete -r 5 -y\n
        $ python3 -m file_retention mail ~/.file_retention/mail.yml -r 5\n
    """
    ...


@cli.command(
    "snapshot",
    short_help="Capture all files from directory recursively and save to a yaml file ",
)
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--extension",
    "-e",
    default="*",
    help="Files Extension. Default value *. Ex: mp4",
    required=True,
)
def snapshot(path, extension):
    logging.info("Função iniciada")
    """Capture all files from directory recursively and save to a yaml file\n
    Ex:\n
        $ python3 -m file_retention snapshot /tmp/create_files/ -e md"""
    files_now = get_files(path, extension)
    dicts = create_dict(files_now, path)
    create_yaml(dicts, today(), path)


@cli.command("delete", short_help="Delete the files")
@click.option(
    "--retention",
    "-r",
    type=int,
    help="Days in numbers. Ex: 1 = a day ago",
    required=True,
)
@click.option(
    "--yes", "-y", default=False, help="Confirm file deletion", is_flag=True
)
def delete(yes, retention):
    logging.info("Função iniciada")
    """Delete the files\n
    Obs: Use -y / --yes with care\n
    Ex:\n
        $ python3 -m file_retention delete -r 5 -y\n
    """
    days_ago = today() - timedelta(days=retention)
    files_ago = read_yaml(days_ago, "arquivos")
    filename = os.path.join(output_yaml_file(), f"{days_ago}.yml")
    if yes:
        delete_files(days_ago, files_ago, retention)

    else:
        click.echo(f"{trace()}\nArquivos não foram deletados.\n{trace()}")
        logging.info("Arquivos não foram deletados.")


@cli.command(
    "mail", short_help="Send the emails based on a yml configuration file"
)
@click.argument("mail_file", type=click.Path(exists=True))
@click.option(
    "--retention",
    "-r",
    type=int,
    help="Days in numbers. Ex: 1 = a day ago",
    required=True,
)
def mail(mail_file, retention):
    logging.info("Função iniciada")

    """Send the emails based on a yml configuration file\n
    Obs: When file_retention is installed, it automatically creates the file
    ~/.file_retention/mail.yaml so just edit the file with the necessary
    email conformations\n
    Ex:\n
        $ python3 -m file_retention mail ~/.file_retention/mail.yml -r 5
    """
    send_mail(mail_file, retention)


@cli.command(
    "install",
    short_help="Creates the directories and files needed for the CLI to work",
)
def install():
    logging.info("Função iniciada")
    """Create the ~/.file_retention directory and the configuration file for sending emails ~/.file_retention/mail.yml"""
    setup()
