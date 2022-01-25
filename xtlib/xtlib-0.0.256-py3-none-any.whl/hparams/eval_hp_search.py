#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# eval_hp_search.py: evaluates runs to-date from specified hyperparameter search (job or experiment name)
# runnable standalone or from XT (xt plot summary)

import os
import math
import json
import time
import yaml
import argparse
import numpy as np
from os.path import exists

from yaml import nodes

from xtlib import utils
from xtlib import console
from xtlib import constants
from xtlib import search_helper
from xtlib.hparams import hp_helper
from xtlib.storage.store import Store
from xtlib.helpers.xt_config import get_merged_config


plt = None     # JIT import to keep XT from always loading matplotlib (and font cache building)


# TERMINOLOGY
# hp, setting, value - If a hyperparameter is a dial, a setting is one mark on the dial, and each mark has a value.


MIN_COL_WID = 9

def plot(xs, ys, ds, job_name, y_axis_label):
    ''' Displays a plot of the hyperparameter search progress. '''
    title = 'Retrospective evaluation of the best HP combination after each run'
    fig = plt.figure(figsize=(12, 8))
    fig.canvas.manager.set_window_title('xt plot summary')
    perf_axes = fig.add_axes([0.08, 0.09, 0.88, 0.84])
    perf_axes.set_title(title, fontsize=16)
    ymax = ys + ds
    ymin = ys - ds
    color = 'blue'
    perf_axes.set_xlabel("Completed runs", fontsize=16)
    perf_axes.set_ylabel(y_axis_label, fontsize=16)
    perf_axes.fill_between(xs, ymax, ymin, color=color, alpha=0.2)
    perf_axes.plot(xs, ys, color=color, label=job_name)  # , label=label, color=color, alpha=alpha, linewidth=LINEWIDTH, linestyle=linestyle, marker='o')
    perf_axes.legend(loc='lower right', prop={'size': 16})
    plt.show()


def get_end_id(run):
    return run.end_id

def get_neg_run_value(run):
    return -run.value

