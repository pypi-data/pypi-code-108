#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# node_helper.py: flat functions for working with node data

from .console import console
from .report_builder import ReportBuilder   

from xtlib import qfe
from xtlib import utils
from xtlib import errors
from xtlib import file_utils
from xtlib import job_helper
from xtlib import run_helper
from xtlib import store_utils

node_info_props = \
    {
        "_id": 1, 'ws_name': 1, "job_id": 1, "node_name": 1, "node_id": 1, 
        "node_index": 1, "node_num": 1, "target": 1, "total_runs": 1, 
        "box_name": 1, "run_name": 1, "exper_name": 1,
        "controller_port": 1, "ip_addr": 1, "secret": 1, "service_info": 1,
    }

node_stats_props = \
    {
        "_id": 1, 'ws_name': 1, "node_status": 1, 
        "completed_runs": 1, "error_runs": 1, "running_runs": 1,  
        'create_time': 1, 'prep_start_time': 1, "app_start_time": 1, 
        "post_start_time": 1, "post_end_time": 1, 
        'queue_duration': 1, 'prep_duration': 1, 
        "app_duration": 1, "post_duration": 1, 
        'restarts': 1, 'db_retries': 1, 'storage_retries': 1
    }

def get_node_property_dicts():
    # user-friendly property names for nodes
    user_to_actual = { 
        # NODE_INFO: creation time properties
        "ws_name": "ws_name",
        "job_id": "job_id", 
        "node_name": "node_name",
        "node_id": "node_id",
        "node_index": "node_index",
        "node_num": "node_num",
        "exper_name": "exper_name",
        "target": "target",
        "total_runs": "total_runs",
        "box_name": "box_name",
        "run_name": "run_name",
        "secret": "secret",
        "service_info": "service_info",

        # NODE_STATS: updatable properties
        "status": "node_status",
        "tags": "tags",
        "controller_port": "controller_port", 
        "ip_addr": "ip_addr",
        "completed_runs": "completed_runs",
        "error_runs": "error_runs",
        "running_runs": "running_runs",

        "create_time": "create_time",
        "prep_start_time": "prep_start_time",
        "app_start_time": "app_start_time",
        "post_start_time": "post_start_time",
        "post_end_time": "post_end_time",

        "queue_duration": "queue_duration",
        "prep_duration": "prep_duration",
        "app_duration": "app_duration",
        "post_duration": "post_duration",

        "restarts": "restarts",
        "db_retries": "db_retries",
        "storage_retries": "storage_retries",
    }

    std_cols_desc = {
        # the key here is the USER friendly name (not the physical name)
        "ws_name": "the workspace that the associated job is defined within",
        "job": "the id of the job that this node belongs to",
        "name": "the name of the node (jobNN/N)",
        "node_id": "the id of the node, within the job",
        "node_index": "the index of the node, within the job",
        "node_num": "a combination of the job/node that is used to sort by the node name",
        "exper_name": "experiment name associated with this node's job",
        "target": "the name of the compute target this node is part of",
        "total_runs": "the number of runs assigned to this node",
        "box_name": "the user-friendly name of this node",
        "run_name": "the name of the flat or parent run associated with this node",
        "secret": "the key for connecting with this node",
        "service_info": "a JSON blob of information used by the backend service for this node",

        # dynamic properties (get updated at various stages of the node)
        "status": "one of: created, running, completed",
        "tags": "the user-defined tags that have been added to the node record",
        "controller_port": "the controller port used by XT to talk with the node", 
        "ip_addr": "the IP address used by XT to talk with the node",
        "completed_runs": "the number of runs that have completed (with or without errors)",
        "error_runs": "the number of runs that have terminated with an error",
        "running_runs": "the number of this job's runs that are current running",

        "create_time": "when the node and job were created",
        "prep_start_time": "when the XT setup script started",
        "app_start_time": "when the XT controller began running on the node",
        "post_start_time": "when the POST section of the XT setup script started",
        "post_end_time": "when the XT setup script completed",

        "queue_duration": "the number of seconds that this node was queued before running",
        "prep_duration": "the number of seconds that XT spent setting up the node",
        "app_duration": "the number of seconds the XT controller (and user scripts) spent running",
        "post_duration": "the number of seconds the POST section of the XT setup script spend running",

        "restarts": "the number of times this node has been restarted",
        "db_retries": "the total number of database retries performed by the runs of this node",
        "storage_retries": "the total number of storage retries performed by the runs of this node",
    }

    return user_to_actual, std_cols_desc

