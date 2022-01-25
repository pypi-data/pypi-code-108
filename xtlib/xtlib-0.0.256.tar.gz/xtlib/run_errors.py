# run_errors.py: helper functions for recording db/storage retry errors for each run on a node
import os
import json

from xtlib import utils
from xtlib import console
from xtlib import pc_utils
from xtlib import file_utils

WINDOWS_RUN_ERRORS_DIR = "%XT_CWD%\\run_errors"
LINUX_RUN_ERRORS_DIR = "$XT_CWD/run_errors"

def error_names_dir():
    if pc_utils.is_windows():
        dir = os.path.expandvars(WINDOWS_RUN_ERRORS_DIR)
    else:
        dir = os.path.expandvars(LINUX_RUN_ERRORS_DIR)
    return dir

def clear_run_errors_for_node():

    run_error_dir = error_names_dir()
    file_utils.ensure_dir_clean(run_error_dir)

    return run_error_dir

def record_run_error(error_type, error, context, traceback_lines=None, run_name=None):

    is_compute_node = pc_utils.is_compute_node()
    if is_compute_node:

        if not run_name:
            run_name = os.getenv("XT_RUN_NAME")
            if not run_name:
                run_name = "controller"

        run_error_dir = error_names_dir()
        fn = "{}/{}.jsonl".format(run_error_dir, run_name)
        file_utils.ensure_dir_exists(file=fn)

        # append error to file
        print("APPENDING to RUN_ERRORS file: ", fn, flush=True)

        ed = {"error_type": error_type, "error": str(error), "context": str(context), 
            "traceback": traceback_lines, "run_name": run_name}

        ed_text = json.dumps(ed) + "\n"
        file_utils.write_text_file(fn, ed_text, open_mode="a")

def count_run_errors(run_name=None, fn=None):
    db_errors = 0
    storage_errors = 0

    if not fn:
        if not run_name:
            run_name = os.getenv("XT_RUN_NAME")
            
        if run_name:
            run_error_dir = error_names_dir()
            fn = "{}/{}.jsonl".format(run_error_dir, run_name)
        
    if os.path.exists(fn):
        text = file_utils.read_text_file(fn)
        error_list = utils.load_json_records(text)
        for ed in error_list:
            err_type = utils.safe_value(ed, "error_type")
            if err_type == "db":
                db_errors += 1
            elif err_type == "storage":
                storage_errors += 1

    # console.print("count_run_errors: run_name={}, fn={}, db_errors={}, storage_errors={}".\
    #     format(run_name, fn, db_errors, storage_errors))

    return db_errors, storage_errors

def count_node_errors():
    db_errors = 0
    storage_errors = 0
    run_error_dir = error_names_dir()

    if os.path.exists(run_error_dir):
        for entry in os.listdir(run_error_dir):

            # count errors for run_name in ENTRY
            fn = "{}/{}".format(run_error_dir, entry)
            if os.path.isfile(fn):
                db_err, st_err = count_run_errors(fn=fn)
                db_errors += db_err
                storage_errors += st_err

    return db_errors, storage_errors
