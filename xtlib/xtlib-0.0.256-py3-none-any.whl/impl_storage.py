#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# impl_storage.py: definition and implementation of XT storage commands
from multiprocessing import Value
import os
import sys
import time
import json
import psutil
import shutil
import fnmatch
import datetime
import tempfile
import subprocess
from threading import Lock

from xtlib import qfe
from xtlib import utils
from xtlib import errors
from xtlib import capture 
from xtlib import pc_utils
from xtlib import constants
from xtlib import file_utils
from xtlib import job_helper
from xtlib import run_helper
from xtlib import node_helper
from xtlib import store_utils
from xtlib import plot_builder
from xtlib import search_helper
from xtlib import process_utils
from xtlib import box_information
from xtlib.helpers.scanner import Scanner
from xtlib.helpers.feedbackParts import feedback as fb

from xtlib.storage.store import Store
from xtlib.client import Client
from xtlib.console import console
from xtlib.cmd_core import CmdCore
from xtlib.impl_base import ImplBase
from xtlib.helpers import file_helper
from xtlib.backends import backend_aml 
from xtlib.cache_client import CacheClient
from xtlib.report_builder import ReportBuilder   
from xtlib.impl_storage_api import ImplStorageApi
from xtlib.hparams.eval_hp_search import SearchHistory
from xtlib.hparams.hparam_explorer import HyperparameterExplorer
from xtlib.qfe import command, argument, hidden, keyword_arg, option
from xtlib.qfe import flag, faq, root, example, clone, command_help, see_also

'''
This module implements the following commands:

manage resources:
     - xt create workspace <name>               # create new workspace
     - xt delete workspace <name>               # delete the specified workspace
     - xt extract <name> to <output directory>  # copy the specified run from the store to a local directory

general information:
     - xt list workspaces                       # list workspaces 
     - xt list experiments [ <wildcard> ]       # list all (or matching) experiments in current workspace
     - xt list jobs [ <wildcard> ]              # list all jobs in store
     - xt list boxes [ <wildcard> ]             # list all boxes defined in config file
     - xt list pools [ <wildcard> ]             # list all pools defined in config file
     - xt view console <name>                   # view console output from run (after it has finished running)
     - xt view log <name>                       # view live log of run name, job name, or "controller"
     - xt view metrics <name>                   # view the metrics logged for the specified run
     - xt plot <name list>                      # display a line plot for the metrics of the specified runs
     - xt explore <name>                        # run hyperparameter explorer on specified experiment
     - xt cat [ <path> ]                        # display contents of store file
     - xt workspace                             # display the default workspace
     - xt list runs [ <name list> ]             # list all (or matching) runs in current workspace

blob/file store:
     - xt upload blob(s) from <local path> [ to <path> ]      # upload local file to blob store path or blob name
     - xt upload file(s) from <local path> [ to <path> ]      # upload local files to file store path or filename
     - xt download blob(s) from <path> to [ <local path> ]    # download file from blob store to local directory or filename
     - xt download file(s) from <path> [ to <local path> ]    # download files from file store to local directory or filename
     - xt list blobs [ <path> ]                               # list files in blob store
     - xt list files [ <path> ]                               # list files in file store
     - xt delete files [ <path> ]                             # delete files from file store
'''     

