import os
import click
import logging
import yaml


## get value from HOME/lab/mlsteam.yml
def get_value(key, default=None):
    _dir = os.getenv('HOME', None)
    if not _dir:
        logging.warning("use default value for {}, HOME environment variable undefined.".format(key))
        return default
    param_file = os.path.join(_dir, "lab", "mlsteam.yml")
    if not os.path.exists(param_file):
        logging.warning("use default value for {}, mlsteam.yml not found.".format(key))
        return default
    params = {}
    with open(param_file, encoding='utf-8', mode='r') as f:
        params = yaml.safe_load(f)
    if "params" not in params:
        logging.warning("use default value for {}, undefined variable.".format(key))
        return default
    for k, v in params["params"].items():
        if key == k:
            if isinstance(params["params"][key], list):
                click.echo("hyperparameter - {}: {}".format(key, params["params"][key][0]))
                return params["params"][key][0]
            click.echo("hyperparameter - {}: {}".format(key, params["params"][key]))
            return params["params"][key]
    click.echo("hyperparameter - {}: {}(default)".format(key, default))
    return default
