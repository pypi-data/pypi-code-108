#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# store.py - implements the STORE API of Experiment Tools
import numpy as np
import os
import sys
import math
import time
import json
import uuid
import shutil
import socket 
import logging
#from multiprocessing import Pool
from threading import Thread, Lock

from xtlib import utils
from xtlib import errors
from xtlib import pc_utils
from xtlib import constants
from xtlib import file_utils
from xtlib import run_helper
from xtlib import store_utils
from xtlib import run_errors
from xtlib.storage import mongo_v2
from xtlib.storage import odbc
from xtlib.helpers import xt_config
from xtlib.utils import log_info, log_title
from xtlib.helpers.feedbackParts import feedback as fb

from xtlib.console import console
from xtlib.helpers.bag import Bag
from xtlib.helpers.part_scanner import PartScanner
from xtlib.constants import RUN_STDOUT, RUN_STDERR
from xtlib.helpers.stream_capture import StreamCapture
from xtlib.constants import WORKSPACE_DIR, WORKSPACE_LOG, RUN_LOG

from .store_objects import StoreBlobObjs

# access to AML
#from azureml.core import Workspace
#from azureml.core import Experiment

# globals
logger = logging.getLogger(__name__)

# public function (used by tensorboard_reader)
def create_from_props_dict(pd):
    return Store(**pd) 

# public function
def store_from_context(context):

    # build db_options from context
    db_options = context.database
    console.diag("store_from_context: db_options={}".format(db_options))
    #assert bool(db_options)

    db_creds = context.db_creds

    store = Store(context.store_creds, provider_code_path=context.store_code_path, 
        db_creds=db_creds, db_options=db_options, show_missing_jobid_calls=context.show_missing_jobid_calls)

    return store

def init_store_utils(use_v1):
    if use_v1:
        # JIT import to minimize impact of V1
        from xtlib.storage_v1.store_v1 import build_store_utils_v1
        build_store_utils_v1()
    else:
        build_store_utils_v2()

def is_version1_store(config=None, storage_creds=None, provider_code_path=None):
    if config:
        if not storage_creds:
            storage_creds = config.get_storage_creds()

        if not provider_code_path:
            provider_code_path = config.get_storage_provider_code_path(storage_creds)

    # instantiate the provider
    class_ctr = utils.get_class_ctr(provider_code_path)
    provider = class_ctr(storage_creds)

    # does the version 1 system info container exist?
    if provider.does_container_exist(constants.INFO_CONTAINER_V2):
        use_v1 = False
    else:
        use_v1 = provider.does_container_exist(constants.INFO_CONTAINER_V1)

    return use_v1, provider

# public function
def Store(storage_creds=None, config=None, max_retries=25, run_cache_dir=None, feedback_enabled=True,  db_creds=None, 
        provider_code_path=None, validate_creds=False, db_options=None, show_missing_jobid_calls=False):
    '''
    This function peeks at the version number in the storage and chooses StoreV1 or StoreV2 as the store 
    class to return an instance of.
    '''

    console.diag("Store: db_options={}".format(db_options))
    #assert bool(db_options)

    use_v1, provider = is_version1_store(config=config, storage_creds=storage_creds, 
        provider_code_path=provider_code_path)

    # initialize functions of data of share_utils to use v1 or v2 storage format
    init_store_utils(use_v1)

    if use_v1:
        #----- V1 store ----
        # JIT import to minimize impact of V1
        from xtlib.storage_v1.store_v1 import StoreV1
        assert not provider.does_container_exist(constants.INFO_CONTAINER_V2)

        store = StoreV1(storage_creds, config, max_retries, run_cache_dir, feedback_enabled,  db_creds, 
            provider_code_path, validate_creds)

        assert not provider.does_container_exist(constants.INFO_CONTAINER_V2)
    else:
        #----- V2 store ----
        assert not provider.does_container_exist(constants.INFO_CONTAINER_V1)

        store = StoreV2(storage_creds, config, max_retries, run_cache_dir, feedback_enabled,  db_creds, 
            provider_code_path, validate_creds, db_options=db_options, show_missing_jobid_calls=show_missing_jobid_calls)

        assert not provider.does_container_exist(constants.INFO_CONTAINER_V1)

    return store

