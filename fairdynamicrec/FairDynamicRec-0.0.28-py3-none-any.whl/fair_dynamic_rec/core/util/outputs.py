import numpy as np
import os
from pathlib import Path
import json
from fair_dynamic_rec.core.util.utils import get_dict_key_from_value, get_dict_keys_from_list, get_param_config_name

def save_rankings_online_simulator(config, dataObj, params_name, round, rankings, clicks, users_batch):
    pre_path = make_output_dir(config, params_name)
    rankings_dict = {}
    for i in range(len(users_batch)):
        rankings_mapped_to_original = np.asarray(get_dict_keys_from_list(dataObj.itemid_mapped_data, rankings[i]))
        rankings_dict[str(get_dict_key_from_value(dataObj.userid_mapped_data, users_batch[i]))] = {'r': list(rankings_mapped_to_original), 'c': list(rankings_mapped_to_original[clicks[i].astype(np.bool)])}
    output_path = pre_path / Path(str(round))
    with open(output_path, 'w+') as f:
        json.dump(rankings_dict, f)

def save_rewards(config, rankers, overall_optimal_reward, overall_rewards):
    i = 0
    for ranker in rankers:
        pre_path = make_output_dir(config, get_param_config_name(ranker["config"]))
        output_path = pre_path / 'optimal-reward'
        with open(output_path, 'w+') as f:
            json.dump({'reward': list(overall_optimal_reward)}, f)
        output_path = pre_path / 'ranker-reward'
        with open(output_path, 'w+') as f:
            json.dump({'reward': list(overall_rewards[i])}, f)
        i += 1

def make_output_dir(config, params_name):
    if not os.path.exists(config._target / Path('results')):
        os.makedirs(config._target / Path('results'))
    if not os.path.exists(config._target / Path('results/' + params_name)):
        os.makedirs(config._target / Path('results/' + params_name))
    return config._target / Path('results/' + params_name)