class ImplStorage(ImplBase):
    def __init__(self, config, store):
        super(ImplStorage, self).__init__()
        self.config = config
        self.store = store
        self.core = CmdCore(self.config, self.store, None)
        self.client = Client(config, store, None)
        self.client.core = self.core
        self.impl_storage_api = ImplStorageApi(self.config, self.store)
        self.next_error_count = 0
        self.next_name_num = 1

    def get_first_last_filtered_names(self, names, first_count=None, last_count=None, top_adjust=0, bot_adjust=0):
        if first_count:
            names = names[:first_count]   #  + top_adjust]
        elif last_count:
            # don't forget to include header + blank line (first 2 lines)
            #names = names[0:2] + names[-(last_count + bot_adjust):]
            names = names[-last_count:]

        return names            

    #---- LIST SHARES command ----
    @example(task="list shares in current Azure storage", text="xt list shares")
    @command(kwgroup="list", help="list currently defined shares")
    def list_shares(self):
        shares = self.store.get_share_names()
        console.print("\nXT shares:")
        for share in shares:
            console.print("  {}".format(share))

    #---- LIST WORKSPACES command ----
    @option("detail", default="names", help="when specified, some details about each workspace will be included")
    @example(task="list workspaces known to XT", text="xt list work")
    @command(kwgroup="list", help="list currently defined workspaces")
    def list_workspaces(self, detail):
        show_counts = detail=="counts"

        # # AML workspaces
        # names = self.azure_ml.get_workspaces()

        # STORE workspaces
        names = self.store.get_workspace_names()
        #console.print("names=", names)
        fmt_workspace = utils.format_store(self.store.store_type)
        store_name = self.config.get("store")

        console.print("workspaces on {}:".format(store_name))
        
        # console.print HEADERS
        if show_counts:
            console.print('  {:20.20s} {:>8s}\n'.format("NAME", "RUNS"))  

            # console.print VALUES for each record
            for name in names:
                exper_count = len(self.store.get_run_names(name))
                if len(name) > 20:
                    name = name[0:18] + "..."
                console.print('  {:20.20s} {:>8d}'.format(name, exper_count))
        else:
            for name in names:
                console.print('  {:20.20s}'.format(name))

    #---- CREATE SHARE command ----
    @argument("share", help="the name for the newly created share")
    @example(task="create a new share named 'trajectories", text="xt create share trajectories")
    @command(kwgroup="create", help="creates a new XT share")
    def create_share(self, share):
        self.store.create_share(share)
        console.print("share created: " + share)

    #---- CREATE WORKSPACE command ----
    @argument("workspace", help="the name for the newly created workspace")
    @option("database", default="__default__", help="the name of the MongoDB database to add the workspace to")
    @flag("reset-database", help="caution: will remove all data in the database (for dev use only) ")
    @example(task="create a new workspace named 'project-x", text="xt create work project-x")
    @command(kwgroup="create", help="creates a new XT workspace")
    def create_workspace(self, workspace, database, reset_database):
        ''' creates a new XT workspace.  Note that the workspace name can only contain letters, digits,
        and the "-" character.
        '''

        # backdoor way to set database options from a command
        if reset_database:
            self.config.data["database"]["reset-database"] = True

        self.store.create_workspace(workspace, database)

        if database == "__default__":
            console.print("workspace created: {}".format(workspace))
        else:
            console.print("workspace created: {} (database: {})".format(workspace, database))

    #---- DELETE SHARE command ----
    @argument("share", help="the name of the share to be deleted")
    @option("response", default=None, help="the response to be used to confirm the share deletion")
    @example(task="delete the share named 'trajectories'", text="xt delete share trajectories")
    @command(kwgroup="delete", help="deletes the specified share")
    def delete_share(self, share, response):
        if not self.store.does_share_exist(share):
            errors.store_error("share not defined: " + share)
        else:
            # get top level folders
            fs = self.impl_storage_api.create_file_accessor(use_blobs=True, share=share, ws_name=None, exper_name=None, job_name=None, run_name=None)
            dd = fs.list_directories("", subdirs=0)
            folders = dd["folders"]
            count = len(folders)

            answer = pc_utils.input_response("Enter '{}' to confirm deletion of share ({} top level folders): ".format(share, count), response)
            if answer == share:
                self.store.delete_share(share)
                console.print("share deleted: " + share)
            else:
                console.print("share not deleted")

    #---- DELETE WORKSPACE command ----
    @argument("workspace", help="the name of the workspace to be deleted")
    @option("response", default=None, help="the response to be used to confirm the workspace deletion")
    @example(task="delete the workspace named 'project-x'", text="xt delete work project-x")
    @command(kwgroup="delete", help="deletes the specified workspace")
    def delete_workspace(self, workspace, response):
        '''
        delete specified workspace from both storage and db.  
        '''
        deleted = False

        # delete workspace even when it only exists on 1 of storage or db
        
        if not self.store.does_workspace_exist(workspace):

            # cleanup workspace in database, if needed
            if self.store.database.delete_workspace_if_needed(workspace):
                console.print("workspace (found only in db) deleted: " + workspace)
            else:
                errors.store_error("workspace not defined: " + workspace)
        else:
            try:
                count = self.store.database.get_run_count(workspace)
            except:
                count = None

            if count:
                answer = pc_utils.input_response("Enter '{}' to confirm deletion of workspace ({} runs): ".format(workspace, count), response)
            else:
                # no verification required if ws has no runs
                answer = workspace

            if answer == workspace:
                self.store.delete_workspace(workspace)
                console.print("workspace deleted: " + workspace)
            else:
                console.print("workspace not deleted")

    #---- LIST EXPERIMENTS command ----
    @option("detail", default="names", help="when specified, some details about each workspace will be included")
    @option(name="workspace", default="$general.workspace", help="the name of the workspace containing the experiments")
    @argument(name="wildcard", required=False, help="a wildcard pattern used to select matching experiment names")
    @example(task="list the experiments in the current workspace", text="xt list exper")
    @example(task="list the experiments starting with the name 'george' in the 'curious' workspace", text="xt list exper george* --work=curious")
    @command(kwgroup="list", kwhelp="displays the specified storage items", help="list experiments defined in the current workspace")
    def list_experiments(self, wildcard, workspace, detail):
        ws_name = workspace 
        store_name = self.config.get("store")
        console.print("experiments on {}/{}:".format(store_name, workspace))

        names = self.store.get_experiment_names(ws_name)

        for name in names:
            if not wildcard or fnmatch.fnmatch(name, wildcard):
                console.print("  " + name)
        
    #---- LIST BOXES command ----
    @argument(name="wildcard", required=False, help="a wildcard pattern used to select box names")
    @option(name="first",  help="limit the list to the first N items", type=int)
    @option(name="last",  help="limit the list to the last N items", type=int)
    @flag(name="detail",  help="when specified, the associated job information is included")
    @example(task="list the boxes defined in the XT config file", text="xt list boxes")
    @command(kwgroup="list", help="list the boxes (remote computers) defined in your XT config file")
    def list_boxes(self, wildcard, detail, first, last):
        # get all box names
        names = list(self.config.get("boxes").keys())

        if wildcard:
            names = [name for name in names if fnmatch.fnmatch(name, wildcard)]
        names = self.get_first_last_filtered_names(names, first, last)

        if detail:
            # show detail of matching boxes
            console.print("box definitions:")
            for name in names:
                dd = self.config.get("boxes", name)
                console.print("  {}: {}".format(name, dd))
        else:
            console.print("boxes defined in config file:")
            for name in names:
                console.print("  " + str(name))

    #---- LIST TARGETS command ----
    @argument(name="wildcard", required=False, help="a wildcard name used to select 1 or more compute targets")
    @option(name="first",  help="limit the list to the first N items", type=int)
    @option(name="last",  help="limit the list to the last N items", type=int)
    @flag(name="detail",  help="when specified, the associated job information is included")
    @example(task="list the compute targets along with their definitions", text="xt list computes --detail")
    @command(kwgroup="list", help="list the user-defined compute targets")
    def list_targets(self, wildcard, detail, first, last):
        # get all compute names
        names = list(self.config.get("compute-targets").keys())

        if wildcard:
            names = [name for name in names if fnmatch.fnmatch(name, wildcard)]
        names = self.get_first_last_filtered_names(names, first, last)

        if detail:
            # show detail of matching boxes
            console.print("compute targets:")
            for name in names:
                dd = self.config.get_target_def(name)
                console.print("  {}: {}".format(name, dd))
        else:
            console.print("compute targets:")
            for name in names:
                console.print("  " + str(name))

    #---- VIEW CONSOLE command ----
    @argument(name="name", help="the name of the run or job")
    @option(name="workspace", default="$general.workspace", help="the workspace that the run resides in")
    @option(name="node-index", default=0, help="the node index for the specified job")
    @example(task="view the console output for run26 in the curious workspace", text="xt view console curions/run26")
    @example(task="view the console output for job201, node3", text="xt view console job201 --node-index=3")
    @command(kwgroup="view",  help="view console output for specified run")
    def view_console(self, name, workspace, node_index):
        if job_helper.is_job_id(name):
            # treat target as job_name
            job_name = name
            job_helper.validate_job_name_with_ws(self.store, workspace, job_name, True)
            fn = "node-{}/after/stdout.txt".format(node_index)

            if not self.store.does_job_file_exist(workspace, job_name, fn):
                console.print("job '{}' has no file'{}'".format(job_name, fn))
            else:
                console.print("{} for {}:\n".format(fn, job_name))

                text = self.store.read_job_file(workspace, job_name, fn)
                text = pc_utils.make_text_display_safe(text)
                console.print(text)            
        else:
            # treat target as run_name
            run_name = name
            ws, run_name, full_run_name = run_helper.validate_run_name(self.store, workspace, run_name, parse_only=False)

            fn = "after/output/console.txt"
            if not self.store.does_run_file_exist(ws, run_name, fn):
                # legacy run layout 
                fn = "after/console.txt"

            if not self.store.does_run_file_exist(ws, run_name, fn):
                console.print("run '{}' has no file'{}'".format(full_run_name, fn))
            else:
                console.print("{} for {}:\n".format(fn, full_run_name))

                text = self.store.read_run_file(ws, run_name, fn)
                text = pc_utils.make_text_display_safe(text)
                console.print(text)

    #---- EXPORT WORKSPACE command ----
    @argument(name="output-file", help="the name of the output file to export workspace to")
    @option(name="workspace", default="$general.workspace", help="the workspace that the run resides in")
    @option(name="experiment", type="str_list", help="matches jobs belonging to the experiment name")
    @option(name="tags-all", type="str_list", help="matches jobs containing all of the specified tags")
    @option(name="tags-any", type="str_list", help="matches jobs containing any of the specified tags")
    @option(name="jobs", type="str_list", help="list of jobs to include")
    @flag(name="v1", help="force data to be written in storage v1 style")
    @option("response", default=None, help="the response to be used to confirm the existing file deletion")
    @example(task="export workspace ws5 to ws5_workspace.zip", text="xt export workspace ws5_workspace.zip --workspace=ws5")
    @command(help="exports a workspace to a workspace archive file")
    def export_workspace(self, output_file, workspace, tags_all, tags_any, jobs, experiment, response, v1):

        self.impl_storage_api.export_workspace(output_file, workspace, tags_all, tags_any, jobs, experiment, 
            show_output=True, response=response, force_v1=v1)

    #---- IMPORT WORKSPACE command ----
    @argument(name="input-file", help="the name of the archive file (.zip) to import the workspace from")
    @option(name="workspace", type=str, help="the new name for the imported workspace")
    @option(name="job-prefix", default="imp", help="the prefix to use for imported jobs (version 1 format)")
    @flag(name="overwrite", help="when True, an existing workspace of the same name will be overwritten")
    @example(task="import workspace from workspace.zip as new_ws5", text="xt import workspace workspace.zip --work=new_ws5")
    @command(help="imports a workspace from a workspace archive file")
    def import_workspace(self, input_file, workspace, job_prefix, overwrite):

        self.impl_storage_api.import_workspace(input_file, workspace, job_prefix, overwrite, show_output=True)

    #---- VIEW RUN command ----
    @argument(name="run-name", help="the name of the run")
    @option(name="workspace", default="$general.workspace", help="the workspace that the run resides in")
    @example(task="view information for run26", text="xt view run26")
    @command(kwgroup="view",  help="view information for specified run")
    def view_run(self, run_name, workspace):
        console.print("run: {}".format(run_name))

    #---- VIEW ERRORS command ----
    @argument(name="name", help="The name of the job, node, or run whose errors are to be viewed")
    @option(name="workspace", default="$general.workspace", help="the workspace that the job resides in")
    @option("node-index", default=0, type=int, help="the node index for multi-node jobs")
    @option("max-workers", default="$general.max-run-workers", type=int, help="the maximum number of background workers used to gather run errors")
    @flag("group-by-context", default=False, help="when True, errors are grouped by context")
    @example(task="view the error summary job42", text="xt view errors job42")
    @command(kwgroup="view",  help="view the error summary for the specified job, node, or run")
    def view_errors(self, name, workspace, node_index, max_workers, group_by_context):
        if job_helper.is_job_id(name):
            return self.view_job_errors(workspace, name, node_index, max_workers, group_by_context) 

    def view_job_errors(self, ws_name, job_id, node_index, max_workers, group_by_context):

        if node_index:
            nodes = [node_index]
        else:
            # get number of nodes for job
            record = job_helper.get_job_record(self.store, ws_name, job_id, {"node_count": 1})
            node_count = record["node_count"]
            nodes = list(range(node_count))

        data_by_node = self.gather_errors_for_nodes(ws_name, job_id, nodes, max_workers)

        total_db_counts = {}
        total_storage_counts = {}
        total_fatal_counts = {}

        for node_index in nodes:

            db_counts = {}
            storage_counts = {}
            fatal_counts = {}
            node_id = utils.node_id(node_index)

            runs_for_node = data_by_node[node_id]

            if (not runs_for_node):
                continue

            # if detail in ["nodes", "runs"]:
            #     console.print("\n{}, node{}:".format(job_id, node_index))
    
            for run_data in runs_for_node:

                # process entries for run
                for entry in run_data:

                    error_type = entry["error_type"]
                    error = entry["error"]
                    context = entry["context"]

                    if group_by_context:
                        entry2 = dict(entry)
                        del entry2["run_name"]

                        error_key = str(entry2)
                    else:
                        error_key = error

                    # if detail in ["nodes", "runs"]:
                    #     console.print("\n  error_type: {}, error: {}".format(error_type, error))
                    #     console.print("    context: {}".format(context))

                    if error_type == "db":
                        if not error_key in db_counts:
                            db_counts[error_key] = []
                        if not error_key in total_db_counts:
                            total_db_counts[error_key] = []

                        db_counts[error_key].append(entry)
                        total_db_counts[error_key].append(entry)

                    elif error_type == "storage":
                        if not error_key in db_counts:
                            storage_counts[error_key] = []
                        if not error_key in total_storage_counts:
                            total_storage_counts[error_key] = []

                        storage_counts[error_key].append(entry)
                        total_storage_counts[error_key].append(entry)

                    elif error_type == "fatal":
                        if not error_key in fatal_counts:
                            fatal_counts[error_key] = []
                        if not error_key in total_fatal_counts:
                            total_fatal_counts[error_key] = []

                        fatal_counts[error_key].append(entry)
                        total_fatal_counts[error_key].append(entry)

            # if detail in ["nodes", "runs"]:
            #     self.print_error_counts("database error retries", db_counts)
            #     self.print_error_counts("storage error retries", storage_counts)
            #     self.print_error_counts("fatal errors", fatal_counts)

        # top level counts
        self.next_error_count = 1

        console.print("\nErrors for {}:".format(job_id))
        if len(total_db_counts) + len(total_storage_counts) + len(total_fatal_counts) == 0:
            print("  <no errors found>")
        else:
            self.print_error_counts("fatal errors", total_fatal_counts)
            self.print_error_counts("database error retries", total_db_counts)
            self.print_error_counts("storage error retries", total_storage_counts)

    def gather_node_errors(self, ws_name, job_id, node_index):
        job_path = "nodes/node{}/after/run_errors".format(node_index)
        dirs, path_names = self.store.get_job_filenames(ws_name, job_id, job_path)
        runs_for_node = []

        for pn in path_names:
            pnx = "{}/{}".format(job_path, pn)
            run_json = self.store.read_job_file(ws_name, job_id, pnx)
            run_data = utils.load_json_records(run_json)

            runs_for_node.append(run_data)

        return runs_for_node

    def gather_errors_for_nodes(self, ws_name, job_id, node_index_list, max_workers):
        # gather errors for nodes on worker threads
        next_progress_num = 1
        run_data_list_by_node = {}
        thread_lock = Lock()   

        def thread_worker(indexes, ws_name, job_id):
            for node_index in indexes:
                nonlocal next_progress_num

                runs_for_node = self.gather_node_errors(ws_name, job_id, node_index)

                with thread_lock:
                    node_id = utils.node_id(node_index)
                    run_data_list_by_node[node_id] = runs_for_node

                    node_msg = "  gathering errors from nodes: {}/{}".format(next_progress_num, len(node_index_list))
                    fb.feedback(node_msg, id="node_err_msg")  # , add_seperator=is_last)
                    next_progress_num += 1

        utils.run_on_threads(thread_worker, node_index_list, max_workers, [ws_name, job_id])
        fb.feedback("done", is_final=True)
        return run_data_list_by_node
        
    def print_error_counts(self, name, counts):
        #console.print("\n  {}:".format(name))

        if counts:
            for error_key, entries in counts.items():
                entry = entries[0]
                error_type = entry["error_type"]
                error = entry["error"].strip()
                context = entry["context"].strip()
                traceback_lines = entry["traceback"]

                context_name = "context"

                if error_type == "db":
                    error_type = "retryable database error"
                elif error_type == "storage":
                    error_type = "retryable storage error"
                else:
                    error_type = "fatal error"
                    context_name = "exit code"
                
                run_list = [entry["run_name"] for entry in entries]
                if len(run_list) > 5:
                    count_str = "{} ({}, ...)".format(len(entries), ", ".join(run_list[0:5]))
                else:
                    count_str = "{} ({})".format(len(entries), ", ".join(run_list[0:5]))

                console.print()
                console.print("  ======= #{} ======================================================================================".\
                    format(self.next_error_count))
                self.next_error_count += 1

                console.print("  error: \t{}".format(error))
                console.print("  type: \t{}".format(error_type))
                console.print("  count: \t{}".format(count_str))
                console.print("  {}: \t{}".format(context_name, context))

                if traceback_lines:
                    console.print("  traceback:\t(most recent call last)")
                    for line in traceback_lines:
                        if line.startswith("File "):
                            console.print("    ----------------------------------------------")
                            # file, line, module
                            console.print("    {}".format(line))
                        else:
                            # source code
                            console.print("    {}".format(line))

        # else:
        #     console.print("    <none>")

    #---- VIEW LOG command ----
    @argument(name="target", help="the name of the run or job")
    @option(name="data-name", type="str", help="only show log records that contain the specified data property name")
    @option(name="data-value", type="str", help="only show log records that contain the specified data property name and the specified value")
    @option(name="event", type="str", help="only show log records matching the specified event")
    @option(name="export", type="str", help="will create a tab-separated file for the report contents")
    @flag(name="raw", help="view the log records in their raw form (vs. column report)")
    @option(name="workspace", default="$general.workspace", help="the workspace that the run resides in")
    @example(task="view the log entries for run26 in the curious workspace", text="xt view log curious/run26")
    @command(kwgroup="view", help="view the run log for specified run")
    def view_log(self, target, workspace, export, raw, event, data_name, data_value):

        if job_helper.is_job_id(target):
            # view JOB LOG
            records = self.store.get_job_log(target)
            self.impl_storage_api.log_report(self.client, target, records, view_raw=raw, export=export, 
                event=event, data_name=data_name, data_value=data_value)

        else:
            # view RUN LOG
            #errors.user_error("must specify a run name, job name, or 'controller'")
            ws, run_name, full_run_name = run_helper.validate_run_name(self.store, workspace, target, parse_only=False)
            records = self.store.get_run_log(ws, run_name)

            self.impl_storage_api.log_report(self.client, full_run_name, records, view_raw=raw, export=export, 
                event=event, data_name=data_name, data_value=data_value)

    #---- VIEW METRICS command ----
    @argument(name="runs", type="str_list", help="a comma separated list of runs, jobs, or experiments", required=True)
    @argument(name="metrics", type="str_list", required=False, help="optional list of metric names")
    @option(name="workspace", default="$general.workspace", help="the workspace that the run resides in")
    @option(name="steps", type="int_list", help="show metrics only for the specified steps")
    @option(name="export", type="str", help="will create a tab-separated file for the report contents")
    @flag(name="merge", help="will merge all datasets into a single table")
    @flag(name="clean", default=True, help="when True, removes old metrics from restarted runs")
    @option(name="hparams", type="str_list", help="will list the specified hyperparmeter names and values before the metrics")
    @example(task="view the logged metrics for run153 in the current workspace", text="xt view metrics run153")
    @command(kwgroup="view", help="view the set of logged metrics for specified run")
    def view_metrics(self, runs, workspace, steps, merge, metrics, hparams, export, clean):

        pure_run_list, ws_name = run_helper.expand_run_list(self.store, self.store.database, workspace, runs)
        if not pure_run_list:
            errors.general_error("no matching runs found")

        fd = {"ws_name": ws_name, "run_name": {"$in": pure_run_list}}
        fields = {"_id": 1, "run_name": 1, "node_index": 1, "job_id": 1, "exper_name": 1, "ws_name": 1, "hparams": 1, "log_records": 1}

        run_log_records = self.store.database.get_info_for_runs(ws_name, fd, fields, include_log_records=True)

        store_utils.simplify_records_id(run_log_records)

        for rr in run_log_records:
            console.print("\n{}:".format(rr["_id"]), end="")

            if hparams:
                #console.print("  hyperparameters:")
                rrh = rr["hparams"]
                first_value = True

                for name in hparams:
                    value = utils.safe_value(rrh, name)
                    if first_value:
                        console.print(" (", end="")
                        first_value = False
                    else:
                        console.print(", ", end="")

                    console.print("{}: {}".format(name, value), end="")

                # finish line and skip a line
                if first_value:
                    console.print("\n")
                else:
                    console.print(")\n")
            else:
                console.print("")
 
            # build the metric sets
            log_records = rr["log_records"]
            metric_sets = run_helper.build_metrics_sets(log_records, steps, merge, metrics, clean)
            just_one = len(metric_sets) == 1

            for i, ms in enumerate(metric_sets):
                lb = ReportBuilder(self.config, self.store)

                if export:
                    sep_char = "\t"
                    count = lb.export_records(export, ms["records"], ms["keys"], sep_char)
                    console.print("report exported to: {} ({} rows)".format(export, count-1))
                else:
                    if not just_one:
                        console.print("Dataframe {}:".format(1+i))

                    text, row_count = lb.build_formatted_table(ms["records"], ms["keys"])
                    # indent text 2 spaces on each line
                    text = "  " + text.replace("\n", "\n  ")
                    console.print(text)

    #---- PLOT command ----
    # args, flags, options
    @argument(name="runs", type="str_list", help="a comma separated list of runs, jobs, or experiments", required=True)
    @argument(name="col-list", type="str_list", required=False, help="a comma separated list of metric names to plot")

    @option(name="aggregate", values=["none", "mean", "min", "max", "std", "var", "sem"], help="how to aggregate data from multiple runs into a single plot")
    @option(name="alpha", type=float, default=1, help="the alpha blending factor to plot with")
    @option(name="background-color", type="str", default=None, help="set the background color of all subplots'")
    @option(name="bins", type="int", default=None, help="the number of bins to use for a histogram")
    @option(name="break-on", type="str_list", help="the entity that triggers a plot change: usually 'run', 'node', 'col' or 'group'")
    @option(name="buffer-size", type="int", default=50, help="the number of run records to retreive at a time from cloud storage")
    @flag(name="child", help="only include child runs")
    @flag(name="clean", default=True, help="when True, removes old metrics from restarted runs")
    @option(name="color-indexes", type="int_list", default=None, help="the color indexes to assign to each plotted line")
    @option(name="colors", type="str_list", help="the colors to cycle thru for each trace in a plot")
    @option(name="color-map", type="str", help="the name of a matplotlib color map to use for trace colors")
    @option(name="color-highlight", type="str", default="$plots.color-highlight", help="specifies how to highlight a legend line: set to bold, italic, or matplotlib color")
    @option(name="color-steps", type="int", default=10, help="the number of steps in the color map")
    @option(name="error-bars", values=["none", "std", "var", "sem"], help="value to use for error bars")
    @option(name="filter", type="prop_op_value", multiple=True, help="a list of filter expressions used to include matching runs")
    @option(name="first", type=int, help="limit to the first N runs")
    @option(name="grid-color", type="str", default=None, help="set the grid color of all subplots'")
    @option(name="group-by", required=False, values=["run", "node", "job", "experiment", "workspace"], help="the column to group data by (for --aggregate option) ")
    @option(name="height", type=float, default=10, help="the height of the plot figure in inches")
    @option(name="highlight", type=str, default="$plots.highlight", help="set to '$alive' to highlight legend text of alive runs/jobs/nodes/experiments ")
    @option(name="last", type=int, help="limit to the last N items")
    @option(name="layout", help="specifies how the plots should be layed out, e.g., '2x3'")
    @option(name="legend-args", type="named_arg_list", help="a list of name=value arguments to pass to the matplotlib legend object")
    @option(name="legend-suffix", type=str, help="add the text to the end of each legend title (can contain $run, $job, etc.)")
    @option(name="legend-titles", type="str_list", help="the titles to show in the legends of each plot")
    @option(name="line-sizes", type="num_list", default=[1], help="the line width to be used for each line plotted")
    @option(name="line-styles", type="str_list", default=None, help="the line style to be used for each line plotted")
    @option(name="margins", type=str, default=None, help="the margins for the X and Y axes")
    @option(name="max-traces", type=int, default=64, help="the maximum number of plot traces to draw")
    @option(name="max-workers", type=int, default="$database.max-log-workers", help="the maximum number of background workers for reading log records")
    @option(name="metric-aliases", type="str_list", help="alternate names for each metric in subset of runs")
    @flag(name="outer", help="only include outer (top) level runs")
    @flag(name="parent", help="only include parent runs")
    @option(name="plot-args", type="named_arg_list", help="a list of name=value arguments to pass to the matplotlib plot object")
    @option(name="plot-titles", type="str_list", help="the titles to display on the plots")
    @option(name="plot-type", default="line", values=["line", "bar", "scatter", "histogram"], help="the type of plot to produce")
    @flag(name="reverse", help="reverse the sorted items")
    @option(name="save-to", help="path to file to which the plot will be saved")
    @option(name="shadow-alpha", type=float, default=.2, help="the alpha blending factor used to draw the plot shadow ")
    @option(name="shadow-type", default="none", values=["none", "pre-smooth", "min-max", "std", "var", "sem"], help="the type of plot shadow to draw")
    @flag(name="show-legend", default=True, help="controls if the legend is shown")
    @flag(name="show-plot", default=True, help="specifies if plot should be displayed")
    @flag(name="show-toolbar", default=True, help="controls if the matplotlib toolbar is shown")
    @option(name="skip", type=int, default=0, help="number of runs to skip in returned results")
    @option(name="smoothing-factor", type="float", help="the smoothing factor to apply to values before plotting (0.0-1.0)")
    @option(name="source", default="metrics", values=["metrics", "runs", "nodes", "jobs"], help="the source of the data for plotting")
    @option(name="sort", default="$run-reports.sort", help="the name of the run column to use in sorting the sub-plots")
    @option(name="style", values=["darkgrid", "whitegrid", "dark", "white", "ticks", "none"], default="darkgrid", help="the seaborn plot style to use")
    @option(name="tags-all", type="str_list", help="matches runs containing all of the specified tags")
    @option(name="tags-any", type="str_list", help="matches runs containing any of the specified tags")
    @option(name="timebase", values=["none", "run", "metric"], default="metric", help="relative __time__ column adjustment for plotting on x axis")
    @option(name="timeout", type=float, help="the maximum number of seconds the window will be held open")
    @option(name="title", type="str", help="the title to use for the set of plots")
    @option(name="width", type=float, default=16, help="the width of the plot figure in inches")
    @option(name="workspace", default="$general.workspace", help="the workspace for the runs to be displayed")
    @option(name="x", default=None, help="the metric to use for plotting along the x axis")
    @option(name="x-format", type="str", help="python format string for formatting x axis label values")
    @flag(name="x-int", default=None, help="when true, forces x ticks/labels to be integer values")
    @option(name="x-label", default=None, help="the label to display on the x axis")
    @option(name="x-labels-col", default=None, help="the col used to display labels along the x axis")
    @option(name="x-max", type="float", default=None, help="set the upper value of the x-axis")
    @option(name="x-min", type="float", default=None, help="set the lower value of the x-axis")
    @option(name="x-share", default="all", values=["none", "all", "row", "col"], help="specifies which subplots share the x axis")
    @option(name="y-format", type="str", help="python format string for formatting y axis label values")
    @flag(name="y-int", default=None, help="when true, forces y ticks/labels to be integer values")
    @option(name="y-label", default=None, help="the label to display on the y axis")
    @option(name="y-max", type="float", default=None, help="set the upper value of the y-axis")
    @option(name="y-min", type="float", default=None, help="set the lower value of the y-axis")
    @option(name="y-ticks", type="num_list", default=None, help="set the position values for y-axis tick marks")
    @option(name="y-share", default="row", values=["none", "all", "row", "col"], help="specifies which subplots share the y axis")

    # plot attribute options
    # @option(name="cap-size", type=float, default=5, help="the size of cap on the error bars")
    # @option(name="edge-color", type=str, help="the color of the edges of the marker")
    # @option(name="marker-shape", type=str, help="the marker shape to plot with")
    # @option(name="marker-size", type=float, default=2, help="the size of the markers drawn on the plot")

    @see_also("XT Plotting", "plotting")
    @example(task="plot the specified metrics for the specified runs, with a new plot for each run, in a 2x3 grid of plots", 
        text="xt plot run2264.1-run2264.6  train-acc, test-acc --break=run --layout=2x3", image="../images/plot2x3.png")
    @command(help="plot the logged metrics for specified runs in a matrix of plots")
    
    # command
    def plot(self, runs, col_list, x, layout, break_on, title, show_legend, plot_titles, legend_titles, 
        smoothing_factor, workspace, timeout, aggregate, shadow_type, shadow_alpha, style, 
        show_toolbar, max_traces, group_by, error_bars, show_plot, save_to, 
        x_label, x_labels_col, y_label, legend_args, plot_args, colors, color_map, color_steps, x_min, x_max, y_min, y_max, 
        sort, reverse, alpha, color_indexes, line_styles, line_sizes, timebase, x_format, y_format, buffer_size, 
        x_share, y_share, background_color, grid_color, clean, width, height, 
        first, last, skip, tags_any, tags_all, filter, highlight, color_highlight, legend_suffix, 
        max_workers, x_int, y_int, child, outer, parent, bins, source, margins, metric_aliases, 
        plot_type, y_ticks):

        calc_exps = {}

        # fixup line styles
        if line_styles and len(line_styles)==1 and "," in line_styles[0]:
            # user specified the list as a single string
            line_styles = line_styles[0].split(",")
            line_styles = [style.strip() for style in line_styles]

        # do we need any nested properties (hparams, tags)?
        sd = {}

        for nest in ["hparams", "tags"]:
            for col in col_list:
                if col.startswith(nest + "."):
                    sd[nest] = 1

        if source == "metrics":
            if "hparams" in sd:
                errors.general_error("cannot mix plot source type and columns between std/hparam/metrics: {}".format(col_list))

        default_max_runs = 50  
        if not first and not last:
            first = default_max_runs

        # refer to it by clearer name
        x_col = x

        if x_col is None:
            # provide default column name for x_col
            if source == "metrics":
                x_col = self.config.get("general", "step-name")

        qfe.set_explicit_options({"parent": False})

        if parent is None and source == "metrics":
            parent = False 

        # build args for "list runs" type of run retrieval 
        # NOTE: we filter our parent runs since they contain no reported metrics
        args = {"run_list": runs, "workspace": workspace, "all": True, 
            "child": child, "outer": outer, "parent": parent, 
            "sort": sort, "reverse": reverse, "first": first, "last": last, 
            "skip": skip, "tags_any": tags_any, "tags_all": tags_all, "filter": filter, 
            "columns": ["run", "metrics.*"], "buffer_size": buffer_size }

        self.store.set_max_workers(max_workers)
        
        # store col names used here
        col_dict = {"run_name": 1, "node_index": 1, "job_id": 1, "exper_name": 1, "ws_name": 1, 
            "search_style": 1, "tags": 1}

        if source == "nodes":
            col_dict["node_name"] = 1

        title, legend_vars = self.build_legend_title_vars(legend_titles, title)
        self.next_name_num = 1

        if source == "metrics":
            col_dict["log_records"] = 1

        if True:    # else:

            if source != "metrics":
                # add y cols (specified std or hparams.*) to requested fields
                for i, col in enumerate(col_list):
                    col_name = self.parse_calc_expression(col_dict, calc_exps, col)
                    col_list[i] = col_name
                
                # add x_col to requested fields
                if x_col:
                    x_col = self.parse_calc_expression(col_dict, calc_exps, x_col)

                if x_labels_col:
                    x_labels_col = self.parse_calc_expression(col_dict, calc_exps, x_labels_col)

                # add break_on to requested fields
                if break_on:
                    for i, col in enumerate(break_on):
                        if not col in ["run", "col", "group", "node"]:
                            col_name = self.parse_calc_expression(col_dict, calc_exps, col)
                            break_on[i] = col_name

            # add group by to requested fields
            if group_by:
                group_by = self.parse_calc_expression(col_dict, calc_exps, group_by)

            # add legend_vars to requested fields
            for i, lv in enumerate(legend_vars):
                var_name = self.parse_calc_expression(col_dict, calc_exps, lv)
                legend_vars[i] = var_name

        if source == "nodes":
            # nodes
            args["node_list"] = args["run_list"]
            args["columns"] = col_dict

            records, using_default_last, user_to_actual, available, builder = \
                node_helper.get_list_nodes_records(self.store, self.config, args)
        else:
            # runs or metrics            
            records, using_default_last, user_to_actual, available, builder, last, std_cols_desc = \
                run_helper.get_filtered_sorted_limit_runs(self.store, self.config, False, col_dict=col_dict, 
                preserve_order=True, col_names_are_external=False, flatten_records=False, args=args)

        # now, replace any hparams.xxx in col names with hparams_xxx
        for nest in ["hparams", "tags"]:
            have_nest = False
            nest_dot = nest + "."
            nest_under = nest + "_"
            nest_len = len(nest)

            for i, col in enumerate(col_list):
                if col.startswith(nest_dot):
                    col = nest_under + col[nest_len:]
                    col_list[i] = col
                    have_nest = True

            if x_col and x_col.startswith(nest_dot):
                x_col = nest_under + x_col[1+nest_len:]
                have_nest = True

            if x_labels_col and x_labels_col.startswith(nest_dot):
                x_labels_col = nest_under + x_labels_col[1+nest_len:]
                have_nest = True

            if group_by and group_by.startswith(nest_dot):
                group_by = nest_under + group_by[1+nest_len:]
                have_nest = True

            for i, var in enumerate(legend_vars):
                if var.startswith(nest_dot):
                    var = nest_under + var[1+nest_len:]
                    legend_vars[i] = var
                    have_nest = True

            # now fixup records the same way
            for record in records:
                if have_nest:
                    self.fixup_nest(record, nest)

                self.add_calc_expressions(calc_exps, record)

        record_count = len(records)
        if record_count == default_max_runs:
            console.print("plotting first {} runs (use --first or --last to override)".format(default_max_runs))

        # metric string will later contain calculated expressions
        if not col_list:
            col_list = []

        if source == "nodes":
            obj_names = [rlr["node_name"] for rlr in records]
        else:
            obj_names = [rlr["run_name"] for rlr in records]

        # CAREFUL: must match order of plotbuilder __init__  params
        pb = plot_builder.PlotBuilder(self.store, obj_names, col_list, x_col, layout, break_on, title, 
            show_legend, plot_titles, legend_titles, smoothing_factor, plot_type, timeout, aggregate, 
            shadow_type, shadow_alpha, records, style, show_toolbar, max_traces, 
            group_by, error_bars, show_plot, save_to, x_label, x_labels_col,
            y_label, colors, color_map, color_steps, legend_args, 
            x_min, x_max, y_min, y_max, alpha, color_indexes, line_styles, line_sizes, timebase, x_format, y_format, 
            x_share, y_share, background_color, grid_color, clean, width, height, highlight, color_highlight,
            legend_suffix, source, x_int, y_int, bins, legend_vars, margins, metric_aliases, y_ticks,
            plot_args)

        pb.build()

    def add_calc_expressions(self, calc_exps, record):
        for ce_name, ce_exp in calc_exps.items():
            value = None
            try:
                value = eval(ce_exp, record)
            except BaseException as ex:
                # for now, allow any errors
                pass

            record[ce_name] = value

    def get_run_or_job_column_name(self, user_name):
        '''
        job_info and run_info tables have a set of user_friendly names that map 
        to actual column names used by the database system.  
        if user_name arg is one of these, this will return the column name, 
        otherwise we assume user_name is another property.
        '''
        col_name = job_helper.get_job_property_internal_name(user_name)
        if not col_name:
            col_name = run_helper.get_run_property_internal_name(user_name)
            if not col_name:
                col_name = user_name

        return col_name

    def parse_calc_expression(self, cd, calc_expressions, exp):
        '''
        Processing:
            - parse a single id or id=expression
            - extract all id's found and store them in cd
            - return the name of the single id or the left-hand id 
        '''
        ce_name = None
        is_calc_exp = False
        first_id = None

        if "=" in exp:
            ce_name, exp = exp.split("=", 1)
            is_calc_exp = True

        # parse exp to extract id's used into cd
        scanner = Scanner(exp)

        while scanner.scan(allow_extended_ids=False):
            if scanner.token_type == "id":
                col_name = self.get_run_or_job_column_name(scanner.token)
                cd[col_name] = 1
                if not first_id:
                    first_id = scanner.token
            else:
                is_calc_exp = True

        if is_calc_exp:
            # if no name= was specified, use a generated name
            if not ce_name:
                ce_name = "calc_exp" + str(self.next_name_num)
                self.next_name_num += 1

            # replace nested reference with underscore
            exp = exp.replace(".", "_")

            calc_expressions[ce_name] = exp
        else:
            if not ce_name:
                ce_name = first_id

        return ce_name

    def fixup_nest(self, record, nest):

        if nest in record:
            # flatten nested dict
            nd = record[nest]
            for key, value in nd.items():
                flat_key = nest + "_" + key
                record[flat_key] = value
            del record[nest]
        else:
            # rename "foo.bar" vars to "foo_bar"
            nest_dot = nest + "."
            key_list = list(record)

            for key in key_list:
                if key.startswith(nest_dot):
                    new_key = key.replace(".", "_")
                    utils.rename_dict_key(record, key, new_key) 

    def build_legend_var(self, vars, text):
        new_text = ""
        parts = text.split("@")

        if len(parts) > 2:
            # contains 1 or more @xxx@ entries

            while len(parts) >= 2:
                left = parts.pop(0)
                var_name = parts.pop(0)
                
                # update @xx@ with var index
                var_index = len(vars)
                vars.append(var_name)
                new_text += "{}@{}@".format(left, var_index)

            new_text += parts.pop()
        return new_text

    def build_legend_title_vars(self, legend_titles, title):
        vars = []

        if legend_titles:
            for i, text in enumerate(legend_titles):
                legend_titles[i] = self.build_legend_var(vars, text)

        if title:
            title= self.build_legend_var(vars, title)

        return title, vars

    #---- EXTRACT command ----
    @argument(name="runs", type="str_list", help="a comma separated list of runs, jobs, or experiments", required=True)
    @argument(name="dest-dir", help="the path of the outpt directory where job/run subdirs will be created")
    @flag(name="browse", help="specifies that an folder window should be opened for the dest_dir after the extraction has completed")
    @option(name="workspace", default="$general.workspace", help="the workspace that the runs resides in")
    @option("response", default=None, help="the response to be used to confirm the job/run subdir deletion")
    @example(task="extract files from curious/run26 to c:/runs", text="xt extract curious/run26 c:/runs")
    @command(help="download all files associated with the job or run to the specified directory")
    def extract(self, runs, dest_dir, workspace, response, browse):

        console.print("extracting files for: {}...".format(runs))
        extract = True
        others_dict = {}

        if extract:

            # first, determine nodes to be added to dest_dir
            nodes = "run"   # default

            for name_entry in runs:
                if job_helper.is_job_id(name_entry):
                    # if we find at least 1 job name specified, output to dest_dir/jobNNN/runNNN
                    if not nodes == "exper":
                        nodes = "job"
                elif not run_helper.is_run_name(name_entry):
                    # if we find at least 1 experiment, output to dest_dir/experFoo/jobNNN/runNNN
                    # this takes priority over all other nodes values
                    nodes = "exper"
            
            # convert list of runs, jobs, experiments into a list of runs
            pure_run_list, actual_ws = run_helper.expand_run_list(self.store, self.store.database, workspace, runs)

            overwrite_confirmed = {}    # names user has approved for overwritting
            answer = None

            # process by run (but include any node info)
            for run_name in pure_run_list:

                if "/" in run_name:
                    run_name = run_name.split("/")[-1]

                if nodes == "exper":
                    # get exper_name and job_id of run
                    record = self.store.database.get_info_for_runs(actual_ws, {"_id": run_name}, {"job_id": 1, "exper_name": 1})
                    job_id = utils.safe_cursor_value(record, "job_id")
                    exper_name = utils.safe_cursor_value(record, "exper_name")
                    
                    actual_dest_dir = "{}/{}/{}/{}".format(dest_dir, exper_name, job_id, run_name)
                    overwrite_dir = "{}/{}".format(dest_dir, exper_name)    # exper name

                elif nodes == "job":
                    # get job_id of run
                    id = store_utils.make_id(actual_ws, run_name)
                    record = self.store.database.get_info_for_runs(actual_ws, {"_id": id}, {"job_id": 1})
                    job_id = utils.safe_cursor_value(record, "job_id")

                    actual_dest_dir = "{}/{}/{}".format(dest_dir, job_id, run_name)
                    overwrite_dir = os.path.dirname(actual_dest_dir)    # job dir

                else:
                    # run_name only
                    actual_dest_dir = "{}/{}".format(dest_dir, run_name)
                    overwrite_dir = actual_dest_dir    # run dir
                    
                if os.path.exists(overwrite_dir) and not overwrite_dir in overwrite_confirmed:
                    # get user permission to overwrite this dir
                    msg = "'{}' already exists; OK to delete? (d=delete, a=delete all, s=skip, c=cancel): ".format(overwrite_dir)
                    if response:
                        answer = response
                        console.print(msg + str(answer))
                    elif answer == "a":
                        console.print(msg + str(answer))
                    else:
                        answer = "xx"
                        # get a valid answer from user
                        while not answer in "dasc":
                            answer = pc_utils.input_response(msg, response)

                    if answer == "s":
                        continue
                    elif answer == "c":
                        break
                    elif answer in ["d", "a"]:
                        shutil.rmtree(overwrite_dir)
                        overwrite_confirmed[overwrite_dir] = 1

                # download files for run (and unzip as needed)
                files = capture.download_run(self.store, actual_ws, run_name, actual_dest_dir, others_dict)
                console.print("  {} files downloaded to: {}".format(len(files), actual_dest_dir))

            if browse:
                if pc_utils.is_windows():
                    os.startfile(dest_dir)
                else:
                    subprocess.Popen(['xdg-open', dest_dir])


    #---- EXTRACT LOGS command ----
    @argument(name="name", type="str", help="the name of the run or job to get logs for", required=True)
    @argument(name="dest-dir", help="the path of the directory where logs will be copied")
    @flag(name="browse", help="specifies that an folder window should be opened for the dest_dir after the extraction has completed")
    @option(name="type", arg_name="log_type", default="all", values=["service", "xt", "all"], help="download logs from the backend service for specified run")
    @option(name="workspace", default="$general.workspace", help="the workspace that the runs resides in")
    @option("response", default=None, help="the response to be used to confirm the directory deletion")
    @option("node-index", default=0, type=int, help="when a job id is specified, this is used to identify the compute node whose logs are being requested")
    @example(task="extract logs from curious/run26 to my_logs dir", text="xt extract logs run26 my_logs --workspace=curious")
    @command(help="download all logs associated with the run to the specified directory")
    def extract_logs(self, name, node_index, dest_dir, workspace, response, browse, log_type):
        
        console.print("extracting log files for: {}...".format(name))
        extract = True

        if run_helper.is_run_name(name):
            job_id, node_index = run_helper.get_job_node_index(self.store, self.core, workspace, name)
        elif job_helper.is_job_id(name):
            job_id = name
        else:
            errors.general_error("expected a run name or a job id for the 'name' argument (but found: {})".format(name))

        # ensure dest_dir is clean
        if os.path.exists(dest_dir):
            answer = pc_utils.input_response("'{}' already exists; OK to delete? (y/n): ".format(dest_dir), response)
            if answer != "y":
                extract = False

        if extract:
            # download files to dest_dir
            file_utils.ensure_dir_clean(dest_dir)

            items = []

            if log_type in ["service", "all"]:
                # service logs 
                log_dir = dest_dir + "/service_logs"
                job_helper.download_logs_from_storage(workspace, self.store, items, 
                    job_id, node_index, store_path="after/service_logs/**", dest_dir=log_dir)

            if log_type in ["xt", "all"]:
                # xt logs
                log_dir = dest_dir + "/xt_logs"
                job_helper.download_logs_from_storage(workspace, self.store, items, 
                    job_id, node_index, store_path="after/xt_logs/**", dest_dir=log_dir)

            count = len(items) if items else 0
            console.print("  {} files downloaded to: {}".format(count, dest_dir))

    #---- CLEAR CREDENTIALS command ----
    @example(task="clears the XT authentication credentials cache", text="xt clear credentials")
    @command(kwgroup="clear", kwhelp="clears the specified object", help="clears the XT credentials cache")
    def clear_credentials(self):
        cc = CacheClient()
        response = cc.terminate_server()

        if response:
            console.print("XT cache server cleared")
        else:
            console.print("XT cache was not active")

    # ---- PLOT SUMMARY command ----
    @argument(name="aggregate-name", help="the name of the job or experiment where run have been aggregated (hyperparameter search)")
    @option(name="workspace", default="$general.workspace", help="the workspace that the experiment resides in")
    @option(name="timeout", type=float, help="the maximum number of seconds the window will be held open")
    @option(name="primary-metric", type=str, help="the name of the metric to explore")
    @flag(name="maximize-metric", help="True if the primary metric should be maximized; False if it should be minimized")
    @option("max-workers", default="$general.max-run-workers", type=int, help="the maximum number of background workers used to gather run summaries")
    @option("max-runs", default=0, type=int, help="the maximum number of completed runs to be considered. Later runs are ignored. Default is 0 for all runs.")
    @flag("show_single_valued_hps", default=False, help="when True, HPs with only a single search value are also included in the report.")
    @flag("verbose", default=False, help="when True, extra output is printed to the console for debugging.")
    @flag("use-azure-storage", default=False, help="when True, run results are pulled from Azure Storage instead of SQL DB (the default).")
    @example(task="plot a summary of hp search from job5002", text="xt plot summary job5002")
    @command(help="plot runset summary of hyperparameter search")
    def plot_summary(self, aggregate_name, workspace, timeout, primary_metric, maximize_metric, max_workers, max_runs, show_single_valued_hps, verbose, use_azure_storage):

        dest_name = aggregate_name
        aggregate_dest = "job" if job_helper.is_job_id(dest_name) else "experiment"

        hp_config_path = search_helper.get_hp_config_path(self.store, workspace, 
            aggregate_dest, aggregate_name)

        if aggregate_dest == "job" and (primary_metric is None or maximize_metric is None):
            # read primary-metric and maximize-metric values from job's context (MRC) file
            mrc_data = run_helper.get_job_context(self.store, aggregate_name, workspace)
            context_by_nodes = mrc_data["context_by_nodes"]
            node0 = context_by_nodes["node0"]
            runs = node0["runs"]
            run0 = runs[0]

            if primary_metric is None:
                primary_metric = run0["primary_metric"] 

            if maximize_metric is None:
                maximize_metric = run0["maximize_metric"] 

        search_history = SearchHistory(agg_name=aggregate_name, workspace=workspace, timeout=timeout, primary_metric=primary_metric, maximize_metric=maximize_metric,
            show_single_valued_hps=show_single_valued_hps, hp_config_file_name=hp_config_path, max_workers=max_workers, max_runs=max_runs, xt_config=self.config, 
            verbose=verbose, use_azure_storage=use_azure_storage)
            
        search_history.evaluate()

    #---- EXPLORE command ----
    @argument(name="aggregate-name", help="the name of the job or experiment where run have been aggregated (hyperparameter search)")
    @option(name="cache-dir", default="$hyperparameter-explorer.hx-cache-dir", help="the local directory used to cache the Hyperparameter Explorer runs")
    #@option(name="search-rollup", default="$hyperparameter-search.search-rollup", help="the name of the aggregate function to apply to the primary metric values within a run")
    @option(name="workspace", default="$general.workspace", help="the workspace that the experiment resides in")
    @option(name="timeout", type=float, help="the maximum number of seconds the window will be held open")

    # hyperparameter-explorer hyperparameter name
    @option(name="steps-name", default="$hyperparameter-explorer.steps-name", help="the name of the steps/epochs hyperparameter")
    @option(name="log-interval-name", default="$hyperparameter-explorer.log-interval-name", help="the name of the log interval hyperparameter")

    # hyperparameter-explorer metric name
    @option(name="primary-metric", default="$general.primary-metric", help="the name of the metric to explore")
    @option(name="step-name", default="$general.step-name", help="the name of the step/epoch metric")
    @option(name="time-name", default="$hyperparameter-explorer.time-name", help="the name of the time metric")
    @option(name="success-rate-name", default="$hyperparameter-explorer.success-rate-name", help="the name of the success rate metric")
    @option(name="sample-efficiency-name", default="$hyperparameter-explorer.sample-efficiency-name", help="the name of the sample efficiency metric")

    @example(task="explore the results of all runs from job2998", text="xt explore job2998")
    @command(help="run the Hyperparameter Explorer on the specified job or experiment")
    def explore(self, aggregate_name, workspace, cache_dir, steps_name, log_interval_name, 
        primary_metric, step_name, time_name, success_rate_name, sample_efficiency_name, timeout): 
    
        # we need to respond to the job or experiment name user has specified
        dest_name = aggregate_name
        aggregate_dest = "job" if job_helper.is_job_id(dest_name) else "experiment"

        hp_config_path = search_helper.get_hp_config_path(self.store, workspace, aggregate_dest, aggregate_name)

        #console.print("found hp-hp_config_path file: ", hp_config_path)

        # plotted_metric is the Y axis for big HX plot
        plotted_metric = primary_metric    # default value

        if job_helper.is_job_id(dest_name):
            job_ws = workspace
            if job_ws:
                console.diag("{} found in ws={}".format(dest_name, job_ws))

            # See if this job has tags for metric names needed by HX.
            filter_dict = {"job_id": dest_name}
            fields_dict = {"tags.plotted_metric": 1, "tags.primary_metric": 1, "tags.step_name": 1}
            records = self.store.database.get_info_for_jobs(workspace, filter_dict, fields_dict)
            tags = utils.safe_cursor_value(records, "tags")
            value = utils.safe_value(tags, "plotted_metric")
            if value:
                plotted_metric = value
            value = utils.safe_value(tags, "primary_metric")
            if value:
                primary_metric = value
            value = utils.safe_value(tags, "step_name")
            if value:
                step_name = value

        hx = HyperparameterExplorer(
            store=self.store,
            ws_name=workspace,
            run_group_type=dest_name,
            run_group_name=aggregate_dest,
            hp_config_cloud_path=hp_config_path,
            hp_config_local_dir=cache_dir,
            plot_x_metric_name=step_name,
            plot_y_metric_name=plotted_metric,
            hist_x_metric_name=primary_metric)
        hx.run(timeout)

    #---- VIEW BLOB command ----
    @argument(name="path", help="the relative or absolute store path to the blob)")
    @option(name="share", help="the share name that the path is relative to")
    @option(name="workspace", default="$general.workspace", help="the workspace name that the path is relative to")
    @option(name="job", help="the job id that the path is relative to")
    @option(name="run", help="the run name that the path is relative to")
    @option(name="experiment", help="the experiment that the path is relative to")
    @example(task="display the contents of the specified file from the 'after' snapshot for the specified run", text="xt view blob after/output/userapp.txt --run=curious/run14")
    @command(kwgroup="view", kwhelp="view the specified storage item", help="display the contents of the specified storage blob")
    def view_blob(self, path, share, workspace, job, experiment, run):

        use_blobs = True
        fs = self.impl_storage_api.create_file_accessor(use_blobs=True, share=share, ws_name=workspace, 
            exper_name=experiment, job_name=job, run_name=run)

        text = fs.read_file(path)

        console.print("contents of " + path + ":")
        console.print()
        console.print(text)

    #---- VIEW WORKSPACE command ----
    @option(name="workspace", default="$general.workspace", help="the name of the workspace to use")
    @example("xt view workspace", task="display information about the current workspace")
    @command(kwgroup="view", help="display information about the current or specified workspace")
    def view_workspace(self, workspace):
        # for now, its just an echo of your CURRENT (or specified) workspace name
        store_name = self.config.get("store")

        console.print("  workspace: {}".format(workspace))
        console.print("  store: {}".format(store_name))

    #---- VIEW PORTAL command ----
    @argument(name="target-name", help="the name of the target whose portal is to be opened")
    # @option(name="job", help="the name of the job to navigate to in the portal")
    # @option(name="experiment", default="$general.experiment", help="the name of the experiment to use")
    # @option(name="run-name", help="the name of the run to navigate to in the portal")
    # @option(name="workspace", default="$general.workspace", help="the workspace for the run")
    @option("cluster", help="the name of the Philly cluster to be used")
    @option("vc", help="the name of the Philly virtual cluster to be used")
    @flag("browse", help="specifies that the URL should be opened in the user's browser")
    @example("xt view portal aml --experiment=exper5", task="view the AML portal for exper5")
    @command(kwgroup="view", help="display or browse the URL for the specified backend service portal")
    def view_portal(self, target_name, cluster, vc, browse):

        # get service dict from target name
        service = self.config.get_external_service_from_target(target_name)

        service_name = service["name"]
        service_type = service["type"]

        if service_type == "aml":
            subscription_id = service["subscription-id"]
            resource_group = service["resource-group"]

            url = "https://ml.azure.com/experiments?wsid=/subscriptions/{}/resourcegroups/{}/workspaces/{}".format(\
                subscription_id, resource_group, service_name)

        elif service_type == "itp":
            subscription_id = service["subscription-id"]
            resource_group = service["resource-group"]

            url = "https://ml.azure.com/experiments?wsid=/subscriptions/{}/resourcegroups/{}/workspaces/{}".format(\
                subscription_id, resource_group, service_name)

        elif service_type == "philly":
            username = self.config.expand_system_symbols("$username")
            if not cluster:
                target = self.config.get_target_def(target_name)
                cluster = target["cluster"]

            url = "https://philly/#/jobSummary/{}/all/{}".format(cluster, username)

        elif service_type == "batch":
            url = '"" "C:\\Program Files\\BatchExplorer\\BatchExplorer.exe"'

        else:
            errors.syntax_error("Unrecognized service_type: " + service_type)

        if browse:
            import webbrowser
            webbrowser.open(url)
        else:
            console.print("the portal url: {}".format(url))

    #---- VIEW EXPERIMENT command ----
    @option(name="experiment", default="$general.experiment", help="the name of the experiment to use")
    @flag(name="portal", help="specifies that the backend portal for the job should be opened")
    @example("xt view experiment", task="display information about the current experiment")
    @command(kwgroup="view", help="display information about the current or specified experiment")
    def view_experiment(self, experiment, portal):
        # for now, its just an echo of your CURRENT (or specified) workspace name
        console.print("experiment: {}".format(experiment))

    #---- VIEW STORE command ----
    @argument(name="name", default="$store", required=False, help="the name of the store to view")
    @example("xt view store dilbert", task="show information about the specified store")
    @command(kwgroup="view", help="display information about the current or specified store")
    def view_store(self, name):
        # for now, its just an echo of your CURRENT (or specified) store
        ss_info = self.config.get_store_info(name)

        ss_info = dict(ss_info)    # make copy we can change
        name = ss_info["name"]
        del ss_info["name"]

        console.print("store {}: {}".format(name, ss_info))

    #---- LIST STORES command ----
    @example("xt list stores", task="show the stores defined in the xt config file")
    @command(kwgroup="list", help="show the stores defined in the xt config file")
    def list_stores(self):
        stores = self.config.get("stores")

        console.print("stores:")
        for name, store in stores.items():
            console.print("  {}: {}".format(name, store))

    #---- LIST RUNS command ----
    @argument(name="run-list", type="str_list", help="a comma separated list of: run names, name ranges, or wildcard patterns", required=False)
    @option(name="buffer-size", type="int", default=50, help="the number of run records to retreive at a time from cloud storage")
    @option(name="workspace", default="$general.workspace", help="the workspace for the runs to be displayed")
    @option(name="job", type="str_list", help="a list of jobs names (acts as a runs filter)")
    @option(name="experiment", type="str_list", help="a list of experiment names (acts as a runs filter)")
    #@option(name="application", help="the application name for the runs to be displayed (acts as a filter)")
    @option(name="box", type="str_list", help="a list of boxes on which the runs were running (acts as a filter)")
    @option(name="target", type="str_list", help="a list of compute targets used by runs (acts as a filter)")
    @option(name="service-type", type="str_list", help="a list of back services on which the runs executed (acts as a filter)")

    # report options 
    @flag(name="all", help="don't limit the output; show all records matching the specified filters")
    @option(name="add-columns", type="str_list", help="list of columns to add to those in config file")
    @flag(name="count", default="$run-reports.count", help="returns the number of runs being retrieved at the top of the report")
    @option(name="first", type=int, help="limit the output to the first N items")
    @option(name="last", type=int, default="$run-reports.last", help="limit the output to the last N items")
    @option(name="filter", type="prop_op_value", multiple=True, help="a list of filter expressions used to include matching records")
    @option(name="skip", type=int, default=0, help="number of runs to skip before returning results")
    @option(name="tag", type="str", help="matches records containing the specified tag")
    @option(name="tags-all", type="str_list", help="matches records containing all of the specified tags")
    @option(name="tags-any", type="str_list", help="matches records containing any of the specified tags")
    @option(name="group", default="$run-reports.group", help="the name of the column used to group the report tables")
    @flag(name="number-groups", default="$run-reports.number-groups", help="the name of the column used to group the report tables")
    @option(name="sort", default="$run-reports.sort", help="the name of the report column to use in sorting the results")
    @option(name="max-width", type=int, default="$run-reports.max-width", help="set the maximum width of any column")
    @option(name="precision", type=int, default="$run-reports.precision", help="set the number of factional digits for float values")
    @option(name="columns", type="str_list", help="specify list of column names, or the name of a named-columns entry in the XT config file")
    @option(name="export", type="str", help="will create a tab-separated file for the report contents")
    @option(name="status", type="str_list", default="$run-reports.status", 
        values= ["created", "allocating", "queued", "spawning", "running", "completed", "error", "cancelled", "aborted", "unknown"], 
        help="match runs whose status is one of the values in the list")
    @option(name="username", type="str_list", help="a list of usernames to filter the runs")

    # report flags
    @flag(name="flat", help="do not group runs")
    @flag(name="reverse", help="reverse the sorted items")
    #@flag(name="boxout", help="only list the latest run record for each box")
    @flag(name="parent", help="specifies if parent runs should be listed (default: None)")
    @flag(name="child", help="only list child runs")
    @flag(name="outer", help="only outer (top) level runs")
    @flag(name="available", help="show the columns (std, hyperparameter, metrics) available for specified runs")

    # examples
    @example("xt list runs", task="display a runs report for the current workspace")
    @example("xt list runs run302.*", task="display the child runs for run302")
    @example("xt list runs --job=job2998 --last=10 --sort=metrics.test-acc", task="display the runs of job132, sorted by the metric 'test-acc', showing only the last 10 records")
    @example("xt list runs --status=error", task="display the runs that were terminated due to an error")
    @example("xt list runs --filter='epochs > 100'", task="only display runs that have run for more than 100 epochs")
    @faq("how can I find out which columns are available", "use the --available flag")
    @faq("why do some runs show their status as 'created', even though they have completed", "runs that are executed in direct mode, on a service backend without using the XT controller, do not always update the XT database correctly")
    @see_also("Using the XT CLI", "cmd_options")
    @command(kwgroup="list", pass_by_args=True, user_filters=True, help="displays a run report for the specified runs")
    def list_runs(self, args):
        '''
        This command is used to display a tabular report of runs.  
        
        The columns shown can be customized by the run-reports:column entry in the XT config file.  In addition to specifying which columns to display, 
        you can also customize the appearance of the column header name and the formatting of the column value.  Examples:

            - To display the hyperparameter "discount_factor" as "discount", specify the column as "discount_factor=factor".
            - To display the value for the "steps" metric with the thousands comma format, specify the column as "steps:,".  
            - To specify the column "train-acc" as "accuracy" with 5 decimal places, specify it as "train-acc=accuracy:.5f".  

        The --filter option can be used to show a subset of all runs in the workspace.  The general form of the filter is <column> <relational operator> <value>. 
        Values can take the form of integers, floats, strings, and the special symbols $true, $false, $none, $empty (which are replaced with the corresponding Python values).

        Examples:
        
            - To show runs where the train-acc metric is > .75, you can specify: --filter="train-acc>.75".
            - To show runs where the hyperparameter lr was == .03 and the test-f1 was >= .95, you can specify the filter option twice: --filter="lr=.03"  --filter="test-f1>=.95"
            - To show runs where the repeat is set to something other than None, --filter="repeat!=$none".
        '''
        return run_helper.list_runs(self.store, self.config, args)

    #---- COMPARE RUNS command ----
    @argument(name="run-list", type="str_list", help="a comma separated list of: run names, name ranges, or wildcard patterns", required=False)
    @option(name="workspace", default="$general.workspace", help="the workspace for the runs to be compared")
    @option(name="job", type="str_list", help="a list of jobs names (acts as a runs filter)")
    @option(name="experiment", type="str_list", help="a list of experiment names (acts as a runs filter)")
    #@option(name="application", help="the application name for the runs to be displayed (acts as a filter)")
    @option(name="box", type="str_list", help="a list of boxes on which the runs were running (acts as a filter)")
    @option(name="target", type="str_list", help="a list of compute targets used by runs (acts as a filter)")
    @option(name="service-type", type="str_list", help="a list of back services on which the runs executed (acts as a filter)")

    # report options 
    @flag(name="all", help="don't limit the output; show all records matching the specified filters")
    @option(name="add-columns", type="str_list", help="list of columns to add to those in config file")
    @flag(name="count", default="$run-reports.count", help="returns the number of runs being retrieved at the top of the report")
    @option(name="first", type=int, help="limit the output to the first N items")
    @option(name="last", type=int, default="$run-reports.last", help="limit the output to the last N items")
    @option(name="filter", type="prop_op_value", multiple=True, help="a list of filter expressions used to include matching records")
    @option(name="skip", type=int, default=0, help="number of runs to skip before returning results")
    @option(name="tags-all", type="str_list", help="matches records containing all of the specified tags")
    @option(name="tags-any", type="str_list", help="matches records containing any of the specified tags")
    @option(name="group", default="$run-reports.group", help="the name of the column used to group the report tables")
    @flag(name="number-groups", default="$run-reports.number-groups", help="the name of the column used to group the report tables")
    @option(name="sort", default="$run-reports.sort", help="the name of the report column to use in sorting the results")
    @option(name="max-width", type=int, default="$run-reports.max-width", help="set the maximum width of any column")
    @option(name="precision", type=int, default="$run-reports.precision", help="set the number of factional digits for float values")
    @option(name="columns", type="str_list", help="specify list of columns to include")
    @option(name="export", type="str", help="will create a tab-separated file for the report contents")
    @option(name="status", type="str_list", default="$run-reports.status", 
        values= ["created", "allocating", "queued", "spawning", "running", "completed", "error", "cancelled", "aborted", "unknown"], 
        help="match runs whose status is one of the values in the list")
    @option(name="username", type="str_list", help="a list of usernames to filter the runs")
    
    # report flags
    @flag(name="flat", help="do not group runs")
    @flag(name="reverse", help="reverse the sorted items")
    #@flag(name="boxout", help="only list the latest run record for each box")
    @flag(name="parent", help="only list parent runs")
    @flag(name="child", help="only list child runs")
    @flag(name="outer", help="only outer (top) level runs")
    @flag(name="available", help="show the columns (std, hyperparameter, metrics) available for specified runs")

    # examples
    @example("xt compare runs job34-job36", task="compares all of the runs for job34, job35, and job36")
    @see_also("Using the XT CLI", "cmd_options")
    @command(kwgroup="compare", pass_by_args=True, help="compare the hyperparameter values for the specified runs")
    def compare_runs(self, args):
        '''
        This command is used to list a tabular report of the hyperparameters whose values differ amont the specified runs.
        '''
        return run_helper.list_runs(self.store, self.config, args, compare=True)

    #---- LIST JOBS command ----
    @argument(name="job-list", type="str_list", required=False, help="a comma separated list of job names, or a single wildcard pattern")
    @flag(name="count", default="$run-reports.count", help="returns the number of jobs being retrieved at the top of the report")
    @option(name="workspace", default="$general.workspace", help="the workspace for the job to be displayed")
    @option(name="experiment", type="str_list", help="a list of experiment names for the jobs to be displayed (acts as a filter)")
    #@option(name="application", help="the application name for the runs to be displayed (acts as a filter)")
    @option(name="target", type="str_list", help="a list of compute target associated with the jobs (acts as a filter)")
    @option(name="status", type="str_list", help="a list of status values associated with the jobs (acts as a filter)")
    @option(name="service-type", type="str_list", help="a list of backend services associated with the jobs (acts as a filter)")

    # report options 
    @flag(name="all", help="don't limit the output; show all records matching the specified filters")
    @option(name="first", type=int, help="limit the output to the first N items")
    @option(name="last", type=int, default="$job-reports.last", help="limit the output to the last N items")
    @option(name="filter", type="prop_op_value", multiple=True, help="a list of filter expressions used to include matching records")
    @option(name="tag", type="str", help="matches records containing the specified tag")
    @option(name="tags-all", type="str_list", help="matches records containing all of the specified tags")
    @option(name="tags-any", type="str_list", help="matches records containing any of the specified tags")
    @option(name="sort", default="$run-reports.sort", help="the name of the report column to use in sorting the results")
    @option(name="max-width", type=int, default="$run-reports.max-width", help="set the maximum width of any column")
    @option(name="precision", type=int, default="$run-reports.precision", help="set the number of factional digits for float values")
    @option(name="add-columns", type="str_list", help="list of columns to add to those in config file")
    @option(name="columns", type="str_list", default="$job-reports.columns", help="specify list of columns to include")
    @option(name="export", type="str", help="will create a tab-separated file for the report contents")
    @option(name="username", type="str_list", help="a list of usernames that started the jobs (acts as a filter)")
    
    # report flags
    @flag(name="reverse", help="reverse the sorted items")
    @flag(name="available", help="show the columns (name, target, search-type, etc.) available for jobs")

    # examples, FAQs
    @example(task="display a report of the last 5 jobs that were run", text="xt list jobs --last=5")
    @see_also("Using the XT CLI", "cmd_options")
    @command(kwgroup="list", pass_by_args=True, help="displays a job report for the specified jobs")
    def list_jobs(self, args):
        '''
        This command is used to display a tabular report of jobs.  
        
        The columns shown can be customized by the job-reports:column entry in the XT config file.  In addition to specifying which columns to display, 
        you can also customize the appearance of the column header name and the formatting of the column value.  Examples:

            - To display the column "job_status" as "status", specify the column as "job_status=status".

        The --filter option can be used to show a subset of all runs in the workspace.  The general form of the filter is <column> <relational operator> <value>. 
        Values can take the form of integers, floats, strings, and the special symbols $true, $false, $none, $empty (which are replaced with the corresponding Python values).

        Examples:
        
            - To show runs where the repeat is set to something other than None, --filter="repeat!=$none".
        '''
        return job_helper.list_jobs(self.store, self.config, args)

    #---- LIST NODES command ----
    @argument(name="node-list", type="str_list", required=False, help="a comma separated list of node or job names")
    @option(name="workspace", default="$general.workspace", help="the workspace for the nodes to be displayed")
    @option(name="experiment", type="str_list", help="a list of experiment names for the jobs to be displayed (acts as a filter)")
    @option(name="status", type="str_list", help="a list of status values associated with the jobs (acts as a filter)")
    @option(name="target", type="str_list", help="a list of compute target associated with the jobs (acts as a filter)")
    #@option(name="application", help="the application name for the runs to be displayed (acts as a filter)")
    #@option(name="service-type", type="str_list", help="a list of backend services associated with the jobs (acts as a filter)")

    # report options 
    @flag(name="all", help="don't limit the output; show all records matching the specified filters")
    @option(name="first", type=int, help="limit the output to the first N items")
    @option(name="last", type=int, default="$job-reports.last", help="limit the output to the last N items")
    @option(name="filter", type="prop_op_value", multiple=True, help="a list of filter expressions used to include matching records")
    @option(name="tag", type="str", help="matches records containing the specified tag")
    @option(name="tags-all", type="str_list", help="matches records containing all of the specified tags")
    @option(name="tags-any", type="str_list", help="matches records containing any of the specified tags")
    @option(name="sort", default="$node-reports.sort", help="the name of the report column to use in sorting the results")
    @option(name="max-width", type=int, default="$node-reports.max-width", help="set the maximum width of any column")
    @option(name="precision", type=int, default="$node-reports.precision", help="set the number of factional digits for float values")
    @option(name="add-columns", type="str_list", help="list of columns to add to those in config file")
    @option(name="columns", type="str_list", default="$node-reports.columns", help="specify list of columns to include")
    @option(name="export", type="str", help="will create a tab-separated file for the report contents")
    #@option(name="username", type="str_list", help="a list of usernames that started the jobs (acts as a filter)")
    
    # report flags
    @flag(name="reverse", help="reverse the sorted items")
    @flag(name="available", help="show the columns (name, target, search-type, etc.) available for jobs")

    # examples, FAQs
    @example(task="display a report of all the nodes in job42", text="xt list nodes job42")
    @see_also("Using the XT CLI", "cmd_options")
    @command(kwgroup="list", pass_by_args=True, help="displays a nodes report for the specified jobs")
    def list_nodes(self, args):
        '''
        This command is used to display a tabular report of nodes.  
        
        The columns shown can be customized by the job-reports:column entry in the XT config file.  In addition to specifying which columns to display, 
        you can also customize the appearance of the column header name and the formatting of the column value.  Examples:

            - To display the column "node_status" as "status", specify the column as "node_status=status".

        The --filter option can be used to show a subset of all items in the report.  The general form of the filter is <column> <relational operator> <value>. 
        Values can take the form of integers, floats, strings, and the special symbols $true, $false, $none, $empty (which are replaced with the corresponding Python values).

        Examples:
        
            - To show nodes where the repeat is set to something other than None, --filter="repeat!=$none".
        '''

        return node_helper.list_nodes(self.store, self.config, args)

    #---- COMPARE JOBS command ----
    @argument(name="job-list", type="str_list", required=False, help="a comma separated list of job names, or a single wildcard pattern")
    @flag(name="count", default="$run-reports.count", help="returns the number of jobs being retrieved at the top of the report")
    @option(name="workspace", default="$general.workspace", help="the workspace for the job to be displayed")
    @option(name="experiment", type="str_list", help="a list of experiment names for the jobs to be displayed (acts as a filter)")
    #@option(name="application", help="the application name for the runs to be displayed (acts as a filter)")
    @option(name="target", type="str_list", help="a list of compute target associated with the jobs (acts as a filter)")
    @option(name="status", type="str_list", help="a list of status values associated with the jobs (acts as a filter)")
    @option(name="service-type", type="str_list", help="a list of backend services associated with the jobs (acts as a filter)")

    # report options 
    @flag(name="all", help="don't limit the output; show all records matching the specified filters")
    @option(name="first", type=int, help="limit the output to the first N items")
    @option(name="last", type=int, default="$job-reports.last", help="limit the output to the last N items")
    @option(name="filter", type="prop_op_value", multiple=True, help="a list of filter expressions used to include matching records")
    @option(name="tags-all", type="str_list", help="matches records containing all of the specified tags")
    @option(name="tags-any", type="str_list", help="matches records containing any of the specified tags")
    @option(name="sort", default="$run-reports.sort", help="the name of the report column to use in sorting the results")
    @option(name="max-width", type=int, default="$run-reports.max-width", help="set the maximum width of any column")
    @option(name="precision", type=int, default="$run-reports.precision", help="set the number of factional digits for float values")
    @option(name="add-columns", type="str_list", help="list of columns to add to those in config file")
    @option(name="columns", type="str_list", default="$job-reports.columns", help="specify list of columns to include")
    @option(name="export", type="str", help="will create a tab-separated file for the report contents")
    @option(name="username", type="str_list", help="a list of usernames that started the jobs (acts as a filter)")
    
    # report flags
    @flag(name="reverse", help="reverse the sorted items")
    @flag(name="available", help="show the columns (name, target, search-type, etc.) available for jobs")

    # examples, FAQs
    @example(task="compare the last 5 jobs that were run", text="xt compare jobs --last=5")
    @see_also("Using the XT CLI", "cmd_options")
    @command(kwgroup="compare", pass_by_args=True, kwhelp="compare runs or jobs", help="displays a report of the hyperparameter differences for the specified jobs")
    def compare_jobs(self, args):
        '''
        This command is used to display a tabular comparison of hyperparameters for the specified jobs. 
        
        The --filter option can be used to show a subset of all runs in the workspace.  The general form of the filter is <column> <relational operator> <value>. 
        Values can take the form of integers, floats, strings, and the special symbols $true, $false, $none, $empty (which are replaced with the corresponding Python values).
        '''
        return job_helper.list_jobs(self.store, self.config, args, compare=True)

    #---- UPLOAD command ----
    @argument(name="local-path", help="the path for the local source file, directory, or wildcard")
    @argument(name="store-path", required=False, help="the path for the destination store blob or folder")
    @option(name="share", help="the name of the share that the path is relative to")
    @option(name="workspace", default="$general.workspace", help="the workspace name that the path is relative to")
    @option(name="job", help="the job id that the path is relative to")
    @option(name="experiment", help="the experiment that the path is relative to")
    @option(name="run", help="the run name that the path is relative to")
    @flag(name="feedback", default=True, help="when True, incremental feedback will be displayed")
    @example(task="copy python files from local directory to the BLOB store area associated with workspace 'curious'", text="xt upload *.py . --work=curious")
    @example(task="copy the local file 'single_sweeps.txt' as 'sweeps.txt' in the BLOB store area for job2998", text="xt upload single_sweeps.txt sweeps.txt  --job=job2998")
    @example(task="copy MNIST data from local dir to data upload folder name 'my-mnist'", text="xt upload c:/mnist/** my-mnist --share=data")
    @command(help="copy local files to an Azure storage location")
    def upload(self, local_path, store_path, share, workspace, experiment, job, run, feedback):
        self.impl_storage_api.upload(local_path, store_path, share, workspace, experiment, job, run, feedback, show_output=True)

    #---- DOWNLOAD command ----
    @argument(name="store-path", help="the path for the source store blob or wildcard")
    @argument(name="local-path", required=False,help="the path for the destination file or directory")
    @option(name="share", help="the name of the share that the path is relative to")
    @option(name="workspace", default="$general.workspace", help="the workspace name that the path is relative to")
    @option(name="job", help="the job id that the path is relative to")
    @option(name="experiment", help="the experiment that the path is relative to")
    @option(name="run", help="the run name that the path is relative to")
    @flag(name="feedback", default=True, help="when True, incremental feedback will be displayed")
    @flag(name="snapshot", help="when True, a temporary snapshot of store files will be used for their download")
    @example(task="download all blobs in the 'myrecent' folder (and its children) of the BLOB store area for job2998 to local directory c:\zip", text="xt download myrecent/** c:\zip --job=job2998")
    @command(help="copy Azure store blobs to local files/directory")
    def download(self, store_path, local_path, share, workspace, experiment, job, run, feedback, snapshot):
        self.impl_storage_api.download(store_path, local_path, share, workspace, experiment, job, run, feedback, snapshot, show_output=True)

    #---- LIST BLOBS command ----
    @argument(name="path", required=False, help="the path for the source store blob or wildcard")
    @option(name="share", help="the name of the share that the path is relative to")
    @option(name="workspace", default="$general.workspace", help="the workspace name that the path is relative to")
    @option(name="job", help="the job id that the path is relative to")
    @option(name="experiment", help="the experiment that the path is relative to")
    @option(name="run", help="the run name that the path is relative to")
    @option(name="subdirs", type=int, help="controls the depth of subdirectories listed (-1 for unlimited)")
    @flag(name="recursive", help="show all subfolders and their contents, recursively")
    @example(task="list blobs from store for job2998", text="xt list blobs --job=job2998")
    @example(task="list blobs from 'models' share", text="xt list blobs --share=models")
    @command(kwgroup="list", kwhelp="displays the specified storage items", help="lists the Azure store blobs matching the specified path/wildcard and options")
    def list_blobs(self, path, share, workspace, experiment, job, run, subdirs, recursive):

        if recursive:
            subdirs = -1

        if subdirs is None:
            subdirs = 0
        elif subdirs == -1:
            subdirs = True

        run_name = run
        use_blobs = True

        fs = self.impl_storage_api.create_file_accessor(use_blobs, share, workspace, experiment, job, run)

        dd = fs.list_directories(path, subdirs)
        #console.print("dd[folders]=", dd["folders"])

        console.print("")
        console.print("Volume " + dd["store_name"])

        for folder in dd["folders"]:
            if use_blobs:
                console.print("\nDirectory of blob-store:/{}".format(folder["folder_name"]))
            else:
                console.print("\nDirectory of file-store:/{}".format(folder["folder_name"]))
            console.print("")
            
            # find maximum size of files in this folder
            max_size = 0
            for fi in folder["files"]:
                size = fi["size"]
                max_size = max(size, max_size)

            max_size_str = "{:,d}".format(max_size)
            size_width = max(5, len(max_size_str))

            fmt_folder = "{:20s}  {:<99s}  {}".replace("99", str(size_width))
            fmt_file =   "{:20s}  {:>99,d}  {}".replace("99", str(size_width))
            #console.print("fmt_folder=", fmt_folder)

            for dir_name in folder["dirs"]:
                console.print(fmt_folder.format("", "<DIR>", dir_name))

            for fi in folder["files"]:
                size = fi["size"]
                name = fi["name"]
                dt = datetime.datetime.fromtimestamp(fi["modified"])
                dt = dt.strftime("%m/%d/%Y  %I:%M %p")
                console.print(fmt_file.format(dt, size, name))

            console.print("               {} Blob(s)".format(len(folder["files"])))
            
            dir_count = len(dd["folders"])

            if dir_count:
                console.print("               {} Dir(s)".format(dir_count))

    def remove_store_dir(self, fs, dir_path, nesting=0):
        file_count = 0
        dir_count = 0

        # this is a shallow dir listing (not recursive)
        dir_names, file_names = fs.get_filenames(dir_path, full_paths=True)

        for dname in dir_names:
            #self.remove_store_dir(fs, "/" + dname, nesting=1+nesting)
            self.remove_store_dir(fs, dname, nesting=1+nesting)
            if not nesting:
                dir_count += 1

        for fname in file_names:
            #fs.delete_file("/" + fname)
            fs.delete_file(fname)
            if not nesting:
                file_count += 1

        # now, delete this directory
        fs.delete_directory(dir_path)

        return file_count, dir_count

    #---- DELETE BLOBS command ----
    @argument(name="path", required=False, help="the path for the store blob or wildcard")
    @option(name="share", help="the name of the share that the path is relative to")
    @option(name="workspace", default="$general.workspace", help="the workspace name that the path is relative to")
    @option(name="job", help="the job id that the path is relative to")
    @option(name="experiment", help="the experiment that the path is relative to")
    @option(name="run", help="the run name that the path is relative to")
    @example(task="delete the blobs under project-x for workspace curious", text="xt delete blobs project-x --work=curious")
    @command(kwgroup="delete", kwhelp="deletes the specified storage object", help="deletes specified Azure store blobs")
    def delete_blobs(self, path, share, workspace, experiment, job, run):
        # currently, deleting blobs is not supported to minimize risk of XT Store corruption
        use_blobs = True    # (object_type != "files") 

        if not share:
            errors.general_error("To help minimize the risk of corrupting XT run data, 'xt remove' currently can only be used with the --share option")

        store_path = path
        if not store_path:
            errors.syntax_error("must supply a STORE file path")
        #console.print("store_path=", store_path)

        # should the main dir and its child directories be removed?
        remove_dirs = store_path.endswith("**") or not "*" in store_path

        fs = self.impl_storage_api.create_file_accessor(use_blobs, share, workspace, experiment, job, run)

        uri = fs.get_uri(store_path)

        if not "*" in store_path and not "?" in store_path and fs.does_file_exist(store_path):
            # special case: a named file
            fs.delete_file(store_path)
            if use_blobs:
                console.print("blob removed: \n   " + uri)
            else:
                console.print("file removed: \n   " + uri)
            return 

        if remove_dirs:
            # special case: a named directory
            file_count, dir_count = self.remove_store_dir(fs, store_path)
            FILES = "file" if file_count == 1 else "files"
            SUBDIRS = "subdirectory" if dir_count == 1 else "subdirectories"
            console.print("\nremoved directory:\n   {} ({} {}, {} {})".format(uri, file_count, FILES, dir_count, SUBDIRS))
            return

        # process wildcard specification
        dir_names, file_names = fs.get_filenames(store_path, full_paths=False)
        what = "blobs" if use_blobs else "files"

        if len(file_names) == 0:
            console.print("no matching {} found in: {}".format(what, uri))
            return

        if len(file_names) == 1:
            what = "blob" if use_blobs else "file"

        console.print("\nfrom {}, removing {} {}:".format(uri, len(file_names), what))

        max_name_len = max([len(name) for name in file_names])
        name_width =  1 + max_name_len
        #console.print("max_name_len=", max_name_len, ", name_width=", name_width)

        for bn in file_names:
            rel_bn = uri + "/" + bn
            console.print("  {1:<{0:}} ".format(name_width, bn + ":"), end="", flush=True)
            fs.delete_file(rel_bn)
            console.print("removed")

    def dump_db_doc(self, name, doc, prev_indent, show_log_records=False):
        console.print("{}{}:".format(prev_indent, name))
        indent = prev_indent + "  "
        keys = list(doc.keys())
        keys.sort()

        for key in keys:
            value = doc[key]

            if key == "log_records":
                if show_log_records:
                    console.print("{}{}: {} records".format(indent, key, len(value)))
                    for i, lr in enumerate(value):
                        self.dump_db_doc("[{}]".format(i), lr, indent)
                else:
                    console.print("{}{}: {} records (not shown)".format(indent, key, len(value)))

            elif isinstance(value, dict):
                self.dump_db_doc(key, value, indent)
            else:
                console.print("{}{}: {}".format(indent, key, value))

    def load_template(self, name):
        fn = file_utils.get_xtlib_dir() + "/templates/" + name
        td = utils.load_json_file(fn)
        return td

    #---- CREATE SERVICES TEMPLATE command ----
    @example(task="create a template for a new XT team", text="xt create services template")
    @flag(name="base", help="generate a template to create XT base services")
    @flag(name="batch", help="generate a template to create XT base services with Azure Batch")
    @flag(name="all", help="generate a template to create all XT services")
    @flag(name="aml", help="generate a template to create XT base services with Azure Machine Learning")
    @command(kwgroup="create", kwhelp="create the specified storage object", help="generate an Azure template for creating a set of resources for an XT Team")
    def create_services_template(self, base, batch, all, aml):
        '''Once you have run this command to generate a team template, follow these instructions to complete the process:
        
        1. browse to the Azure Portal Custom Template Deployment page: https://ms.portal.azure.com/#create/Microsoft.Template
        2. select 'Build your own template in the editor'
        3. copy/paste the contents of the generated file into the template editor
        4. click 'Save'
        5. select the billing subscription for the resources
        6. for resource group, choose 'Create new' and enter a simple, short, unique team name (no special characters)
        7. check the 'I Agree' checkbox and click on 'Purchase'
        8. if you receive a 'Preflight validation error', you may need to choose another (unique) team name
        9. after 5-15 minutes, you should receive a 'Deployment succeeded' message in the Azure Portal
        '''

        # if not flags specified, use BATCH as the default
        if not (base or batch or aml or all):
            batch = True

        # always read base part of template
        template = self.load_template("teamResourcesBase.json")

        if batch or all:
            bt = self.load_template("teamResourcesBatch.json")
            template["resources"].extend(bt)

        if aml or all:
            at = self.load_template("teamResourcesAml.json")
            template["resources"].extend(at)

        # load the template as a string
        template_text = json.dumps(template, indent=4)

        # # personalize it for team name
        # template = template.replace("teamx7", name)

        # add user's object_id from azure active directory
        object_id = self.config.get_vault_key("object_id")
        template_text = template_text.replace("$object_id", object_id)
        
        # write to local directory
        fn_team_template = "azure_template.json"
        file_utils.write_text_file(fn_team_template, template_text)

        # explain how to use
        PORTAL_URL = "https://ms.portal.azure.com/"
        TEMPLATE_URL = "https://ms.portal.azure.com/#blade/Microsoft_Azure_Marketplace/MarketplaceOffersBlade/selectedMenuItemId/home/searchQuery/template"

        console.print()
        console.print("To create the resources for your XT team:")
        console.print("  1. browse to the Azure Portal Custom Template Deployment page: https://ms.portal.azure.com/#create/Microsoft.Template")
        console.print("  2. select 'Build your own template in the editor'")
        console.print("  3. copy/paste the contents of the generated file into the template editor")
        console.print("  4. click 'Save'")
        console.print("  5. select the billing subscription for the resources")
        console.print("  6. for resource group, choose 'Create new' and enter a simple, short, unique team name (no special characters)")
        console.print("  7. check the 'I Agree' checkbox and click on 'Purchase'")
        console.print("  8. if you receive a 'Preflight validation error', you may need to choose another (unique) team name")
        console.print("  9. after 5-15 minutes, you should receive a 'Deployment succeeded' message in the Azure Portal")
        console.print("  10. at this point, you can create a new local XT config file for your team, for example:")

        console.print()
        console.print("--> template file generated: {}".format(fn_team_template))
        console.print()

        # TODO: add --team option to xt config cmd
        #console.print("  > xt config --template=batch --team=YourTeamNameHere")
        
    #---- VIEW DATABASE command ----
    @argument(name="name", help="the name of the run or job to show the database data for")
    @option(name="workspace", default="$general.workspace", help="the workspace that the run is defined in")
    @flag(name="log-records", help="display set of log records for run")
    @example(task="view the db-db information for run23 in the curious workspace", text="xt view db curious/run23")
    @command(kwgroup="view", help="view the database JSON data associated with the specified run")
    def view_database(self, name, workspace, log_records):
        # view db-DB document for run or job

        if run_helper.is_run_name(name):
            ws, run_name, full_run_name = run_helper.validate_run_name(self.store, workspace, name)

            include_log = False         # can make this an option later
            run_names = [run_name]      # can support multiple runs later
            filter_dict = {}

            filter_dict["run_name"] = {"$in": run_names}
            fields_dict = {"run_info": 1, "run_stats": 1, "hparams": 1, "metrics": 1, "tags": 1, 
                "log_records": log_records}

            db_docs = self.store.database.get_info_for_runs(ws, filter_dict, fields_dict)

            for doc in db_docs:
                #console.print("doc:")
                self.dump_db_doc("\nDatbase data for " + full_run_name, doc, "", log_records)

        elif job_helper.is_job_id(name):
            ws = job_helper.validate_job_name_with_ws(self.store, workspace, name, True)

            include_log = False         # can make this an option later
            job_names = [name]      # can support multiple runs later
            db = self.store.get_database()

            filter_dict = {}
            filter_dict["job_id"] = {"$in": job_names}

            # in addition to specifying single columns, we can specify special groups of columns
            fields_dict = {"job_info": 1, "job_stats": 1, "connect_info_by_node": 1, 
                "service_info_by_node": 1, "secrets_by_node": 1, "runs_by_box": 1, 
                "hparams": 1, "tags": 1}

            db_docs = db.get_info_for_jobs(workspace, filter_dict, fields_dict)

            for doc in db_docs:
                #console.print("doc:")
                self.dump_db_doc("\nDatabase data for " + name, doc, "")
        else:
            errors.syntax_error("name argument must start with 'run' or 'job'")

    def find_available_tensorboard_port(self):
        port = None
        ports_used = {}

        for process in psutil.process_iter():
            try:
                if "python" in process.name().lower():
                    cmd_line = process.cmdline()
                    if len(cmd_line) > 3 and "(port=" in cmd_line[3]:
                        pycmd = cmd_line[3]
                        index = 6 + pycmd.index("(port=")
                        portstr = pycmd[index:index+4]
                        ports_used[portstr] = 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        for p in range(6006, 6999):
            pstr = str(p)
            if not pstr in ports_used:
                port = p
                break

        return port

    def get_runs_by_prop(self, ws_name, prop, value):
        db = self.store.get_database()
        records = db.get_info_for_runs(ws_name, {prop: value}, {"_id": 1, "compute": 1, "run_name": 1})
        #names = [rr["_id"] for rr in records]
        return records

    def record_has_cols(self, rr, columns):
        found_all = True

        for col in columns:
            if not col in rr:
                found_all = False
                break
        
        return found_all

    def find_value_in_parts(self, text, name, terminator=","):
        value = None

        if name in text:
            pre, post = text.split(name, 1)
            if terminator in post:
                value, _ = post.split(terminator, 1)
            else:
                value = post

        return value

    #---- VIEW EVENTS command ----
    @keyword_arg(name="name", keywords=["xt", "controller", "quick-test"], help="name of the event log")
    @option(name="last", default=25, help="the number of most recent entries to display")
    @flag(name="all", help="specify to display all entries")
    @example(task="view the most recent events in the XT log", text="xt view events xt")
    @command(kwgroup="view", help="view formatted information in the XT event log")
    def view_events(self, name, last, all):
        
        file_names = {"xt": constants.FN_XT_EVENTS, "controller": constants.FN_CONTROLLER_EVENTS, "quick-test": constants.FN_QUICK_TEST_EVENTS}
        fn = os.path.expanduser(file_names[name])

        if not os.path.exists(fn):
            console.print("no file found: {}".format(fn))
        else:
            lines = file_utils.read_text_file(fn, as_lines=True)

            if not all:
                lines = lines[-last:]

            in_stack_trace = False

            for line in lines:
                if not line:
                    continue

                parts = line.split(",", 3)
                if len(parts) < 4 or len(parts[0]) != 10:
                    # STACK TRACE
                    if not in_stack_trace:
                        console.print("\n========================================")
                        in_stack_trace = True
                    console.print(line)
                    continue

                if in_stack_trace:
                    console.print("")
                    in_stack_trace = False

                date = parts[0].strip()
                time = parts[1].strip()
                level = parts[2].strip()
                extra = parts[3].strip()

                if ":" in extra:
                    name, rest = extra.split(":", 1)
                    name = name.strip()
                else:
                    name = extra
                    rest = ""

                if level == "ERROR":
                    in_stack_trace = True
                    console.print("\n==================================")

                if not "Client-Request-ID=" in line:
                    # non-auzre event
                    msg = "{}, {}, {}, {}: {}".format(date, time, level, name, rest)
                    console.print(line)
                    continue

                # this is an azure traffic entry
                codes = rest.split("-")
                client_id = codes[2][-4:]

                msg = "{}, {}, {}, {} [{}]: ".format(date, time, level, name, client_id)
                parts = rest.split(" ", 2)
                rest = parts[2]

                if rest.startswith("Outgoing request:"):
                    # skip a line to improve readability
                    msg = "\n" + msg

                    method = self.find_value_in_parts(rest, "Method=")
                    if method:
                        msg += method + ": " 

                    path = self.find_value_in_parts(rest, "Path=")
                    if path:
                        msg += path

                elif rest.startswith("Receiving Response:"):
                    parts = rest.split(" ", 4)

                    status = self.find_value_in_parts(rest, "HTTP Status Code=")
                    if status:
                        msg += "status=" + status

                    message = self.find_value_in_parts(rest, "Message=")
                    if message:
                        msg += " ({})".format(message)
                
                elif rest.startswith("Received expected http error"):
                    msg += "error recognized"
                    # parts = rest.split(" ", 4)

                    # status = self.find_value_in_parts(rest, "HTTP Status Code=")
                    # if status:
                    #     msg += "status=" + status

                    # exception = self.find_value_in_parts(rest, "Exception=", terminator="<")
                    # if exception:
                    #     msg += " ({})".format(exception)

                console.print(msg)
          

    #---- VIEW TENSORBOARD command ----
    @argument(name="run-list", type="str_list", required=False, help="a comma separated list of: run names, name ranges, or wildcard patterns")

    @option(name="experiment", help="the experiment that the path is relative to")
    @option(name="interval", type=int, default=10, help="specifies interval between polling for changes in the run's 'output' storage")
    @option(name="job", help="the job id that the path is relative to")
    @option(name="template", default="$tensorboard.template", type="template_value", help="specifies a template for building the collected log paths")
    @flag(name="browse", help="specifies that a browser page should be opened for the link")
    @option(name="workspace", default="$general.workspace", help="the workspace that the runs are defined within")
    @example(task="view tensorboard plots for run23 in the curious workspace", text="xt view tensorboard curious/run23")
    @command(kwgroup="view", help="create a tensorboard instance to show data associated with the specified runs")
    def view_tensorboard(self, run_list, experiment, interval, job, browse, workspace, template):
        '''
        this cmd will run a separate process that runs the XTLIB tensorboard_reader to run TB and sync TB logs to 
        local files.
        '''
        # extract columns from template
        columns = []
        us_columns = []     # modified version of col names for use with python format() calls
        templ = template

        while "{" in templ:
            index = templ.index("{")
            if not "}" in templ:
                errors.syntax_error("template '{}' is missing a matching '}' at index={}".format(template, index))
            index2 = templ.index("}")

            col = templ[index+1:index2].strip()
            if "." in col:
                # python format() doesn't like dotted names, so convert to underscore name
                col2 = col.replace(".", "_")
                template = template.replace(col, col2)
                columns.append(col)
                us_columns.append(col2)
            else:
                columns.append(col)
                us_columns.append(col)
            templ = templ[index2+1:]

        if not "job" in columns:
            columns.append("job")

        args = {"experiment": experiment, "job": job, "run_list": run_list, "workspace": workspace, "columns": columns}

        # don't default to --last=10
        args["all"] = True

        # gather run records for specified runs
        orig_records, using_default_last, user_to_actual, available, builder, last, std_cols_desc = \
            run_helper.get_filtered_sorted_limit_runs(self.store, self.config, True, args=args)

        # build tb_path for each run record
        run_records = []

        for rr in orig_records:

            # replace dotted names with underscore names
            rr = {key.replace(".", "_"): value for key, value in rr.items()}

             # logdir not available in run records, so add a placeholder that tensorboard reader will replace/update
            rr["logdir"] = "{logdir}"  

            # ensure all requests columns are present; if not, skip run (e.g., could be parent run)
            if not self.record_has_cols(rr, us_columns):
                continue

            # remove pesky leading zeros by pre-formatting values
            for key, value in rr.items():
                if isinstance(value, float):
                    value = str(value).lstrip("0")
                    rr[key] = value                    

            # format the partial path
            tb_path = template.format(**rr)

            # store in run record for tensorboard reader 
            # reader will write log files for this run to tb_path in local dir
            rr["tb_path"] = tb_path

            run_records.append(rr)

        if not run_records:
            console.print("searched over {:,} runs with columns: {}".format(len(orig_records), us_columns))
            errors.general_error("no matching run(s) found")

        cwd = file_utils.fix_slashes(file_utils.make_tmp_dir("xt_tb_reader_", False), True)

        spd = self.store.get_props_dict()
        port = self.find_available_tensorboard_port()
        if not port:
            errors.internal_error("No available port for tensorboard")

        pd = {"cwd": cwd, "store_props_dict": spd, "ws_name": workspace, "run_records": run_records, 
            "browse": browse, "interval": interval}
        text = json.dumps(pd)

        # due to large number of run_records, json text can be too long for OS, so we pass as a temp file 
        fn_base = "run_records.json"
        fn_temp = os.path.join(cwd, fn_base)

        with open(fn_temp, "wt") as outfile:
            outfile.write(text)
            outfile.flush()

        fn_temp_esc = fn_temp.replace("\\", "\\\\")     # escape single backslashes

        # get quotes right (start cmd wants double quotes around python cmd)
        python_cmd = '"import xtlib.tensorboard_reader as reader; reader.main(port={}, fn_run_records=\'{}\')"'.format(port, fn_temp_esc)
        console.print("launching tensorboard reader process...")

        # we want to start a new visible command window running python with our command
        if pc_utils.is_windows():
            # EASIEST way to do this without creating a separate .bat file is to use os.system
            full_cmd = 'start /D "{}" cmd /K python -u -c {}'.format(cwd, python_cmd)
            console.diag("cmd=", full_cmd)

            os.system(full_cmd)
        else:
            # linux
            parts = ["gnome-terminal", "--", "bash", "-c", "python -c {}".format(python_cmd)]
            console.diag("parts=", parts)

            subprocess.Popen(args=parts)

    def build_tag_fd(self, tag_list):
        fd = {}
        # convert tags to filter dictionary entries
        for tag in tag_list:
            if "=" in tag:
                name, value = tag.split("=")
                fd["tags." + name] = value
            else:
                fd["tags." + tag] = None

        return fd

    def get_storage_tracker_processes(self):
        found_processes = []
        processes = psutil.process_iter()

        for p in processes:
            try:
                name = p.name().lower()
                #print("process name: {}".format(name))

                if name.startswith("python"):
                    cmd_line = " ".join(p.cmdline())
                    #print("cmd_line: {}".format(cmd_line))

                    if "storage_tracker.py"in cmd_line:
                        found_processes.append(p)

            except BaseException as ex:
                pass
            
        return found_processes

    def is_storage_tracker_running(self):
        processes = self.get_storage_tracker_processes()
        return bool(processes)

    #---- START STORAGE TRACKER command ----
    @example(task="start running storage tracker (as background process)", text="xt start storage tracker")
    @command(help="start the storage tracker background process")
    def start_storage_tracker(self):
        if self.is_storage_tracker_running():
            errors.general_error("storage tracker is already running")

        ss_info = self.config.get_store_info(None)
        track_storage = utils.safe_value(ss_info, "track-storage")
        if not track_storage:
            errors.general_error("service set 'track-storage' property must be set to 'true'")

        tracker_path = file_utils.get_xtlib_dir() + "/storage/storage_tracker.py"
        cmd_parts = ["python", "-u", tracker_path]
        wd = "."    # must run in current dir to use correct xt config file

        xt_path = os.path.expanduser("~/.xt")
        fn_log = xt_path + "/storage_tracker.log"

        p = process_utils.start_async_run_detached(cmd_parts, wd, fn_log)

        # give it 2 seconds to detect immediate error
        try:
            p.wait(3)

            # process exited
            log_content = file_utils.read_text_file(fn_log)
            print("storage tracker log:\n{}".format(log_content))
            errors.general_error("could not start storage tracker")
        except subprocess.TimeoutExpired:
            # process did not exit
            console.print("storage tracker: started")

    #---- VIEW STORAGE TRACKER command ----
    @example(task="view status of storage tracker", text="xt view storage tracker")
    @command(help="view the status of the storage tracker background process")
    def view_storage_tracker(self):
        running = self.is_storage_tracker_running()
        if running:
            console.print("storage tracker: running")
        else:
            console.print("storage tracker: not running")

    #---- STOP STORAGE TRACKER command ----
    @example(task="stop running storage tracker (background process)", text="xt stop storage tracker")
    @command(help="stop the storage tracker background process")
    def stop_storage_tracker(self):
        if not self.is_storage_tracker_running():
            errors.general_error("storage tracker is not running")

        processes = self.get_storage_tracker_processes()
        for p in processes:
            p.kill()
            console.print("storage tracker: stopped (process={})".format(p.pid))

    #---- SET TAGS command ----
    @argument(name="name-list", type="str_list", required=True, help="a comma separated list of job or run names, or a single wildcard pattern")
    @argument(name="tag-list", type="tag_list", required=True, help="a comma separated list of tag name or tag assignments")
    @option(name="workspace", default="$general.workspace", help="the workspace for the job to be displayed")
    # examples, FAQs, command
    @example(task="add the tag 'description' with the value 'explore effects of 5 hidden layers' to the jobs job3341 thru job3356", text="xt set tags job3341-job3356 description='explore effects of 5 hidden layers'")
    @command(help="set tags on the specified jobs or runs")
    def set_tags(self, name_list, tag_list, workspace):
        first_name = name_list[0]
        fd = self.build_tag_fd(tag_list)
        db = self.store.get_database()

        if job_helper.is_job_id(first_name):
            job_helper.set_job_tags(self.store, db, name_list, tag_list, workspace, fd, clear=False)
        elif run_helper.is_run_name(first_name):
            run_helper.set_run_tags(self.store, db, name_list, tag_list, workspace, fd, clear=False)
        else:
            errors.syntax_error("first name must start with 'run' or 'job', found '{}'".format(first_name))

    #---- CLEAR TAGS command ----
    @argument(name="name-list", type="str_list", required=True, help="a comma separated list of job or run names, or a single wildcard pattern")
    @argument(name="tag-list", type="tag_list", required=True, help="a comma separated list of tag names")
    @option(name="workspace", default="$general.workspace", help="the workspace for the job to be displayed")
    # examples, FAQs, command
    @example(task="clears the tag 'description' for job3341 and job5535", text="xt clear tags job3341, job5535 description")
    @command(kwgroup="clear", help="clear tags on the specified jobs or runs")
    def clear_tags(self, name_list, tag_list, workspace):
        first_name = name_list[0]
        fd = self.build_tag_fd(tag_list)
        db = self.store.get_database()

        if job_helper.is_job_id(first_name):
            job_helper.set_job_tags(self.store, db, name_list, tag_list, workspace, fd, clear=True)
        elif run_helper.is_run_name(first_name):
            run_helper.set_run_tags(self.store, db, name_list, tag_list, workspace, fd, clear=True)
        else:
            errors.syntax_error("first name must start with 'run' or 'job'")

    #---- LIST TAGS command ----
    @argument(name="name-list", type="str_list", required=True, help="a comma separated list of job or run names, or a single wildcard pattern")
    @argument(name="tag-list", type="tag_list", required=False, help="a comma separated list of tag names")
    @option(name="workspace", default="$general.workspace", help="the workspace for the job to be displayed")
    @option(name="sort", values=["ascending", "descending"], help="the direction in which to sort the tag names")
    # examples, FAQs, command
    @example(task="list the tags for job3341 and job5535", text="xt list tags job3341, job5535")
    @command(kwgroup="list", help="list tags of the specified jobs or runs")
    def list_tags(self, name_list, tag_list, workspace, sort):
        first_name = name_list[0]
        db = self.store.get_database()

        if job_helper.is_job_id(first_name):
            # jobs
            job_helper.list_job_tags(self.store, db, workspace, name_list, tag_list, sort)

        elif run_helper.is_run_name(first_name):
            # runs
            run_helper.list_run_tags(self.store, db, workspace, name_list, tag_list, sort)

        else:
            errors.syntax_error("first name must start with 'run' or 'job'")
   
