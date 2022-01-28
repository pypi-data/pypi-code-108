import configparser
import os
from getpass import getpass


def update_authinfo(display_username=True, display_password=False):
    base_dir = os.path.dirname(__file__)

    # userファイルのアップデート
    user_conf = configparser.ConfigParser()
    user_file = os.path.join(base_dir, "config/user.ini")
    user_conf.read(user_file)
    token_path = input("enter token_path: ")
    if display_username:
        username = input("enter username: ")
    else:
        username = getpass("enter username: ")

    if display_password:
        password = input("enter password: ")
    else:
        password = getpass("enter password: ")

    user_conf["AuthInfo"] = { 
            "token_path": token_path,
            "username": username,
            "password": password
    }

    with open(user_file, "w") as f:
        user_conf.write(f)

    # configファイルのアップデート
    config = configparser.ConfigParser()
    conf_file = os.path.join(base_dir, "config/config.ini")
    config.read(conf_file)
    config["AuthInfo"]["access_token"] = "******"
    config["AuthInfo"]["refresh_token"] = "******"
    config["AuthInfo"]["expires_in"] = "1900-01-01 00:00:00"
    config["AuthInfo"]["refresh_expires_in"] = "1900-01-01 00:00:00"
    with open(conf_file, "w") as f:
        config.write(f)