# main class that implements the XT STORE API
class StoreV2():
    '''This class provides access to the XT Store, which is based on a storage provider.
    Methods are provided to manage workspaces, experiments, runs, and related files.

    You can create an instance of XTStore by providing any of these:
        - a XTConfig instance (holds information from the XT configuration file)
        - the storage credentials dictionary containing the key, name, etc., as required by the provider

    :param storage_creds: storage credentials dict (specific to the current storage provider)
    :param config: an instance of the XTConfig class.
    :param max_retries: the number of times to return an Azure error before failing the associated call.
    :param db_creds: a dictionary of database credential properties (specific to database type).
    :param provider_code_path: a string containing a python module.class reference to the provider code

    :Example:

        >>> from store import Store
        >>> store = Store(config=my_config)
        >>> run_names = store.get_run_names("ws1")

    '''
    
    def __init__(self, storage_creds=None, config=None, max_retries=25, run_cache_dir=None, feedback_enabled=True,  db_creds=None, 
        provider_code_path=None, validate_creds=False, db_options=None, show_missing_jobid_calls=False):
        '''This is the constructor for the Store class. '''

        self.feedback_enabled = feedback_enabled
        self.show_missing_jobid_calls = show_missing_jobid_calls

        if not db_creds and config:
            db_creds = config.get_database_creds()

        self.max_log_workers = utils.safe_value(db_options, "max-log-workers")

        if config:
            if not storage_creds:
                storage_creds = config.get_storage_creds()

            if not provider_code_path:
                provider_code_path = config.get_storage_provider_code_path(storage_creds)

        self.helper = StoreBlobObjs(storage_creds, provider_code_path=provider_code_path, 
            max_retries=max_retries, owner=self)

        # validate STORAGE credentials
        if validate_creds:
            try:
                self.does_workspace_exist("test")
            except BaseException as ex:
                logger.exception("Error store.__init__, tried to test storage credentials, ex={}".format(ex))

                errors.service_error("Azure Storage service credentials not set correctly" + 
                    "; use 'xt config' to correct")

        self.run_cache_dir = run_cache_dir
        self.provider_code_path = provider_code_path
        self.storage_creds = storage_creds
        self.format = constants.STORAGE_FORMAT_V2

        self.store_type = storage_creds["provider"]

        self.cap_stdout = None
        self.cap_stderr = None

        self.db_conn_str = db_creds["connection-string"]
        self.db_type = db_creds["type"]
        self.db_name = db_creds["name"]

        if self.db_type == "mongo":
            self.database = mongo_v2.MongoDB2(self.db_conn_str, run_cache_dir=run_cache_dir, store=self, 
                db_options=db_options) 
        
        elif self.db_type == "odbc":
            self.database = odbc.OdbcDatabase(db_creds, store=self, db_options=db_options) 

        elif self.db_type:
            errors.config_error("Unsupported database type: {}".format(self.db_type))

        if self.database:
            self.helper.validate_storage_and_db(self.database)

        self.db_creds = db_creds

    def init_store_utils_if_needed(self):
        ''' this function works by forcing creation of JIT store object, which calls init_store_utils()'''
        pass

    def get_name(self):
        return self.helper.get_name()
        
    def get_database(self):
        return self.database

    def get_props_dict(self):
        pd = {"storage_creds": self.storage_creds, "db_creds": self.db_creds, 
            "run_cache_dir": self.run_cache_dir, "provider_code_path": self.provider_code_path}
        return pd

    def _error(self, msg):
        raise Exception("Error - {}".format(msg))

    # ---- SHARES ----

    def _ensure_share_exists(self, share_name, flag_as_error=True):
        return self.helper.ensure_workspace_exists(share_name, flag_as_error)

    def does_share_exist(self, share_name):
        ''' returns True if the specified share exists in the Store; False otherwise.
        '''
        return self.helper.does_share_exist(share_name)

    def create_share(self, share_name, description=None):
        ''' create a new share using the specified name.
        '''
        self.helper.create_share(share_name, description)

    def delete_share(self, share_name):
        ''' delete the specified share, and all of the blobs stored within it
        '''
        result = self.helper.delete_share(share_name)
        if result:
            # remove associated summary cache
            self.database.remove_cache(share_name)

        return result
    
    def get_share_names(self):
        ''' return the names of all shares that are currently defined in the XT Store.
        '''
        return self.helper.get_share_names()

    # ---- WORKSPACE ----

    def ensure_workspace_exists(self, ws_name, flag_as_error=True):
        created = self.helper.ensure_workspace_exists(ws_name, flag_as_error)
        if True:  # created:
            self.database.create_workspace_if_needed(ws_name)

    def get_running_workspace(self):
        ''' returns the name of the workspace associated with the current XT run.
        '''
        return os.getenv("XT_WORKSPACE_NAME", None)

    def does_workspace_exist(self, ws_name):
        ''' returns True if the specified workspace exists in the Store; False otherwise.
        '''
        return self.helper.does_workspace_exist(ws_name)

    def create_workspace(self, ws_name, database=None):
        ''' create a new workspace using the specified name.
        '''
        self.helper.create_workspace(ws_name)

        # log some information
        self.log_workspace_event(ws_name, "created", {"database": database})

        self.database.create_workspace_if_needed(ws_name, database)

    def delete_workspace(self, ws_name):
        ''' delete the specified workspace, and all of the runs stored within it.
        '''

        result = self.helper.delete_workspace(ws_name)
        console.print("delete_workspace: result from storage provider: {}".format(result))

        if result:
            # remove associated database info
            result2 = self.database.delete_workspace_if_needed(ws_name)
            console.print("delete_workspace: result from database: {}".format(result2))

        return result
    
    def log_workspace_event(self, ws_name, event_name, data_dict):
        ''' log the specifed event_name and key/value pairs in the data_dict to the workspace log file.
        '''
        record_dict = {"time": utils.get_arrow_time_str(), "event": event_name, "data": data_dict}
        rd_text = json.dumps(record_dict)

        # append to workspace log file
        self.append_workspace_file(ws_name, WORKSPACE_LOG, rd_text + "\n")

    def get_workspace_names(self, use_database=False):
        ''' return the names of all workspaces that are currently defined in the XT Store.
        '''
        if use_database:
            # use database for more faster workspace names 
            names = self.database.get_workspace_names()
        else:
            # storage is the ground truth for workspace names
            names = self.helper.get_workspace_names()

        return names

    def is_legal_workspace_name(self, name):
        ''' return True if 'name' is a legal workspace name for the current XT Store.
        '''
        return self.helper.is_legal_workspace_name(name)

    # ---- WORKSPACE FILES ----

    def create_workspace_file(self, ws_name, ws_fn, text):
        ''' create a workspace file 'ws_fn" containing 'text', within the workspace 'ws_name'.
        '''
        #return self.helper.create_workspace_file(ws_name, ws_fn, text)
        wf = self.workspace_files(ws_name, use_blobs=True)
        return wf.create_file(ws_fn, text)

    def append_workspace_file(self, ws_name, ws_fn, text):
        ''' append the 'text' to the 'ws_fn' workspace file, within the workspace 'ws_name'.
        '''
        #return self.helper.append_workspace_file(ws_name, ws_fn, text)
        wf = self.workspace_files(ws_name, use_blobs=True)
        return wf.append_file(ws_fn, text)

    def read_workspace_file(self, ws_name, ws_fn):
        ''' return the text contents of the specified workspace file.'
        '''
        #return self.helper.read_workspace_file(ws_name, ws_fn)
        wf = self.workspace_files(ws_name, use_blobs=True)
        return wf.read_file(ws_fn)

    def upload_file_to_workspace(self, ws_name, ws_fn, source_fn):
        ''' upload the file 'source_fn' from the local machine to the workspace 'ws_name' as file 'ws_fn'.
        '''
        #return self.helper.upload_file_to_workspace(ws_name, ws_fn, source_fn)
        wf = self.workspace_files(ws_name, use_blobs=True)
        return wf.upload_file(ws_fn, source_fn)

    def upload_files_to_workspace(self, ws_name, ws_folder, source_wildcard):
        ''' upload the local files matching 'source_wildcard' to the workspace folder 'ws_folder' within the workspace 'ws_name'.
        '''
        #return self.helper.upload_files_to_workspace(ws_name, ws_folder, source_wildcard)
        wf = self.workspace_files(ws_name, use_blobs=True)
        return wf.upload_files(ws_folder, source_wildcard)

    def download_file_from_workspace(self, ws_name, ws_fn, dest_fn):
        ''' download the file 'ws_fn' from the workspace 'ws_name' as local file 'ws_fn'.
        '''
        #dest_fn = os.path.abspath(dest_fn)      # ensure it has a directory specified
        #return self.helper.download_file_from_workspace(ws_name, ws_fn, dest_fn)
        wf = self.workspace_files(ws_name, use_blobs=True)
        return wf.download_file(ws_fn, dest_fn)

    def download_files_from_workspace(self, ws_name, ws_wildcard, dest_folder):
        ''' download the workspace files matching 'ws_wildcard' to the local folder 'dest_folder'.
        '''
        #return self.helper.download_files_from_workspace(ws_name, ws_wildcard, dest_folder)
        wf = self.workspace_files(ws_name, use_blobs=True)
        return wf.download_files(ws_wildcard, dest_folder)

    def get_workspace_filenames(self, ws_name, ws_wildcard=None):
        ''' return the name of all workspace files matching 'ws_wildcard' in the workspace 'ws_name'.
        '''
        #return self.helper.get_workspace_filenames(ws_name, ws_wildcard)    
        wf = self.workspace_files(ws_name, use_blobs=True)
        return wf.get_filenames(ws_wildcard)
        
    def delete_workspace_file(self, ws_name, filename):
        ''' return the workspace files 'filename' from the workspace 'ws_name'.
        '''
        wf = self.workspace_files(ws_name, use_blobs=True)
        return wf.delete_file(filename)

    def does_workspace_file_exist(self, ws_name, ws_fn):
        ''' return True if the specified workspace file exists in the workspace 'ws_name'.
        '''
        #return self.helper.does_workspace_file_exist(ws_name, ws_fn)
        wf = self.workspace_files(ws_name, use_blobs=True)
        return wf.does_file_exist(ws_fn)

    # def get_job_workspace(self, job_id):
    #     return self.database.get_job_workspace(job_id)

    # ---- EXPERIMENT ----

    def does_experiment_exist(self, ws_name, exper_name):
        return self.helper.does_experiment_exist(ws_name, exper_name)

    def create_experiment(self, ws_name, exper_name):
        if self.does_experiment_exist(ws_name, exper_name):
            raise Exception("experiment already exists: workspace={}, experiment={}".format(ws_name, exper_name))
        return self.helper.create_experiment(ws_name, exper_name)

    def get_running_experiment(self):
        return os.getenv("XT_EXPERIMENT_NAME", None)

    def get_experiment_names(self, ws_name):
        ''' get list of all unique logged "exper_name" in the workspace. '''

        use_runs = False    # using runs is slower, but reads older experiment names (experiment names added to jobs 11/21/2019)
        if use_runs:
            fields_dict = {"exper_name": 1}
            items = self.get_all_runs(None, ws_name, None, None, fields_dict, use_cache=False)
            
            # convert dicts to run_names
            items = [item["exper_name"] for item in items]

            # needed as of 11/21/2019 (TEMP - handle bad records where xt bug caused exper_name to be logged as dict instead of str)
            items = [rec for rec in items if isinstance(rec, str) ]

            items = list(set(items))
        else:
            items = self.database.get_all_experiments_in_ws(ws_name)

        return items

    def get_run_names(self, ws_name):
        ''' get a flat list of all run_names in the workspace. '''

        # use database for faster results
        #return self.helper.get_run_names(ws_name)

        records = self.database.get_info_for_runs(ws_name, {"ws_name": ws_name}, {"run_name": 1})
        run_names = [r["run_name"] for r in records]

        return run_names

    # def append_experiment_run_name(self, ws_name, exper_name, run_name):
    #     self.helper.append_experiment_run_name( ws_name, exper_name, run_name)

    def get_experiment_run_names(self, ws_name, exper_name):
        return self.helper.get_experiment_run_names(ws_name, exper_name)

    # ---- EXPERIMENT FILES ----

    def create_experiment_file(self, ws_name, exper_name, exper_fn, text):
        ''' create an experiment file 'exper_fn" containing 'text'.
        '''
        ef = self.experiment_files(ws_name, exper_name, use_blobs=True)
        return ef.create_file(exper_fn, text)

    def append_experiment_file(self, ws_name, exper_name, exper_fn, text):
        ''' append 'text' to the experiment file 'exper_name'.
        '''
        ef = self.experiment_files(ws_name, exper_name, use_blobs=True)
        return ef.append_file(exper_fn, text)

    def read_experiment_file(self, ws_name, exper_name, exper_fn):
        ''' return the text contents of the experiment file 'exper_name'.
        '''
        #return self.helper.read_experiment_file(ws_name, exper_name, exper_fn)
        ef = self.experiment_files(ws_name, exper_name, use_blobs=True)
        return ef.read_file(exper_fn)

    def upload_file_to_experiment(self, ws_name, exper_name, exper_fn, source_fn):
        ''' upload the local file 'source_fn' as the experiment file 'exper_fn'.
        '''
        # return self.helper.upload_file_to_experiment(ws_name, exper_name, exper_fn, source_fn)
        ef = self.experiment_files(ws_name, exper_name, use_blobs=True)
        return ef.upload_file(exper_fn, source_fn)

    def upload_files_to_experiment(self, ws_name, exper_name, exper_folder, source_wildcard):
        ''' upload the local files specified by 'source_wildcard' to the experiment file folder 'exper_folder'.
        '''
        #return self.helper.upload_files_to_experiment(ws_name, exper_name, exper_folder, source_wildcard)
        ef = self.experiment_files(ws_name, exper_name, use_blobs=True)
        return ef.upload_files(exper_folder, source_wildcard)

    def download_file_from_experiment(self, ws_name, exper_name, exper_fn, dest_fn):
        ''' download file file 'exper_fn' to the local file 'dest_fn'.
        '''
        dest_fn = os.path.abspath(dest_fn)      # ensure it has a directory specified
        #return self.helper.download_file_from_experiment(ws_name, exper_name, exper_fn, dest_fn)
        ef = self.experiment_files(ws_name, exper_name, use_blobs=True)
        return ef.download_file(exper_fn, dest_fn)

    def download_files_from_experiment(self, ws_name, exper_name, exper_wildcard, dest_folder):
        ''' download the experiment files matching 'ws_wildcard' to the  folder 'dest_folder'.
        '''
        ef = self.experiment_files(ws_name, exper_name, use_blobs=True)
        return ef.download_files(exper_wildcard, dest_folder)

    def get_experiment_filenames(self, ws_name, exper_name, exper_wildcard=None):
        ''' return the name of all experiment files matching 'exper_wildcard'.
        '''
        ef = self.experiment_files(ws_name, exper_name, use_blobs=True)
        return ef.get_filenames(exper_wildcard)
        
    def delete_experiment_file(self, ws_name, exper_name, filename):
        ''' delete the experiment file 'filename'.
        '''
        ef = self.experiment_files(ws_name, exper_name, use_blobs=True)
        return ef.delete_file(filename)

    def does_experiment_file_exist(self, ws_name, exper_name, exper_fn):
        ''' return True if the experiment file 'exper_fn' exists.
        '''
        #return self.helper.does_experiment_file_exist(ws_name, exper_name, exper_fn)
        ef = self.experiment_files(ws_name, exper_name, use_blobs=True)
        return ef.does_file_exist(exper_fn)
    
    # ---- RUN ----

    def get_running_run(self):
        return os.getenv("XT_RUN_NAME", None)

    def does_run_exist(self, ws_name, run_name):
        return self.helper.does_run_exist(ws_name, run_name)

    def get_job_id_of_run(self, ws_name, run_name):
        id = store_utils.make_id(ws_name, run_name)
        record = self.database.get_info_for_runs(ws_name, {"_id": id}, {"job_id": 1})
        job_id = utils.safe_cursor_value(record, "job_id")

        return job_id

    def get_node_id_of_run(self, ws_name, run_name):
        id = store_utils.make_id(ws_name, run_name)
        record = self.database.get_info_for_runs(ws_name, {"_id": id}, {"node_index": 1})
        node_index = utils.safe_cursor_value(record, "node_index")
        node_id = utils.node_id(node_index)

        return node_id

    def _create_next_run_directory(self, ws_name, is_parent):

        # is this a legacy workspace?
        default_next = self.helper.get_legacy_next_run_id(ws_name)
        if not default_next:
            default_next = 1

        # allow for pending runs to write to our recycled workspace (deleted and then recreated)
        # this is a common problem with the current quicktest and the "xt-demo" workspace
        while True:
            run_id = self.database.get_next_run_id(ws_name, default_next=default_next)
            run_name = "run{}".format(run_id)

            # ensure we are not somehow overwriting an existing run
            exists = self.does_run_exist(ws_name, run_name)
            if exists:
                errors.warning("skipping allocation of: run_name={}, workspace={} (found existing run in storage)".format( \
                    run_name, ws_name))
            else:
                break

        return self.helper.create_next_run_by_name(ws_name, run_name)

    def _create_next_child_directory(self, ws_name, parent_name, child_name):

        if not child_name:
            child_id = self.database.get_next_child_id(ws_name, parent_name, default_next=1)
            console.print("database returned child_id=" + str(child_id))

            child_name = "{}.{}".format(parent_name, child_id)
            console.print("child_run_name=" + str(child_name))

        return self.helper.create_next_run_by_name(ws_name, child_name)

    def gather_run_hyperparams(self, log_records):
        # get metric name/value to report
        cmd_records = [r for r in log_records if r["event"] == "cmd"]
        hp_records = [r for r in log_records if r["event"] == "hparams"]

        hparams = {}

        if len(cmd_records):
            # get last cmd record (app may have updated cmd line hp's)
            cr = cmd_records[-1]

        # now, allow app to overwrite/supplement with HP records
        for hp in hp_records:
            #console.print("hp=", hp)
            if "data" in hp:
                dd = hp["data"]
                for name, value in dd.items():
                    #console.print("found hp: ", name, ", value=", value)
                    # for hparams, we keep original str of value specified
                    hparams[name] = value

        #console.print("returning hparams=", hparams)
        return hparams

    def start_child_run(self, ws_name, parent_run_name, exper_name=None, cmd_line_args=None, all_args=None, description=None, 
            from_ip=None, from_host=None, app_name=None, repeat=None, box_name="local", job_id=None, pool=None, 
            node_index=None, username=None, aggregate_dest=None, path=None, child_name=None, compute=None, 
            service_type=None, search_type=None, sku=None, search_style=None, run_index=None):
        '''
        This is usually called from the XT COMPUTE box, so we CANNOT get from_ip and from_computer_name from the local machine.
        '''

        utils.log_info("start_child_run, node_index", node_index)
        
        self._create_next_child_directory(ws_name, parent_run_name, child_name=child_name)

        # we are called from controller, so our box_name is the name of this machine
        hostname = pc_utils.get_hostname()

        # always log the true name of the box (since there can be multiple clients which would otherwise produce multiple "local"s)
        if box_name == "local":
            box_name = hostname

        self.start_run_core(ws_name, child_name, exper_name=exper_name, description=description, username=username,
            box_name=box_name, app_name=app_name, repeat=None, is_parent=False, job_id=job_id, pool=pool, node_index=node_index,
            aggregate_dest=aggregate_dest, path=path, aml_run_id=None, compute=compute, service_type=service_type, search_type=search_type,
            sku=sku, search_style=search_style, is_child=True, run_index=run_index)           

        # finally, add a "child_created" record to the parent
        self.log_run_event(ws_name, parent_run_name, "child_created", {"child_name": child_name}, job_id=job_id)

    def start_run_core(self, ws_name, run_name, exper_name=None, description=None, username=None,
            box_name=None, app_name=None, repeat=None, is_parent=False, job_id=None, pool=None, node_index=None,
            aggregate_dest="none", path=None, aml_run_id=None, compute=None, service_type=None, search_type=None,
            sku=None, search_style=None, is_child=False, run_index=None, tag_dict=None):

        console.diag("start_run: after create_next_run_directory")

        # log "created" event for run
        ip = pc_utils.get_ip_address()
        hostname = pc_utils.get_hostname()

        # always log the true name of the box (since there can be multiple clients which would otherwise produce multiple "local"s)
        if box_name == "local":
            box_name = hostname

        if exper_name:
            # create the experiment, if it doesn't already exist
            if not self.does_experiment_exist(ws_name, exper_name):
                self.create_experiment(ws_name, exper_name)

        # for cases where workspaces are deleted, renamed, etc, this gives a truely unique id for the run
        run_guid = str(uuid.uuid4())
        run_num = run_helper.get_run_number(run_name)
        script = os.path.basename(path) if path else None
        create_time = utils.get_arrow_time_str()

        build_parts = constants.BUILD.split(",")
        xt_version = build_parts[0].split(":")[1].strip()
        xt_build = build_parts[1].split(":")[1].strip()

        dd = {
            # RUN_INFO: flat READONLY props (27)
            "app_name": app_name, 
            "box_name": box_name, 
            "compute": compute, 
            "create_time": create_time,
            "description": description, 
            "exper_name": exper_name, 
            "from_ip": ip, 
            "from_computer_name": hostname, 
            "is_child": is_child, 
            "is_outer": True, 
            "is_parent": is_parent, 
            "job_id": job_id, 
            "node_index": node_index, 
            "path": path, 
            "repeat": repeat, 
            "run_index": run_index, 
            "run_name": run_name, 
            "run_num": run_num, 
            "run_guid": run_guid, 
            "script": script, 
            "search_style": search_style, 
            "search_type": search_type, 
            "service_type": service_type, 
            "sku": sku,
            "tags": tag_dict,
            "username": username, 
            "ws_name": ws_name, 
            "xt_build": xt_build, 
            "xt_version": xt_version, 
            }

        if aml_run_id:
            dd["aml_run_id"] = aml_run_id

        # this call will also create run in database, as appropriate
        self.log_run_event(ws_name, run_name, "created", dd, job_id=job_id)

        console.diag("start_run: after log_run_event")

        # append "start" record to workspace summary log
        dd["time"] = utils.get_arrow_time_str()
        dd["event"] = "created"
        text = json.dumps(dd) + "\n"

        # append to summary file in run dir
        self.append_run_file(ws_name, run_name, constants.RUN_SUMMARY_LOG, text, job_id=job_id)

        console.diag("start_run: after append_workspace_file")

        return run_name

    def get_ws_run_names(self, ws_name, filter_dict=None):
        fields_dict = {"_id": 1}
        items = self.get_all_runs(None, ws_name, None, filter_dict, fields_dict, use_cache=False)
        
        # convert dicts to run_names
        items = [item["_id"] for item in items]
        return items

    def update_run_at_end(self, ws_name, run_name, status, exit_code, end_time, log_records, hparams, metrics):
        result = None

        if self.database:
            result = self.database.update_run_at_end(ws_name, run_name, status, exit_code, end_time, log_records, hparams, metrics)

        return result

    def end_run(self, ws_name, run_name, status, exit_code, hparams_dict, metrics_rollup_dict, end_time=None, 
         aggregate_dest=None, dest_name=None, job_id=None):

        utils.log_info("end_run", run_name)

        if not end_time:
            end_time = utils.get_arrow_time_str()

        self.log_run_event(ws_name, run_name, "ended", {"status": status, "exit_code": exit_code, \
            "metrics_rollup": metrics_rollup_dict}, event_time=end_time, job_id=job_id)

        # append "end" record to workspace summary log
        end_record = {"ws_name": ws_name, "run_name": run_name, "time": end_time, "event": "end", 
            "status": status, "exit_code": exit_code, "hparams": hparams_dict, "metrics": metrics_rollup_dict}

        text = json.dumps(end_record) + "\n"

        # append to summary file in run dir
        self.append_run_file(ws_name, run_name, constants.RUN_SUMMARY_LOG, text, job_id=job_id)

    def delete_run(self, ws_name, run_name):
        return self.helper.delete_run(ws_name, run_name)

    def nest_run_records(self, ws_name, run_name):
        ''' return a single record that includes the all of the run_log in the data dictionary '''
        records = self.get_run_log(ws_name, run_name)    
        last_end_time = records[-1]["time"]

        log_record = {"run_name": run_name, "log": records}
        text = json.dumps(log_record) + "\n"
        #console.print("\ntext=", text)
        return text, last_end_time

    def download_all_runs_blobs(self, ws_name, aggregator_dest, job_or_exper_name, dest_fn, 
        fn_cache=None, max_workers=1):
        '''
        download the all_runs.jsonl storage blob from specified job or experiment.
        '''
        nodes_read = 0

        if aggregator_dest == "job":
            # for v2, we have distributed the all_runs for a job to smaller blobs on each of job's nodes
            nodes = self.database.get_info_for_nodes(ws_name, {"job_id": job_or_exper_name}, {"node_id": 1})
            node_id_list = [n["node_id"] for n in nodes]

            allruns_text = ""
            from threading import Lock
            worker_lock = Lock()

            # read each node's blob on a bg thread
            next_progress_num = 1

            def thread_worker(node_ids, ws_name, job_id):
                    
                for node_id in node_ids:
                    store_path = "nodes/{}/{}".format(node_id, constants.ALL_RUNS_FN)
                    if self.does_job_file_exist(ws_name, job_id, store_path):
                        node_text = self.read_job_file(ws_name, job_id, store_path)
                    else:
                        node_text = None

                    with worker_lock:
                        nonlocal allruns_text, next_progress_num, nodes_read

                        node_msg = "searching nodes: {}/{}".format(next_progress_num, len(node_id_list))
                        fb.feedback(node_msg, id="node_msg")  
                        next_progress_num += 1

                        if node_text:
                            allruns_text += node_text
                            nodes_read += 1

            utils.run_on_threads(thread_worker, node_id_list, max_workers, [ws_name, job_or_exper_name])
    
            # write to dest_fn
            file_utils.write_text_file(dest_fn, allruns_text)

        elif aggregator_dest == "exper":
            self.download_file_from_experiment(ws_name, job_or_exper_name, constants.ALL_RUNS_FN, dest_fn)

        else:
            errors.general_error("unknown aggregator_dest: {}".format(aggregator_dest))

        return nodes_read
            
    def rollup_and_end_run(self, ws_name, run_name, aggregate_dest, dest_name, status, exit_code, primary_metric, maximize_metric, 
        report_rollup, use_last_end_time=False, node_id=None, job_id=None):

        utils.log_info("rollup_and_end_run", run_name)

        end_time = utils.get_arrow_time_str()

        # write run to ALLRUNS file
        if aggregate_dest and aggregate_dest != "none":
            # convert entire run log to a single nested record
            utils.log_info("calling nest_run_records", run_name)
            text, last_end_time = self.nest_run_records(ws_name, run_name)

            # append nested record to the specified all_runs file
            if dest_name:
                if aggregate_dest == "experiment":
                    self.append_experiment_file(ws_name, dest_name, constants.ALL_RUNS_FN, text)
                elif aggregate_dest == "job":
                    # append to node-relative all_runs file
                    #self.append_job_file(ws_name, dest_name, constants.ALL_RUNS_FN, text)
                    node_path = "{}/nodes/{}".format(dest_name, node_id)
                    utils.log_info("appending to all_runs file", node_path)
                    self.append_job_file(ws_name, node_path, constants.ALL_RUNS_FN, text)

        # LOG END RUN
        log_records = self.get_run_log(ws_name, run_name)
    
        hparams = self._roll_up_hparams(log_records) 
        utils.log_info("rolled up hparams", hparams)

        metrics = self.rollup_metrics_from_records(log_records, primary_metric, maximize_metric, report_rollup) 
        utils.log_info("rolled up metrics", metrics)

        self.end_run(ws_name, run_name, status, exit_code, hparams, metrics,
            end_time=end_time, aggregate_dest=aggregate_dest, dest_name=dest_name, job_id=job_id)

        # this causes needless db traffic, so don't do it
        # if self.database:
        #     self.database.update_run_at_end(ws_name, run_name, status, exit_code, end_time, log_records, hparams, metrics)

    def _roll_up_hparams(self, log_records):
        hparams_dict = {}

        for record in log_records:
            if record["event"] == "hparams":
                dd = record["data"]
                for key,value in dd.items():
                    hparams_dict[key] = value
                    
        return hparams_dict

    def rollup_metrics_from_records(self, log_records, primary_metric, maximize_metric, report_rollup):

        # this causes confusion when applied here; keep it OFF for now
        report_rollup = False

        metrics_records = [record for record in log_records if record["event"] == "metrics"]

        # collect valid records and values for primary_metric
        records = []
        values = []
        last_record = None

        for mr in metrics_records:
            if "data" in mr:
                dd = mr["data"]
                last_record = dd

                if primary_metric in dd:
                    value = dd[primary_metric]
                    if value:

                        try:
                            # ---- some strings may be invalid ints/floats - just ignore them for now
                            if isinstance(value, str):
                                #console.print("string found: key=", key, ", value=", value)  # , ", ex=", ex)
                                if "." in value or value == 'nan':
                                    value = float(value)
                                else:
                                    value = int(value)

                        except BaseException as ex:
                            logger.exception("Error in rollup_metrics_from_records, ex={}".format(ex))
                            #console.print("exception found: key=", key, ", value=", value, ", ex=", ex)

                        #console.print("rollup gather: key={}, value={}".format(key, value))
                        values.append(value)
                        records.append(dd)

        # find rollup-record
        if records:
            index = -1

            if report_rollup:
                try:
                    if maximize_metric:
                        index = np.argmax(values)
                    else:
                        index = np.argmin(values)
                except:
                    # when above fails, just use 'last' 
                    pass

            rollup_record = records[index]
        else:
            rollup_record = last_record        
    
        return rollup_record

    def copy_run(self, ws_name, run_name, ws_name2, run_name2):
        return self.helper.copy_run(ws_name, run_name, ws_name2, run_name2)

    def get_run_log(self, ws_name, run_name):
        return self.helper.get_run_log(ws_name, run_name)

    def log_run_event(self, ws_name, run_name, event_name, data_dict=None, event_time=None, job_id=None):
        #console.print("log_run_event: ws_name={}, run_name={}, event_name={}".format(ws_name, run_name, event_name))

        if not event_time:
            event_time = utils.get_arrow_time_str()

        if data_dict and not isinstance(data_dict, dict):   
            raise Exception("data_dict argument is not a dict: " + str(data_dict))

        record_dict = {"time": event_time, "event": event_name, "data": data_dict}
        #console.print("record_dict=", record_dict)

        rd_text = json.dumps(record_dict)
        # append to run log file
        self.append_run_file(ws_name, run_name, RUN_LOG, rd_text + "\n", job_id=job_id)

        if self.database:
            # log all backend types to database
            self.database.process_run_event(ws_name, run_name, event_name, data_dict, record_dict)

    def get_job_names(self, filter_dict=None, fields_dict=None):
        return self.database.get_job_names(filter_dict, fields_dict)

    def get_job_names_from_storage(self):
        return self.helper.get_job_names()

    def get_all_runs(self, aggregator_dest, ws_name, job_or_exper_name, filter_dict=None, fields_dict=None, use_cache=False, 
        fn_cache=None, batch_size=None):

        return self.database.get_all_runs(aggregator_dest, ws_name, job_or_exper_name, filter_dict, fields_dict, use_cache,
            fn_cache, batch_size=batch_size)

    def wrapup_run(self, ws_name, run_name, aggregate_dest, dest_name, status, exit_code, primary_metric, maximize_metric, 
        report_rollup, rundir, after_files_list, log_events=True, capture_files=True, job_id=None, is_parent=False, 
        after_omit_list=None, node_id=None, run_index=None, start_time=None):

        utils.log_info("wrapup_run", run_name)

        if log_events:  
            # LOG "ENDED" to run_log, APPEND TO ALLRUNS
            self.rollup_and_end_run(ws_name, run_name, aggregate_dest, dest_name, status, exit_code, 
                primary_metric=primary_metric, maximize_metric=maximize_metric, report_rollup=report_rollup, 
                node_id=node_id, job_id=job_id)

        if rundir and capture_files:
            # CAPTURE OUTPUT FILES
            started = time.time()
            copied_files = []

            for output_files in after_files_list:
                
                from_path = os.path.dirname(output_files)
                to_path = "after/" + os.path.basename(from_path) if from_path else "after" 
                output_files = os.path.abspath(file_utils.path_join(rundir, output_files))
                #console.print("\nprocessing AFTER: ws_name=", ws_name, ", run_name=", run_name, ", output_files=", output_files, ", from_path=", from_path, ", to_path=", to_path)

                try:
                    copied = self.upload_files_to_run(ws_name, run_name, to_path, output_files, exclude_dirs_and_files=after_omit_list)
                    #console.print("AFTER files copied=", copied)
                    copied_files += copied

                    log_info("captured {} AFTER files".format(len(copied)), 
                        output_files)
                except BaseException as ex:
                    log_info("error uploading AFTER files", output_files) 
                    log_info("upload exception", ex) 

            elapsed = time.time() - started
            self.log_run_event(ws_name, run_name, "capture_after", {"elapsed": elapsed, "count": len(copied_files)}, 
                job_id=job_id)

        # tell database RUNS that this run has completed
        if self.database:
            db_retries, storage_retries = run_errors.count_run_errors(run_name)

            utils.log_info("RUN db_retries", db_retries)
            utils.log_info("RUN storage_retries", storage_retries)
            
            self.database.run_exit(ws_name, run_name, status, exit_code, db_retries, storage_retries, 
                 start_time)

            if not is_parent:
                # tell database this job has a completed run
                node_index = utils.node_index(node_id)

                utils.log_info("calling DATABASE job_run_exit", run_name)
                self.database.job_run_exit(ws_name, job_id, exit_code)

                utils.log_info("calling DATABASE node_run_end", run_name)
                self.database.node_run_end(ws_name, job_id, node_index, exit_code)

    def copy_run_files_to_run(self, ws_name, from_run, run_wildcard, to_run, to_path):
        return self.helper.copy_run_files_to_run(ws_name, from_run, run_wildcard, to_run, to_path)

    #---- LOW LEVEL ----
            
    def list_blobs(self, container, blob_path, return_names=True):
        return self.helper.list_blobs(container, blob_path, return_names=return_names)

    # ---- RUN FILES ----

    def create_run_file(self, ws_name, run_name, run_fn, text):
        '''create the specified run file 'run_fn' from the specified 'text'.
        '''
        #return self.helper.create_run_file(ws_name, run_name, run_fn, text)
        rf = self.run_files(ws_name, run_name, use_blobs=True)
        return rf.create_file(run_fn, text)

    def append_run_file(self, ws_name, run_name, run_fn, text, job_id=None):
        '''append 'text' to the run file 'run_fn'.
        '''
        rf = self.run_files(ws_name, run_name, use_blobs=True, job_id=job_id)
        return rf.append_file(run_fn, text)

    def read_run_file(self, ws_name, run_name, run_fn):
        '''return the contents of the run file 'run_fn'.
        '''
        #return self.helper.read_run_file(ws_name, run_name, run_fn)
        rf = self.run_files(ws_name, run_name, use_blobs=True)
        return rf.read_file(run_fn)

    def upload_file_to_run(self, ws_name, run_name, run_fn, source_fn, job_id=None):
        '''upload the local file 'source_fn' as the run file 'run_fn'.
        '''
        #return self.helper.upload_file_to_run(ws_name, run_name, run_fn, source_fn)
        rf = self.run_files(ws_name, run_name, use_blobs=True, job_id=job_id)
        return rf.upload_file(run_fn, source_fn)

    def upload_files_to_run(self, ws_name, run_name, run_folder, source_wildcard, exclude_dirs_and_files=[], job_id=None):
        '''upload the local files specified by 'source_wildcard' to the run folder 'run_folder'.
        '''
        #return self.helper.upload_files_to_run(ws_name, run_name, run_folder, source_wildcard, exclude_dirs)
        rf = self.run_files(ws_name, run_name, use_blobs=True, job_id=job_id)
        return rf.upload_files(run_folder, source_wildcard, exclude_dirs_and_files=exclude_dirs_and_files)

    def read_log_records(self, ws_name, run_name):
        text = self.read_run_file(ws_name, run_name, "run.log")
        records = utils.load_json_records(text)
        id = "{}/{}".format(ws_name, run_name)

        # make this look like a database record so consuming code is happy
        for record in records:
            record["key"] = id
            record["_id"] = str(uuid.uuid4())   # GUID

        return records

    def set_max_workers(self, value):
        self.max_log_workers = value

    def get_log_records_for_runs(self, ws_name, id_list):

        # gather the log records on worker threads
        next_progress_num = 1
        all_run_records = []

        from threading import Lock
        worker_lock = Lock()

        def thread_worker(ids, ws_name):
            for id in ids:
                run_name = id.split("/")[-1]
                results = self.read_log_records(ws_name, run_name)

                with worker_lock:
                    nonlocal all_run_records, next_progress_num
                    all_run_records += results

                    node_msg = "gathering log records: {}/{}".format(next_progress_num, len(id_list))
                    fb.feedback(node_msg, id="gather_msg")  
                    next_progress_num += 1

        utils.run_on_threads(thread_worker, id_list, self.max_log_workers, [ws_name])
        return all_run_records

    def download_file_from_run(self, ws_name, run_name, run_fn, dest_fn, job_id=None):
        '''download the run file 'run_fn' to the local file 'dest_fn'.
        '''
        dest_fn = os.path.abspath(dest_fn)      # ensure it has a directory specified
        rf = self.run_files(ws_name, run_name, use_blobs=True, job_id=job_id)
        return rf.download_file(run_fn, dest_fn)

    def download_files_from_run(self, ws_name, run_name, run_wildcard, dest_folder, job_id=None):
        '''download the run files specified by 'run_wildcard' to the local folder 'dest_folder'.
        '''
        #return self.helper.download_files_from_run(ws_name, run_name, run_wildcard, dest_folder)
        rf = self.run_files(ws_name, run_name, use_blobs=True, job_id=job_id)
        return rf.download_files(run_wildcard, dest_folder)

    def get_run_filenames(self, ws_name, run_name, run_wildcard=None, full_paths=False):
        '''return the names of the run files specified by 'run_wildcard'.
        '''
        #return self.helper.get_run_filenames(ws_name, run_name, run_wildcard)    
        rf = self.run_files(ws_name, run_name, use_blobs=True)
        return rf.get_filenames(run_wildcard, full_paths=full_paths)
        
    def delete_run_file(self, ws_name, run_name, filename, job_id=None):
        '''delete the run file specified by 'filename'.
        '''
        rf = self.run_files(ws_name, run_name, use_blobs=True, job_id=job_id)
        return rf.delete_file(filename)

    def delete_run_subfolder_and_files(self, ws_name, run_name, subfolder_name, job_id=None):
        '''delete all files under the specified folder_name.
        '''
        rf = self.run_files(ws_name, run_name, use_blobs=True, job_id=job_id)
        return rf.delete_files(subfolder_name + "/**")

    def does_run_file_exist(self, ws_name, run_name, run_fn, job_id=None):
        '''return True if the specified run file 'run_fn' exists.
        '''
        #return self.helper.does_run_file_exist(ws_name, run_name, run_fn)
        rf = self.run_files(ws_name, run_name, use_blobs=True, job_id=job_id)
        return rf.does_file_exist(run_fn)

    #---- JOBS ----

    def create_job(self, ws_name):
        job_num = self.database.get_next_job_id(ws_name, "next_job_number")

        job_name = "job{}".format(job_num)

        # create LAST JOB CREATED blob 
        blob_fn = constants.WORKSPACE_DIR + "/" + constants.WORKSPACE_LAST_JOB
        self.helper._create_blob(ws_name, blob_fn, str(job_num))

        return job_name

    def get_job_secret(self, ws_name, job_id):
        key = "{}/{}".format(ws_name, job_id)

        records = self.database.get_info_for_jobs( filter_dict={"_id": key}, fields_dict={"job_secret": 1} )
        value = records[0]["job_secret"] if len(records) else None
        return value

    def read_job_info_file(self, ws_name, job_id):
        return self.helper.read_job_info_file(ws_name, job_id)

    def log_job_info(self, ws_name, job_id, dd):
        text = json.dumps(dd, indent=4)
        self.helper.write_job_info_file(ws_name, job_id, text)

        # update database-db for fast access
        self.database.create_db_job(dd)

    def log_job_event(self, ws_name, job_id, event_name, data_dict=None, event_time=None):
        if not event_time:
            event_time = utils.get_arrow_time_str()

        if data_dict and not isinstance(data_dict, dict):   
            raise Exception("data_dict argument is not a dict: " + str(data_dict))
        record_dict = {"time": event_time, "event": event_name, "data": data_dict}
        #console.print("record_dict=", record_dict)

        rd_text = json.dumps(record_dict)
        # append to run log file
        self.append_job_file(ws_name, job_id, constants.JOB_LOG, rd_text + "\n")

    def log_node_event(self, ws_name, job_id, node_id, event_name, data_dict=None, event_time=None):
        if not event_time:
            event_time = utils.get_arrow_time_str()

        if data_dict and not isinstance(data_dict, dict):   
            raise Exception("data_dict argument is not a dict: " + str(data_dict))

        record_dict = {"time": event_time, "event": event_name, "data": data_dict}
        #console.print("record_dict=", record_dict)

        rd_text = json.dumps(record_dict)
        # append to node.log
        node_path = "nodes/{}/node.log".format(node_id)
        self.append_job_file(ws_name, job_id, node_path, rd_text + "\n")

    def get_job_log(self, ws_name, job_id):
        text = self.read_job_file(ws_name, job_id, constants.JOB_LOG)
        records = utils.load_json_records(text)
        return records

    #---- JOB FILES ----

    def create_job_file(self, ws_name, job_name, job_path, text):
        '''create a job file specified by 'job_path' from the text 'text'.
        '''
        #self.helper.create_job_file(job_name, job_path, text)
        jf = self.job_files(ws_name, job_name, use_blobs=True)
        return jf.create_file(job_path, text)

    def append_job_file(self, ws_name, job_name, job_path, text):
        '''append text 'text' to the job file 'job_path'.
        '''
        #self.helper.append_job_file(job_name, job_path, text)
        jf = self.job_files(ws_name, job_name, use_blobs=True)
        return jf.append_file(job_path, text)

    def read_job_file(self, ws_name, job_name, job_path):
        '''return the contexts of the job file 'job_path'.
        '''
        #return self.helper.read_job_file(job_name, job_path)
        jf = self.job_files(ws_name, job_name, use_blobs=True)
        return jf.read_file(job_path)

    def upload_file_to_job(self, ws_name, job_name, fn_job, fn_source):
        '''upload the local file 'fn_source' as the job file 'fn_job'.
        '''
        #return self.helper.upload_file_to_job(job_name, job_folder, fn_source)
        jf = self.job_files(ws_name, job_name, use_blobs=True)
        return jf.upload_file(fn_job, fn_source)

    def upload_files_to_job(self, ws_name, job_name, job_folder, source_wildcard, recursive=False, exclude_dirs_and_files=[]):
        '''upload the local files specified by 'source_wildcard' to the job folder 'job_folder'.
        '''
        #return self.helper.upload_files_to_job(job_name, job_folder, source_wildcard)
        jf = self.job_files(ws_name, job_name, use_blobs=True)
        return jf.upload_files(job_folder, source_wildcard, recursive=recursive, exclude_dirs_and_files=exclude_dirs_and_files)

    def download_file_from_job(self, ws_name, job_name, job_fn, dest_fn):
        '''download the job file 'job_fn' to the local file 'dest_fn'.
        '''
        #return self.helper.download_file_from_job(job_name, job_fn, dest_fn)
        jf = self.job_files(ws_name, job_name, use_blobs=True)
        return jf.download_file(job_fn, dest_fn)

    def download_files_from_job(self, ws_name, job_name, job_wildcard, dest_folder):
        #return self.helper.download_files_from_job(job_name, job_wildcard, dest_folder)
        jf = self.job_files(ws_name, job_name, use_blobs=True)
        return jf.download_files(job_wildcard, dest_folder)

    def get_job_filenames(self, ws_name, job_name, job_wildcard=None, full_paths=False):
        '''return the names of the job files specified by 'job_wildcard'.
        '''
        #return self.helper.get_run_filenames(ws_name, run_name, run_wildcard)    
        jf = self.job_files(ws_name, job_name, use_blobs=True)
        return jf.get_filenames(job_wildcard, full_paths=full_paths)

    def delete_job_file(self, ws_name, job_name, filename):
        '''delete the job files specified by 'job_wildcard'.
        '''
        #return self.helper.delete_run_files(ws_name, run_name, run_wildcard)
        jf = self.job_files(ws_name, job_name, use_blobs=True)
        return jf.delete_file(filename)

    def does_job_file_exist(self, ws_name, job_name, job_path):
        '''return True if the job file 'job_path' exists.
        '''
        #return self.helper.does_job_file_exist(job_name, job_path)
        jf = self.job_files(ws_name, job_name, use_blobs=True)
        return jf.does_file_exist(job_path)

    def does_job_exist(self, ws_name, job_id):
        return self.helper.does_job_exist(ws_name, job_id)


    # def append_job_run_name(self, job_name, run_name):
    #     return self.helper.append_job_run_name(job_name, run_name)

    def get_job_run_names(self, ws_name, job_name):
        return self.helper.get_job_run_names(job_name)

    # ---- DIRECT ACCESS ----
    
    def read_store_file(self, ws, path):
        return self.helper.read_store_file(ws, path)

    # ---- CAPTURE OUTPUT ----

    # def capture_stdout(self, fn=RUN_STDOUT):
    #     self.cap_stdout = StreamCapture(sys.stdout, fn)
    #     sys.stdout = self.cap_stdout

    # def capture_stderr(self, fn=RUN_STDERR):
    #     self.cap_stderr = StreamCapture(sys.stderr, fn)
    #     sys.stderr = self.cap_stderr

    def release_stdout(self):
        if self.cap_stdout:
            sys.stdout = self.cap_stdout.close()

    def release_stderr(self):
        if self.cap_stderr:
            sys.stderr = self.cap_stderr.close()

    # ---- FILES OBJECTS ----

    def root_files(self, root_name, use_blobs=False):
        return self.helper.root_files(root_name, use_blobs)

    def workspace_files(self, ws_name, use_blobs=False):
        return self.helper.workspace_files(ws_name, use_blobs)

    def run_files(self, ws_name, run_name, use_blobs=False, job_id=None):
        if job_id is None and self.show_missing_jobid_calls:

            console.print("internal warning: job_id is None in call to run_files() [will run slower as a result]")
            print("----> diagnostic stack trace")
            import traceback
            traceback.print_stack()
            print("<------")

        return self.helper.run_files(ws_name, run_name, use_blobs, job_id=job_id)

    def experiment_files(self, ws_name, exper_name, use_blobs=False):
        return self.helper.experiment_files(ws_name, exper_name, use_blobs)

    def job_files(self, ws_name, job_name, use_blobs=False):
        return self.helper.job_files(ws_name, job_name, use_blobs)


