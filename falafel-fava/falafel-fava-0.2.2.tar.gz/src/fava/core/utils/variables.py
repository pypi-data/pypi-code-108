import os
import toml
from shutil import copy2


def load_file(file_name):
    base_dir = os.getcwd()
    try:
        return toml.load(base_dir + file_name)
    except OSError:
        print("Cannot open variables file", file_name)
        return None


def get(name):
    """
    :param name:
    :return:
    """
    global_variables_from_file = load_file("/app/config/variables.toml")
    database_variables_from_file = load_file("/app/config/database.toml")
    project_variables_from_file = load_file("/settings.toml")

    if project_variables_from_file is None:
        copy2(get_app_dir() + "/settings.toml.example", get_app_dir() + "/settings.toml")

    if global_variables_from_file.get("default").get(name) is not None:
        return global_variables_from_file.get("default").get(name)

    if database_variables_from_file.get("default").get(name) is not None:
        return global_variables_from_file.get("default").get(name)

    if project_variables_from_file.get("default").get(name) is not None:
        return project_variables_from_file.get("default").get(name)

    return None


def get_database_uri():
    """
    :return:
    """
    if get("DB_CONNECTION") == "sqlite":
        return get("DB_CONNECTION") + ":///" + get_app_dir() + "/" + get("DB_NAME")

    return f"{get('DB_CONNECTION')}://{get('DB_USERNAME')}:{get('DB_PASSWORD')}" \
           f"@{get('DB_HOST')}:{get('DB_PORT')}/{get('DB_NAME')}"


def get_app_dir():
    """
    :return :str
    """
    return os.getcwd()
