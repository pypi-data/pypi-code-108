#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# runner.py: code to prepare to build a run submission (shared code for all backends)
import os
import sys
import json
import math
import time
import yaml
import uuid
import shutil
from typing import List
from threading import Lock

from xtlib.client import Client
from xtlib.console import console
from xtlib.cmd_core import CmdCore
from xtlib.helpers import file_helper
from xtlib.helpers.scanner import Scanner
from xtlib.hparams.hp_client import HPClient
from xtlib.helpers.feedbackParts import feedback as fb

from xtlib import qfe
from xtlib import utils
from xtlib import errors
from xtlib import capture
from xtlib import xt_dict
from xtlib import pc_utils
from xtlib import scriptor
from xtlib import constants
from xtlib import file_utils
from xtlib import job_helper
from xtlib import store_utils
from xtlib import process_utils
from xtlib import box_information

class Runner():
    ''' class to consolidate all shared code for run submission '''
    def __init__(self, config, core, temp_dir):
        self.config = config
        self.core = core
        self.store = core.store
        self.backend = None
        self.is_docker = None
        self.target_dir = None
        self.temp_dir = temp_dir

    def process_args(self, args):

        run_script = None
        parent_script = None
        run_cmd_from_script = None
        target_file = args["script"]
        target_args = args["script_args"]
        code_upload = args["code_upload"]

        # user may have wrong slashes for this OS
        target_file = file_utils.fix_slashes(target_file)

        if os.path.isabs(target_file):
            errors.syntax_error("path to app file must be specified with a relative path: {}".format(target_file))

        is_rerun = "is_rerun" in args
        if is_rerun:
            # will be running from script dir, so remove any path to script file
            self.script_dir = os.path.dirname(target_file)
            target_file = os.path.basename(target_file)

        if target_file.endswith(".py"):
            # PYTHON target
            cmd_parts = ["python"]
            cmd_parts.append("-u")
            cmd_parts.append(target_file)
        else:
            cmd_parts = [target_file] 

        if target_args:
            # split on unquoted spaces
            arg_parts = utils.cmd_split(target_args)
            cmd_parts += arg_parts

        if target_file == "docker":
            self.is_docker = True
            
        if not self.is_docker and code_upload and not os.path.exists(target_file):
            errors.env_error("script file not found: {}".format(target_file))

        ps_path = args["parent_script"]
        if ps_path:
            parent_script = file_utils.read_text_file(ps_path, as_lines=True)

        if target_file.endswith(".bat") or target_file.endswith(".sh"):
            # a RUN SCRIPT was specified as the target
            run_script = file_utils.read_text_file(target_file, as_lines=True)
            run_cmd_from_script = scriptor.get_run_cmd_from_script(run_script)

        return cmd_parts, ps_path, parent_script, target_file, run_script, run_cmd_from_script

    def build_compute_def(self, args):
        compute = args["target"]
        box_def = self.config.get("boxes", compute, suppress_warning=True)

        compute_def = dict(self.config.get_target_def(compute))

        if not "service" in compute_def:
            errors.config_error("compute target '{}' must define a 'service' property".format(compute))

        service = compute_def["service"]
        if service in ["local", "pool"]:
            # its a list of box names
            boxes = compute_def["boxes"]
            if len(boxes)==1 and boxes[0] == "localhost":
                pool = None
                box = "local"
                service_type = "pool"
            else:
                pool = compute
                box = None
                service_type = "pool"
        else:
            # it a set of compute service properties
            pool = compute
            box = None
            service_name = compute_def["service"]
            service_type = self.config.get_service_type(service_name)

        # elif box_def:
        #     # translate single box name to a compute_def
        #     box = compute
        #     pool = None
        #     service_type = "pool"
        #     compute_def = {"service": service_type, "boxes": [box], setup: setup_name}
        # else:
        #     errors.config_error("unknown target or box: {}".format(compute))

        compute_def["name"] = compute

        hold = args["hold"]
        update_compute_def_from_cmd_options(compute_def, hold)

        args["target"] = compute
        args["compute_def"] = compute_def
        args["service_type"] = service_type

        # for legacy code
        args["box"] = box
        args["pool"] = pool

        # update args["setup"] with default
        setup_name = utils.safe_value(compute_def, "setup")
        if not setup_name:
            setup_name = utils.safe_value(box_def, "setup")
            args["setup"] = setup_name

        return compute, compute_def, service_type, setup_name

    def ensure_script_ext_matches_box(self, script_name, fn_script, box_info):
        _, file_ext = os.path.splitext(fn_script)
        if file_ext in [".bat", ".sh"]:
            expected_ext = ".bat" if box_info.box_os == "windows" else ".sh"

            if file_ext != expected_ext:
                errors.combo_error("{} file ext='{}' doesn't match box.os='{}'".format(script_name, file_ext, box_info.box_os))

    def build_first_run_for_node(self, node_index, run_count, total_run_count, box_name, run_script_path, parent_script_path, 
            using_hp, use_aml_hparam, run_specs, job_id, parent_name, cmds, compute_def, repeat_count, fake_submit, 
            search_style, box_secret, node_count, run_name=None, args=None):
            
        exper_name = args['experiment']

        box_info = box_information.BoxInfo(self.config, box_name, self.store, args=args)

        if node_index == 0:
            # check that script file extensions match OS of first box
            if run_script_path:
                self.ensure_script_ext_matches_box("run script", run_script_path, box_info)

            if parent_script_path:
                self.ensure_script_ext_matches_box("parent script", parent_script_path, box_info)

        node_id = "node" + str(node_index)
        # if using_hp:
        #     if not node_id in cmds_by_node:
        #         errors.combo_error("you specified more nodes/boxes than hyperparameter search runs")

        cmd_parts = run_specs["cmd_parts"]
        actual_parts = None

        if cmd_parts:
            actual_parts = list(cmd_parts)
            if box_info.box_os == "linux" and actual_parts[0] == "docker":
                # give our user permission to run DOCKER on linux
                actual_parts.insert(0, "sudo")
                # run nvidia-docker to gain access to machines GPUs
                actual_parts[1] = "nvidia-docker"
            #console.print("actual_parts=", actual_parts)

        # CREATE RUN 
        path = os.path.realpath(args["script"])

        run_name, full_run_name, box_name, pool = \
            self.create_run(job_id, actual_parts, box_name=box_name, parent_name=parent_name, 
                node_index=node_index, using_hp=using_hp, 
                repeat=repeat_count, app_info=None, path=path, exper_name=exper_name, compute_def=compute_def, 
                fake_submit=fake_submit, search_style=search_style, run_count=run_count, 
                total_run_count=total_run_count, run_name=run_name, args=args)

        run_data = {"run_name": run_name, "run_specs": run_specs, "box_name": box_name, "box_index": node_index, 
            "box_info": box_info, "repeat": repeat_count, "box_secret": box_secret}

        return run_data
       
    def write_node_info_data(self, _id, ws_name, job_id, node_index, total_run_count, node_count, 
        box_name, run_name, secret, service_info, exper_name, args):

        target = args["target"]
        str_now = utils.get_arrow_time_str()

        job_num = job_helper.get_job_number(job_id)
        node_num = job_num*1000*1000 + node_index
        node_name = "{}/{}".format(job_id, node_index)

        # compute node_run_count
        first, last = self.core.compute_run_indexes_for_node(total_run_count, node_count, node_index)
        node_run_count = last - first + 1
        node_id = utils.node_id(node_index)
        service_info_text = json.dumps(service_info)

        dd = {"_id": _id, "ws_name": ws_name, "job_id": job_id, "exper_name": exper_name, 
            "node_name": node_name, "node_id": node_id, "node_index": node_index, "node_num": node_num, 
            "target": target, "total_runs": node_run_count, "box_name": box_name, "run_name": run_name,
            "secret": secret, "service_info": service_info_text}

        # write dd record to node_info
        self.store.database.update_collection("node_info", ws_name, dd)

    def write_node_stats_data(self, _id, ws_name):
        str_now = utils.get_arrow_time_str()

        dd = {"_id": _id, "node_status": "created", 
            "completed_runs": 0, "error_runs": 0, "running_runs": 0,
            "create_time": str_now, "restarts": 0, "db_retries": 0, "storage_retries": 0}

        # write dd record to node_stats
        self.store.database.update_collection("node_stats", ws_name, dd)

    def write_node_tags_data(self, _id, ws_name, job_id, tag_dict):

        if not tag_dict:
            tag_dict = {}

        tag_dict["_id"] = _id        
        tag_dict["job_id"] = job_id        

        # write dd record to node_stats
        self.store.database.update_collection("node_tags", ws_name, tag_dict)

    def write_hparams_to_job(self, ws_name, job_id, cmds, fake_submit, using_hp, args):
        # write to job-level sweeps-list file
        #console.print("cmds=", cmds)   
        cmds_text = json.dumps(cmds)

        if not fake_submit:
            self.store.create_job_file(ws_name, job_id, constants.HP_SWEEP_LIST_FN, cmds_text)

        # NOTE: pool_info is legacy form of compute_def and is being eliminated 
        boxes, _, service_type = box_information.get_box_list(self, job_id=job_id, args=args)
        num_boxes = len(boxes)

        is_distributed = args["distributed"]
        if is_distributed:
            # check for conflicts
            if using_hp:
                errors.combo_error("Cannot do hyperparamer search on a distributed-training job")

            if service_type != "aml":
                errors.combo_error("Distributed-training is currently only supported for AML jobs")

        return boxes, num_boxes

    def create_run(self, job_id, user_cmd_parts, box_name="local", parent_name=None, rerun_name=None, node_index=0, 
            using_hp=False, repeat=None, app_info=None, path=None, exper_name=None, compute_def=None, fake_submit=False, 
            search_style=None, run_count=None, total_run_count=None, run_name=None, args=None):
        '''
        'create_run' does the following:
            - creates a new run name (from the job name and node)
            - logs a "created" record in the run log
            - logs a "created" record in the workspace summary log
            - logs a "cmd" record in the run log
            - log an optional "notes" record in the run log
            - captures the run's "before" files to the store's run directory
        '''
        console.diag("create_run: start")

        app_name = None   # app_info.app_name
        box_nane = args["box"]
        pool = args["pool"]
        
        log_to_store = self.config.get("logging", "log")
        aggregate_dest = args["aggregate_dest"]

        if log_to_store:
            if not exper_name:
                exper_name = input("experiment name (for grouping this run): ")

            #console.print("calling store.start_run with exper_name=", exper_name)
            username = args["username"]
            description = args["description"]
            workspace = args["workspace"]

            console.diag("create_run: before start_run")

            service_type = args["service_type"]
            compute = args["target"]
            search_type = args["search_type"]

            # compute_def has been updated with args[sku]
            sku = utils.safe_value(compute_def, "sku")
            if sku:
                sku = sku.lower()

            # create RUN in store
            if fake_submit:
                run_name = "fake_run123"
            else:
                is_parent = search_style != "single"

                if not run_name:
                    run_name = self.store.database.get_next_run_name(workspace, job_id, 
                        is_parent, total_run_count, node_index)

                tag_dict = args["tags"]

                self.store.start_run_core(workspace, run_name=run_name, exper_name=exper_name, box_name=box_name, app_name=app_name, 
                    username=username, repeat=repeat, pool=pool, job_id=job_id, node_index=node_index, sku=sku,
                    description=description, aggregate_dest=aggregate_dest, path=path, compute=compute, service_type=service_type, 
                    search_style=search_style, is_parent=is_parent, tag_dict=tag_dict)

            console.diag("create_run: after start_run")

            # always log cmd (for re-run purposes)
            xt_cmd = args["xt_cmd"]

            if not fake_submit:
                self.store.log_run_event(workspace, run_name, "cmd", {"cmd": user_cmd_parts, "xt_cmd": xt_cmd }, job_id=job_id)

            # for now, don't log args (contain private credentials and not clear if we really need it)
            # record all "args" (from cmd line, user config, default config) in log (for audit/re-run purposes)
            #self.store.log_run_event(workspace, run_name, "args", args)

            store_type = self.config.get_storage_type()
            full_run_name = utils.format_workspace_exper_run(store_type, workspace, exper_name, run_name)

            # log NOTES record
            if not fake_submit:
                if self.config.get("logging", "notes") in ["before", "all"]:
                    text = input("Notes: ")
                    if text:
                        self.store.log_run_event(workspace, run_name, "notes", {"notes": text})
        else:
            full_run_name = ""

        console.diag("create_run: after logging")
        workspace = args['workspace']

        return run_name, full_run_name, box_name, pool

    def upload_sweep_data(self, sweeps_text, exper_name, job_id, args):
        '''
        we have extracted/parsed HP sweeps data; write it to the experiment/job store
        where we can find it during dynamic HP searches (running in controller).
        '''
        # upload SWEEP file to job or experiment directory
        fn_sweeps = args["hp_config"]
        agg_dest = args["aggregate_dest"]
        ws_name = args["workspace"]

        if not fn_sweeps:
            # must have extracted sweeps data from cmd line options
            fn_sweeps = constants.HP_CONFIG_FN
            args["hp_config"] = fn_sweeps

        # upload to a known folder name (since value of fn_sweeps can vary) and we need to find it later (HX usage)
        target_name = file_utils.path_join(constants.HP_CONFIG_DIR, os.path.basename(fn_sweeps))
        
        if agg_dest == "experiment":
            self.store.create_experiment_file(ws_name, exper_name, target_name, sweeps_text)
        else:
            self.store.create_job_file(ws_name, job_id, target_name, sweeps_text)

    def build_runs_by_box(self, job_runs, workspace):
        # build box_name => runs dict for job info file
        runs_by_box = {}
        last_run = None

        # for each node
        for run_data_list in job_runs:
            for run_data in run_data_list:   
                box_name = run_data["box_name"]

                # process a run for box_name
                if not box_name in runs_by_box:
                    runs_by_box[box_name] = [] 

                # create as dict; we will later add "service_run_id" to the dict (for philly, batch, aml)
                rr = {"ws_name": workspace, "run_name": run_data["run_name"], "box_index": run_data["box_index"]}

                runs_by_box[box_name].append(rr)
                last_run = run_data["run_name"]

        return runs_by_box, last_run

    def adjust_script_dir(self, cmd_parts):
        '''
        NOTE: cmd_parts is modified directly.
        '''

        script_dir = None    # default to the current directory
        found_script = False

        parts = cmd_parts
        dest_linux = not self.backend.gen_for_windows

        for i, part in enumerate(parts):

            if found_script and part.startswith("@"):
                part = part[1:]   # remove the "@"
                if os.path.isfile(part):
                    # ensure the slashes in the path match targeted OS 
                    parts[i] = "@" + file_utils.fix_slashes(part, is_linux=dest_linux)

            elif not part.startswith("-"):
                if os.path.isfile(part):
                    # ensure the slashes in the path match targeted OS 
                    fixed_path = file_utils.fix_slashes(part, is_linux=dest_linux)
                    parts[i] = fixed_path

                    script_dir = os.path.dirname(fixed_path)
                    found_script = True

        if not script_dir:
            script_dir = "."

        return script_dir

    def remove_script_dir_from_parts(self, cmd_parts):
        '''
        NOTE: cmd_parts is modified directly.
        '''

        script_dir = "."    # default to the current directory
        found_script = False

        parts = cmd_parts
        for i, part in enumerate(parts):

            if found_script and part.startswith("@"):
                part = part[1:]   # remove the "@"
                if os.path.isfile(part):
                    # remove the path from the arg file 
                    parts[i] ="@" + os.path.basename(part)
            elif not part.startswith("-"):
                path = os.path.realpath(part)
                if os.path.isfile(path):
                    script_dir = os.path.dirname(path)

                    # remove the path from the script 
                    parts[i] = os.path.basename(path)
                    found_script = True

        return script_dir

    def build_docker_cmd(self, docker_name:str, target: str, bootstrap_dir: str, job_secret: str, 
            setup_name: str, args: List[str]):
        '''
        This is only called for backends that don't have their own support for running in docker.  Currently, this is
        just the POOL backend.  This function will replace the user's script cmd with:

            - optional 'docker login' cmd
            - 'docker run' cmd
        '''
        for_windows = self.backend.is_windows
        login_cmd = None

        timeout = args["docker_pull_timeout"]
        if timeout:
            # validate timeout (e.g., "30s" or "5d")
            if timeout.isnumeric():
                # will default to seconds
                pass
            else:
                unit = timeout[-1]
                if not unit in 'smhd':
                    raise Exception("illegal duration specified for general.docker-pull-timeout (try: 30m)")
                if " " in timeout:
                    raise Exception("illegal duration specified for general.docker-pull-timeout (try: 30m)")

        docker_image, login_server, docker_registry = self.config.get_docker_info(target, docker_name, required=False)
        creds_required = utils.make_numeric_if_possible( utils.safe_value(docker_registry, "login") )

        setup_def = self.config.get("setups", setup_name, suppress_warning=True)
        use_sudo = not for_windows   # utils.safe_value(setup_def, "use-sudo") or self.backend.name in ["pool", "batch"]
        sudo = "sudo " if use_sudo else ""

        if creds_required:
            username = utils.safe_value(docker_registry, "username")
            password = utils.safe_value(docker_registry, "password")

            # avoid docker login warning about password and CLI
            #login_cmd = "echo {} | {}docker login {} --username {} --password-stdin".format(password, sudo, login_server, username)
            login_cmd = "{}docker login {} --username {} --password {}".format(sudo, login_server, username, password)

        args["docker_login_cmd"] = login_cmd

        dest_src_dir = "/usr/src"     # "/root/.xt/cwd"
        script_dir = "%CD%" if for_windows else "$PWD"
        mappings = "-v {}:{}".format(script_dir, dest_src_dir)
        options = "--rm"

        # collect env vars 
        env_vars = {"XT_IN_DOCKER": 1, "XT_USERNAME": pc_utils.get_username()}
        scriptor.add_controller_env_vars(env_vars, self.config, job_secret, "node0")

        full_image = login_server + "/" + docker_image if login_server else docker_image

        # don't use data_local or model_local mappings for docker because docker
        # always runs linux where blobfuse is available 

        # # build a mapping for data
        # if target == "local":
        #     data_local = args["data_local"]
        #     if data_local:
        #         if "$scriptdir" in data_local:
        #             data_local = data_local.replace("$scriptdir", script_dir)

        #         data_local = os.path.realpath(data_local)
        #         mappings += " -v {}:/usr/data".format(data_local)
        #         env_vars["XT_DATA_DIR"] = "/usr/data"

        # write env vars to file in bootstrap_dir 
        fn_env_var = os.path.join(bootstrap_dir, constants.FN_EV)
        lines = [name + "=" + str(value) for name,value in env_vars.items()]
        text = "\n".join(lines)
        file_utils.write_text_file(fn_env_var, text)

        # specify env var file (in current directory) to docker
        options += " --env-file={}".format(constants.FN_EV)

        # inherit ENV VARS from running environment
        options += " -e XT_RUN_NAME -e XT_WORKSPACE_NAME -e XT_EXPERIMENT_NAME"

        # flags needed by blobfuse usage
        #options += " --cap-add SYS_ADMIN --device /dev/fuse --security-opt apparmor:unconfined"
        options += " --privileged"

        # append user options
        other_options = args["docker_other_options"]
        if other_options:
            options += " " + other_options

        # currently, we don't support running in a windows-based container
        docker_is_windows = False
        args["docker_is_windows"] = docker_is_windows
        args["full_docker_image"] = full_image

        pass_args = "%*" if for_windows else "$*"
        sh_prefix = "bash --login"

        if for_windows:
            # launching docker from windows
            docker_cmd = "{}docker run {} {} {} {} {}/{} {}".format(sudo, mappings, options, full_image, sh_prefix, dest_src_dir, constants.FN_INNER_SH, pass_args)
        else:
            # launching docker from linux
            # we set DOCKER_RUN just before this command is executed (see backend_base.py)
            docker_cmd = "{}$DOCKER_RUN {} {} {} {} {}/{} {}".format(sudo, mappings, options, full_image, sh_prefix, dest_src_dir, constants.FN_INNER_SH, pass_args)
            #docker_cmd = "{}docker run --gpus all {} {} {} {} {}/{} {}".format(sudo, options, mappings, full_image, sh_prefix, dest_src_dir, constants.FN_INNER_SH, pass_args)

        # store for use by backend_base.wrap_user_cmds()
        args["docker_cmd"] = docker_cmd

    def get_installed_package_version(self, pkg_name):
        import pkg_resources

        
        version = pkg_resources.get_distribution(pkg_name).version
        return version

    def adjust_pip_packages(self, args):
        '''
        convert any package=* in pip-packages to use local machine version (from pip freeze)
        '''
        pip_packages = args["pip_packages"]
        new_pip_packages = []

        for pp in pip_packages:
            if pp.endswith("==*"):
                package = pp[:-3]
                version = self.get_installed_package_version(package)
                if not version:
                    errors.env_error("version number for specified pip package not found in environment: " + package)
                pp = package + "==" + version

            new_pip_packages.append(pp)

        args["pip_packages"] = new_pip_packages

    def snapshot_all_code(self, bootstrap_dir, snapshot_dir, cmd_parts, args):
        '''
        keep code simple (and BEFORE upload fast):
            - always copy code dir to temp dir
            - if needed, copy xtlib subdir
            - later: if needed, add 2 extra controller files
            - later: zip the whole thing at once & upload 
        '''
        code_dirs = args["code_dirs"]
        xtlib_capture = args["xtlib_upload"]
        code_omit = args["code_omit"]
        script_dir = None

        code_upload = args["code_upload"]

        # new design: script dir must be relative and we don't touch it
        # # this step should always be done so that script_dir is removed from cmd_parts
        # script_dir = self.remove_script_dir_from_parts(cmd_parts)
        script_dir = self.adjust_script_dir(cmd_parts)

        if code_upload:
            for i, code_dir in enumerate(code_dirs):
                # fixup "$scriptdir" relative paths
                if "$scriptdir" in code_dir:
                    code_dir = code_dir.replace("$scriptdir", script_dir)

                if "==>" in code_dir:
                    code_dir, dest_dir = code_dir.split("==>")
                elif "::" in code_dir:
                    # "::" is legacy version of "==>"
                    code_dir, dest_dir = code_dir.split("::")
                else:
                    dest_dir = "."
                capture.make_local_snapshot(code_dir, snapshot_dir, dest_dir, code_omit)
        else:
            script_dir = snapshot_dir

        if xtlib_capture:
            xtlib_dir = file_utils.get_xtlib_dir()

            # copy XTLIB directory to "xtlib" subdir of CODE SNAPSHOT
            dest_dir = snapshot_dir + "/xtlib"
            file_utils.ensure_dir_deleted(dest_dir)
            shutil.copytree(xtlib_dir, dest_dir, ignore=shutil.ignore_patterns("demo_files"))

        console.diag("after create local snapshot")
        return script_dir

    def process_run_command(self, args):
        self.args = args

        # ensure workspace exists
        workspace = args['workspace']
        dry_run = args['dry_run']
        fake_submit = args["fake_submit"]

        if not fake_submit:
            self.store.ensure_workspace_exists(workspace, flag_as_error=False)

        # PRE-PROCESS ARGS
        cmd_parts, ps_path, parent_script, target_file, run_script, run_cmd_from_script = \
            self.process_args(args)

        compute, compute_def, service_type, setup_name = self.build_compute_def(args)

        # create backend helper (pool, philly, batch, aml)
        username = args["username"]

        self.backend = self.core.create_backend(compute, compute_def, username=username)

        # add conda_packages and pip_packages from SETUP to ARGS
        setup_def = self.config.get_setup_from_target_def(compute_def, setup_name)

        conda_packages = utils.safe_value(setup_def, "conda-packages")
        pip_packages = utils.safe_value(setup_def, "pip-packages")
        python_path = utils.safe_value(setup_def, "python-path")
        other_cmds = utils.safe_value(setup_def, "other-cmds")
        pre_cmds = utils.safe_value(setup_def, "pre-cmds")
        install_blobfuse = utils.safe_value(setup_def, "install-blobfuse")

        args["conda_packages"] = conda_packages if conda_packages else []
        args["pip_packages"] = pip_packages if pip_packages else []
        args["python_path"] = python_path if python_path else []
        args["other_cmds"] = other_cmds if other_cmds else []
        args["pre_cmds"] = pre_cmds if pre_cmds else []

        # install blobfuse defaults to True
        args["install_blobfuse"] = True if install_blobfuse is None else install_blobfuse

        self.adjust_pip_packages(args)

        snapshot_base = self.temp_dir
        snapshot_dir = os.path.join(snapshot_base, "code")

        # for now, don't separate code and bootstrap (causes issues: requirements.txt file)
        bootstrap_dir = snapshot_dir   # os.path.join(snapshot_base, "bootstrap")

        # pass to everyone
        args["bootstrap_dir"] = bootstrap_dir

        # parse arguments before paths are removed
        job_hparams = self.build_job_hparams(cmd_parts)

        if fake_submit:
            script_dir = snapshot_dir
        else:
            # note: always create a snapshot dir for backends to add needed files
            file_utils.ensure_dir_deleted(snapshot_dir)
            script_dir = self.snapshot_all_code(bootstrap_dir, snapshot_dir, cmd_parts, args)

        self.script_dir = script_dir
        direct_run = args["direct_run"]

        # do we need to start the xt controller?
        use_controller = not direct_run
        adjustment_scripts = None

        # create a job_secret that can later be used to authenticate with the XT controller
        # NOTE: we currently log this secret as a job property, which allows all team members to view and control this job
        job_secret = str(uuid.uuid4())

        # do we need to build a "docker run" command?
        args["docker_login_cmd"] = None
        args["docker_cmd"] = None
        args["docker_is_windows"] = False

        if not self.backend.provides_container_support():
    
            docker_name = args["docker"]
            if not docker_name:
                docker_name = utils.safe_value(compute_def, "docker")
                args["docker"] = docker_name
    
            if docker_name and docker_name != "none":
                self.build_docker_cmd(docker_name, compute, bootstrap_dir, job_secret, setup_name, args)
                
        # BUILD CMDS (from static hparam search, user multi cmds, or single user cmd)
        cmds, runsets, total_run_count, repeat_count, run_specs, using_hp, using_aml_hparam, sweeps_text, search_style = \
            self.build_cmds_with_search(service_type, cmd_parts, parent_script, run_script, run_cmd_from_script, use_controller, dry_run, args)

        if dry_run:
            return

        # make new values available
        args["search_style"] = search_style
        args["total_run_count"] = total_run_count

        resume_name = args['resume_name']
        keep_name = False  # args['keep_name']
        experiment = args['experiment']
        is_distributed = args['distributed']
        direct_run = args["direct_run"]

        # CREATE JOB to hold all runs
        if fake_submit:
            # use lastrun/lastjob info to get a fast incremental fake job number
            xtd = xt_dict.read_xt_dict()
            fake_job_num = xtd["fake_job_num"] if "fake_job_num" in xtd else 1
            xtd["fake_job_num"] = fake_job_num + 1
            xt_dict.write_xt_dict(xtd)
            job_id = "fake_job" + str(fake_job_num)
        else:
            job_id = self.store.create_job(workspace)
        fb.feedback(job_id)

        if experiment:
            # create the experiment, if it doesn't already exist
            if not self.store.does_experiment_exist(workspace, experiment):
                self.store.create_experiment(workspace, experiment)

        # start the feedback (by parts)
        fb.feedback("{}: {}".format("target", compute))

        # make available to everyone
        args["job_id"] = job_id

        # write hparams to job-level file
        boxes, num_boxes = self.write_hparams_to_job(workspace, job_id, cmds, fake_submit, using_hp, args)

        if sweeps_text and not fake_submit:
            self.upload_sweep_data(sweeps_text, experiment, job_id, args=args)

        # if num_boxes > 1 and service_type != "batch":
        #     fb.feedback("", is_final=True)

        parent_name = None

        # BUILD RUNS, by box
        job_runs = []
        run_count = 1 if is_distributed else len(boxes) 
        secrets_by_node = {}
        remote_control = args["remote_control"]

        self.build_all_node_runs(boxes, remote_control, run_count, total_run_count, 
                target_file, ps_path, using_hp, using_aml_hparam, run_specs, job_id, 
                parent_name, cmds, compute_def, repeat_count, fake_submit, search_style, job_runs, 
                secrets_by_node, is_distributed, service_type, args)

        # build box: runs dict for job info file
        runs_by_box, last_run = self.build_runs_by_box(job_runs, workspace)

        node_count = len(boxes)
        args["node_count"] = node_count

        # now that we have run names for all static run names for all nodes, we can adjust cmds (and before files) for using the controller
        if use_controller:
            # we will create 2 temp. controller files in the CURRENT DIRECTORY (that will be captured to JOB)
            # this will also adjust commands for each node to run the XT controller
            adjustment_scripts = self.core.adjust_job_for_controller_run(job_id, job_runs, cmds, runsets, using_hp, experiment, service_type, bootstrap_dir, 
                search_style, args=args)

        else:
            adjustment_scripts = self.core.adjust_job_for_direct_run(job_id, job_runs, cmds, using_hp, experiment, service_type, snapshot_dir, 
                search_style, args=args)

        # add env vars used by both controller and runs
        env_vars = args["env_vars"]

        # create a job guid to uniquely identify this job across all XT instances
        job_guid = str(uuid.uuid4())

        # we add with "node0" and "job_secret", but backend service will override for each node
        scriptor.add_controller_env_vars(env_vars, self.config, None, "node0")

        data_local = args["data_local"]
        if "$scriptdir" in data_local:
            data_local = os.path.realpath(data_local.replace("$scriptdir", script_dir))
            args["data_local"] = data_local

        model_local = args["model_local"]
        if "$scriptdir" in model_local:
            model_local = os.path.realpath(model_local.replace("$scriptdir", script_dir))
            args["model_local"] = model_local

        # ADJUST CMDS: this allows backend to write scripts to snapshot dir, if needed, as a way of adjusting/wrapping run commands
        self.backend.adjust_run_commands(job_id, job_runs, using_hp, experiment, service_type, snapshot_dir, args=args)

        # upload CODE from snapshot_dir
        code_upload = args["code_upload"]
        code_omit = args["code_omit"]
        code_zip = args["code_zip"]
    
        fb.feedback("uploading files: ", add_seperator=False)
        copied_code_files = None

        if not fake_submit:
            if code_upload:
                # upload users CODE FILES
                copied_code_files = self.core.upload_before_files_to_job(job_id, snapshot_dir, "before/code", 
                    code_omit, code_zip, "code", args)

            # upload DATA from data_local (do we need to keep this?  should we upload to normal DATA location, vs. job?)
            data_upload = args["data_upload"]
            if data_upload:
                if not data_local:
                    errors.config_error("cannot do data-upload because no data-local path is defined in the XT config file")

                data_omit = args["data_omit"]
                data_zip = "none"

                self.core.upload_before_files_to_job(job_id, data_local, "before/data", data_omit, data_zip, "data", args)
        
        # dispatch to BACKEND submitters
        '''
        Note: backend submitter functions are responsible for:
            - submitting the job (for each node, queue runs for that node)
            - return service job id (or list of them if per node)
        '''
        code_uploaded_dir = snapshot_dir

        # change the snapshot_dir to a new dir that contains only files that were uploaded
        if not code_zip or code_zip == "none":
            pass
        elif copied_code_files:
            code_uploaded_dir = snapshot_base + "/code_uploaded"
            file_utils.ensure_dir_exists(code_uploaded_dir)
            
            for fn in copied_code_files:
                fn_dst = code_uploaded_dir + "/" + os.path.basename(fn)
                shutil.copyfile(fn, fn_dst)

        # SUBMIT JOB 
        service_job_info, service_info_by_node = \
            self.backend.submit_job(job_id, job_runs, workspace, compute_def, resume_name, 
                repeat_count, using_hp, runs_by_box, experiment, code_uploaded_dir, adjustment_scripts, args)

        # POST SUBMIT processing
        if not fake_submit:

            # mark runs as QUEUED
            self.log_runs_queued(runs_by_box, workspace, job_id, total_run_count, secrets_by_node, 
                service_info_by_node, args)

            fb.feedback("logging job")

            # write the job info file (now that backend has had a chance to update it)
            job_num = int(job_id[3:])

            xt_cmd = args["xt_cmd"]
            schedule = args["schedule"]
            concurrent = args["concurrent"]

            # this job property is used to ensure we don't exceed the specified # of runs when using repeat_count on each node
            dynamic_runs_remaining = None if search_style == "single" else total_run_count
            node_count = len(runs_by_box)

            # NOTE: for mongo v2, we only support schedule=static
            #child_runs_by_node, child_runs_key = self.store.database.build_child_runs_schedule_data(total_run_count, node_count)

            tag_dict = args["tags"]

            dd = {
                # JOB_INFO: flat READONLY props (18)
                "compute": compute, 
                "concurrent": concurrent,
                "exper_name": experiment, 
                "hold": args["hold"], 
                "job_id": job_id, 
                "job_num": job_num, 
                "job_guid": job_guid, 
                "job_secret": job_secret, 
                "node_count": node_count, 
                #"maximize_metric": args["maximize_metric"],      # not yet in DB/job_stats
                "primary_metric": args["primary_metric"], 
                "run_count": total_run_count, 
                "repeat": repeat_count, 
                "schedule": schedule, 
                "search_style": search_style,     
                "search_type": args["search_type"], 
                "username": args["username"], 
                "ws_name": workspace, 
                "xt_cmd": xt_cmd, 

                # embedded READONLY props (2)
                "pool_info": compute_def, 
                "service_job_info": service_job_info, 

                # JOB_STATS: flat UPDATABLE props (8)
                "completed_runs": 0, 
                "dynamic_runs_remaining": dynamic_runs_remaining, 
                "error_runs": 0, 
                "job_status": "submitted", 
                "running_nodes": 0, 
                "running_runs": 0, 
                "started": utils.get_arrow_time_str(), 

                # SERVICE_INFO: embedded READONLY props BY NODE (2)
                "runs_by_box": runs_by_box, 
                "service_info_by_node": service_info_by_node,
                
                # CONNECT_INFO: embedded UPDATABLE props (2)
                "connect_info_by_node": {}, 
                "secrets_by_node": secrets_by_node,  

                # job-detectable HPARAMS
                "hparams": job_hparams,

                # TAGS
                "tags": tag_dict,
            }

            self.store.log_job_info(workspace, job_id, dd)

        fb.feedback("done", is_final=True)

        escape = args["escape"]

        # update lastrun/lastjob info
        xtd = xt_dict.read_xt_dict()

        xtd["last_run"] = last_run
        xtd["last_job"] = job_id

        xt_dict.write_xt_dict(xtd)

        # return values for API support (X)
        return cmds, run_specs, using_hp, using_aml_hparam, sweeps_text, compute_def, job_id 

    def log_run_and_node(self, workspace, box_name, runs_by_box, job_id, total_run_count, secrets_by_node, 
        service_info_by_node, args):

        runs_for_box = runs_by_box[box_name]
        first_run = runs_for_box[0]
        run_name = first_run["run_name"]
        node_index = first_run["box_index"]
        node_count = len(runs_by_box)
        node_id = utils.node_id(node_index)

        box_secret = secrets_by_node[node_id]
        service_info = service_info_by_node[node_id]

        ws_name = args["workspace"]
        exper_name = args["experiment"]

        id_for_node = "{}/{}/{}".format(ws_name, job_id, node_index)

        # does format supports NODE INFO?
        if store_utils.STORAGE_FORMAT == "2":
            # create NODE_INFO record 
            self.write_node_info_data(id_for_node, ws_name, job_id, node_index, total_run_count, node_count, 
                box_name, run_name, box_secret, service_info, exper_name, args)

            # create NODE_STATS record 
            self.write_node_stats_data(id_for_node, ws_name)

            # create NODE_TAGS record 
            tag_list = args["tags"]
            td = utils.tag_dict_from_list(tag_list)
            self.write_node_tags_data(id_for_node, ws_name, job_id, td)

        # log QUEUED event for flat/parent run        
        self.store.log_run_event(workspace, run_name, "status-change", {"status": "queued"}, job_id=job_id) 

    def log_runs_queued(self, runs_by_box, ws_name, job_id, total_run_count, secrets_by_node, 
        service_info_by_node, args):

        from threading import Lock
        worker_lock = Lock()

        # create each run on a worker thread
        next_progress_num = 1
        box_name_list = list(runs_by_box.keys())

        def thread_worker(box_names, workspace):
            for box_name in box_names:
                nonlocal next_progress_num

                self.log_run_and_node(workspace, box_name, runs_by_box, job_id, total_run_count, 
                    secrets_by_node, service_info_by_node, args)

                with worker_lock:
                    node_msg = "logging runs: {}/{}".format(next_progress_num, len(box_name_list))
                    fb.feedback(node_msg, id="log_msg")  # , add_seperator=is_last)
                    next_progress_num += 1

        max_workers = args["max_workers"]

        # turn ON insert buffering
        self.store.database.set_insert_buffering(100)

        utils.run_on_threads(thread_worker, box_name_list, max_workers, [ws_name])

        # turn OFF insert buffering
        self.store.database.set_insert_buffering(0)

        # change status of all runs for this job to "queued", in database
        self.store.database.update_job_run_stats(ws_name, job_id, {"status": "queued"})

        # TODO: change all parent run status from created to queued with single:
        #   update [run_stats] set [status] = 'queued' where [_id] like 'ws4/job17_%'

    def build_all_node_runs(self, boxes, remote_control, run_count, total_run_count, 
        target_file, ps_path, using_hp, using_aml_hparam, run_specs, job_id, 
        parent_name, cmds, compute_def, repeat_count, fake_submit, search_style, job_runs, 
        secrets_by_node, is_distributed, service_type, args):

        # create each run on a worker thread
        thread_lock = Lock()   
        next_progress_num = 1

        def thread_worker(node_indexes, boxes, remote_control, run_count, total_run_count, 
            target_file, ps_path, using_hp, using_aml_hparam, run_specs, job_id, 
            parent_name, cmds, compute_def, repeat_count, fake_submit, search_style, job_runs, 
            secrets_by_node, is_distributed, service_type, run_names, args):

            node_count = len(node_indexes)

            for node_index in node_indexes:
                # generate a box secret for talking to XT controller for this node
                box_secret = str(uuid.uuid4()) if remote_control else ""
                run_name = run_names[node_index]

                run_data = self.build_first_run_for_node(node_index, run_count, total_run_count, 
                    boxes[node_index], target_file, ps_path, using_hp, using_aml_hparam, run_specs, job_id, 
                    parent_name, cmds, compute_def, repeat_count, fake_submit, search_style, box_secret, 
                    node_count, run_name=run_name, args=args)

                with thread_lock:
                    nonlocal next_progress_num

                    # for now, adhere to the more general design of multiple runs per box (to be removed)
                    box_runs = [run_data]      
                    job_runs.append(box_runs)

                    node_id = utils.node_id(node_index)            
                    secrets_by_node[node_id] = box_secret

                    # FEEDBACK 
                    ptype = "single " if search_style == "single" else "parent "
                    if is_distributed:
                        ptype = "master "

                    if run_count == 1:
                        node_msg = "creating {}run".format(ptype)
                    else:
                        node_msg = "creating {}runs: {}/{}".format(ptype, next_progress_num, run_count)

                    fb.feedback(node_msg, id="node_msg")  # , add_seperator=is_last)
                    next_progress_num += 1

        max_workers = args["max_workers"]
        node_index_list = range(len(boxes))

        # we want to create run names in "normal order" (not subject to random bg workers races)
        # so, we create all the run_names up-front
        ws_name = args["workspace"]
        is_parent = search_style != "single"

        run_names = []
        for node_index in node_index_list:
            run_name = self.store.database.get_next_run_name(ws_name, job_id, is_parent, total_run_count, node_index)
            run_names.append(run_name)

        args_for_worker = [boxes, remote_control, run_count, total_run_count, 
            target_file, ps_path, using_hp, using_aml_hparam, run_specs, job_id, 
            parent_name, cmds, compute_def, repeat_count, fake_submit, search_style, job_runs, 
            secrets_by_node, is_distributed, service_type, run_names, args]

        # turn ON insert buffering
        self.store.database.set_insert_buffering(100)

        utils.run_on_threads(thread_worker, node_index_list, max_workers, args_for_worker)

        # turn OFF insert buffering (and flush buffers)
        self.store.database.set_insert_buffering(0)

        # sort job_runs to normal order
        job_runs.sort(key=lambda r: r[0]["box_index"])

    def get_cmd_line_args_from_file(self, fn):
        with open(fn, "rt") as infile:
            text = infile.read()
            lines = text.split("\n")

        arg_parts = []

        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                # remove comments from line with arg(s)
                if "#" in line:
                    line = line.split("#", 1)[0]

                line = line.strip()
                if line:
                    parts = line.split()
                    arg_parts += parts

        hd = self.parse_script_args(arg_parts)
        return hd

    def build_job_hparams(self, cmd_parts):
        hparams = None

        # make copy to modify
        first_arg_index = None

        # first index of first script or app arg
        if cmd_parts[0].startswith("python"):

            # look for python options before script name
            for i, part in enumerate(cmd_parts[1:]):
                if not part.startswith("-"):
                    # found script at i+1
                    first_arg_index = i+2
                    break

        else:
            first_arg_index = 1

        if first_arg_index:
            pending_name = None

            args = cmd_parts[first_arg_index:]
            hparams = self.parse_script_args(args)

        return hparams

    def parse_script_args(self, args):
        hparams = {}
        pending_name = None

        for arg in args:
            '''
            look for arg/value in 3 forms:
                - arg=value
                - arg
                - arg value  (value is in following arg)
            '''
            if arg.startswith("-"):
                # strip the leading dashes
                arg = arg.lstrip("-")

                # found an arg name
                if "=" in arg:
                    name, value = arg.split("=")
                    hparams[name] = value
                    pending_name = None

                    if value.startswith("["):
                        # in-line HPARAM SEARCH specification
                        return None
                else:
                    # for now, treat as option without value
                    hparams[arg] = None
                    pending_name = arg
            elif arg.startswith("@"):
                fn = arg[1:]
                ad = self.get_cmd_line_args_from_file(fn)
                hparams.update(ad)
            else:
                # is this a value for a pending name?
                if pending_name:
                    hparams[pending_name] = arg
                    pending_name = None

                    if arg.startswith("["):
                        # in-line HPARAM SEARCH specification
                        return None

        return hparams if hparams else None

    def fixup_script_in_cmd(self, cmd):
        cmd_parts = utils.cmd_split(cmd)
        
        self.adjust_script_dir(cmd_parts)

        # add "-u" for python cmds
        if len(cmd_parts) > 1 and cmd_parts[0].startswith("python") and cmd_parts[1] != "-u":
            cmd_parts.insert(1, "-u")

        new_cmd = " ".join(cmd_parts)
        return new_cmd

    def read_user_multi_commands(self, using_hp, run_script, cmd_parts, args):
        '''
        args:
            using_hp: if True, we are doing a hyperparameter search
            run_script: the path to the ML script specified for the run command
            cmd_parts: the run command and args, in list form
            args: the big list of run command arguments, options, and flags

        processing:
            - there are 2 possible sources of user-generated commands:
                - the run script (if --multi-commands option was specified)
                - the config file (if it contains a "commands" outer property)
            
            - if using the run script for commands, it can be a text file
              (containing 1 command per line), or a .yaml file with the
              outer property constants.HPARAM_RUNSETS.

        returns:
            - if no commands or runsets found, returns None
            - else, returns (commands, runsets)
        '''
        cmds = None
        runsets = None
        
        lines = self.config.get("commands")
        multi_commands = args["multi_commands"]
 
        if lines:
            if using_hp:
                errors.combo_error("Cannot specify commands in config file with hyperparameter search")
            if multi_commands:
                errors.combo_error("Cannot specify commands in config file with --multi-commands")

            # commands specified in the config file
            args["multi_commands"] = True
            cmds = [self.fixup_script_in_cmd(line) for line in lines]

        elif multi_commands:
            if using_hp:
                errors.combo_error("Cannot specify --multi-commands with hyperparameter search")

            # read MULTI CMDS
            fn_script = args["script"]  # run_script if run_script else cmd_parts[0]
            ext = os.path.splitext(fn_script)[1]

            if ext == ".yaml":
                data = file_utils.load_yaml(fn_script)

                if not constants.HPARAM_RUNSETS in data:
                    errors.ConfigError("--multi-commands .yaml file is missing required section: {}".format( \
                        constants.HPARAM_RUNSETS))

                if not constants.HPARAM_COMMAND in data:
                    errors.ConfigError("--multi-commands .yaml file is missing required section: {}".format( \
                        constants.HPARAM_COMMAND))

                runsets = data[constants.HPARAM_RUNSETS]
                cmd = data[constants.HPARAM_COMMAND]
                cmds = [self.fixup_script_in_cmd(cmd)]
            else:
                lines = file_utils.read_text_file(fn_script, as_lines=True)
                lines = [line.strip() for line in lines if line and not line.strip().startswith("#")]
                cmds = [self.fixup_script_in_cmd(line) for line in lines]

        return (cmds, runsets) if cmds else None

    def gen_runsets_report(self, runsets):
        fn = os.path.expanduser("~/.xt/runsets.txt")
        fn = os.path.abspath(fn)

        with open(fn, "wt") as outfile:
            for rs in runsets:
                outfile.write("runset: {}\n".format(rs))

        console.print("--> to view generated HP runsets, see the file: {}".format(fn))

    def build_cmds_with_search(self, service_type, cmd_parts, parent_script, run_script, run_cmd_from_script, 
        use_controller, dry_run, args):
        '''
        args:
            - service_type: the type of backend service being used (aml, batch, etc.)
            - cmd_parts: list of the user's ML app and arg/options 
            - parent_script: user-specified script that needs to be run to configure box for all child runs
            - run_script: if user app is a shell script or command line .bat file, the text of file
            - run_cmd_from_script: if user's ML app is a shell or command line script, the run command located within it
            - use_controller: if False, XT controller is not being used (direct run)
            - dry_run: if True, job will not be submitted (user just wants to see list of static runs)

        processing:
            - determine the search_style needed, the associated list of user commands, and the total number of runs

        returns:
            - cmds: the list of 1 or more commands to be run
            - run_count: to total number runs to be executed
            - repeat_count: if number of runs per node (approximately)
            - run_specs: a dictionary of run information (easier to pass around)
            - using_hp: if True, a static or dynamic hyperparameter search is being done
            - using_aml_hparam: if True, we are doing a direct-run AML hyperparameter search
            - sweeps_text: hyperparameter search specs 
            - search_style: one of: single, multi, repeat, static, dynamic
        '''
        using_hp = False
        show_run_report = True
        repeat_count = None
        using_aml_hparam = False
        search_style = None
        cmds = None
        runsets = None
        run_count = None

        # get run_cmd
        run_cmd = run_cmd_from_script
        if not run_cmd:
            run_cmd = " ".join(cmd_parts)

        # by default, we return same cmd
        new_run_cmd = run_cmd

        is_aml = (service_type == "aml")        # self.is_aml_ws(workspace)
        use_aml_for_hparam = (is_aml and not use_controller)

        # get info about nodes/boxes
        boxes, _, service_type = box_information.get_box_list(self.core, args=args)
        node_count = len(boxes)

        # HPARAM SEARCH
        cmds, runsets, sweeps_text, new_run_cmd = self.build_static_hparam_cmds(run_cmd, node_count, args)
        
        # NOTE: if runsets is not None, then this is a static search where user needs YAML files generated for each child run 
        #       if this is a static search and runsets is None, then runsets have already been applied to cmdlines

        if runsets is not None:
            show_run_report = False
            
        using_hp = not(not sweeps_text)
        if using_hp and use_aml_for_hparam:
            using_aml_hparam = True
            # for AML hyperdrive, we pass only constant args from cmd_parts
            #cmd_parts = [tp for tp in template_parts if tp != '{}']

        if runsets:
            self.gen_runsets_report(runsets)

        if cmds:
            # STATIC HPARAM SEARCH
            #run_count = len(runsets) if runsets else len(cmds)
            run_count = len(cmds)
            #runsets = None      # do not process further in controller
            search_style = "static"

        runs = args["runs"]
        max_runs = args["max_runs"]
        node_repeat = args["node_repeat"]

        # USER MULTI CMDS
        result = self.read_user_multi_commands(using_hp, run_script, cmd_parts, args)
        if result:
            cmds, runsets = result

            # set run_count 
            result_count = len(runsets) if runsets else len(cmds)

            if runs:
                run_count = runs
            elif max_runs:
                run_count = min(max_runs, result_count)
            else:
                run_count = result_count

            search_style = "multi"
            new_run_cmd = cmds[0]

        if not cmds:
            # SINGLE CMD 
            # DYNAMIC HPARAM or REPEAT or SINGLE search style

            # we will use repeat_count on each node, as needed, to reach specified runs
            run_count = runs if runs else node_count 
            
            if using_hp:
                search_style = "dynamic"
            else:
                search_style = "repeat" if run_count > 1 else "single"

            if search_style != "single":
                repeat_count = math.ceil(run_count / node_count)

            cmds = [new_run_cmd]
            show_run_report = False

        if node_repeat:
            # duplicate cmds so they are repeated N times on each node
            # nodes are assigned runs in round-robin fashion
            new_cmds = []
            for cmd in cmds:
                new_cmds += [cmd]*node_repeat
            
            cmds = new_cmds
            run_count = len(cmds)

        if show_run_report:
            console.print()   
            dr = " (dry-run)" if dry_run else ""
            search_type = args["search_type"]
            stype = "(search-type=" + search_type + ") " if search_style=="static" else ""

            console.print("{} {}runs{}:".format(search_style, stype, dr))

            if node_repeat:
                runsets = None
                search_style = "static"
                node_index = -1

                for i, run_cmd_parts in enumerate(cmds):
                    if i % node_repeat == 0:
                        node_index += 1

                    node_id = utils.node_id(node_index)
                    console.print("  {}. {} ({})".format(i+1, run_cmd_parts, node_id))
            else:
                if runsets:
                    console.print("  command: {}".format(cmds[0]))
                    console.print("  runsets:")

                    for i, runset in enumerate(runsets):
                        console.print("    {}. {}".format(i+1, runset))
                else:
                    for i, run_cmd_parts in enumerate(cmds):
                        console.print("  {}. {}".format(i+1, run_cmd_parts))

            console.print()   

        # finally, package info into run_specs to make info easier to pass thru various APIs
        new_cmd_parts = utils.cmd_split(new_run_cmd)
        run_specs = {"cmd_parts": new_cmd_parts, "run_script": run_script, "run_cmd": new_run_cmd, "parent_script": parent_script}

        return cmds, runsets, run_count, repeat_count, run_specs, using_hp, using_aml_hparam, sweeps_text, search_style

    def build_static_hparam_cmds(self, cmd_line, node_count, args):
        '''
        args:
            - cmd_line: user's ML app and its arguments
            - args: dictionary of XT run cmd args/options

        processing:
            - gather hyperparameter search specs from either special app command line options or
              user-specified hp-config file (.yaml)
            - if doing random or grid search, generate the commands that comprise
              the search
             
        return:
            - generated run commands
            - runsets (a list of runset dicts)
            - the search specs (sweeps text)
            - the run cmd (with hp search options removed, if any found)
        '''
        num_runs = args["runs"]
        max_runs = args["max_runs"]
        option_prefix = args["option_prefix"]
        search_type = args["search_type"]
        fn_sweeps = args["hp_config"]
        static_search = args["static_search"]

        # if not cmd_line:
        #     cmd_line = " ".join(cmd_parts)

        # default return values
        run_cmd = cmd_line
        sweeps_text = None
        run_cmds = None
        runsets = None

        # gather hyperparameters (command line options or hp-search.yaml file)
        if search_type != None:
            hp_client = HPClient()
            dd = {}
            
            if option_prefix:
                # see if hp search params specified in ML app's command line options
                dd, run_cmd = hp_client.extract_dd_from_cmdline(cmd_line, option_prefix)

            if not dd and fn_sweeps:
                # get hp search params from search.yaml file
                dd = hp_client.yaml_to_dist_dict(fn_sweeps)

            if dd:
                # write parameters to YAML file for run record 
                # and use by dynamic search, if needed
                sweeps_yaml = hp_client.dd_to_yaml(dd)
                sweeps_text = yaml.dump(sweeps_yaml)
                
                # should we preform the search now?
                if (search_type == "grid") or (static_search and search_type in ["random"]):
                    runsets = hp_client.generate_hp_sets(dd, search_type, num_runs, max_runs, node_count)
        
                    if option_prefix and option_prefix in cmd_line:
                        # apply runsets to run_cmd to generate cmd list
                        cmd_line_base = run_cmd
                        run_cmds = hp_client.generate_runs(runsets, cmd_line_base)
                        runsets = None    # since we have applied them to run_cmds
                    else:
                        # controller will use runsets when launching each child run (and generate a runset yaml file to be read by that child)
                        # run_cmds = [cmd_line]
                        run_cmds = len(runsets)*[cmd_line]   # duplicate the cmd_line for each run_set

                else:
                    # dynamic HP
                    pass
                #print("{} commands generated".format(len(run_cmds)))

        return run_cmds, runsets, sweeps_text, run_cmd

# flat functions
def update_compute_def_from_cmd_options(compute_def, hold=False):

    compute_props = ["vm-size", "azure-image", "low-pri", "box-class", "docker", "setup", "boxes", 
        "vc", "cluster", "queue", "sku", "nodes"]

    # apply any compute-def properties found in explicit args to compute_def
    explict_opts = qfe.get_explicit_options()

    for name, value in explict_opts.items():
        if name in compute_props:
            compute_def[name] = value

    # if "hold" specified and queue not explictly set, queue defaults to "interactive"
    if hold and "cluster" in compute_def and "queue" not in explict_opts:
        compute_def["queue"] = "interactive"

            
