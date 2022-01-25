#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# search_helper.py: functions share by various search related commands
from xtlib import errors
from xtlib import constants

def get_hp_config_path(store, ws_name, aggregate_dest, aggregate_name, last_chance=False):
    path = _get_hp_config_path_inner(store, ws_name, aggregate_dest, aggregate_name, constants.HP_CONFIG_DIR)
    if not path:
        # try old config dir name
        path = _get_hp_config_path_inner(store, ws_name, aggregate_dest, aggregate_name, constants.OLD_HP_CONFIG_DIR, 
            last_chance=True)

    return path

def _get_hp_config_path_inner(store, ws_name, aggregate_dest, dest_name, hp_config_dir, last_chance=False):
    if aggregate_dest == "job":
        _, filenames = store.get_job_filenames(ws_name, dest_name, hp_config_dir)
        if not filenames and last_chance:
            errors.store_error("Missing hp-config file for job={}".format(dest_name))
    else:
        _, filenames = store.get_experiment_filenames(ws_name, dest_name, hp_config_dir)
        if not filenames and last_chance:
            errors.store_error("Missing hp-config file for experiment={}".format(dest_name))

    hp_config_path = None

    if filenames:
        for f in filenames:
            if f.endswith('.yaml'):
                filename = f
                hp_config_path = hp_config_dir + "/" + filename
                break

    return hp_config_path