# sample code for path objects
#   wp = store.WorkspaceFiles(ws_name="ws1")  
#   wp.create_file("test.txt", "this is test.txt contents")

def build_store_utils_v2():
    # update PROPERTIES of store_utils for version 2 values
    store_utils.DATA_STORE_ROOT = make_share_name("data")
    store_utils.MODELS_STORE_ROOT = make_share_name("models")
    store_utils.STORAGE_FORMAT = constants.STORAGE_FORMAT_V2

    # update FUNCTIONS of store_utils for version 1 behavior
    store_utils.make_share_name = make_share_name
    store_utils.is_share_name = is_share_name
    store_utils.get_run_path = get_run_path
    store_utils.get_jobs_container = get_jobs_container
    store_utils.make_id = make_id
        
#---- store helpers (for replacement of store_utils) ----
def make_share_name(name):
    return "00-share-{}".format(name)

def is_share_name(name):
    return isinstance(name, str) and name.startswith("00-share-")

def get_run_path(job_id, run_name):
    path = "jobs/{}/runs/{}".format(job_id, run_name)
    return path

def get_jobs_container(ws_name):
    return ws_name    

def make_id(ws_name, obj_name):
    if "/" in obj_name:
        id = obj_name
    else:
        id = ws_name + "/" + obj_name

    return id

def simplify_id(record):
    if "_id" in record:
        _id = record["_id"]
        if "/" in _id:
            _id = _id.split("/")[-1]
            record["_id"] = _id

def simplify_records_id(records):
    if records:
        for r in records:
            simplify_id(r)

# inner function (runs on each background process)
def worker_read_log_records(info):
    config, ws_name, run_name = info
    #print("reading log...", run_name, flush=True)

    store = Store(config=config)
    records = store.read_log_records(ws_name, run_name)

    run = {"run_name": run_name, "records": records}
    return run