class RunSet():
    ''' Encapsulates a list of runs that share the same HP combination. '''
    def __init__(self, id, history, hp_id__setting_id__list, config_str):
        self.id = id
        self.history = history
        self.hp_id__setting_id__list = hp_id__setting_id__list
        self.config_str = config_str
        self.runs = []
        self.sample_count = 0
        self.sample_mean = 0.
        self.sample_m2 = 0.
        self.post_mean = None
        self.post_var = None
        # A circular, doubly-linked list of RunSets, continually sorted by posterior mean in ascending order.
        self.sent = False  # The sentinel, for which dn is the best runset, and up is the worst.
        self.up = None  # The next best runset (or the sentinel).
        self.dn = None  # The next worst runset (or the sentinel).
        self.in_list = False  # Whether in_list or not, dn and up are always valid.

    def update_posteriors(self, prior_mean, prior_var):
        '''
        Uses Bayesian inference to estimate posterior mean and variance,
        assuming that each run's metric values are normally distributed.
        '''
        N = self.sample_count
        if N == 0:
            self.post_mean = prior_mean
            self.post_var = prior_var
        else:
            sample_mean = self.sample_mean
            sample_var = (prior_var + (N - 1) * self.get_sample_var()) / N  # Interpolation
            mean_numer = sample_var * prior_mean + N * prior_var * sample_mean
            var_numer = sample_var * prior_var
            denom = sample_var + N * prior_var
            if denom <= 0.:
                denom = 1.
            self.post_mean = mean_numer / denom
            self.post_var = var_numer / denom

    def insert(self, dn=None, up=None):
        ''' Inserts the runset into the list at either the current or specified location. '''
        assert not self.in_list
        if dn:
            self.dn = dn
        if up:
            self.up = up
        assert self.dn.up == self.up
        assert self.up.dn == self.dn
        self.dn.up = self
        self.up.dn = self
        self.in_list = True

    def remove(self):
        ''' Removes the runset from the list, keeping pointers to the previous neighbors. '''
        assert self.in_list
        assert self.dn.up == self
        assert self.up.dn == self
        self.dn.up = self.up
        self.up.dn = self.dn
        self.in_list = False

    def reposition(self):
        ''' Move the runset to its sorted position within the list. '''
        if self.should_move_up():
            if self.in_list:
                self.remove()
            while self.should_move_up():
                self.move_up()
        elif self.should_move_down():
            if self.in_list:
                self.remove()
            while self.should_move_down():
                self.move_dn()
        if not self.in_list:
            self.insert()

    def is_better_than(self, other):
        # Higher mean is better.
        if self.post_mean > other.post_mean:
            return True
        elif self.post_mean < other.post_mean:
            return False
        # Lower variance is better.
        if self.post_var < other.post_var:
            return True
        elif self.post_var > other.post_var:
            return False
        # Older is better.
        return self.runs[0].end_id < other.runs[0].end_id

    def should_move_up(self):
        # True if the runset above this one belongs below it.
        if self.up.sent:
            return False
        return self.is_better_than(self.up)

    def should_move_down(self):
        # True if the runset below this one belongs above it.
        if self.dn.sent:
            return False
        return self.dn.is_better_than(self)

    def move_up(self):
        # Walks this runset up one step in the list.
        assert not self.in_list
        self.dn = self.up
        self.up = self.up.up

    def move_dn(self):
        # Walks this runset down one step in the list.
        assert not self.in_list
        self.up = self.dn
        self.dn = self.dn.dn

    def report_configuration(self):
        i = 0
        for hp in self.history.hparams:
            assert hp.id == self.hp_id__setting_id__list[i][0]
            console.print("{} = {}".format(hp.name, hp.settings[self.hp_id__setting_id__list[i][1]].value))
            i += 1

    def report_configuration_string(self):
        i = 0
        sz = ''
        for hp in self.history.hparams:
            width = max(MIN_COL_WID, len(hp.name))
            format_string = ' {' + ':{}s'.format(width) + '}'

            try:
                setting_index = ""
                setting_index = self.hp_id__setting_id__list[i][1]
                val = hp.settings[setting_index]
                txt = str(val.value)
            except BaseException as ex:
                txt = "[{}]?".format(setting_index)
            sz += format_string.format(txt)
            i += 1
        return sz

    def report(self, title):
        fixed_values = '   {}   {}             {:9.3f}'.format(self.id, len(self.runs), self.post_mean)
        console.print('     ' + self.report_configuration_string() + fixed_values)

    def add_run(self, run):
        ''' Welford's online algorithm for single-pass computation of variance. '''
        self.runs.append(run)
        value = run.value
        self.sample_count += 1
        delta = value - self.sample_mean
        self.sample_mean += delta / self.sample_count
        delta2 = value - self.sample_mean
        self.sample_m2 += delta * delta2

    def get_sample_var(self):
        if self.sample_count < 2:
            sample_var = 0.
        else:
            sample_var = self.sample_m2 / (self.sample_count - 1)  # Sample variance
        return sample_var


class RunSetTrophy():
    def __init__(self, run_i, runset):
        ''' A new trophy is award to every runset that becomes the best so far. '''
        self.run_i = run_i
        self.num_runs = 1
        self.runset = runset


class Run():
    def __init__(self, run_summary, primary_metric, maximize_metric, verbose=False, use_azure_storage=False):
        ''' Maintains the per-run information. '''
        if use_azure_storage:
            # run_summary comes from Azure Storage.
            self.run_name = None
            self.hpname_hpvalue_list = []
            self.skip = True
            self.value = 0.
            self.end_id = None
            json_line = json.loads(run_summary)
            event_dict_list = json_line['log']
            for event_dict in event_dict_list:
                event_type = event_dict["event"]
                if event_type == "hparams":
                    hp_data = event_dict["data"]
                    for hpname in hp_data:
                        self.hpname_hpvalue_list.append((hpname, hp_data[hpname]))
                elif event_type == "metrics":
                    metric_dict = event_dict["data"]
                    if primary_metric in metric_dict:
                        if maximize_metric:
                            self.value += float(metric_dict[primary_metric])
                        else:
                            self.value -= float(metric_dict[primary_metric])
                        self.skip = False
                elif event_type == "created":
                    if self.run_name is not None:
                        # There was a previous "created" event, so apparently the run was restarted.
                        if verbose:
                            console.print('Unexpected created event in {}. Resetting the run.'.format(self.run_name))
                        # Reset all fields.
                        self.run_name = None
                        self.hpname_hpvalue_list = []
                        self.skip = True
                        self.value = 0.
                        self.end_id = None
                    run_data = event_dict["data"]
                    self.run_name = run_data["run_name"]
                self.end_id = event_dict["time"]  # The time of the last event of the run.
            if self.skip and verbose:
                console.print("Skipping {}. (Missing {} metric report.)".format(self.run_name, primary_metric))
        else:
            # run_summary comes from the database.
            self.skip = False
            self.value = 0.
            self.run_name = run_summary['run_name']
            self.end_id = run_summary['end_id']
            metrics = run_summary['metrics']
            if primary_metric in metrics:
                if maximize_metric:
                    self.value = float(metrics[primary_metric])
                else:
                    self.value = -float(metrics[primary_metric])
                self.hparams = run_summary['hparams']
            else:
                self.skip = True
                if verbose:
                    console.print("Skipping {}. (Missing {} metric report.)".format(self.run_name, primary_metric))


