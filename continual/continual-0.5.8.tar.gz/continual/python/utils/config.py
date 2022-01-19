import os
import logging
import toml

CONFIG_ENV = "CONFIG_ENV"
CONFIG_LOCAL_BASE = "CONFIG_LOCAL_BASE"


def get_config(config_type):

    env = os.environ.get(CONFIG_ENV, "dev")
    if env != "dev" and env != "prod" and env != "stage" and env != "local":
        # TODO Exception.
        logging.info("In config - Exiting -  " + env + "-")
        return None

    overrride_file = ""
    config_base_file = "/app/{0}-config-base.toml".format(config_type)
    config_file = "/app/{0}-config.toml".format(config_type)
    local_base = "."

    if env == "local":
        # get local base
        if os.environ.get(CONFIG_LOCAL_BASE, None) is not None:
            local_base = os.environ.get(CONFIG_LOCAL_BASE, None)

    if env == "dev":
        overrride_file = "/app/{0}-config-override.toml".format(config_type)
    elif env == "local":
        config_base_file = "{0}/deployment/config/base/{1}.toml".format(
            local_base, config_type
        )
        config_file = "{0}/deployment/config/dev/{1}.toml".format(
            local_base, config_type
        )
        overrride_file = "{0}/deployment/config/dev/{1}-override.toml".format(
            local_base, config_type
        )

    cfg = {}
    with open(config_base_file, "r") as inp:
        c = toml.load(inp)
        cfg.update(c)

    with open(config_file, "r") as inp:
        c = toml.load(inp)
        cfg.update(c)

    if os.path.isfile(overrride_file):
        with open(overrride_file, "r") as inp:
            c = toml.load(inp)
            cfg.update(c)

    return cfg
