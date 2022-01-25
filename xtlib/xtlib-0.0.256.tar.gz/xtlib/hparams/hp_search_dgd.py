#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# hp_search_dgd.py: generate the next HP set based on DGD algorithm

import time
import random
import numpy as np
import json
from interface import implements

from xtlib import console
from xtlib import constants
from xtlib.hparams import hp_helper
from xtlib.hparams.hp_search_interface import HpSearchInterface

# TERMINOLOGY
# hyperparameter - A tunable variable along with one or more potential values.
# hp - Short term for hyperparameter, or prefix for something related to hyperparameters.
# hparam - An object of the Hyperparameter class.
# hp, setting, value - If a hp is a dial, a setting is one mark on the dial, and each mark has a value.
# Setting - The class used to instantiate setting objects. The Hyperparameter class contains a list of these.
# value_str - The string form of the value for some hp setting.
# configuration - A single combination of hyperparameter settings, one setting per hp.
# config - Short term for configuration.
# RunSet - The class encapsulating a list of runs that share the same configuration.

verbose = True 
verbose2 = False 

dgd_rand = random.Random(time.time())  # For 'truly' random hyperparameter selection.
# dgd_rand = random.Random(1)  # Deterministic, for debugging only!


class DGDSearch(implements(HpSearchInterface)):
    def __init__(self):
        pass

    def need_runs(self):
        return True
        
    def search(self, run_name, store, context, hp_records, runs):
        '''
        use dgd module to perform dgd search for next hparam set.
        '''
        dgd = DGD()
        dgd.build(store, hp_records, runs, context.primary_metric, maximize_metric=context.maximize_metric)
        
        runset = dgd.choose_config()
        arg_dict = dgd.arg_dict_from_runset(runset)

        return arg_dict


class RunSet(object):
    def __init__(self, hp_id__setting_id__list, config_str):
        self.hp_id__setting_id__list = hp_id__setting_id__list
        self.config_str = config_str
        self.runs = []
        self.metric = None
        self.id = -1  # For temporary usage.

    def report(self, title):
        sz = "{}  {}".format(title, self.config_str)
        if self.metric is not None:
            sz += "    {:12.5f},  {} runs".format(self.metric, len(self.runs))
        console.print(sz)


class Run(object):
    def __init__(self, run_summary, primary_metric, maximize_metric=True):
        self.skip = False
        self.value = 0.
        self.run_name = run_summary["run_name"]
        self.hpname_hpvalue_list = []

        # process "hparams" subrecord
        if "hparams" in run_summary:
            self.hparams = run_summary["hparams"]    
        else:
            self.skip = True
            if verbose:
                console.print("Skipping {}. (Missing hparams subrecord.)".format(self.run_name))

        # process "metrics" subrecord
        if "metrics" in run_summary:
            metrics = run_summary["metrics"]
            if primary_metric in metrics:
                self.value = float(metrics[primary_metric])

                if not maximize_metric:
                    # flip the sign to search towards the minimum of primary metric
                    self.value = -self.value
            else:
                self.skip = True
                if verbose:
                    console.print("Skipping {}. (Missing {} metric report.)".format(self.run_name, primary_metric))
        else:
            self.skip = True
            if verbose:
                console.print("Skipping {}. (Missing metrics subrecord.)".format(self.run_name))


class HyperparameterSetting(object):
    ''' Stores the allowed values for a given hyperparameter. '''
    def __init__(self, id, hparam, value):
        self.id = id
        self.hparam = hparam
        self.value = value


class Hyperparameter(object):
    ''' Stores the name and settings for a single hyperparameter. '''
    def __init__(self, id, name, value_string):
        self.id = id
        self.name = name
        self.value_setting_dict = {}
        self.settings = []
        self.has_multiple_values = False
        value_strs = value_string.split(',')
        self.values = []
        for value_str in value_strs:
            value = self.cast_value(value_str.strip())
            self.values.append(value)
        for value in self.values:
            self.add_setting(value)
        self.has_multiple_values = (len(self.settings) > 1)

    def cast_value(self, value_str):
        if value_str == 'None':
            new_value = None
        elif value_str == 'True':
            new_value = True
        elif value_str == 'False':
            new_value = False
        else:
            try:
                new_value = int(value_str)
            except ValueError:
                try:
                    new_value = float(value_str)
                except ValueError:
                    new_value = value_str
        return new_value

    def add_setting(self, value):
        assert value not in self.value_setting_dict.keys()
        setting = HyperparameterSetting(len(self.settings), self, value)
        self.value_setting_dict[value] = setting
        self.settings.append(setting)

    def report(self):
        sz = "{} = {}".format(self.name, self.values)
        console.print(sz)


