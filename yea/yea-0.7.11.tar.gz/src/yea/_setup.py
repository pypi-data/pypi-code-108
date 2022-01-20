import importlib
import multiprocessing as mp
import os


def _setup_params():
    names = os.environ.get("YEA_PARAM_NAMES")
    values = os.environ.get("YEA_PARAM_VALUES")
    if not names or not values:
        return {}
    names = names.split(",")
    values = values.split(",")
    params = dict(zip(names, values))
    return params


def setup_mp(params):
    start_method = params.get(":yea:start_method")
    if not start_method:
        return
    print(f"INFO: start_method= {start_method}")
    mp.set_start_method(start_method)
    # TODO: check mp setup?


def setup_plugins(params):
    plugins = os.environ.get("YEA_PLUGINS")
    if not plugins:
        return
    plugins = plugins.split(",")
    for plug in plugins:
        mod_name = f"yea_{plug}"
        mod = importlib.import_module(mod_name)
        mod_setup = getattr(mod, "setup", None)
        if not mod_setup:
            continue
        mod_setup()


def setup():
    p = _setup_params()
    setup_mp(params=p)
    setup_plugins(params=p)
