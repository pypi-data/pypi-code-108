#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# run.py - simple API for ML apps to log info and get info related to current run
import os
import sys
import json
import atexit
import random
import numpy as np
from collections import OrderedDict

# xtlib
from xtlib import utils
from xtlib import errors
from xtlib import constants
from xtlib import file_utils
from xtlib import store_utils
from xtlib import impl_storage

#from xtlib.storage.store import Store, store_from_context
from xtlib.console import console
from xtlib.impl_shared import StoreOnDemand
from xtlib.helpers.xt_config import get_merged_config
from xtlib.helpers.key_press_checker import KeyPressChecker

FN_CHECKPOINT_FILE = "checkpoints/file.dat"
FN_CHECKPOINT_DICT = "checkpoints/dict_cp.json"
FN_CHECKPOINT_WILD = "checkpoints/*"

class Run():

    def __init__(self, config=None, store=None, xt_logging=True, aml_logging=True, checkpoints_enabled=True,
        tensorboard_path=None, supress_normal_output=False, auto_close=True):
        ''' 
        this initializes an XT Run object so that ML apps can use XT services from within their app, including:
            - hyperparameter logging
            - metrics logging
            - uploading files to an XT share
            - downloading files from an XT share
            - checkpoint support
            - explict HP search calls

        note: Azure ML child runs seem to get their env variables inherited from their parent run 
        correctly, so we no need to use parent run for info. '''

        self.store = None
        self.xt_logging = False
        self.metric_report_count = 0
        self.metric_names = OrderedDict()
        self.supress_normal_output = supress_normal_output
        self.user_requests = []
        self.closed = False

        # TODO: find/remove any unneeded AML logic (leftover from XT original-approach AML support)
        self.is_aml = None
        self.aml_run = None
        self.aml_logging = False

        self.db_creds = None
        self.store_creds = None

        if auto_close:
            atexit.register(self.close)

        # tensorboard writers
        self.train_writer = None
        self.test_writer = None

        # 2nd set of writers for Philly
        self.train_writer2 = None
        self.test_writer2 = None

        self.tensorboard_path = tensorboard_path
        if self.tensorboard_path:
            # TENSORBOARD WORKAROUND: this code causes tensorboard files to be closed when they are appended to
            # this allow us to just write the files to MOUNTED output dir (and not have to mirror them)
            try:
                from tensorboard.compat import tf
                delattr(tf.io.gfile.LocalFileSystem, 'append')
            except:
                import tensorflow as tf
                import tensorboard as tb
                tf.io.gfile = tb.compat.tensorflow_stub.io.gfile
                delattr(tf.io.gfile.LocalFileSystem, 'append')

            self.init_tensorboard()

        self.ws_name = os.getenv("XT_WORKSPACE_NAME", None)
        self.exper_name = os.getenv("XT_EXPERIMENT_NAME", None)
        self.run_name = os.getenv("XT_RUN_NAME", None)
        self.job_id = os.getenv("XT_JOB_ID", None)
        self.resume_name = os.getenv("XT_RESUME_NAME")

        # load context, if present
        self.context = None
        provider_code_path = None

        if self.run_name:
            self.context = utils.load_context_from_mrc()
            if self.context:
                if not supress_normal_output:
                    console.print("run context loaded: {}".format(self.context.run_name))
            else:
                if not supress_normal_output:
                    console.print("run context file not found")

            db_creds64 = os.getenv("XT_DB_CREDS")
            db_creds_json = utils.base64_to_text(db_creds64)
            self.db_creds = json.loads(db_creds_json)

            # convert store_creds from string to dict
            sc = os.getenv("XT_STORE_CREDS")
            self.store_creds = utils.base64_to_text(sc)
            if self.store_creds:
                self.store_creds = json.loads(self.store_creds)

            provider_code_path = os.getenv("XT_STORE_CODE_PATH")

        run_cache_dir = None
        self.config = config

        # if config:
        #     run_cache_dir = config.get("general", "run-cache-dir")

        is_aml_run = bool(os.getenv("AML_WORKSPACE_NAME"))
        
        if is_aml_run:
            # load azure libraries on demand
            from .backends.backend_aml import AzureML
            from azureml.core import Run as AmlRun

            self.aml_run = AmlRun.get_context()     # assumes app is running under AML
        else:
            self.aml_run = None

        self.aml_logging = aml_logging
        self.is_aml_child = False    

        # try to create the Store object, even if we are not in a run
        if not self.store_creds and not config:
            # if store_creds not set, this app is running outside of XT control
            # provide access to XT store for dev/test purposes
            config = get_merged_config(suppress_warning=True)
            
        self.config = config

        self.store = StoreOnDemand(config)

        # if self.context:
        #     self.store = store_from_context(self.context)
        # else:
        #     self.store = Store(self.store_creds, provider_code_path=provider_code_path, run_cache_dir=run_cache_dir, 
        #         db_creds=self.db_creds, config=config)

        # if not supress_normal_output:
        #     console.print("XT logging enabled: ", self.run_name)

        # distributed training support
        self.rank = None
        self.world_size = None
        self.master_ip = None
        self.master_port = None

        self.xt_logging = xt_logging and self.run_name !=  None
        self.checkpoints_enabled = checkpoints_enabled

        self.direct_run = not os.getenv("XT_CONTROLLER")

        if self.xt_logging and self.direct_run and self.store:
            # log stuff normally done by controller at start of run
            self.store.log_run_event(self.ws_name, self.run_name, "started", {})   

            if self.store.database:
                self.store.database.run_start(self.ws_name, self.run_name)
                if self.context:
                    self.store.database.job_run_start(self.ws_name, self.context.job_id)

    def check_for_user_request(self):

        request = None

        if self.run_name:
            # running under XT
            # check user request file (filled by controller)
            fn = os.path.expanduser(constants.FN_USER_REQUEST)
            if os.path.exists(fn):
                # TODO: make read/delete an ATOMIC operation
                text = file_utils.read_text_file(fn)
                file_utils.zap_file(fn)

                requests = text.split("\n")
                self.user_requests += requests

            if self.user_requests:
                request_text = self.user_requests.pop(0)
                if request_text:
                    request = json.loads(request_text)
        else:
            # if running standalone, just see if a keypress event is available
            with KeyPressChecker() as checker:
                request = checker.getch_nowait()

        return request
        
    def init_tensorboard(self):
        # as of Oct-04-2019, to use torch.utils.tensorboard on DSVM systems, we need to do one of the following:
        #   - clear the env var PYTHONPATH (before running this app)
        #   - remove the caffe2/build path from sys.path
        path = "/opt/caffe2/build"
        if path in sys.path:
            sys.path.remove(path)
        from torch.utils.tensorboard import SummaryWriter

        # to use tensorboardX, it needs to be in our install requirements.txt
        #from tensorboardX import SummaryWriter

        # since tensorboard doesn't close their files between writes (just flushes), the
        # changes won't be pushed thru blobfuse mnt_output_dir, so write them to 
        # local_output_dir where we will use XT mirroring to push their changes to "mirroring" path 
        # in run's storage

        serial_num = random.randint(1,100000)
        log_dir = "{}/logs/{}".format(self.tensorboard_path, serial_num)

        # tensorboard: SummaryWriter will output to ./runs/ directory by default
        log_path = os.path.expanduser(log_dir)
        
        log_train_path = log_path + "/train"
        file_utils.ensure_dir_exists(log_train_path)

        # debug path problem
        fn = log_train_path + "/test.txt"
        print("writing fn=", fn)
        with open(fn, "wt") as outfile:
            outfile.write("testing...\n")

        print("opening SummaryWriter on path=", log_train_path)
        self.train_writer = SummaryWriter(log_train_path)

        log_test_path = log_path + "/test"
        file_utils.ensure_dir_exists(log_test_path)
        self.test_writer = SummaryWriter(log_test_path)

        philly_path = os.getenv("PHILLY_JOB_DIRECTORY")
        if philly_path:
            self.train_writer2 = SummaryWriter(philly_path + "/train")
            self.test_writer2 = SummaryWriter(philly_path + "/test")

    def get_child_run(self, parent_run, child_run_number):
        target_run = None

        runs = parent_run.get_children()
        runs = [run for run in runs if run.number == child_run_number]
        child_run = runs[0] if len(runs) else None

        return child_run

    def close(self):

        if self.closed:
            # avoid calling close twice (once by app, once by auto_close)
            return

        print("run.close() starting...")

        # careful not to trigger store method if not needed so that local script runs
        # don't trigger need for authentication unnecessarily 
        has_store = False
        if self.store and self.store.actual_store is not None:
            has_store = True

        if self.context:
            context = self.context
            if context.hp_config and context.search_style == "dynamic":
                # this run is part of a dynamic HP search: ensure primary_metrics is in logged metrics
                primary_metric = context.primary_metric
                
                filter_dict = {"run_name": self.run_name}
                fields_dict = {"metrics": 1}
                records = self.store.database.get_info_for_runs(self.ws_name, filter_dict, fields_dict)

                logged_metrics = utils.safe_cursor_value(records, "metrics")
                if not primary_metric in logged_metrics:
                    print("raising error...")
                    errors.user_error("primary_metric '{}' not logged by this run (dynamic hyperparameter search runs must log their primary metric at least once)".format(primary_metric))
  
        if self.xt_logging and self.direct_run and has_store and self.context:
            context = self.context
            print(" context.hp_config=",  context.hp_config)
            print(" context.search_style=",  context.search_style)
            print(" context.primary_metric=",  context.primary_metric)

            status = "completed"
            exit_code = 0
            rundir = "."
            node_id = utils.node_id(context.node_index)

            # wrap up the run (usually done by controller)
            self.store.wrapup_run(context.ws, self.run_name, context.aggregate_dest, context.dest_name, 
                status=status, exit_code=exit_code, primary_metric=context.primary_metric, 
                maximize_metric=context.maximize_metric, report_rollup=context.report_rollup, rundir=rundir, 
                after_files_list=context.after_files_list, after_omit_list=context.after_omit_list, log_events=context.log, 
                capture_files=context.after_upload, job_id=context.job_id, is_parent = True, node_id=node_id, 
                run_index=None)

        if has_store and self.store.database:        
            self.store.database.on_run_close(self.ws_name, self.run_name)

            print("RUN: database call stats")
            self.store.database.print_call_stats()

        if self.train_writer:
            self.train_writer.close()
            self.test_writer.close()

        if self.train_writer2:
            self.train_writer2.close()
            self.test_writer2.close()

        if os.getenv("XT_MOUNTING_ENABLED") == "False":
            console.print("run.close(): uploading output directory to RUN storage")
            self.upload_output_dir()

        if self.is_aml and has_store:
            # partially log the end of the run

            # TODO: how to do this partial log for killed/error runs?
            status = "completed"   
            exit_code = 0
            hparams_dict = None
            metrics_rollup_dict = None
            end_time = utils.get_arrow_time_str()
            log_records = []

            self.store.end_run(self.ws_name, self.run_name, status, exit_code, hparams_dict, metrics_rollup_dict, end_time=None, 
                aggregate_dest=None, dest_name=None, is_aml=True, job_id=self.job_id)

            self.store.update_run_at_end(self.ws_name, self.run_name, status, exit_code, end_time, log_records, 
                hparams_dict, metrics_rollup_dict)

        self.closed = True

    def get_store(self):
        return self.store

    def log_hparam(self, name, value):
        if self.store and self.xt_logging:
            self.store.log_run_event(self.ws_name, self.run_name, "hparams", {name: value})

        if self.is_aml and self.aml_logging:
            self.aml_run.log(name, value)

    def log_hparams(self, data_dict):
        #console.print("log_hparam, self.store=", self.store)

        if self.store and self.xt_logging:
            self.store.log_run_event(self.ws_name, self.run_name, "hparams", data_dict, job_id=self.job_id)

        if self.is_aml and self.aml_logging:
            self.aml_run.log_row("hparams", **data_dict)

    def log_metrics(self, data_dict, step_name=None, stage=None):
        #console.print("log_metrics: self.store=", self.store, ", xt_logging=", self.xt_logging)

        dd = dict(data_dict)

        # # fix up metric values (numpy floats)
        # for key, value in dd.items():
        #     if isinstance(value, (np.float32, np.float64)):
        #         dd[key] = value.item()

        if step_name and step_name in dd:
           step_num = dd[step_name]
        else:
            self.metric_report_count += 1
            step_num = self.metric_report_count
            step_name = constants.INDEX
            dd[step_name] = step_num

        # add stage- in front of metric names
        if stage:
            orig_dd = dict(dd)
            dd = {}
            for name, value in orig_dd.items():
                if name == step_name:
                    dd[name] = value
                else:
                    dd[stage+"-"+name] = value

        # update ordered list of metric names
        metric_names_changed = False

        for name in dd.keys():
            if not name in self.metric_names:
                self.metric_names[name] = 1
                metric_names_changed = True

        # each metric set may have a unique step name so log it each time with metrics
        dd[constants.STEP_NAME] = step_name

        # log to XT
        if self.store and self.xt_logging:
            #console.print("logging run_event for metrics...")
            self.store.log_run_event(self.ws_name, self.run_name, "metrics", dd, job_id=self.job_id)

            if metric_names_changed:
                ddx = {"metric_names": list(self.metric_names)}
                # if not self.supress_normal_output:
                #     console.print("updating metric_names: {}".format(ddx))

                if self.store.database:
                    self.store.database.update_run_info(self.ws_name, self.run_name, ddx)

        # log to AML
        if self.is_aml and self.aml_logging:
            for name, value in dd.items():
                self.aml_run.log(name, value)

        # log to TENSORBOARD
        if stage is None or stage == "train":

            # log TRAIN metrics
            if self.train_writer:
                for name, value in data_dict.items():
                    if name != step_name and not isinstance(value, str):
                        self.train_writer.add_scalar(name, value, global_step=step_num)
                self.train_writer.flush()

            if self.train_writer2:
                for name, value in data_dict.items():
                    if name != step_name and not isinstance(value, str):
                        self.train_writer2.add_scalar(name, value, global_step=step_num)
                self.train_writer2.flush()

        elif stage in ["eval", "test"]:

            # log TEST metrics
            if self.test_writer:
                for name, value in data_dict.items():
                    if name != step_name:
                        self.test_writer.add_scalar(name, value, global_step=step_num)
                self.test_writer.flush()

            if self.test_writer2:
                for name, value in data_dict.items():
                    if name != step_name:
                        self.test_writer2.add_scalar(name, value, global_step=step_num)
                self.test_writer2.flush()

    def log_event(self, event_name, data_dict):
        if self.store and self.xt_logging:
            self.store.log_run_event(self.ws_name, self.run_name, event_name, data_dict)

    def is_resuming(self):
        # return a bool using not not
        return not not self.resume_name 

    def set_checkpoint(self, dict_cp, fn_cp=None):
        if self.store and self.checkpoints_enabled and not self.is_aml:
            if fn_cp:
                #console.print("uploading checkpoint file: ws={}, run={}, file={}".format(self.ws_name, self.run_name, FN_CHECKPOINT_FILE))
                self.store.upload_file_to_run(self.ws_name, self.run_name, FN_CHECKPOINT_FILE, fn_cp)
            text = json.dumps(dict_cp)
            #console.print("uploading checkpoint dict: ws={}, run={}, file={}".format(self.ws_name, self.run_name, FN_CHECKPOINT_DICT))
            self.store.create_run_file(self.ws_name, self.run_name, FN_CHECKPOINT_DICT, text)

            # also log the checkpoint
            self.store.log_run_event(self.ws_name, self.run_name, "set_checkpoint", dict_cp)
            return True
        return False

    def clear_checkpoint(self):
        if self.store and self.checkpoints_enabled and not self.is_aml:
            dict_cp = {}    # should this be passed by caller?
            self.store.delete_run_files(self.ws_name, self.run_name, FN_CHECKPOINT_WILD)
            self.store.log_run_event(self.ws_name, self.run_name, "clear_checkpoint", dict_cp)
            return True
        return False

    def get_checkpoint(self, fn_cp_dest=None):
        dict_cp = None

        if self.store and self.is_resuming() and self.checkpoints_enabled and not self.is_aml:
            if self.store.does_run_file_exist(self.ws_name, self.resume_name, FN_CHECKPOINT_DICT):
                if fn_cp_dest:
                    #console.print("downloading checkpoint file: ws={}, run={}, file={}".format(self.ws_name, self.resume_name, FN_CHECKPOINT_FILE))
                    self.store.download_file_from_run(self.ws_name, self.resume_name, FN_CHECKPOINT_FILE, fn_cp_dest)
                #console.print("downloading checkpoint dict: ws={}, run={}, file={}".format(self.ws_name, self.resume_name, FN_CHECKPOINT_DICT))
                text = self.store.read_run_file(self.ws_name, self.resume_name, FN_CHECKPOINT_DICT)
                dict_cp = json.loads(text)
                # log that we retreived the checkpoint
                self.store.log_run_event(self.ws_name, self.run_name, "get_checkpoint", dict_cp)

        return dict_cp

    def delete_run_subfolder_in_store(self, run_subfolder, show_feedback=False):

        if self.store:
            #store_path = "$jobs/{}/runs/run/output".format(self.job_id, self.run_name)
            store_path = "$" + store_utils.get_run_path(self.job_id, self.run_name) + "/" + run_subfolder
            count = self.store.delete_run_subfolder_and_files(self.ws_name, self.run_name, store_path)
        
    def upload_run_subfolder_to_store(self, local_path=None, run_subfolder="output", show_feedback=False):

        # # TEMP TEMP TEMP
        # self.job_id = "job1837"
        # self.run_name = "run6146"
        # self.ws_name = "tpx"

        if self.store:

            if not local_path:
                local_path = os.getenv("XT_OUTPUT_DIR", "output")

            # bug workaround: force self.store usage to avoid problem calling store_utils
            result = self.store.does_job_exist(self.ws_name, self.job_id)
            
            #store_path = "$jobs/{}/runs/run/output".format(self.job_id, self.run_name)
            store_path = "$" + store_utils.get_run_path(self.job_id, self.run_name) + "/" + run_subfolder
            storage = impl_storage.ImplStorage(self.config, self.store)

            count = storage.impl_storage_api.upload(local_path=local_path, store_path=store_path, share=None, feedback=show_feedback, 
                workspace=self.ws_name, run=None, experiment=None, job=None, show_output=show_feedback)
    
    def upload_output_dir(self, local_path=None, show_feedback=False):
        return self.upload_run_subfolder_to_store(local_path, "output")

    def upload_files_to_share(self, share, store_path, local_path, show_feedback=False):
        '''
        note: show_feedback not implemented; caller should call console.set_level() to control type of output
        emitted by XTLib API.
        '''
        storage = impl_storage.ImplStorage(self.config, self.store)

        count = storage.upload(local_path=local_path, store_path=store_path, share=share, feedback=show_feedback, 
            workspace=None, run=None, experiment=None, job=None)

        path = "store://{}/{}".format(store_utils.make_share_name(share), store_path)
        return {"count": count, "path": path}

    def download_files_from_share(self, share, store_path, local_path, show_feedback=False, snapshot=False):
        storage = impl_storage.ImplStorage(self.config, self.store)
        
        count = storage.download(local_path=local_path, store_path=store_path, share=share, 
            feedback=show_feedback, snapshot=snapshot, workspace=None, run=None, experiment=None, job=None)
            
        path = "store://{}/{}".format(store_utils.make_share_name(share), store_path)
        return {"count": count, "path": path}

    def get_next_hp_set_in_search(self, hp_space_dict, search_type=None, hparam_search=None):
        '''
        args:
            hp_space_dict: a dict of HP name/space_text pairs (space_text specifies search space for HP)
            search_type: type of search to perform (None will default to search_type specified for job)

        processing:
            1. extract the HP name and search spaces from hp_space_dict.  Valid space expressions:
                - single value (string, number)
                - list of values, e.g.: [.01, 02, .03]
                - $linspace() to generate specified # of discrete values: $linspace(.01, .98, 10)
                - hyperopt search space functions, e.g.: $randint() or $uniform(32, 256)

            2. call the HP search alrorithm identified by search_type

        return:
            the resulting HP set (dict) of name/value pairs, returned by the search algorithm
        '''

        from xtlib.hparams.hparam_search import HParamSearch
        
        if not search_type:
            search_type = self.context.search_type

        if not hparam_search:
            hparam_search = HParamSearch()
            
        space_records = hparam_search.parse_hp_config_yaml(hp_space_dict, search_type)

        hp_dict = hparam_search.hp_search_core(self.context, search_type, self.store, run_name=self.run_name, space_records=space_records)
        return hp_dict

    def tag_run(self, tag_dict):
        if not self.run_name:
            errors.api_error("tag_run requires app to be run under XT")

        # convert tag dict to tag list
        tag_list = []
        for key, value in tag_dict.items():
            if value is None:
                tag_list.append(key)
            else:
                tag_list.append("{}={}".format(key, value))

        storage = impl_storage.ImplStorage(self.config, self.store)
        storage.set_tags([self.run_name], tag_list, self.ws_name)

    def tag_job(self, tag_dict):
        if not self.context:
            errors.api_error("tag_job requires app to be run under XT")

        # convert tag dict to tag list
        tag_list = []
        for key, value in tag_dict.items():
            if value is None:
                tag_list.append(key)
            else:
                tag_list.append("{}={}".format(key, value))

        storage = impl_storage.ImplStorage(self.config, self.store)
        storage.set_tags([self.context.job_id], tag_list, self.ws_name)
