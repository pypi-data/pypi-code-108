#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# backend_batch.py: support for running a XT job on a 1-N Azure Batch Compute boxes.

from calendar import c
import os
import io
import sys
import math
import time
import datetime
import numpy as np
from interface import implements
from threading import Lock
from datetime import timedelta

from xtlib import utils
from xtlib import errors
from xtlib import scriptor
from xtlib import constants
from xtlib import job_helper
from xtlib import file_utils
from xtlib import store_utils
from xtlib.console import console
from xtlib.helpers.xt_config import XTConfig
from xtlib.report_builder import ReportBuilder
from xtlib.helpers.feedbackParts import feedback as fb
from xtlib.helpers.key_press_checker import KeyPressChecker

from .backend_interface import BackendInterface
from .backend_base import BackendBase

# azure library, loaded on demand
batch = None   
azureblob = None
azuremodels = None
batchmodels = None

class AzureBatch(BackendBase):
    ''' 
    This class submits and controls Azure Batch jobs.  Submit process consists of:
        - building a "node_record" that describes how to launch each node
        - call the appropriate Batch SDK API's to build a batch job and launch it.

    Building a node record:
        - create a Batch ResourceFile for each input file and the expected output files
        - wraps the command(s) for the node by prefixing these commands:

            unzip CODE_ZIP_FN               (the user's source tree)
            conda activate py36             (activate py36 known good ML environment)
            pip install xtlib               (for controller and/or user's script)
            export XT_NODE_ID=nodeNN        (for controller to get his run info from the MRC file)
    '''

    def __init__(self, compute, compute_def, core, config, username=None, arg_dict=None):
        super(AzureBatch, self).__init__(compute, compute_def, core, config, username, arg_dict)

        # import azure libraries on demand
        global azureblob, batchmodels, batch
        import azure.storage.blob as azureblob
        import azure.batch.models as batchmodels
        import azure.batch as batch
        # CAUTION: "batchmodels" is NOT the same as batch.models

        if not compute_def:
            compute_def = config.get_target_def(compute)

        self.compute = compute
        self.compute_def = compute_def
        self.core = core
        self.config = config
        self.username = username
        self.custom_image_name = None

        # first, ensure we have a config file
        if config:
            self.config = config
        else:
            self.config = self.core.config

        self.store = self.core.store if core else None
        self.batch_job = None

        store_creds = self.config.get_storage_creds()
        store_name = store_creds["name"]
        store_key = store_creds["key"]
        self.store_name = store_name

        blob_client = azureblob.BlockBlobService(account_name=store_name, account_key=store_key)
        blob_client.retry = utils.make_retry_func()
        self.blob_client = blob_client
        self.batch_client = None
        #console.print("blob_client=", blob_client)

    def get_name(self):
        return "batch"

    # API call
    def provides_container_support(self):
        '''
        Returns:
            returns True if docker run command is handled by the backend.
        Description:
            For Azure Batch, we use the XT-level container support. We had problems getting the Azure Batch container support to work.
        '''
        return False

    def adjust_run_commands(self, job_id, job_runs, using_hp, experiment, service_type, snapshot_dir, args):
        '''
        This method is called to allow the backend to inject needed shell commands before the user cmd.  At the
        time this is called, files can still be added to snapshot_dir.
        '''
        store_data_dir, data_action, data_writable, store_model_dir, model_action, model_writable,  \
            storage_name, storage_key = self.get_action_args(args)

        # local or POOL of vm's
        fn_wrapped = None     # we use same cmd on each box/job
        username = args["username"]
        nowrap = args["nowrap"]

        for i, box_runs in enumerate(job_runs):
            node_id = "node" + str(i)
            br = box_runs[0]
            box_info = br["box_info"]
            run_name = br["run_name"]
            actions = ["data", "model"]
            box_secret = br["box_secret"]

            is_windows = False

            run_specs = br["run_specs"]
            cmd_parts = run_specs["cmd_parts"]

            if nowrap:
                # run user's script directly
                fn_direct = os.path.basename(args["script"])
                #run_specs["cmd_parts"] = ["echo i was here; ls -lt; echo bye now"]   # [fn_direct]
                cmd = "/bin/bash --login -c 'echo starting script: {}; {}; echo script ended'".format(fn_direct, fn_direct)
                run_specs["cmd_parts"] = [cmd]
            
            else:
                # just create the fn_wrapped for the first node (but use for all nodes)
                if i == 0:
                    node_cmd = " ".join(cmd_parts)

                    fn_wrapped = self.wrap_cmd_for_batch(node_cmd, node_id, store_data_dir, data_action, data_writable, 
                        store_model_dir, model_action, model_writable, storage_name, storage_key, snapshot_dir, 
                        box_secret, args)

                # NOTE: we pass the NODE_INDEX and RUN_NAME as parameters to the fn_wrapped script
                # so that we can share a single script among all nodes
                wrapped_parts = ['/bin/bash', '--login', '{} {} {}'.format(os.path.basename(fn_wrapped), i, run_name)]
                run_specs["cmd_parts"] = wrapped_parts

                merge_batch_logs = args["merge_batch_logs"]
                if merge_batch_logs:
                    # recompose this command to pass along all script arguments
                    wrapped_parts = ['/bin/bash', '--login', '{} $*'.format(os.path.basename(fn_wrapped))]
        
                    # create a STDBOTH.tmp that merged stdout and stderr
                    node_cmd = "{} > ../stdboth.tmp 2>&1 && cp ../stdboth.tmp ../stdboth.txt".format(" ".join(wrapped_parts))

                    # create a helper file to call our node cmd
                    fn_helper = snapshot_dir + "/" + constants.FN_BATCH_HELPER
                    file_utils.write_text_file(fn_helper, node_cmd)

                    run_specs["cmd_parts"] = ["bash", constants.FN_BATCH_HELPER, str(i), run_name]

                    console.diag(run_specs)

    def wrap_cmd_for_batch(self, user_cmd, node_id, store_data_dir, data_action, data_writable, 
        store_model_dir, model_action, model_writable, storage_name, storage_key, snapshot_dir, box_secret, args):

        cmds = []
        
        gen_for_windows = False
        self.capture_setup_cmds = args["capture_setup_cmds"]

        # default for backends is to pass these 2 args to their __wrapped__.xx script (philly is different)
        node_id = "node$1"
        run_name = "$2"
        docker_cmd = args["docker_cmd"]
        job_id = args["job_id"]

        # for wrapper building functions to access 
        self.node_id = node_id
        self.run_name = run_name
        
        add_pre_cmds = False

        if add_pre_cmds:
            # add env vars (the Batch Task environment_setting property seems to be broken
            env_vars = dict(args["env_vars"])
            scriptor.add_controller_env_vars(env_vars, self.config, box_secret, None)

            self.append_title(cmds, "PRE-SETUP cmds:")
            for name, value in env_vars.items():
                cmd = "export {}={}".format(name, value)
                self.append(cmds, cmd)

        # our initial working dir: .../wd
        # this will change us to: .../wd/.xt/cwd
        self.add_first_cmds(cmds, homebase="$HOME", cwd="$HOME/.xt/cwd", args=args)

        self.append_title(cmds, "UNZIP code/bootstrap files:")

        # unzip files from wd to current directory
        if docker_cmd:
            fn_bootstrap = "/usr/src/" + constants.CODE_ZIP_FN
            self.append_unzip(cmds, fn_bootstrap, ".")
        else:
            fn_bootstrap = "../../" + constants.CODE_ZIP_FN
            self.append_unzip(cmds, fn_bootstrap, ".")
            self.append(cmds, "rm {}".format(fn_bootstrap))

        self.append_dir(cmds)

        super().add_setup_cmds(cmds, remove_zip=False, gen_for_windows=gen_for_windows, 
            args=args)

        super().add_other_cmds(cmds, args)
        super().add_report_cmds(cmds, args=args)

        # since node id is the only different between nodes (in this __wrapped__.sh file), make it a parameter
        self.append(cmds, 'export XT_NODE_ID=node$1')       #  + node_id)

        actions = ["data", "model"]

        # try to install blobfuse, but it may already be installed on some images
        install_blobfuse = True

        # sudo is available, but causes problems with subsequent MNT directory access
        sudo_available = False     

        self.add_mount_cmds(cmds, sudo_available, storage_name, storage_key, 
            actions, data_action, model_action, store_data_dir, store_model_dir, data_writable, model_writable,
            use_username=False, use_allow_other=False, install_blobfuse=install_blobfuse, args=args)

        fn_wrapped = self.create_wrapper_and_inner(cmds, user_cmd, sudo_available, args)
        return fn_wrapped

    def print_things(self, things, columns):
        
        if not things:
            print("no matches found\n")
            return
            
        # convert to a list of dict items
        things = [thing.__dict__ for thing in things]

        for thing in things:
            created = thing["creation_time"]
            now = datetime.datetime.now(tz=created.tzinfo)
            elapsed = now - created
            thing["created"] = str(created)
            thing["elapsed"] = str(elapsed)

        lb = ReportBuilder(self.config, self.store)
        text, rows = lb.build_formatted_table(things, columns)
        console.print(text)

    def match_stage(self, job, stage_flags):
        
        state = job.state
        if state == "active":  # this means 'queued' for batch
            match = "queued" in stage_flags
        elif state == "completed":
            match = "completed" in stage_flags
        else:
            match = "active" in stage_flags

        return match

    def view_status(self, run_name, workspace, job, monitor, escape_secs, auto_start, 
            stage_flags, status, max_finished):

        if not self.batch_client:
            self.create_batch_client()

        # get/report JOBS
        jobs = self.batch_client.job.list()

        # filter jobs by stage
        jobs = [job for job in jobs if self.match_stage(job, stage_flags)]

        console.print("\ntarget={} jobs:".format(self.compute))

        self.print_things(jobs, ["id", "state", "created", "elapsed"])

        # get/report POOLS

        if "active" in stage_flags:
            pools = self.batch_client.pool.list()
            console.print("\ntarget={} pools:".format(self.compute))

            self.print_things(pools, ["id", "state", "created", "elapsed"])

    def make_batch_job_id(self, ws_name, job_id):
        # qualify job_id with store_name and ws_name to minimize duplicate job names
        store_name = self.config.get("store")
        name = "{}__{}__{}".format(store_name, ws_name, job_id)
        return name
        
    def submit_job(self, job_id, job_runs, workspace, compute_def, resume_name, 
            repeat_count, using_hp, runs_by_box, experiment, snapshot_dir, controller_scripts, args):
        '''
        This runs the controller on one or more boxes within an Azure Batch pool.
        '''
        #console.print("pool_info=", pool_info)

        vm_size = compute_def["vm-size"]
        vm_image = utils.safe_value(compute_def, "azure-image")
        num_nodes = compute_def["nodes"]
        use_low_pri = compute_def["low-pri"]

        if num_nodes is None:
            num_nodes = 0

        if num_nodes <= 0:
            errors.config_error("nodes must be > 0")
        
        search_type = args["search_type"]
        multi_commands = args["multi_commands"]
        
        static_run_cmds = (search_type == "grid" or multi_commands)

        # fb.feedback("azure-batch (vm_size={}, vm_image={}, num_nodes={}, use_low_pri={})".format(vm_size, vm_image, 
        #     num_nodes, use_low_pri), is_final=static_run_cmds)

        ws_name = args["workspace"]
        is_distributed = args["distributed"]
        merge_batch_logs = args["merge_batch_logs"]

        # first, build a list of runs for each node in our azure batch pool
        node_records = []
        service_info_by_node = {}

        self.prep_all_nodes(job_id, job_runs, num_nodes, use_low_pri, using_hp, experiment, 
            static_run_cmds, node_records, workspace, service_info_by_node, merge_batch_logs, args)

        # "hold" is now used to hold open the xt controller task AND the created pool
        auto_pool = not args["hold"]

        fb.feedback("submitting job to batch")

        # finally, launch the job on AZURE BATCH
        pool_id = self.launch(job_id, node_records, auto_pool=auto_pool, ws_name=ws_name, vm_size=vm_size, 
            vm_image=vm_image, num_nodes=num_nodes, use_low_pri=use_low_pri, is_distributed=is_distributed, args=args)

        service_run_info = {"batch_job_id": self.batch_job_id, "pool_id": pool_id}

        return service_run_info, service_info_by_node    

    def prep_all_nodes(self, job_id, job_runs_list, num_nodes, use_low_pri, using_hp, exper_name, 
        static_run_cmds, node_records, workspace, service_info_by_node, merge_batch_logs, args):

        # create each run on a worker thread
        next_progress_num = 1
        job_count = len(job_runs_list)
        thread_lock = Lock()

        def thread_worker(job_runs, job_id, num_nodes, use_low_pri, 
                using_hp, exper_name, static_run_cmds, args):

            # process a subset of all jobs on this thread
            for run_data_list in job_runs:
                
                node_index = run_data_list[0]["node_index"]

                node_record = self.prep_node(job_id, node_index, run_data_list, num_nodes, use_low_pri, 
                    using_hp=using_hp, exper_name=exper_name, static_run_cmds=static_run_cmds, args=args)

                with thread_lock:
                    nonlocal next_progress_num

                    node_records.append(node_record)

                    node_msg = "building nodes: {}/{}".format(next_progress_num, job_count)

                    fb.feedback(node_msg, id="node_msg")  # , add_seperator=is_last)
                    next_progress_num += 1

                    node_id = "node" + str(node_index)
                    batch_job_id = self.make_batch_job_id(workspace, job_id)

                    service_info_by_node[node_id] = {"workspace": workspace, "job_id": job_id, "batch_job_id": batch_job_id, 
                        "node_id": node_id, "task_index": node_index, "merge_batch_logs": merge_batch_logs}

        # create each Batch Task on a worker thread
        max_run_workers = args["max_workers"]
        utils.run_on_threads(thread_worker, job_runs_list, max_run_workers, [job_id, num_nodes, use_low_pri, 
                using_hp, exper_name, static_run_cmds, args])

        # sort node_records to normal order
        node_records.sort(key=lambda r: r["node_index"])

    def prep_node(self, job_id, node_index, run_data_list, num_nodes, use_low_pri, using_hp,  
            exper_name, static_run_cmds, args):
        '''prepare runs for node node_index'''

        first_run = run_data_list[0]
        box_info = first_run["box_info"]

        box_name = "{}-{}-{}".format(job_id, "batch", node_index)
        
        # target_sh, node_cmd, fn_context, fn_sh, run_names = self.prep_for_controller_run(run_data_list, node_index, job_id, tmp_dir, using_hp, 
        #     box_info, exper_name, args=args)
        run_names = ", ".join([rd["run_name"] for rd in run_data_list])

        # build RESOURCE FILES for each file we have uploaded into "before"  directory
        before_path = "before/code"      # job store
        after_path = "nodes/node{}/after/service_logs".format(node_index)         # run store

        # use blob service from store 
        store_provider = self.store.helper.provider

        # get list of BEFORE blobs (captured by runner, with controller adjustments)
        before_blob_path = file_utils.path_join(constants.JOBS_DIR, job_id, before_path)

        workspace = args["workspace"]
        jobs_container = store_utils.get_jobs_container(workspace)

        fake_submit = utils.safe_value(args, "fake_submit")

        # BATCH BUG WORKAROUND: tried to create a resource file for FOLDER instead of enumerating all blobs
        # but always get "blob not found" error (before, before/, before/** - no form works)
        #blob_names = [before_blob_path + "/**"]
        blob_names = store_provider.list_blobs(jobs_container, before_blob_path)

        if not fake_submit:
            assert len(blob_names) > 0

        # for the DEST FILENAME on the node, strip off the blob path prefix
        bbp_len = 1 + len(before_blob_path)    # +1 to remove the trailing "/"
        node_file_names = [ bn[bbp_len:] for bn in blob_names ]

        #console.diag("  local_file_names=" + str(local_file_names))
        console.diag("  files uploaded to blobs: " + str(blob_names))
        console.diag("  node_file_names=" + str(node_file_names))

        # use our helper to convert blobs and filenames to resource files
        node_res_files = self.convert_blobs_to_resource_files(jobs_container, blob_names, node_file_names)

        # convert OUTPUT WILDCARDS to output files
        output_file_list = ["controller.log", "../*.txt"]

        after_blob_path = constants.JOBS_DIR + "/" + job_id + "/" + after_path
        job_container = workspace if store_utils.STORAGE_FORMAT == "2" else constants.INFO_CONTAINER_V1
        node_output_files = self.build_output_files(job_container, after_blob_path, output_file_list)

        # if static_run_cmds:
        #     fb.feedback("  adding node: {}, run(s): {}".format(box_name.upper(), run_names.upper()), is_final=True)

        node_specs = first_run["run_specs"]
        box_secret = first_run["box_secret"]
        node_cmd = " ".join(node_specs["cmd_parts"])

        return {"node_cmd": node_cmd, "node_res_files": node_res_files, "node_output_files": node_output_files, 
            "box_secret": box_secret, "node_index": node_index}

    def launch(self, job_id, node_records, auto_pool=True, description=None, ws_name=None, 
            vm_size=None, vm_image=None, num_nodes=1, use_low_pri=True, is_distributed=False, args=None):
        
        fake_submit = utils.safe_value(args, "fake_submit")

        self.auto_pool = auto_pool
        self.description = description

        workspace = args["workspace"]
        batch_job_id = self.make_batch_job_id(workspace, job_id)

        self.batch_job_id = batch_job_id
        self.pool_id = "_pool_{}_{}_".format(workspace, job_id)

        self.vm_size = vm_size
        self.azure_image = vm_image 
        self.num_nodes = num_nodes 
        self.use_low_pri = use_low_pri 

        self.start_time = datetime.datetime.now().replace(microsecond=0)

        self.create_batch_client(args)

        if not fake_submit:
            # create our pool and job together 
            self.create_pool_and_job(is_distributed, args)
            
        # add the specified tasks (commands) to our job
        self.add_tasks_to_job(node_records, args)

        # job is now launched (usually remained queued for 2-4 minutes, then starts running)
        return self.pool_id      # may have changed (for auto_pool=True, the default)

    def create_batch_client(self, args=None):
        # create a batch_client to handle most of our azure needs
        if args:
            target = args["target"]
            target_def = args["compute_def"]
        else:
            target = self.compute
            target_def = self.compute_def
            
        service_name = utils.safe_value(target_def, "service")
        if not service_name:
            errors.config_error("{} '{}' missing 'service' property in [compute-targets] of XT config file".format("target", target))

        # validate BATCH credentials
        batch_creds = self.config.get_service(service_name)

        batch_name = service_name
        batch_key = batch_creds["key"]
        batch_url = batch_creds["url"]

        # import azure libraries on demand
        import azure.batch.batch_auth as batch_auth

        #console.print("batch_name={}, batch_key={}, batch_url={}".format(batch_name, batch_key, batch_url))

        credentials = batch_auth.SharedKeyCredentials(batch_name, batch_key)
        batch_client = batch.BatchServiceClient(credentials, batch_url= batch_url)
        
        batch_client.retry = utils.make_retry_func()
        self.batch_client = batch_client

    def get_external_port(self, port_name, node):
        port = None
        ip_addr = None

        for ep in node.endpoint_configuration.inbound_endpoints:
            if ep.name.startswith(port_name):
                # found our address for the specified node_index
                ip_addr = ep.public_ip_address
                port = ep.frontend_port
                break

        return ip_addr, port

    def get_client_cs(self, service_node_info):
        '''
        Args:
            service_node_info: info that service maps to a compute node for a job
        Returns:
            {"ip": value, "port": value, "box_name": value}
        '''
        cs = None

        job_id = service_node_info["job_id"]
        node_id = service_node_info["node_id"]
        node_index = utils.node_index(node_id)
        workspace = service_node_info["workspace"]

        state, ip_addr, controller_port, tensorboard_port = \
            self.get_azure_box_addr(workspace, job_id, node_index)

        if not (ip_addr and controller_port):
            errors.service_error("Node not available (node state: {})".format(state))

        if ip_addr and controller_port:
            cs = {"ip": ip_addr, "port": controller_port, "box_name": node_id}

        return cs

    def get_azure_box_addr(self, ws_name, job_id, node_index):
        ip_addr = None
        port = None
        state = None
        controller_port = None
        tensorboard_port = None

        if not self.batch_client:
            self.create_batch_client()

        # XT always has exactly 1 task running on each node (xt controller), so
        # we can reply on task[x] running on node index x
        batch_job_name = self.make_batch_job_id(ws_name, job_id)
        task_id = "task" + str(node_index)
        task = self.batch_client.task.get(batch_job_name, task_id)

        state = task.state
        if state in ["running", "completed"]:
            node_info = task.node_info
            pool_id = node_info.pool_id
            node_id = node_info.node_id

            try:
                #console.print("job_id=", job_id, ", pool_id=", pool_id, ", mode_id=", node_id)
                node = self.batch_client.compute_node.get(pool_id, node_id)
                #console.print("node.ip_address=", node.ip_address)

                ip_addr, controller_port = self.get_external_port("xt-controller", node)
                ip_addr, tensorboard_port = self.get_external_port("xt-tensorboard", node)
            except BaseException as ex:
                # treat any exception here as the pool being deallocated
                state = "deallocated"

        return state, ip_addr, controller_port, tensorboard_port

    def wait_for_job_completion(self, max_wait_minutes=60):
        # Pause execution until tasks reach Completed state.
        completed = self.wait_for_tasks_to_complete()

    def port_request(self, port_num, port_name, base_offset, rules):
        pr = batchmodels.InboundNATPool(
            name=port_name, 
            protocol='tcp', 
            # NOTE: client machine should connect to the Azure Batch app using the port that is dynamically ASSIGNED 
            # to the node (node_index + AZURE_BATCH_BASE_CONTROLLER_PORT).
            # Note: Azure Batch node should listen via the CONTROLLER_PORT
            backend_port=port_num,   
            frontend_port_range_start=base_offset + constants.AZURE_BATCH_BASE_CONTROLLER_PORT, 
            frontend_port_range_end=base_offset + 500 + constants.AZURE_BATCH_BASE_CONTROLLER_PORT,
            network_security_group_rules=rules)

        return pr

    def create_network_config(self):
        '''open port CONTROLLER_PORT for incoming traffic on all nodes in pool '''
        rules = network_security_group_rules=[

                # for CONTROLLER PORT
                batchmodels.NetworkSecurityGroupRule(priority=179, access=batchmodels.NetworkSecurityGroupRuleAccess.allow,
                    source_address_prefix='*'),
                
                # for TENSORBOARD PORT
                batchmodels.NetworkSecurityGroupRule(priority=181, access=batchmodels.NetworkSecurityGroupRuleAccess.allow,
                    source_address_prefix='*')
            ]

        nat_pools = []
        nat_pools.append(self.port_request(constants.CONTROLLER_PORT, "xt-controller-rpc", 0, [rules[0]]))
        nat_pools.append(self.port_request(constants.TENSORBOARD_PORT, "xt-tensorboard-run", 600, [rules[1]]))

        pep_config = batchmodels.PoolEndpointConfiguration(inbound_nat_pools=nat_pools)
        network_config = batchmodels.NetworkConfiguration(endpoint_configuration=pep_config)

        return network_config

    def create_pool_and_job(self, is_distributed, args):
        # get the required Azure VM image 
        props = self.config.get("azure-batch-images", self.azure_image)
        if not props:
            errors.config_error("No config file entry found in [azure-batch-images] section for azure-image=" + self.azure_image)

        publisher =  utils.safe_value(props, "publisher")
        offer =  utils.safe_value(props, "offer")
        sku =  utils.safe_value(props, "sku")
        version =  utils.safe_value(props, "version")
        node_agent_sku_id =  utils.safe_value(props, "node-agent-sku-id")
        custom_image_id = utils.safe_value(props, "custom-image-id")

        if custom_image_id:
            # supply a custom OS image for each node in the pool
            img_ref = batchmodels.ImageReference(virtual_machine_image_id=custom_image_id)
            vmc = batchmodels.VirtualMachineConfiguration(image_reference=img_ref, node_agent_sku_id=node_agent_sku_id)

        else:
            # use a Microsoft published image
            img_ref = batchmodels.ImageReference(publisher=publisher, offer=offer, sku=sku, version=version)
            vmc = batchmodels.VirtualMachineConfiguration(image_reference=img_ref, node_agent_sku_id=node_agent_sku_id)

        # support for running a user-specified custom container
        target = self.compute

        # docker_name = args["docker"]
        # docker_image, login_server, docker_registry = self.config.get_docker_info(target, docker_name, required=False)

        # if docker_image:

        #     # create/assign container_config
        #     container_config = batch.models.ContainerConfiguration()
        #     vmc.container_configuration = container_config

        #     creds_required = utils.make_numeric_if_possible( utils.safe_value(docker_registry, "login") )
        #     if creds_required:
        #         # get username/password to log into private docker registry service (Azure)
        #         username = utils.safe_value(docker_registry, "username")
        #         password = utils.safe_value(docker_registry, "password")

        #         # create/add registry
        #         container_registry = batch.models.ContainerRegistry(registry_server=login_server, user_name=username, password=password)
        #         container_config.container_registries = [container_registry]
            
        #     # create/add container_config
        #     self.custom_image_name = login_server + "/" + docker_image
        #     container_config.container_image_names = [self.custom_image_name]

        network_config = self.create_network_config()

        #max_tasks_per_node = None
        enable_inter_node_communication = False

        #console.print("is_distributed=", is_distributed)
        
        if is_distributed:
            #max_tasks_per_node = 1
            enable_inter_node_communication = True

        if self.auto_pool:

            # this was working, but looks like it stopped (as of 11/22/2019 - rfernand2)
            # create a dynamically allocated pool
            #dynamic_resize = True
            dynamic_resize = False

            if dynamic_resize:
                target_name = "$TargetLowPriorityNodes" if self.use_low_pri else "$TargetDedicatedNodes"
                target_count = self.num_nodes

                # lots of work here to specify: release nodes when their only task has completed
                formula = ""
                formula += "pending = max(0, $PendingTasks.GetSample(1)); "
                formula += "succeeded = max(0, $SucceededTasks.GetSample(1)); "
                formula += "failed = max(0, $FailedTasks.GetSample(1)); "
                formula += "{} = (pending + succeeded + failed) ? pending : {}; ".format("target_name", target_count)
                formula += "$NodeDeallocationOption = taskcompletion; "

                pool_spec = batch.models.PoolSpecification(
                    #id=self.pool_id,
                    virtual_machine_configuration=vmc,
                    vm_size=self.vm_size,
                    network_configuration=network_config,
                    enable_auto_scale=True,
                    auto_scale_formula=formula,
                    #max_tasks_per_node = max_tasks_per_node,
                    enable_inter_node_communication=enable_inter_node_communication)
            else:
                pool_spec = batch.models.PoolSpecification(
                    #id=self.pool_id,
                    virtual_machine_configuration=vmc,
                    vm_size=self.vm_size,
                    network_configuration=network_config,
                    target_dedicated_nodes=0 if self.use_low_pri else self.num_nodes,
                    target_low_priority_nodes=self.num_nodes if self.use_low_pri else 0,
                    #max_tasks_per_node = max_tasks_per_node,
                    enable_inter_node_communication=enable_inter_node_communication)

            auto_pool = batch.models.AutoPoolSpecification(pool_lifetime_option="job", keep_alive=False, pool=pool_spec)
            pool_info = batch.models.PoolInformation(auto_pool_specification= auto_pool)
        else:
            # create a statically allocated pool
            new_pool = batch.models.PoolAddParameter(id=self.pool_id,
                virtual_machine_configuration=vmc,
                vm_size=self.vm_size,
                network_configuration=network_config,
                target_dedicated_nodes=0 if self.use_low_pri else self.num_nodes,
                target_low_priority_nodes=self.num_nodes if self.use_low_pri else 0,
                #max_tasks_per_node = max_tasks_per_node,
                enable_auto_scale=False,                # don't resize to 0 or we won't be able to connect to node
                resize_timeout=timedelta(minutes=30),                      # allow 30 mins to allocate all needed VMs
                enable_inter_node_communication=enable_inter_node_communication)

            self.batch_client.pool.add(new_pool)
            pool_info = batch.models.PoolInformation(pool_id=self.pool_id)  # , auto_pool_specification= auto_pool)

        # CREATE THE JOB (but doesn't launch it yet)
        batch_job = batch.models.JobAddParameter(id=self.batch_job_id, pool_info=pool_info, 
            on_all_tasks_complete="terminateJob")

        self.batch_client.job.add(batch_job)
        self.batch_job = batch_job

    def get_elevated_user_identify(self):
        aus = batchmodels.AutoUserSpecification(elevation_level=batchmodels.ElevationLevel.admin, 
            scope=batchmodels.AutoUserScope.task)
        user = batchmodels.UserIdentity(auto_user=aus)
        return user

    def delete_container_if_exists(self, name):
        if self.blob_client.exists(name):
            self.blob_client.delete_container(name)

    def get_outfiles_container_url(self, dest_container_name):
        # TODO - move OutputFiles code into AzureLaunchTest and xt_client
        # create container to hold output files
        
        self.blob_client.create_container(dest_container_name, fail_on_exist=False)

        expire_days = self.config.get("general", "storage-cert-days")

        # create an SAS for writing to the container
        sas_token = self.blob_client.generate_container_shared_access_signature(dest_container_name, 
            permission=azureblob.ContainerPermissions.WRITE,
            expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=expire_days*24))

        # secret trick: construct SAS URL for the container
        out_container_url = "https://{}.blob.core.windows.net/{}?{}".format(self.store_name, dest_container_name, sas_token)

        #console.print("sas_token=", sas_token)
        #console.print("out url=", out_container_url)
        return out_container_url

    def add_tasks_to_job(self, node_records, args):

        # we always use exactly 1 task per node (xt controller)
        tasks = []
        for idx, node_record in enumerate(node_records):
            node_cmd = node_record["node_cmd"]
            node_res_files = node_record["node_res_files"]
            node_output_files = node_record["node_output_files"]

            env_vars = dict(args["env_vars"])
            env_vars["XT_NODE_ID"] = "node" + str(idx)
            env_vars["XT_BOX_SECRET"] = node_record["box_secret"]

            task_id = "task{}".format(idx)
            #console.print("add task: id=", task_id, ", node_cmd=", node_cmd)

            # this is so that we can run SUDO on our cmd line (related to bug in "conda create" that requires SUDO)
            elevated_user = self.get_elevated_user_identify()

            # add user-specified environment variables
            env_var_list = []
            for key, value in env_vars.items():
                # wierd API; need to specify params by name or get wierd errors
                es = batchmodels.EnvironmentSetting(name=key, value=str(value))
                env_var_list.append(es)

            if self.custom_image_name:
                tcs = batch.models.TaskContainerSettings(image_name=self.custom_image_name)
            else:
                tcs = None

            task_param = batch.models.TaskAddParameter(id=task_id, command_line=node_cmd, environment_settings=env_var_list,
                resource_files=node_res_files, user_identity=elevated_user, output_files=node_output_files, 
                container_settings=tcs)

            tasks.append(task_param)

        fake_submit = args["fake_submit"]

        if not fake_submit:
            # this statement launches the job
            self.batch_client.task.add_collection(self.batch_job_id, tasks)

        # copy to submit-logs
        tasks_data = self.make_submit_data_serializable(tasks)
        dd = {"job_id": self.batch_job_id, "tasks": tasks_data}
        utils.copy_data_to_submit_logs(args, dd, "batch_submit.json")

        ### bug workaround: setting "on_all_tasks_complete" below doesn't seem to work so
        ### we set it on job creation (above)

        # now that we have added all our tasks, terminate the job as soon as all tasks complete (with or without error)
        #self.self.on_all_tasks_complete = "terminatejob"
        #console.print("self.self.on_all_tasks_complete=", self.self.on_all_tasks_complete)

    def make_submit_data_serializable(self, tasks):
        import json
        task_datas = []

        for task in tasks:
            command_line = task.command_line
            id = task.id
            
            env_vars = {}
            es = task.environment_settings
            for ev in es:
                env_vars[ev.name] = ev.value

            res_files = []
            for rf in task.resource_files:
                file_path = rf.file_path
                url = rf.http_url
                res_file = {"file_path": file_path, "url": url}
                res_files.append(res_file)

            out_files = []
            for of in task.output_files:
                dest_url = of.destination.container.container_url
                dest_path = of.destination.container.path

                file_pattern = of.file_pattern
                upload_condition = str(of.upload_options.upload_condition)

                out_file = {"dest_url": dest_url, "dest_path": dest_path, "file_pattern": file_pattern, "upload_condition": upload_condition}
                out_files.append(out_file)                

            td = {"command_line": command_line, "id": id, "env_vars": env_vars, "res_files": res_files, "out_files": out_files}

            #json.dumps(td)     # ensure its serializable
            task_datas.append(td)

        return task_datas

    def build_output_files(self, dest_container_name, blob_path, wildcard_names):
        '''
        For each wildcard string in wildcard_names, build an OutputFile instance that specifies:
            - the source files on the node (specified by the wildcard)
            - the blob destination in the dest_container_name 

        Return the list of OutputFiles built.
        '''
        out_container_url = self.get_outfiles_container_url(dest_container_name)
        output_files = []

        for pattern in wildcard_names:
            # CAUTION: "batchmodels" is NOT the same as batch.models
            upopts = batchmodels.OutputFileUploadOptions(upload_condition="taskCompletion")

            if utils.has_azure_wildcards(pattern):
                dest_blob_path = blob_path
            else:
                # single file names require adjust to blob_path
                dest_blob_path = blob_path + "/" + os.path.basename(pattern)

            dest = batchmodels.OutputFileBlobContainerDestination(container_url=out_container_url, path=dest_blob_path)
            dest2 = batchmodels.OutputFileDestination(container=dest)

            output_file = batchmodels.OutputFile(file_pattern=pattern, destination=dest2, upload_options=upopts)
            #console.print("built output_file: pattern=", pattern, ", dest_container=", out_container_url, ", blob_path=", blob_path)
            output_files.append(output_file)

        return output_files

    def print_status_text(self, task_counts, wait_steps):
        # console.print out status codes as we wait
        #console.print("task_counts=", task_counts)

        status = ""
        for _ in range(task_counts.active):
            status += "q"
        for _ in range(task_counts.running):
            status += "r"
        for _ in range(task_counts.failed):
            status += "f"
        for _ in range(task_counts.succeeded):
            status += "s"

        if len(status) == 0:
            # something went wrong
            status = "."
        elif len(status) > 1:
            # more than one task, separate each sample by a space
            status += " "

        console.print(status, end="")
        if wait_steps > 0 and wait_steps % 60 == 0:
            console.print("")
            
        sys.stdout.flush()

    def wrapup_parent_run(self, store, ws, run_name):
        '''
        wrap up a run from an azure self.  run may have spawned child runs, which also need to be cleaned up.
        '''
        records = self.wrapup_target_run(store, ws, run_name)
        child_records = [rec for rec in records if rec["event"] == "child_created"]
        child_names = [rec["data"]["child_name"] for rec in child_records]

        for child_name in child_names:
            self.wrapup_target_run(store, ws, child_name)

    def wrapup_target_run(self, store, ws, run_name):
        '''
        wrap up a run from azure batch.  run may have started, or may have completed.  
        '''
        # get some needed info from run log
        records = store.get_run_log(ws, run_name)

        if records:
            # is a wrapup needed?
            end_record = [rec for rec in records if rec["event"] == "ended"]
            
            if not end_record:
                dd = records[0]["data"]
                exper_name = dd["exper_name"]
                job_id = dd["job_id"]
                status = "cancelled"
                exit_code = None
                rundir = None      # since job has not started
                log = self.config.get("logging", "log")
                capture = self.config.get("after-files", "after-upload")

                # should we be getting these 3 values from the run itself (its context or logged values for these)?
                primary_metric = self.config.get("general", "primary-metric")
                maximize_metric = self.config.get("general", "maximize-metric")
                report_rollup = self.config.get("run-reports", "report-rollup")

                after_files_list = self.config.get("after-files", "after-dirs")
                after_files_list = utils.parse_list_option_value(after_files_list)

                aggregate_dest = self.config.get("hyperparameter-search", "aggregate-dest")
                dest_name = exper_name if aggregate_dest == "experiment" else job_id

                node_id = utils.node_id(dd["node_index"])
                run_index = dd["run_index"] if "run_index" in dd else None

                store.wrapup_run(ws, run_name, aggregate_dest, dest_name, status, exit_code, 
                    primary_metric, maximize_metric, report_rollup, rundir, after_files_list, log, capture, 
                    job_id=job_id, node_id=node_id)

        return records

    def cancel_job_node(self, store, ws_name, job_id, node_index, run_datas):
        pool_id = None
        node_id = None
        task_killed = False

        if not self.batch_client:
            self.create_batch_client()

        # terminate the TASK
        #console.print("canceling: job={}, node_index={}, run_names={}".format(job_id, node_index, full_run_names))

        batch_job_name = self.make_batch_job_id(ws_name, job_id)
        task = self.batch_client.task.get(batch_job_name, "task" + str(node_index))
        before_status = str(task.state)
        #console.print("task.state=", task.state)

        if task.node_info:
            pool_id = task.node_info.pool_id
            node_id = task.node_info.node_id

        if task.state != "completed":
            try:
                self.batch_client.task.terminate(job_id, task.id)     
                console.print("azure-batch task terminated: {}.{}".format(job_id, task.id))
                task_killed = True
            except:
                pass

        # kill the NODE itself
        # TODO: we need the resource_group to make this call
        #self.batch_client.node.delete(resource_group, node_id)

        # wrap-up each run (logging, capture)
        cancel_results = []

        if run_datas:
            for run_data in run_datas:    
                ws = run_data["ws_name"]
                run_name = run_data["run_name"]

                # watch out for fully-qualified run names
                if "/" in run_name:
                    ws, run_name = run_name.split("/")
                    
                # now, wrapup all runs for the specified azure batch box

                self.wrapup_parent_run(store, ws, run_name)
                kr = {"workspace": ws, "run_name": run_name, "cancelled": True, "status": "cancelled", "before_status": before_status}
                #console.print("kr=", kr)
                cancel_results.append(kr)
 
        #console.print("cancel_results=", cancel_results)
        return cancel_results, pool_id

    def get_job_status(self, job_id):
        if not job_id:
            job_id = self.batch_job_id

        console.print("get_job_status (azure): job_id=", job_id)

        if not self.batch_client:
            self.create_batch_client()
        
        try:
            status = "running"
            task_counts = self.batch_client.job.get_task_counts(job_id)
            if task_counts.active:
                # if any tasks are waiting for a node, consider the job status as allocating
                status = "allocating"    
            elif task_counts.running == 0:
                status = "completed"
        except:
            # job deleted/unknown/corrput
            status = "unknown"
        
        return status

    def attach_task_to_console(self, job_id, run_name):
        self.batch_job_id = job_id

        self.create_batch_client()

        all_tasks_complete = False
        start = datetime.datetime.now()
        detach_requested = False
        console.print()

        with KeyPressChecker() as checker:
            # wait until job starts
            while True:   
                
                # get a dict of the stats for each task
                task_counts = self.batch_client.job.get_task_counts(self.batch_job_id)

                elapsed = utils.elapsed_time(start)
                console.print("waiting for queued job to start... (elapsed time: {}).format(elapsed)", end="\r")

                all_tasks_complete = task_counts.running or task_counts.failed or task_counts.succeeded
                if all_tasks_complete:
                    break

                # check every .5 secs for keypress to be more responsive (but every 1 sec for task counts)
                ch = checker.getch_nowait()
                if ch == constants.ESCAPE:
                    detach_requested = True
                    break
                time.sleep(.5)

                ch = checker.getch_nowait()
                if ch == constants.ESCAPE:
                    detach_requested = True
                    break
                time.sleep(.5)

        console.print()     # end the status line of "..."
        sys.stdout.flush()

        if detach_requested:
            console.print("\n--> experiment detached from console.  to reattach, run:")
            console.print("\txt attach " + run_name)
        else:
            #----- stream output to console ----
            self.print_task_output(self.batch_job_id, 0)

    def print_task_output(self, job_id, task_index):

        # get task_id
        tasks = self.batch_client.task.list(self.batch_job_id)
        console.print("task.list len=", len(tasks))
        
        task = next(iter(tasks), None)
        if not task:
            console.print("error - job has no tasks")
        else:
            task_info = self.batch_client.task.get(self.batch_job_id, task.id)
            node_info = task_info.node_info

            if node_info:
                # node has been allocated and not yet released
                stream = self.batch_client.file.get_from_task(self.batch_job_id, task.id, "stdout.txt")

                while True:
                    for data in stream:
                        text = data.decode("utf-8")
                        console.print(text)

                    task_counts = self.batch_client.job.get_task_counts(self.batch_job_id)
                    if task_counts.running == 0:
                        console.print("<task terminated>")
                        break

                    time.sleep(1)

                #console.print(file_textt)
            else:
                console.print("error - task has no node")


    def print_output_for_tasks(self):
        """Prints the stdout.txt file for each task in the self.
        """
        console.print('Printing task output...')

        tasks = self.batch_client.task.list(self.batch_job_id)

        for task in tasks:
            console.print("getting output for job={}, task={}".format(self.batch_job_id, task.id))
            
            task_info = self.batch_client.task.get(self.batch_job_id, task.id)
            node_info = task_info.node_info

            if node_info:
                node_id = node_info.node_id
                stream = self.batch_client.file.get_from_task(self.batch_job_id, task.id, "stdout.txt")
                file_text = self._stream_to_text(stream)

                console.print("\nTask: {}, Node: {}, Standard output:".format(task.id, node_id))
                console.print(file_text)

    def _stream_to_text(self, stream, encoding='utf-8'):
        output = io.BytesIO()

        try:
            for data in stream:
                output.write(data)
            return output.getvalue().decode(encoding)
        finally:
            output.close()

        raise RuntimeError('could not read task data from stream')

    def convert_blobs_to_resource_files(self, container_name, blob_names, file_names, writable=False, expire_hours=24):
        if writable:
            permission = azureblob.BlobPermissions.WRITE
        else:
            permission = azureblob.BlobPermissions.READ

        resource_files = []

        #for blob_name, file_name in zip(blob_names, file_names):
        for i, blob_name in enumerate(blob_names):
            # create a security token to allow anonymous access to blob
            expire_date = expiry=datetime.datetime.utcnow() + datetime.timedelta(hours=expire_hours)

            sas_token = self.blob_client.generate_blob_shared_access_signature(container_name,
                blob_name, permission=permission, expiry=expire_date)

            # convert SAS to URL
            sas_url = self.blob_client.make_blob_url(container_name, blob_name, sas_token=sas_token)

            # support OPTIONAL file_names
            file_name = file_names[i] if file_names and file_names[i] else "./"

            # finally, create the ResourceFile
            resource_file = batchmodels.ResourceFile(http_url=sas_url, file_path=file_name)
            resource_files.append(resource_file)

        return resource_files

    def upload_files_to_blobs(self, container_name, blob_path, files):
        # create container if needed
        self.blob_client.create_container(container_name, fail_on_exist=False)
        #console.print("result from create_container=", result)

        blob_names = []
        for fn in files:
            blob_dest = os.path.basename(fn)
            if blob_path:
                blob_dest = blob_path + "/" + blob_dest
            self.blob_client.create_blob_from_path(container_name, blob_dest, fn)
            blob_names.append(blob_dest)

        return blob_names

    def close_resources(self, batch_client):

        if self.pool_id:
            console.print("deleting pool...")
            batch_client.pool.delete(self.pool_id)
            self.pool_id = None

        if self.batch_job_id:
            console.print("deleting self...")
            batch_client.self.delete(self.batch_job_id)
            self.batch_job_id = None

    def cancel_runs_by_names(self, workspace, run_names, box_name):
        '''
        Args:
            workspace: the name of the workspace containing the run_names
            run_names: a list of run names
            box_name: the name of the box the runs ran on (pool service)
        Returns:
            cancel_results: a list of kill results records 
                (keys: workspace, run_name, exper_name, killed, status, before_status)
        '''

        # our strategy for this API: 
        #   - use the XT controller to kill specified runs (when controller is available)
        #   - use batch_client "cancel node" if controller not available

        # we build service-based box names to have 3 parts
        job_id, service_name, node_index = box_name.split("-")
        node_index = int(node_index)
        cancelled_by_controller = False
        cancel_results = None

        # is the controller available?
        azure_batch_state, ip_addr, controller_port, tensorboard_port = \
            self.get_azure_box_addr(workspace, job_id, node_index)

        if ip_addr and controller_port:
            # add workspace to run_names
            first_run_name = run_names[0]
            run_names = [workspace + "/" + run_name for run_name in run_names]

            try:
                # from xtlib.client import Client

                # client = Client(self.config, self.store, self.core)
                # if client.connect_to_controller(ip_addr=ip_addr, port=controller_port):
                #     # send request to controller via the client service
                #     cancel_results = client.cancel_runs(run_names)
                #     cancelled_by_controller = True

                from xtlib.xt_client import XTClient
                from xtlib import run_helper

                cs, box_secret = run_helper.get_client_cs(self.core, workspace, first_run_name)
                if not cs:
                    console.print("could not find info for run: {}/{}".format(workspace, first_run_name))
                else:
                    with XTClient(self.config, cs, box_secret) as xtc:
                        if xtc.connect():
                            result = xtc.cancel_runs(run_names)

            except BaseException as ex:
                #errors.report_exception(ex)
                pass

        if not cancelled_by_controller:
            # run is in a node that waiting for a pool or has left pool; just kill the whole node
            run_datas = [ {"ws_name": workspace, "run_name": run_name} for run_name in run_names ]
            cancel_results, pool_id = self.cancel_job_node(self.store, workspace, job_id, node_index, run_datas)

        return cancel_results        

    def cancel_runs_by_job(self, job_id, runs_by_box, workspace=None):
        '''
        Args:
            job_id: the name of the job containing the run_names
            runs_by_box: a dict of box_name/run lists
        Returns:
            cancel_results_by box: a dict of box_name, cancel_result records
                (keys: workspace, run_name, exper_name, killed, status, before_status)
        '''
        pool_id = None
        cancel_results_by_box = {}
        workspace = None

        for node_index, box_name in enumerate(runs_by_box.keys()):

            run_datas = runs_by_box[box_name]
            run_names = [rd["run_name"] for rd in run_datas]

            if not workspace:
                # set workspace from first run of job
                workspace = run_datas[0]["ws_name"]

            self.cancel_runs_by_names(workspace, run_names, box_name)

        # for now, do both of these to ensure the job has completed shut down
        terminate_job_explictly = True
        delete_pool = True

        if terminate_job_explictly:
            # terminate the JOB
            try:
                self.batch_client.job.terminate(job_id, terminate_reason="cancelled by user")
                #console.print("job terminated: " + str(job_id))
            except BaseException as ex:
                # avoid rasing errors here (could be a quicktest workspace re-creation issue)
                pass

        if delete_pool and pool_id:
            # delete the POOL (to ensure job charges terminate)
            try:
                self.batch_client.pool.delete(pool_id)
                console.print("pool deleted: " + str(pool_id))
            except:
                pass

        return cancel_results_by_box

    def get_active_jobs(self, ws_name):
        ''' return a list of job_id's running on this instance of Azure Batch '''
        if not self.batch_client:
            self.create_batch_client()

        jobs = self.batch_client.job.list()

        # state values can be one of: 'active', 'disabling', 'disabled', 'enabling', 'terminating', 'completed', 'deleting'
        active_states = ["active", "disabling", "disabled", "enabling"]

        job_ids = [job.id for job in jobs if job.state in active_states]
        return job_ids


    def cancel_runs_by_user(self, ws_name, box_name):
        '''
        Args:
            box_name: the name of the box the runs ran on (pool service)
        Returns:
            cancel_results: a list of kill results records 
                (keys: workspace, run_name, exper_name, killed, status, before_status)
        '''
        cancel_results_by_box = {}

        # get list of active jobs from batch
        job_ids = self.get_active_jobs(ws_name)
        console.diag("after get_active_jobs()")

        if job_ids:
            # get runs_by_job data from MONGO
            db = self.store.get_database()

            filter_dict = {}
            filter_dict["job_id"] = {"$in": job_ids}
            filter_dict["username"] = self.username

            fields_dict = {"runs_by_box": 1}

            job_records = db.get_info_for_jobs(ws_name, filter_dict, fields_dict)
            console.diag("after get_info_for_jobs()")

            # cancel each ACTIVE job
            for job in job_records:
                job_id = job["_id"]
                runs_by_box = job["runs_by_box"]

                kr_by_box = self.cancel_runs_by_job(job_id, runs_by_box)

                cancel_results_by_box.update(kr_by_box)

        return cancel_results_by_box

    def get_node_task(self, service_node_info):
        # get task_id
        if not self.batch_client:
            self.create_batch_client()
        
        batch_job_id = service_node_info["batch_job_id"]
        task_index = service_node_info["task_index"]

        task_id = "task" + str(task_index)
        task = self.batch_client.task.get(batch_job_id, task_id)

        return task

    # BACKEND API
    def get_node_status(self, service_node_info):

        task = self.get_node_task(service_node_info)
        return task.state.value

    # BACKEND API
    def read_log_file(self, service_node_info, log_name, start_offset=0, end_offset=None, 
        encoding='utf-8', use_best_log=True, log_source=None, service_context=None):
        '''
        returns subset of specified log file as text.
        '''
        job_id = service_node_info["job_id"]
        batch_job_id = service_node_info["batch_job_id"]
        node_id = service_node_info["node_id"]
        workspace = service_node_info["workspace"]

        # allow task to be cached in service_context (for multiple calls)
        task = utils.safe_value(service_context, "task")

        new_text = None
        batch_status = None
        simple_status = None
        next_offset = 0
        found_file = False

        if log_name is None:
            log_name = "stdout.txt"
        file_path = os.path.basename(log_name)

        # try to first read from job storage (if task has completed)
        if log_source != "live":
            node_index = utils.node_index(node_id)

            job_path = "nodes/node{}/after/service_logs/{}".format(node_index, file_path)
            if self.store.does_job_file_exist(workspace, job_id, job_path):
                new_text = self.store.read_job_file(workspace, job_id, job_path)
                batch_status = "completed"
                simple_status = "completed"
                found_file = True
                log_source = "after_logs"

            if not found_file:
                job_path = "nodes/node{}/after/xt_logs/{}".format(node_index, file_path)
                if self.store.does_job_file_exist(workspace, job_id, job_path):
                    new_text = self.store.read_job_file(workspace, job_id, job_path)
                    batch_status = "completed"
                    simple_status = "completed"
                    found_file = True
                    log_source = "after_logs"

        if not found_file:

            # this call can take up to 15 secs
            if not task:
                task = self.get_node_task(service_node_info)

            node_info = task.node_info
            batch_status = task.state.value
            simple_status = self.get_simple_status(batch_status)

            if not end_offset:
                end_offset = 1024*1024*1024*16     # 16 GB should be big enough for a log file

            gft_opts = batchmodels.FileGetFromTaskOptions(ocp_range='bytes={}-{}'.format(start_offset, end_offset))

            try:
                # stdboth is a .TMP file when it is read live
                live_log_name = "stdboth.tmp" if log_name == "stdboth.txt" else log_name

                stream = self.batch_client.file.get_from_task(batch_job_id, task.id, file_path=live_log_name, 
                    file_get_from_task_options=gft_opts)

                # put streamed output into "output"
                output = io.BytesIO()

                for data in stream:
                    output.write(data)

                new_bytes = output.getvalue()
                new_text = new_bytes.decode(encoding)
                next_offset = start_offset + len(new_bytes)
                log_source = "live"

            except BaseException as ex:
                # interpret this error as task has terminated
                console.diag("Exception reading batch log file: {}".format(ex))

        return {"new_text": new_text, "simple_status": simple_status, "log_name": log_name, "next_offset": next_offset, 
            "service_status": batch_status, "file_path": file_path, "service_context": {"task": task}, "found_file": found_file, 
            "log_source": log_source}

    # API call
    def get_simple_status(self, status):
        # translates an BATCH status to a simple status (queued, running, completed)

        queued = ["active", "preparing"]
        running = ["running"]
        completed = ["completed"]

        if status in queued:
            ss = "queued"
        elif status in running:
            ss = "running"
        elif status in completed:
            ss = "completed"
        else:
            errors.warning("unexpected Azure Batch status value: {}".format(status))

        return ss

    # API call
    def cancel_job(self, service_job_info, service_info_by_node):
        result_by_node = {}

        for node_id, node_info in service_info_by_node.items():
            result = self.cancel_node(node_info)
            result_by_node[node_id] = result

        return result_by_node

    # API call
    def cancel_node(self, service_node_info):
        task = self.get_node_task(service_node_info)

        service_status = task.state.value
        simple_status = self.get_simple_status(service_status)
        cancelled = False

        if simple_status != "completed":
            
            batch_job_id = service_node_info["batch_job_id"]
            self.batch_client.task.terminate(batch_job_id, task.id)

            # refresh the task for updated status
            task = self.get_node_task(service_node_info)

            service_status = task.state.value
            simple_status = self.get_simple_status(service_status)
            cancelled = (service_status == "completed")     

        result = {"cancelled": cancelled, "service_status": service_status, "simple_status": simple_status}
        return result

    # API call
    def add_service_log_copy_cmds(self, cmds, dest_dir, args):
        # this is done by the batch service at the end of our batch task
        pass            

