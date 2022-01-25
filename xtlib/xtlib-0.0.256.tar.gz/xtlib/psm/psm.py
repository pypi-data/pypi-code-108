#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# psm.py: pool service manager
'''
    - this file should not reference xtlib or other non-standard libraries.
    - this is to keep deployment simple: copy & run on dest machine

    - NOTE: we currently use psutil library (non-standard) that may need 
      to be installed on some systems.  is there an alternative to this?  

    - XT docs should include psutil as a prerequisite for each pool box
'''
import os
import time
import shutil
import zipfile
import datetime
import subprocess

is_windows = (os.name == "nt")
#log_print("is_windows:", is_windows)

PSM_QUEUE = os.path.expanduser("~/.xt/psm_queue")
PSM_LOGDIR = os.path.expanduser("~/.xt/psm_logs")

if is_windows:
    home_drive = os.getenv("HOMEDRIVE")
    CWD = os.path.join(home_drive + "\\.xt", "cwd")
else:
    CWD = os.path.expanduser("~/.xt/cwd")

PSM = "psm.py"
CURRENT_RUNNING_ENTRY = "__current_running_entry__.txt"
FN_WRAPPER = os.path.join(CWD, "__wrapped__.bat" if is_windows else "__wrapped__.sh")
CONTROLLER_NAME_PATTERN = "xtlib.controller"
PY_RUN_CONTROLLER ="__run_controller__.py"

def log_print(*objects, sep=' '):
    # print to console (which is redirected to psm.log)
    text = sep.join([str(obj) for obj in objects])

    if text and not text.startswith("  "):
        # if outer level msg, add timestamp
        now = datetime.datetime.now()
        now_str = str(now).split(".")[0]
        text = "{}: {}".format(now_str, text)

    print(text, flush=True)

def get_controller_wrapped_counts():
    import psutil

    processes = psutil.process_iter()
    controller_count = 0
    wrapped_count = 0

    if is_windows:
        WRAPPED_PARTIAL = ".xt\\cwd\\__wrapped__.bat"
    else:
        WRAPPED_PARTIAL = ".xt/cwd/__wrapped__.sh"

    #log_print("  WRAPPED_PARTIAL: " + WRAPPED_PARTIAL)

    for p in processes:
        try:
            process_name = p.name().lower()
            #log_print("process_name=", process_name)

            if process_name in ["python", "bash", "python.exe", "cmd.exe"]:
                #log_print("process name: {}".format(p.name()))
                cmd_line = " ".join(p.cmdline())
                #log_print("  cmd_line: " + cmd_line)

                if CONTROLLER_NAME_PATTERN in cmd_line or PY_RUN_CONTROLLER in cmd_line:
                    controller_count += 1
                elif WRAPPED_PARTIAL in cmd_line:
                    wrapped_count += 1

        except BaseException as ex:
            pass

    # count the number of entries we have running in docker
    docker_count = 0
    fn_image_name = os.path.join(CWD, "__docker_image_name.txt")

    if os.path.exists(fn_image_name):
        # current run is a docker container run
        with open(fn_image_name, "rt") as infile:
            image_name = infile.read().strip()

        output = os.popen('docker ps').read()
        containers = output.split("\n")[1:]

        # filter to matches of our image name
        containers = [con for con in containers if image_name in con]
        docker_count = len(containers)
        
    return controller_count, wrapped_count, docker_count

def start_async_run_detached(cmd, working_dir, fn_stdout):
    DETACHED_PROCESS = 0x00000008    # if visible else 0
    CREATE_NO_WINDOW = 0x08000000
    
    with open(fn_stdout, 'w') as output:

        if is_windows:
            cflags = CREATE_NO_WINDOW  # | DETACHED_PROCESS
            p = subprocess.Popen(cmd, cwd=working_dir, stdout=output, stderr=subprocess.STDOUT, creationflags=cflags)

        else:
            # linux
            p = subprocess.Popen(cmd, cwd=working_dir, stdout=output, stderr=subprocess.STDOUT)
    return p