class HyperparameterSetting():
    ''' Stores the allowed values for a given hyperparameter. '''
    def __init__(self, id, hparam, value):
        self.id = id
        self.hparam = hparam
        self.value = value


class Hyperparameter():
    ''' Stores the name and settings for a single hyperparameter. '''
    def __init__(self, id, name, value_list):
        self.id = id
        self.name = name
        self.value_setting_dict = {}
        self.settings = []
        for value in value_list:
            self.add_setting(value)

    def add_setting(self, value):
        assert value not in self.value_setting_dict.keys()
        setting = HyperparameterSetting(len(self.settings), self, value)
        self.value_setting_dict[value] = setting
        self.settings.append(setting)


class SearchHistory():
    ''' Loads, processes, and evaluates the runs of a single hyperparameter search job. '''
    def __init__(self, args=None, agg_name=None, workspace=None, timeout=None, primary_metric=None, maximize_metric=True,
        show_single_valued_hps=False, hp_config_file_name=None, max_workers=1, max_runs=0, xt_config=None, verbose=False, use_azure_storage=False):

        global plt
        import matplotlib.pyplot as plt

        if not args:
            arg_list = [agg_name]
            args = parse_args(arg_list)

            # set args from XT
            args.primary_metric = primary_metric
            args.maximize_metric = maximize_metric
            args.hp_def_file = os.path.basename(hp_config_file_name)
            args.max_runs = max_runs
            args.verbose = verbose
            args.use_azure_storage = use_azure_storage

        self.args = args
        self.timeout = timeout
        self.max_workers = max_workers

        self.DIR_PATH = "{}/{}/".format(args.job_dir, args.job)
        self.runs = []
        self.runsets = []
        self.configstr_runset_dict = {}
        self.best_runset_trophies = []
        self.xtstore = None

        self.ws_name = workspace if workspace else args.workspace
        self.xt_config = xt_config
        self.hpmax_name = self.args.primary_metric.upper()
        self.show_single_valued_hps = show_single_valued_hps


    def init_xtstore(self):
        if self.xtstore is None:
            if self.xt_config is None:
                self.xt_config = get_merged_config(create_if_needed=False)
            self.xtstore = Store(config=self.xt_config)

    def load_hp_definitions(self):
        ''' Get the hyperparameter definitions from Azure. '''
        hp_config_path = self.DIR_PATH + self.args.hp_def_file
        self.init_xtstore()
        job_path = search_helper.get_hp_config_path(self.xtstore, self.ws_name, "job", self.args.job)
        self.xtstore.download_file_from_job(self.ws_name, self.args.job, job_path, hp_config_path)
        self.define_hyperparameters_from_config_yaml(hp_config_path)

    def load_runs_from_storage(self):
        ''' Download the runs from Azure. '''
        runs_file_name = constants.ALL_RUNS_FN
        all_runs_file_path = self.DIR_PATH + runs_file_name

        if not self.args.no_download:
            self.init_xtstore()
            started = time.time()

            nodes_read = self.xtstore.download_all_runs_blobs(self.ws_name, "job", self.args.job, 
                all_runs_file_path, max_workers=self.max_workers)

            elapsed = time.time() - started
            console.print("{} nodes read (elapsed: {:.2f} secs)".format(nodes_read, elapsed))

        run_summaries = open(all_runs_file_path, 'r')
        self.num_incomplete_runs = 0
        for run_summary in run_summaries:
            run = Run(run_summary, self.args.primary_metric, verbose=self.args.verbose, use_azure_storage=True)
            skip_this_run = False

            if run.skip:
                continue

            # Try to assemble a configuration string for this run.
            hp_id__setting_id__list = []

            # remove any reported hparams not found in search (allowed in XT)
            hp_list = run.hpname_hpvalue_list
            search_keys = list(self.name_hparam_dict.keys())
            new_list = [(hp_name, hp_value) for hp_name, hp_value in hp_list if hp_name in search_keys]
            run.hpname_hpvalue_list = new_list

            for hp_name, hp_value in run.hpname_hpvalue_list:
                # we no longer require that all run-reported hparams are present in the hp-config file
                # assert is here to ensure above filtering of run.hpname_hpvalue_list worked correctly
                assert hp_name in self.name_hparam_dict.keys()  

                hparam = self.name_hparam_dict[hp_name]
                
                # fixup multi-valued HP where we only use a single value
                if isinstance(hp_value, list) and len(hp_value)==1:
                    hp_value = hp_value[0]

                if hp_value not in hparam.value_setting_dict:
                    if self.args.verbose:
                        console.print("Skipping {}  (Unexpected hparam value {}:{})".format(run.run_name, hparam.name, hp_value))
                    skip_this_run = True
                    break  # Skip this run. Its value must have been removed from config.txt.

                setting = hparam.value_setting_dict[hp_value]
                hp_id__setting_id__list.append((hparam.id, setting.id))

            if skip_this_run:
                continue

            # add this as a valid run
            run.hp_id__setting_id__list = hp_id__setting_id__list
            run.config_str = str(hp_id__setting_id__list)
            self.runs.append(run)

        self.runs.sort(key=get_end_id)

    def load_runs_from_db(self):
        # Get the run summaries.
        self.init_xtstore()
        metric_name = "metrics.{}".format(self.args.primary_metric)
        filter_dict = {"job_id":self.args.job, "end_id":{"$gt": 0}, 'status':'completed', metric_name:{"$exists": True}, 'is_parent':False}
        fields_dict = {'run_name':1, 'end_id':1, 'hparams':1, metric_name:1}
        
        console.print('load_runs_from_db...')
        run_summaries = self.xtstore.get_all_runs("job", self.ws_name, self.args.job, filter_dict, fields_dict, use_cache=False)
        run_dict = {}

        # Create runs from the summaries.
        for run_summary in run_summaries:
            run = Run(run_summary, self.args.primary_metric, self.args.maximize_metric, verbose=self.args.verbose)
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
                    if self.args.verbose:
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
                    if self.args.verbose:
                        console.print("Skipping {}  (Unexpected hparam value {}:{})".format(run.run_name, hparam.name, hp_value))
                    run.skip = True  # Unexpected hparam value.
                    break
                setting = hparam.value_setting_dict[hp_value]
                hp_id__setting_id__list.append((hparam.id, setting.id))
            if run.skip:
                continue

            # Make sure we don't already have this run.
            if run.run_name in run_dict:
                # console.print("Ignoring copy of {}".format(run.run_name))
                # console.print("  current  end_id == {}".format(run.end_id))
                # console.print("  previous end_id == {}".format(run_dict[run.run_name].end_id))
                continue
            else:
                run_dict[run.run_name] = run

            # Add this as a valid run
            run.hp_id__setting_id__list = hp_id__setting_id__list
            run.config_str = str(hp_id__setting_id__list)
            self.runs.append(run)

        # Sort the runs by order of completion.
        self.runs.sort(key=get_end_id)
        for i, run in enumerate(self.runs):
            assert isinstance(run.end_id, int)
            if i > 0:
                if not (run.end_id > self.runs[i-1].end_id):
                    console.print("Problem found with run.end_id values:")
                    console.print("  run[{}].end_id == {}   {}   {}".format(i, run.end_id, run.run_name, run.value))
                    console.print("  run[{}].end_id == {}   {}   {}".format(i-1, self.runs[i-1].end_id, self.runs[i-1].run_name, run.value))
                    if run.end_id < self.runs[i-1].end_id:
                        console.print("    The expected order is reversed.")
                    elif run.end_id == self.runs[i-1].end_id:
                        console.print("    They are equal.")
                    else:
                        console.print("    They cannot be compared.")
                assert run.end_id > self.runs[i-1].end_id

        console.print("runs returned: {:,}, runs loaded: {:,}, primary_metric: {}, maximize_metric: {}".format( \
            len(run_summaries), len(self.runs), self.args.primary_metric, self.args.maximize_metric))

        if self.args.maximize_metric:
            console.print("MAXIMIZING: {}".format(self.args.primary_metric))
        else:
            console.print("MINIMIZING: {}".format(self.args.primary_metric))

    def populate_runsets(self, global_runset):
        ''' Groups runs into runsets that share the same HP combination. '''
        prior_mean = global_runset.sample_mean
        prior_var = global_runset.get_sample_var()
        best_runset = global_runset
        if self.args.verbose:
            console.print("\nDetailed history of trophy holders...")
        for i, run in enumerate(self.runs):
            config_str = run.config_str
            hp_id__setting_id__list = run.hp_id__setting_id__list
            if config_str not in self.configstr_runset_dict.keys():
                runset = RunSet(len(self.runsets), self, hp_id__setting_id__list, config_str)
                self.configstr_runset_dict[config_str] = runset
                self.runsets.append(runset)
            runset = self.configstr_runset_dict[config_str]
            runset.add_run(run)
            runset.update_posteriors(prior_mean, prior_var)
            if not runset.in_list:
                runset.insert(global_runset.dn, global_runset)  # Top of the list.
            runset.reposition()
            if global_runset.dn != best_runset:
                best_runset = global_runset.dn
                self.best_runset_trophies.append(RunSetTrophy(i, best_runset))
                if self.args.verbose:
                    console.print("New trophy goes to runset {}".format(best_runset.id))
                    if best_runset.post_mean is None:
                        console.print("    {} = None".format(self.hpmax_name))
                    else:
                        console.print("    {} = {:9.3f}".format(self.hpmax_name, best_runset.post_mean))
                    if best_runset.dn is not None:
                        if best_runset.dn.post_mean is None:
                            console.print("    prev  = None")
                        else:
                            console.print("    prev  = {:9.3f}".format(best_runset.dn.post_mean))
                    for r in best_runset.runs:
                        console.print('    {}'.format(r.run_name))
            else:
                self.best_runset_trophies[-1].num_runs += 1
        if self.args.verbose:
            console.print("\nAll runsets...")
            for runset in self.runsets:
                runset.report(" {:5d}  ".format(runset.id))

    def define_hyperparameters_from_config_yaml(self, hp_config):
        '''
            Input:   XT's standard HP definition file.
            Outputs:
                self.name_hparam_dict:
                self.hparams:
        '''
        self.name_hparam_dict = {}
        self.hparams = []
        chosen_hp_value_dict = yaml.load(open(hp_config, 'r'), Loader=yaml.Loader)

        # allow for older name "hparams"
        hparams_name = "hparams" if "hparams" in chosen_hp_value_dict else "hyperparameter-distributions"
        hpname_valuelist_dict = chosen_hp_value_dict[hparams_name]

        for hpname in hpname_valuelist_dict:
            valuelist = hpname_valuelist_dict[hpname]

            if not isinstance(valuelist, (tuple, list)):
                # omit single value hparams or unsupported hyperopt functions
                omit_value = True

                if isinstance(valuelist, str):
                    if valuelist.startswith("$"):
                        hd = hp_helper.parse_hp_dist(valuelist)
                        if "args" in hd and hd["args"] is not None:
                            # $choice or $linspace results in a list of values
                            valuelist = list(hd["args"])
                            if len(valuelist) > 0:
                                omit_value = False

                if omit_value:
                    continue

            hp = Hyperparameter(len(self.hparams), hpname, valuelist)
            self.hparams.append(hp)
            self.name_hparam_dict[hpname] = hp

    def show_hp_in_report(self, hp_name):
        show = self.show_single_valued_hps
        if not show:
            # only show hps with more than 1 value
            hp = self.name_hparam_dict[hp_name]
            if len(hp.value_setting_dict) > 1:
                show = True

        return show

    def evaluate(self):
        # Get the hyperparameters and the runs.
        self.load_hp_definitions()
        if self.args.use_azure_storage:
            self.load_runs_from_storage()
        else:
            self.load_runs_from_db()

        # Add the runs to a global runset, which will double as the sentinel of the runset list.
        global_runset = RunSet(0, None, None, None)
        for run in self.runs:
            global_runset.add_run(run)
        global_runset.sent = True
        global_runset.insert(global_runset, global_runset)

        # If max_runs is set, discard all later runs.
        if self.args.max_runs and (self.args.max_runs < len(self.runs)):
            self.runs = self.runs[0:self.args.max_runs]

        if self.args.verbose:
            if self.args.verbose:
                console.print("\nAll runs in order of completion...")
            for run in self.runs:
                console.print('{}  {:9.3f}'.format(run.run_name, run.value))

        # Populate the runset list.
        self.populate_runsets(global_runset)

        # Analyze the search progress, based on the expected performance
        # obtained by stopping the search after some number of runs.
        num_runs = len(self.runs)
        xs = np.zeros((num_runs))
        ys = np.zeros((num_runs))
        ds = np.zeros((num_runs))
        x = 0

        #build headers and rows for report
        hp_names = []
        for hp in self.hparams:
            hp_names.append(hp.name)

        fixed_names = ['RUNSET', 'SIZE', 'BEST_FOR', 'EST_{}'.format(self.hpmax_name), 'BEST_RUN']
        avail_cols = hp_names + fixed_names

        records = []
        for trophy in self.best_runset_trophies:
            trophy.runset.runs.sort(key=get_neg_run_value)
            best = '{}'.format(trophy.runset.runs[0].run_name)  # To show only the best run for each runset.

            hp_values = trophy.runset.report_configuration_string().split()
            hd = {header:utils.make_numeric_if_possible(value) for header, value in zip(hp_names, hp_values) if self.show_hp_in_report(header)}

            if self.args.maximize_metric:
                fixed_values = [trophy.runset.id, len(trophy.runset.runs), trophy.num_runs, trophy.runset.post_mean, best]
            else:
                fixed_values = [trophy.runset.id, len(trophy.runset.runs), trophy.num_runs, -trophy.runset.post_mean, best]

            fd = {name: value for name, value in zip(fixed_names, fixed_values)}

            # merge fd into hd
            hd.update(fd)
            records.append(hd)

            # calc data for plot
            y = trophy.runset.post_mean
            d = math.sqrt(trophy.runset.post_var)

            for i in range(trophy.num_runs):
                xs[x] = x + 1
                ys[x] = y
                ds[x] = d
                x += 1

        from xtlib.report_builder import ReportBuilder   
        builder = ReportBuilder(self.xt_config, self.xtstore)

        # build report (borrow config file settings from run-reports)
        text, row_count = builder.build_formatted_table(records, avail_cols=avail_cols, col_list=hd.keys(), 
            report_type="run-reports", max_col_width=50)

        # print report
        console.print()
        console.print(text)

        console.print("The table above is the history of the best hyperparameter combination (set of runs) after each of the {} completed runs.".format(len(self.runs)))

        # Plot the search progress.
        y_axis_label = "Posterior estimate of {}".format(self.args.primary_metric)
        plot(xs, ys, ds, self.args.job, y_axis_label)


