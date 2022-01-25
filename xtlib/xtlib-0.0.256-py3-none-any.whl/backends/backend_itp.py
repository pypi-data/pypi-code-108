#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# backend_itp.py: support for running jobs under the Microsoft ITP (Integrated Training Platform)

import os
import uuid
from xtlib.backends.backend_aml import AzureML

class ITP(AzureML):

    def __init__(self, compute, compute_def, core, config, username=None, arg_dict=None, disable_warnings=True):
        super(ITP, self).__init__(compute, compute_def, core, config, username, arg_dict, disable_warnings)

        # blobfuse is still busted if we are using their default docker images
        # for now, let's assume we are using latest good pytorch-xtlib docker image
        self.mounting_enabled = True   # False

    def get_name(self):
        return "itp"

    def update_estimator(self, estimator, gpu_count, preemption_allowed):
        # when submitting an ITP job, we do a JIT install of weird AML K8S dependency
        # (doing it here helps keep pip install for XT working correctly, on client
        # machine as well as ITP compute node).
        cmd = "pip install --upgrade --disable-pip-version-check --extra-index-url " + \
            "https://azuremlsdktestpypi.azureedge.net/K8s-Compute/D58E86006C65 azureml_contrib_k8s"

        fn_log = os.path.expanduser("~/.xt/k8s_install.log")
        cmd += " > {} 2>&1".format(fn_log)
        os.system(cmd)

        # create Amlk8s config
        # this line must be included even if you don't need to reference AksCompute
        from azureml.contrib.core.compute.k8scompute import AksCompute
        from azureml.contrib.core.k8srunconfig import K8sComputeConfiguration

        k8sconfig = K8sComputeConfiguration()
        k8s = dict()
        k8s['gpu_count'] = gpu_count
        k8s['preemption_allowed'] = preemption_allowed
        k8sconfig.configuration = k8s      

        estimator.run_config.cmk8scompute = k8sconfig

  # API call
    def add_service_log_copy_cmds(self, cmds, dest_dir, args):

        self.append(cmds, "mkdir -p {}".format(dest_dir))
        self.append(cmds, "cp -r -v /var/log/compute/00_stdout.txt {}".format(dest_dir))
        #self.append(cmds, "cp -r -v /var/log {}".format(dest_dir))
        self.append(cmds, "cp -r -v $XT_ORIG_WORKDIR/logs {}".format(dest_dir))

    def create_wrapper_script(self, cmd_parts, snapshot_dir, store_data_dir, data_action, 
            data_writable, store_model_dir, model_action, model_writable, storage_name, storage_key, actions, 
             sudo_available, username, setup, use_allow_other, args):

        use_gpu = args["use_gpu"]
        self.default_docker_image = self.get_default_docker_image(use_gpu)

        # we keep the working directory assigned to us by AML because our code is already 
        # downloaded here, and the log files are handy to access (as subdirs)
 
        other_cmds = []
        self.build_other_cmds(other_cmds)

        orig_other_cmds = args["other_cmds"]
        args["other_cmds"] = orig_other_cmds + other_cmds

        # we need to move our cwd (default working dir is blob-mapped and slow)
        # as of 10/21/2020, ITP recommends we use "/var/tmp" until they disable the NFS mount for $HOME
        use_var_tmp = True

        if use_var_tmp:
            job_home = "/var/tmp"
        else:
            guid = str(uuid.uuid4())
            job_home = "$HOME/{}".format(guid)
        
        cwd = "{}/.xt/cwd".format(job_home)

        # see if this helps our new blobfuse problem on ITP
        mountbase = "$XT_ORIG_WORKDIR"
        tmpbase = job_home

        # we only do this once (for the first box/job)
        fn_wrapped = super().wrap_user_command(cmd_parts, snapshot_dir, store_data_dir, data_action, 
            data_writable, store_model_dir, model_action, model_writable, storage_name, storage_key, actions, 
            is_windows=False, sudo_available=sudo_available, username=username, use_username=False, 
            install_blobfuse=True, setup=setup, use_allow_other=use_allow_other, 
            remove_zip=False, homebase=job_home, cwd=cwd, args=args, copy_code=True, mountbase=mountbase, 
            tmpbase=tmpbase)

        return fn_wrapped

    def build_other_cmds(self, cmds):
        self.append_title(cmds, "CORRECT python path used for XT on ITP")

        # following code removes any lines containing "/opt/conda/" (lines at top of file)
        # and adds a new line (#!path-to-python) to the xt file 
        # since ITP installs in incorrectly thru conda

        # try as is
        self.append(cmds, "xt --version")

        # show the problem
        self.append(cmds, "xt_file=$(which xt)")
        self.append(cmds, "echo xt script: $xt_file")
        self.append(cmds, "head -2 $xt_file")

        # # fix the problem
        # self.append(cmds, "{ echo '#!'$(which python); grep -v /opt/conda/  $xt_file; } > tmp")
        # self.append(cmds, "sudo mv tmp $xt_file")

        # # show the fix
        # self.append(cmds, "head -2 $xt_file")

        # # test the fix
        # self.append(cmds, "xt --version")
        # self.append(cmds, "sudo chmod +x $xt_file")
        # self.append(cmds, "xt --version")
        # self.append(cmds, "python $xt_file --version")
