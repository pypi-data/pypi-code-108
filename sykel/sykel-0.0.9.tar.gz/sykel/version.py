"""
 
 This module use bumpversion for handling versioning.
 
"""

import os
import configparser
from invoke import run, task

FILE_TO_SEARCH_TEMPL = "bumpversion:file:{filepath}"


def get_config_file():
    """
    Get config file

    We want to use the .bumpversion file only if it is present, otherwise, we should use setup.cfg
    """
    package_default_path = ".bumpversion.cfg"
    unified_config_path = "setup.cfg"
    if os.path.exists(package_default_path):
        return package_default_path
    if os.path.exists(unified_config_path):
        return unified_config_path
    return None


def init():
    config = configparser.ConfigParser()
    config_filepath = get_config_file()
    
    config["bumpversion"] = dict(
        current_version="0.0.1",
        commit=True,
        tag=True)
    
    config[FILE_TO_SEARCH_TEMPL.format(filepath=config_filepath)] = dict()
    
    with open(config_filepath, "w") as config_file:
        config.write(config_file)


def bump(part: str):
    config_filepath = get_config_file()
    cmd = "bumpversion{config_file} --allow-dirty {part}".format(
        # NOTE: Need this to convince bumpversion to work with setup.cfg it seems.
        # Has been observed at least in one case, but might not always be so.
        config_file=" --config-file %s" % config_filepath if config_filepath else "",
        part=part)
    run(cmd, echo=True)
    push = input("\nPush version tags (y/n)? ")
    if push == 'y':
        run('git push && git push --tags')
    else:
        print("Remember to do 'git push && git push --tags' to push version tags.")


def add_file(filepath: str):
    config = configparser.ConfigParser()
    config_filepath = get_config_file()
    config.read(config_filepath)
    config[FILE_TO_SEARCH_TEMPL.format(filepath=filepath)] = dict()
    with open(config_filepath, "w") as config_file:
        config.write(config_file)


@task(name="init")
def init_tsk(ctxt):
    """
    Initialize bumpversion configuration
    """
    init()


@task(name="bump")
def bump_tsk(ctxt, part="patch"):
    """
    Bump version: [--part <major, minor, [patch]>]
    
    Part can be either one of: major | minor | patch (default)
    """
    bump(part)


@task(name="add_file")
def add_file_tsk(ctxt, filepath):
    """
    Add file to that should have version updated: --filepath <>
    """
    add_file(filepath)