class DGD(object):
    def __init__(self):
        self.runsets = []
        self.configstr_runset_dict = {}

    def build(self, store, records, all_runs, primary_metric, report=True, maximize_metric=True):
        self.store = store
        start_time = time.time()

        self.define_hyperparameters(records)
        self.create_run_objects(all_runs, primary_metric, maximize_metric=maximize_metric)
        self.finalize_runsets()

        if verbose2:
            console.print("All runsets...")
            for runset in self.runsets:
                console.print('{}  {:4d} runs  {:10.3f}'.format(runset.config_str, len(runset.runs), runset.metric))

        if report:
            self.report()

    def define_hyperparameters(self, records):
        self.name_hparam_dict = {}
        self.hparams = []

        for record in records:
            name_string = record["name"]
            value_string = record["value"]
            console.print("hyperparameter: {} = {}".format(name_string, value_string))
            hp = Hyperparameter(len(self.hparams), name_string, value_string)
            self.hparams.append(hp)
            self.name_hparam_dict[name_string] = hp

    def create_run_objects(self, run_reports, primary_metric, maximize_metric=True):
        self.runs = []

        if verbose:
            console.print("create_run_objects: len(run_reports)={}, primary_metric={}, maximize_metric={}".format(len(run_reports), primary_metric, maximize_metric))

        for record in run_reports:
            run = Run(record, primary_metric, maximize_metric=maximize_metric)
            if run.skip:
                continue

            # Gather the expected hparams from this run's report.
            search_keys = list(self.name_hparam_dict.keys())
            run.hpname_hpvalue_list = []
            for hp_name in search_keys:
                if hp_name in run.hparams:
                    run.hpname_hpvalue_list.append((hp_name, run.hparams[hp_name]))
                else:
                    run.skip = True  # Some hparam was not found in the report.
                    if verbose:
                        console.print("Skipping {}  (missing hparam={})".format(run.run_name, hp_name))
                    break
            if run.skip:
                continue

            # Try to assemble a configuration string for this run.
            hp_id__setting_id__list = []
            for hp_name, hp_value in run.hpname_hpvalue_list:
                hparam = self.name_hparam_dict[hp_name]

                # fixup multi-valued HP where we only use a single value
                if isinstance(hp_value, list) and len(hp_value)==1:
                    hp_value = hp_value[0]

                if hp_value not in hparam.value_setting_dict:
                    if verbose:
                        console.print("Skipping {}  (Unexpected hparam value {}:{})".format(run.run_name, hparam.name, hp_value))
                    run.skip = True
                    break
                setting = hparam.value_setting_dict[hp_value]
                hp_id__setting_id__list.append((hparam.id, setting.id))
            if run.skip:
                continue

            # Keep this run in a corresponding runset.
            config_str = str(hp_id__setting_id__list)
            self.runs.append(run)
            if config_str not in self.configstr_runset_dict.keys():
                runset = RunSet(hp_id__setting_id__list, config_str)
                self.configstr_runset_dict[config_str] = runset
                self.runsets.append(runset)
            runset = self.configstr_runset_dict[config_str]
            runset.runs.append(run)

    def finalize_runsets(self):
        for runset in self.runsets:
            # Average the run scores (like reward).
            sum = 0.
            for run in runset.runs:
                sum += run.value
            runset.metric = sum / len(runset.runs)

    def report(self):
        self.max_runs_per_runset = 0
        n1 = 0
        for runset in self.runsets:
            num_runs = len(runset.runs)
            if num_runs > self.max_runs_per_runset:
                self.max_runs_per_runset = num_runs
            if num_runs == 1:
                n1 += 1
        console.print("{} runs".format(len(self.runs)))
        console.print("{} runsets".format(len(self.runsets)))
        console.print("{} have 1 run".format(n1))
        console.print("{} max runs per runset".format(self.max_runs_per_runset))

    def choose_config(self):
        # If there are no runs yet, just return a random configuration.
        if len(self.runsets) == 0:
            hp_id__setting_id__list = []
            for hparam in self.hparams:
                last_setting_id = len(hparam.settings) - 1
                setting_id = dgd_rand.randint(0, last_setting_id)
                hp_id__setting_id__list.append((hparam.id, setting_id))
            config_str = str(hp_id__setting_id__list)
            chosen_runset = RunSet(hp_id__setting_id__list, config_str)
            chosen_runset.report('Random runset   ')
            return chosen_runset

        # Find the best runset so far.
        best_runset = self.runsets[0]
        best_metric = best_runset.metric
        for runset in self.runsets:
            if runset.metric >= best_metric:
                best_metric = runset.metric
                best_runset = runset
        best_runset.report('Best runset    ')

        # Build a neighborhood around (and including) the best runset.
        neighborhood = [best_runset]
        for hp_i, hparam in enumerate(self.hparams):
            best_hparam_id = best_runset.hp_id__setting_id__list[hp_i][0]
            assert hparam.id == best_hparam_id
            best_setting_id = best_runset.hp_id__setting_id__list[hp_i][1]
            best_setting = hparam.settings[best_setting_id]
            # console.print("For hp={}, best config's setting is {}".format(hparam.name, best_setting.value))

            if best_setting_id > 0:
                neighbor = self.get_neighbor_runset(best_runset, hp_i, best_hparam_id, best_setting_id - 1)
                neighborhood.append(neighbor)
            if best_setting_id < len(hparam.settings) - 1:
                neighbor = self.get_neighbor_runset(best_runset, hp_i, best_hparam_id, best_setting_id + 1)
                neighborhood.append(neighbor)

        # Choose one runset, weighted by how many runs it needs to exceed those of the runset with the most.
        ceiling = max([len(runset.runs) for runset in neighborhood]) + 1
        console.print("ceiling = {} runs".format(ceiling))
        probs = np.zeros((len(neighborhood)))
        for i, runset in enumerate(neighborhood):
            probs[i] = ceiling - len(runset.runs)
        sum = np.sum(probs)
        probs /= sum

        console.print("Count of runsets in the neighborhood of the best runset (at index 0): {}".format(len(neighborhood)))

        if verbose2:
            console.print("Runsets in the neighborhood of the best runset (at index 0)...")
            for i, runset in enumerate(neighborhood):
                runset.id = i
                runset.report(" {:2d} prob={:6.4f}".format(runset.id, probs[i]))

        chosen_runset = dgd_rand.choices(neighborhood, probs)[0]
        chosen_runset.report('\n {:2d} was chosen '.format(chosen_runset.id))
        return chosen_runset

    def get_neighbor_runset(self, best_runset, hp_i, best_hparam_id, new_setting_id):
        hp_id__setting_id__list = best_runset.hp_id__setting_id__list[:]  # Clone the best config.
        hp_id__setting_id__list[hp_i] = (best_hparam_id, new_setting_id)  # Change one setting.
        config_str = str(hp_id__setting_id__list)
        if config_str in self.configstr_runset_dict.keys():
            runset = self.configstr_runset_dict[config_str]
        else:
            runset = RunSet(hp_id__setting_id__list, config_str)
        return runset

    def arg_dict_from_runset(self, runset):
        arg_dict = {}

        # output values used in runset
        for hp_i, hparam in enumerate(self.hparams):
            hparam_id = runset.hp_id__setting_id__list[hp_i][0]
            assert hparam.id == hparam_id
            
            value_id = runset.hp_id__setting_id__list[hp_i][1]
            value = hparam.settings[value_id]

            arg_dict[hparam.name] = value.value

        return arg_dict

def fake_call_from_job(job_name, workspace, fn_hp_search):
    from xtlib.helpers.xt_config import get_merged_config
    config = get_merged_config()

    # build store
    from xtlib.storage.store import Store
    store = Store(config=config)

    # build context
    from xtlib.utils import PropertyBag
    context = PropertyBag()
    context.primary_metric = config.get("general", "primary-metric")
    context.hp_config = fn_hp_search
    context.search_type = "dgd"
    context.providers = config.get("providers")
    context.aggregate_dest = "job"
    context.dest_name = job_name
    context.ws = workspace

    from xtlib.hparams.hparam_search import HParamSearch
    hps = HParamSearch()

    search_file_text = store.read_job_file(context.ws, context.dest_name, context.hp_config)
    arg_dict = hps.generate_hparam_set("fn_config", search_file_text, "run999", [], store, context)
    print("{}".format(arg_dict))

if __name__ == '__main__':
    #fake_call_from_job("job363", "tpx", "hp-confg-dir/hp_search.yaml")
    fake_call_from_job("job2949", "ws1", "hp-config-dir/uploaded_hp_config.yaml")