def is_node_name(name):
    nn = False
    if "/" in name:
        parts = name.split("/")
        if len(parts)==2:
            job_id, node_index = parts
            if job_helper.is_job_id(job_id):
                if node_index.isdigit():
                    nn = True
                    
    return nn

def build_filter_from_mixed_node_list(store, ws_name, run_list, fd):

    exper_names = []
    job_names = []
    node_names = []
    run_names = []

    exper_fd = {}
    job_fd = {}
    node_fd = {}
    run_fd = {}

    # group into experiments, jobs, runs
    for name in run_list:
        if "-" in name:
            low, high = name.split("-")
            if run_helper.is_run_name(low):
                run_helper.expand_run_range(store, ws_name, low, high, run_names)
            elif job_helper.is_job_id(low):
                job_helper.expand_job_range(store, ws_name, low, high, can_mix=False, job_list=job_names)
            else:
                errors.general_error("only runs and jobs can be used in ranges: {}".format(name))
        elif run_helper.is_run_name(name):
            run_names.append(name)
        elif is_node_name(name):
            node_names.append(name)
        elif job_helper.is_job_id(name):
            job_names.append(name)
        else:
            # must be an experiment name
            # TODO: validate experiment name using database query on jobs 
            exper_names.append(name)
                
    # add EXPERIMENTS
    if len(exper_names) == 1:
        exper_fd["exper_name"] = exper_names[0]
    elif len(exper_names) > 1:
        exper_fd["exper_name"] = {"$in": exper_names}

    # add JOBS
    if len(job_names) == 1:
        job_fd["job_id"] = job_names[0]
    elif len(job_names) > 1:
        job_fd["job_id"] = {"$in": job_names}

    # add NODES
    if len(node_names) == 1:
        run_fd["node_name"] = node_names[0]
    elif len(node_names) > 1:
        run_fd["node_name"] = {"$in": node_names}

    # add RUNS
    if run_names:
        errors.general_error("the 'list nodes' commands currently doesn't support run_name in the node list: {}" \
            .format(run_names))

    # if len(run_names) == 1:
    #     run_fd["run_name"] = run_names[0]
    # elif len(run_names) > 1:
    #     run_fd["run_name"] = {"$in": run_names}

    # merge them together
    fd_list = []
    for fdx in [exper_fd, job_fd, node_fd, run_fd]:
        if fdx:
            fd_list.append(fdx)

    count = len(fd_list)
    if count == 1:
        # merge our only fdx into fd
        fd.update(fd_list[0])
    elif count > 1:
        # combine with an OR
        fd["$or"] = fd_list

