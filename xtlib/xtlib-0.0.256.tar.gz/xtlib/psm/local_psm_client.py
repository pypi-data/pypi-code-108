#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# local_psm_client.py: talk to Pool State Mgr running on local machine
import os
import time
import uuid
import psutil
import shutil

from xtlib import utils
from xtlib import pc_utils
from xtlib import constants
from xtlib import file_utils
from xtlib import process_utils
from xtlib.helpers.xt_config import get_merged_config

CONTROLLER_NAME_PATTERN = "xtlib.controller"
PY_RUN_CONTROLLER = "__run_controller__.py"
PSM_NAME_PATTERN = "psm.py"

class LocalPsmClient():
    def __init__(self):
        self.box_is_windows = pc_utils.is_windows()
        self.psm_queue_path = os.path.expanduser(constants.PSM_QUEUE)
        self.psm_log_path = os.path.expanduser(constants.PSM_LOGDIR)
        self.cwd_path = os.path.expanduser(constants.CWD)
        self.xt_path = os.path.expanduser(constants.XT_HOME)
        self.controller_cwd_path = utils.get_controller_cwd(self.box_is_windows, is_local=True)

        # ensure our required dirs have been created
        if not os.path.exists(self.cwd_path):
            os.makedirs(self.cwd_path)

        if not os.path.exists(self.psm_queue_path):
            os.makedirs(self.psm_queue_path)

    def enqueue(self, team, ws_name, job, run, node_index, fn_zip):
        # copy file to box (with unique name)
        #guid = str(uuid.uuid4())
        ticks = time.time()

        # copy ENTRY as .tmp
        fn_tmp_entry = "{}.{}.{}.{}.{}.{}.tmp".format(team, ws_name, job, run, node_index, int(10*ticks))
        fn_tmp_dest = os.path.join(self.psm_queue_path, fn_tmp_entry)
        shutil.copyfile(fn_zip, fn_tmp_dest)

        # now, rename the file to .zip so that PSM can see it
        fn_entry = os.path.splitext(fn_tmp_entry)[0] + ".zip"
        fn_dest = file_utils.path_join(self.psm_queue_path, fn_entry, for_windows=self.box_is_windows)
        os.rename(fn_tmp_dest, fn_dest)

        return fn_entry

    def dequeue(self, fn_entry):
        # delete file
        fn_dest = os.path.join(self.psm_queue_path, fn_entry)

        if os.path.exists(fn_dest):
            os.remove(fn_dest)

    def enum_queue(self):
        # list contents of queue
        entries = os.listdir(self.psm_queue_path)
        
        # get current entry being processed by controller
        current = self.get_running_entry_name()
        if not self._get_controller_process():
            current = None
        
        return entries, current

    def _is_psm_running(self):
        processes = psutil.process_iter()
        psm_count = 0

        for p in processes:
            try:
                name = p.name().lower()
                #print("process name: {}".format(name))

                if name.startswith("python"):
                    cmd_line = " ".join(p.cmdline())
                    #print("cmd_line: {}".format(cmd_line))

                    if constants.PSM in cmd_line:
                        psm_count += 1

            except BaseException as ex:
                pass
            
        return psm_count > 0

    def _get_controller_process(self):
        processes = psutil.process_iter()
        controller_process = None

        for p in processes:
            try:
                if p.name().lower().startswith("python"):
                    #print("process name: {}".format(p.name()))
                    cmd_line = " ".join(p.cmdline())

                    if CONTROLLER_NAME_PATTERN in cmd_line or PY_RUN_CONTROLLER in cmd_line:
                        controller_process = p
                        break

            except BaseException as ex:
                pass
            
        return controller_process

    def _get_wrapper_process(self):
        processes = psutil.process_iter()
        wrapper_process = None

        for p in processes:
            try:
                name = p.name().lower()
                if name in ["bash", "cmd.exe"]:
                    #print("process name: {}".format(p.name()))
                    cmd_line = " ".join(p.cmdline())
                    #print("cmd_line=", cmd_line)

                    if constants.FN_WRAPPED_SH in cmd_line or constants.FN_WRAPPED_BAT in cmd_line:
                        wrapper_process = p
                        break

            except BaseException as ex:
                pass
            
        return wrapper_process

    def _get_psm_process(self):
        processes = psutil.process_iter()
        psm_process = None

        for p in processes:
            try:
                if p.name().lower().startswith("python"):
                    #print("process name: {}".format(p.name()))
                    cmd_line = " ".join(p.cmdline())

                    if PSM_NAME_PATTERN in cmd_line:
                        psm_process = p
                        break

            except BaseException as ex:
                pass
            
        return psm_process

    def _get_docker_container(self):
        docker_count = 0
        fn_image_name = os.path.join(self.controller_cwd_path, constants.FN_IMAGE_NAME)

        if os.path.exists(fn_image_name):
            # current run is a docker container run
            with open(fn_image_name, "rt") as infile:
                image_name = infile.read().strip()
    
            # count the number of entries we have running in docker
            output = os.popen('docker ps').read()
            containers = output.split("\n")[1:]

            # filter to matches of our image name
            containers = [con for con in containers if image_name in con]
            docker_count = len(containers)

        return docker_count

    def restart_psm_if_needed(self):
        '''
        processing:
            - if PSM is running on old psm.py, kill the process and restart it.  
            - if PMS is not running, start it.
        '''
        kill_needed = False
        start_needed = False

        fn_src = os.path.join(file_utils.get_my_file_dir(__file__), constants.PSM)
        fn_dest = os.path.join(self.xt_path, constants.PSM)

        running = self._is_psm_running()
        #print("PSM running=", running)

        if running:
            # do file contents match?
            text_src = file_utils.read_text_file(fn_src)
            text_dest = file_utils.read_text_file(fn_dest) if os.path.exists(fn_dest) else None

            if text_src != text_dest:
                kill_needed = True
        else:
            start_needed = True

        if kill_needed:
            p = self._get_psm_process()
            if p:
                p.kill()
            start_needed = True

        if start_needed:
            # always copy psm.py (for xt dev/debug purposes)
            shutil.copyfile(fn_src, fn_dest)

            # run psm
            fn_log = os.path.join(self.xt_path, constants.PSMLOG)

            if self.box_is_windows:
                cmd_parts = ["cmd", "/c", "python -u {} > {}".format(fn_dest, fn_log)]
            else:
                cmd_parts = ["bash", "-c", "python -u {} > {}".format(fn_dest, fn_log)]
            
            # put log in known dir
            fn_run_log = os.path.expanduser("~/.xt/runpsm.log")
            
            process_utils.start_async_run_detached(cmd_parts, self.cwd_path, fn_run_log)

    def get_running_entry_name(self):
        text = None

        fn_current = os.path.join(self.controller_cwd_path, constants.CURRENT_RUNNING_ENTRY)
        if os.path.exists(fn_current):
            text = file_utils.read_text_file(fn_current).strip()

        return text

    def get_status(self, fn_entry):
        status = "completed"      # unless below finds different

        fn_queue_entry = os.path.join(self.psm_queue_path, fn_entry)
        if os.path.exists(fn_queue_entry):
            status = "queued"
        else:
            text = self.get_running_entry_name()
            if text == fn_entry:
                # entry might be running; is the runner script OR controller OR docker container active?
                if self._get_controller_process():
                    status = "running"
                elif self._get_wrapper_process():
                    status = "running"
                elif self._get_docker_container():
                    status = "running"
                else:
                    status = "completed"

        return status

    def cancel(self, fn_entry):
        cancelled = False
        status = "completed"

        # don't call get_entry_status - check details JIT to minimize race conditons
        fn_queue_entry = os.path.join(self.psm_queue_path, fn_entry)

        if os.path.exists(fn_queue_entry):
            os.remove(fn_queue_entry)
            cancelled = True
        else:
            text = self.get_running_entry_name()
            if text == fn_entry:
                # entry might be running; is the controller active?
                p = self._get_controller_process()
                if p:
                    p.kill()
                    cancelled = True

        return cancelled, status

    def read_log_file(self, fn_entry, start_offset, end_offset, log_source=None):

        fn_entry_base = os.path.splitext(fn_entry)[0]
        fn_log = os.path.join(self.psm_log_path, fn_entry_base + ".log")

        new_bytes = b""

        if os.path.exists(fn_log):
            with open(fn_log, "rb") as infile:
                infile.seek(start_offset)

                if end_offset:
                    new_bytes = infile.read(end_offset-start_offset)
                else:
                    new_bytes = infile.read()

        return new_bytes