def parse_args(args_list=None):
    example_text = '''Example usage:\n  Evaluate the results of a hyperparameter tuning job:\n    (In rl_nexus...) python scripts/eval_hp_search.py job411'''
    parser = argparse.ArgumentParser(description='Evaluate the results of a hyperparameter tuning job.',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog=example_text)
    parser.add_argument('job', action='store', help='Name of the job.')
    parser.add_argument('--no_download', action='store_true', help='To save time by skipping download of runs for a completed, previously viewed job.')
    parser.add_argument('--job_dir', action='store', help='Path to the parent directory of the given job, where files will be stored. Defaults to dilbert/jobs/', default='../jobs')
    parser.add_argument('--max_runs', action='store', help='Terminate the evaluation after this many runs.', type=int, default=0)
    parser.add_argument('--primary_metric', action='store', help='(For old jobs) Name of the metric maximized by HP tuning. Defaults to hpmax.', default='hpmax')
    parser.add_argument('--maximize_metric', action='store', help='True if the primary metric should be maximized. Defaults to True.', default=True)
    parser.add_argument('--hp_config_file_name', action='store', help='(For old jobs) Name of the file defining the HPs.', default='uploaded_hp_config.yaml')
    parser.add_argument('--workspace', action='store', help='name of the workspace for the job', default='')
    parser.add_argument('--verbose', action='store_true', help='Print extra output to the console for debugging.')
    parser.add_argument('--use_azure_storage', action='store_true', help='Pulls run results from Azure Storage instead of SQL DB (the default).')
    return parser.parse_args(args_list)


if __name__ == '__main__':
    args = parse_args()
    search_history = SearchHistory(args)
    search_history.evaluate()