def build_node_filter_dict(store, ws_name, node_list, user_to_actual, builder, workspace, args):
    fd = {}
    option_filters = ["experiment", "target", "status"]  

    if node_list:
        build_filter_from_mixed_node_list(store, ws_name, node_list, fd)

    # filter by workspace
    if workspace:
        fd["ws_name"] = workspace
        
    # filter by specified options
    for name in option_filters:
        store_name = "exper_name" if name == "experiment" else user_to_actual[name]
        job_helper.build_filter_part(fd, args, name, store_name)

    # filter by filter_list
    filter_exp_list = args["filter"]
    if filter_exp_list:
        builder.process_filter_list(fd, filter_exp_list, user_to_actual)

    # filter by tag
    if "tag" in args:
        tag_name = args["tag"]
        if tag_name:
                fd["tags." + tag_name] = {"$exists": True}

    # filter by tags_all
    tags_all = args["tags_all"]
    if tags_all:
        for tag in tags_all:
            fd["tags." + tag] = {"$exists": True}

    # filter by tags_any
    tags_any = args["tags_any"]
    if tags_any:
        fany_list = []
        
        for tag in tags_any:
            f = {"tags." + tag: {"$exists": True}}
            fany_list.append(f)

        # or all of fany conditions together
        fd["$or"] = fany_list

    return fd


def get_list_nodes_records(store, config, user_columns, args):
    list_nodes = utils.safe_value(args, "list_nodes")

    job_list = args["node_list"] 
    #pool = args["target"]

    if job_list and store_utils.STORAGE_FORMAT == "1":
        # only use workspace if it was explictly set  
        workspace = None   
        explict = qfe.get_explicit_options()
        if "workspace" in explict:
            workspace = explict["workspace"]
    else:
        workspace = args["workspace"]

    if workspace:
        store.ensure_workspace_exists(workspace, flag_as_error=True)

    # get info about job properties
    user_to_actual, std_cols_desc = get_node_property_dicts()        
    actual_to_user = {value: key for key, value in user_to_actual.items()}

    builder = ReportBuilder(config, store)

    # get list of specified jobs
    db = store.get_database()
    job_list, actual_ws = job_helper.expand_job_list(store, db, workspace, job_list)

    # build a filter dict for all specified filters
    filter_dict = build_node_filter_dict(store, workspace, job_list, user_to_actual, builder, workspace, args)

    # get the db records for the matching NODES
    #console.print("gathering job data...", flush=True)
    records, limiter, limiter_value = builder.get_db_records(db, filter_dict, workspace, "nodes", actual_to_user, 
        user_columns=user_columns, args=args)
        
    return records, limiter, limiter_value, user_to_actual, builder

def list_nodes(store, config, args, compare=False):
    available = args["available"]
    report_type = "node-reports"
    user_columns = utils.get_user_columns(args["columns"], report_type, config)

    # we are reusing some of job_helper, so adjust args as needed
    args["list_nodes"] = True
    args["jobs_list"] = args["node_list"]

    if compare:
        args["columns"] = ["job", "hparams.*"]
    
    records, using_default_last, last, user_to_actual, builder \
        = get_list_nodes_records(store, config, user_columns, args)

    if available:
        user_to_actual, std_cols_desc = get_node_property_dicts()        
        hparams_cols = run_helper.extract_dotted_cols(records, "hparams")
        std_cols = list(user_to_actual.keys())
        tag_cols = job_helper.extract_tag_cols(records)
        lines = builder.available_cols_report("job", std_cols, std_cols_desc, hparams_list=hparams_cols, 
            tags_list=tag_cols)

        for line in lines:
            console.print(line)
    else:    
        if compare:
            # filter cols to those that are different
            diff_cols = run_helper.get_different_cols(records)
            args["columns"] = diff_cols 

        avail_list = list(user_to_actual.keys())
        lines, row_count, was_exported = builder.build_report(records, user_columns=user_columns, report_type=report_type, args=args)

        store_name = config.get("store")
        workspace = args["workspace"]
        console.print("nodes from {}/{}:".format(store_name, workspace))

        if was_exported:
            console.print("")

            for line in lines:
                console.print(line)
        else:
            # console.print the report
            if row_count > 0:
                console.print("")

                for line in lines:
                    console.print(line)

                if row_count > 1:
                    if using_default_last:
                        console.print("total nodes listed: {} (limited by --last={})".format(row_count, last))
                    else:
                        console.print("total nodes listed: {}".format(row_count))
            else:
                console.print("no matching nodes found")

