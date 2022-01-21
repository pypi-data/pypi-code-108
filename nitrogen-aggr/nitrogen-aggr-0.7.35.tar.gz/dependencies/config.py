import os
import yaml
from pathlib import Path

ROOT_DIR = f"{Path(__file__).parent.parent}"

CONFIG_DIR_NAME = "configs"
FRAMEWORK_DIR_NAME = "framework"


def load_client_all_step_configs(client):
    location = f"{ROOT_DIR}/{CONFIG_DIR_NAME}/{client}/"
    print(f"root dir is {location}")
    config={}
    for file_name in os.listdir(location):
        if file_name.endswith(".yaml"):
            try:
                file_path = os.path.join(location, file_name)
                with open(file_path, "r") as conf_file:
                    config[file_name.split('.yaml')[0]] = yaml.safe_load(conf_file)
            except FileNotFoundError:
                print(f"Sorry, the file  does not exist, {file_path} ")

    return config

def load_client_step_config(client, step):
    """
        first check client folder for the file, if not exists then check the default
    :param client:
    :param step:
    :return:
    """
    config = {}
    filename = os.path.join(ROOT_DIR, CONFIG_DIR_NAME, client, f"{step}.yaml")
    if not os.path.exists(filename):
        filename = os.path.join(ROOT_DIR, CONFIG_DIR_NAME, "default", f"{step}.yaml")
    print(f"root dir is {ROOT_DIR}")

    if os.path.exists(filename):
        try:
            with open(filename, "r") as conf_file:
                config = yaml.safe_load(conf_file)
        except FileNotFoundError:
            print(f"Sorry, the file  does not exist 1, {filename} ")
    else:
        print(f"Sorry, the file  does not exist  2, {filename} ")

    return config

def load_project_config(client):
    """
            first check client folder for the file, if not exists then check the default

    :param client:
    :param step:
    :return:
    """
    config = {}
    filename = os.path.join(ROOT_DIR, CONFIG_DIR_NAME, client, "project.yaml")
    # Path: nitrogen-aggr/configs/default/project.yaml
    if not os.path.exists(filename):
        filename = os.path.join(ROOT_DIR, CONFIG_DIR_NAME, "default", "project.yaml")

    # Path: nitrogen-aggr/configs/{client}/project.yaml
    if os.path.exists(filename):
        try:
            with open(filename, "r") as conf_file:
                config = yaml.safe_load(conf_file)
        except FileNotFoundError:
            print(f"Sorry, the file  does not exist, {filename} ")
    else:
        print(f"Sorry, the file  does not exist, {filename} ")

    return config

def load_framework_config():
    """
    load any YAML config file that is in ./camdium/configs/project
    :return:
    """
    global file_path
    location = f"{ROOT_DIR}/{CONFIG_DIR_NAME}/{FRAMEWORK_DIR_NAME}/"
    config = {}

    for file_name in os.listdir(location):
        if file_name.endswith(".yaml"):
            try:
                file_path = os.path.join(location, file_name)
                with open(file_path, "r") as conf_file:
                    config[file_name] = yaml.safe_load(conf_file)
            except FileNotFoundError:
                print(f"Sorry, the file  does not exist, {file_path} ")
    return config