def start_entry(fn_entry):
    '''
    Args:
        fn_entry: name of .zip file (w/o dir):  team.job.node.ticks.zip
    Returns: 
        None
    '''

    log_print("PROCESSING: {}".format(fn_entry))
    fn_entry_path = os.path.join(PSM_QUEUE, fn_entry)

    log_print("  zapping CWD")
    log_print("  PWD: " + os.getcwd())

    if os.path.exists(CWD):
        try:
            shutil.rmtree(CWD)
        except BaseException as ex:
            log_print("exception during zap of CWD: ex={}".format(ex))

    if not os.path.exists(CWD):
        os.makedirs(CWD)

    # copy/remove entry from queue
    log_print("  copying entry to CWD")
    fn_current_zip = os.path.join(CWD, "xt_code.zip")
    shutil.copyfile(fn_entry_path, fn_current_zip)

    log_print("  removing entry from queue")
    os.remove(fn_entry_path)

    try:
        # UNZIP code from fn_current to CWD
        exists = os.path.exists(fn_current_zip)
        log_print("  unzipping entry from={}, to={}, exists={}".format(fn_current_zip, CWD, exists))

        # NOTE: this used to fail with "File is not a zip file" error (operating on partially copied file)
        with zipfile.ZipFile(fn_current_zip, 'r') as zip:
            zip.extractall(CWD)

        # write "current job running" file
        log_print("  writing CURRENT_RUNNING_ENTRY")
        fn_current_entry = os.path.join(CWD, CURRENT_RUNNING_ENTRY)
        with open(fn_current_entry, "wt") as outfile:
            outfile.write(fn_entry)

        fn_wrapper = FN_WRAPPER
        if is_windows:
            # fix slashes
            fn_wrapper = fn_wrapper.replace("/", "\\")

        # extract script ARGS: node_id, run_name
        # parts: team, job, run, node, ticks, "zip"
        parts = fn_entry.split(".")
        run_name = parts[3]
        node_index = parts[4]

        fn_base_entry = os.path.splitext(fn_entry)[0]
        fn_log = os.path.join(PSM_LOGDIR, fn_base_entry + ".log")

        # force it to be a legal filename for current platform (correct slashes)
        fn_log = os.path.abspath(fn_log)

        if fn_wrapper.endswith(".bat"):
            cmd_parts = [fn_wrapper, node_index, run_name, fn_log]
        else:
            cmd_parts = ["bash", "--login", fn_wrapper, node_index, run_name, fn_log]

        log_print("  starting ENTRY, cmd_parts={}".format(cmd_parts))
        log_print()

        # run WRAPPED script on local box
        start_async_run_detached(cmd_parts, CWD, fn_log)

    except BaseException as ex:
        # log and move on to next entry
        log_print("  EXCEPTION processing entry: ex={}".format(ex))

def main():
    log_print("PSM starting")
    log_print("  CWD: " + CWD)
    log_print()

    # ensure PSM_QUEUE exist
    if not os.path.exists(PSM_QUEUE):
        os.makedirs(PSM_QUEUE)

    # ensure PSM_LOGDIR exist
    if not os.path.exists(PSM_LOGDIR):
        os.makedirs(PSM_LOGDIR)

    last_entry_count = 0

    while True:
        time.sleep(1)
        #print("tick")

        # list queue
        files = os.listdir(PSM_QUEUE)

        # only look at .zip files (fully copied)
        files = [fn for fn in files if fn.endswith(".zip")]
        entry_count = len(files)

        # anything in queue?
        if entry_count:

            log_print("getting controller wrapped counts...")

            controller_count, wrapped_count, docker_count = get_controller_wrapped_counts()
            
            if True:    # last_entry_count != entry_count:
                log_print("QUEUE/CURRENT check: queue count={}, controller_count={}, wrapped_count={}, docker_count={}:" \
                    .format(len(files), controller_count, wrapped_count, docker_count))

                last_entry_count = entry_count

                # print queue
                for entry in files:
                    log_print("  {}".format(entry))
                log_print()

            if (controller_count + wrapped_count + docker_count) == 0:
                # sort job entries by TICKS part of fn   (team.job.run.node.ticks.zip)
                files.sort( key=lambda fn: int(fn.split(".")[-2]) )

                # use oldest file (smallest tick value) to XT cwd
                fn_entry = files[0]

                # start processing oldest entry
                start_entry(fn_entry)


if __name__ == "__main__":
    main()
