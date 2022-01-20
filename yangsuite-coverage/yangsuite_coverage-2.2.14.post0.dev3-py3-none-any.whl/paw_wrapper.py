# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Pre-commit Automated Workflow (PAW) wrapper
https://wiki.cisco.com/display/DEVXTOOLS/PAW+User+Guide
"""
import os
import argparse
import json
import sys
from yscoverage.precommit import precommit_check, MODELDIRS, MODELPATH
from collections import OrderedDict

paw_results = OrderedDict()
dirname = ""
fcov = "/auto/ddmi/tool/max_model_coverage.txt"
# Default coverage number when script runs in error
unknown_coverage = 999999

# TESTDIRS
TESTPATH = '/mgmt/dmi/model/tests/'
TESTDIRS = [TESTPATH + 'ned/',
            TESTPATH + 'openconfig/']


def setup_args():
    """Setup and return command line parameter parser object. """
    parse = argparse.ArgumentParser(description='Invoke precommit script',
                                    epilog="""
    Example:
    Invoke paw_wrapper
    python paw_wrapper.py -ws /nobackup/graceho/polaris_dev/git/0520/polaris
        -branch polaris_dev -models /nobackup/graceho/wrapper_models.txt
        --baseline
    """)
    parse.add_argument('-ws', '--ws', type=str, dest='ws',
                       required=True,
                       help='Path to the workspace')

    parse.add_argument('-branch', '--branch', type=str, dest='branch',
                       required=True,
                       help='Branch')

    parse.add_argument('-models', '--models', type=str, dest='models',
                       required=True,
                       help='List of modified  models')

    parse.add_argument('-js', '--js', type=str, dest='js',
                       required=False,
                       help='Result file in json format')

    # Add flag for baseline run
    parse.add_argument('--baseline', action='store_true',
                       required=False,
                       help='Baseline run')

    return parse


def check_file_writable(fnm):
    """Check if the file is writable.

       Args:
           fnm (str): Path to a filename

       Returns:
           bool: True if the file is writable. False otherwise.
    """
    if os.path.exists(fnm):
        # path exists
        if os.path.isfile(fnm):  # is it a file or a dir?
            # also works when file is a link and the target is writable
            return os.access(fnm, os.W_OK)
        else:
            return False  # path is a dir, so cannot write as a file
    # target does not exist, check perms on parent dir
    pdir = os.path.dirname(fnm)
    if not pdir:
        pdir = '.'
    # target is creatable if parent dir is writable
    return os.access(pdir, os.W_OK)


def match_directory(matchdirs, dirstr):
    """Check if the modified directory is a match.

       Args:
           matchdirs (str): List of directories to be matched
           dirstr (str): The directory to compare against

       Returns:
           (list): List of matched directories
    """
    result = []
    for matchdir in matchdirs:
        if dirstr.startswith(matchdir):
            result.append(dirstr)
            return result

    return result


def check_model_exist(parentdir, modelname):
    """Check if the model exists in the ws.

       Args:
           parentdir (str): Parent directory
           modelname (str): Modelname

       Returns:
           (bool): True if model exists. False otherwise.
    """
    found = False
    for modeldir in MODELDIRS:
        name = modelname + '.yang'
        binosd = os.path.join(parentdir, 'binos')
        # modeldir[0] is a '/'
        filepath = os.path.join(binosd, modeldir[1:], name)
        if os.path.isfile(filepath):
            found = True
            break

    return found


def get_model_list(modelfile):
    """Get model list.

       Args:
           modelfile (str): Path to a file that contains the
                            list of the models

       Returns:
           (tuple): (list, bool)
               WHERE
               list is the list of modified models
               bool is TRUE if pre-commit check needs to be run.
               False otherwise.
    """
    # TODO: Breaking up the code into classes (Issue #67)
    skip_prefixes = ['-rpc.yang', '-ann.yang', '-types.yang']
    modelnames = []
    run_precommit = False

    with open(modelfile, 'r') as readfile:
        for line in readfile:
            splitline = line.strip().split('binos')
            line = splitline[-1]
            result = match_directory(MODELDIRS + TESTDIRS, line)
            if not result:
                continue
            if result[0].startswith(MODELPATH) and line.endswith('.yang'):
                if any(line.endswith(skip_prefix)
                        for skip_prefix in skip_prefixes):
                    # Skip types, rpc and annotation files
                    continue
                # Get the model name
                filename = os.path.basename(line)
                modelname = os.path.splitext(filename)[0]
                if (not modelname.startswith('Cisco-IOS-XE-') and
                        not modelname.startswith('openconfig-')):
                    continue
                if modelname not in modelnames:
                    modelnames.append(modelname)
                run_precommit = True
            else:
                testdir = result[0]
                if testdir.startswith(TESTPATH):
                    modelname = line.split(TESTPATH)[1].split('/')[1]
                    if (not modelname.startswith('Cisco-IOS-XE-') and
                            not modelname.startswith('openconfig-')):
                        continue
                    if not check_model_exist(splitline[0], modelname):
                        continue
                    if modelname not in modelnames:
                        modelnames.append(modelname)

    return modelnames, run_precommit


def get_baseline_coverage(data, modelname):
    """Get coverage number for baseline model.

       Args:
           data (dict): Dictionary of the results
           modelname (str): Model name

       Returns:
           (float): Coverage number of the baseline model
    """
    coverage = 0
    for base_entries in data["baseline"]:
        if base_entries["modelname"] == modelname:
            coverage = base_entries["coverage"]
            break

    return coverage


def get_max_model_coverage(fcov, modelname):
    """Get maximum coverage number can be attained for a model from a
       configurable file.
       If no matching entry is found in the configurable file, the default
       maximum coverage number is 100.

       The configuration file has two columns.
       First column is the modelname. Second column is the max coverage number.
       i.e.
       Cisco-IOS-XE-aaa 6.2
       Cisco-IOS-XE-bfd 1
       Cisco-IOS-XE-ppp 16.9
       ----

       Args:
           fcov (str): Path to the coverage file
           modelname (str): Model name

       Returns:
           (float): Maximum number for a model
    """
    max_coverage = 0
    with open(fcov) as fh:
        for line in fh:
            items = line.strip().split(' ')
            if items[0] == modelname:
                max_coverage = float(items[-1])
                break

    return max_coverage


def validate_results(fcov, output):
    """Validate results.
       Compare baseline coverage data against updated model coverage data.
       Set status to SUCCESS if updated model coverage data is larger
       than the baseline coverage data

       Args:
           output (str): Path to the json output file

    """
    with open(output, 'r+') as fh:
        data = json.load(fh, object_pairs_hook=OrderedDict)

        # update json here
        for entries in data["withdiffs"]:
            # look for entries model name
            modelname = entries["modelname"]
            baseline_coverage = get_baseline_coverage(data, modelname)
            latest_coverage = entries["coverage"]
            max_coverage = get_max_model_coverage(fcov, modelname)
            if (baseline_coverage == unknown_coverage or
                    latest_coverage == unknown_coverage):
                entries["status"] = "FAILED"
                data["overall_status"] = "FAILED"
                data["exit_code"] = 1
                data["reason"] = "Unable to calculate model coverage"
            elif (latest_coverage >= baseline_coverage and
                  latest_coverage > 0 and latest_coverage >= max_coverage):
                entries["status"] = "SUCCESS"
            else:
                entries["status"] = "FAILED"
                data["overall_status"] = "FAILED"
                data["exit_code"] = 1
                failure_reason = "Model coverage has not increased"
                data["reason"] = failure_reason

        fh.seek(0)
        fh.truncate()
        json.dump(data, fh, sort_keys=False,
                  indent=4, separators=(',', ': '))


def build_results(parent, key, value, create=False, modelname=None):
    """Build json output.

       Args:
           parent (str): Parent key
           key (str): Item key
           value (str): Item value
           create (bool): Create a new list entry
           modelname (str): Model name

        Sample output

    {
        "command": "paw_wrapper.py -ws /nobackup/o/0520/polaris
            -branch polaris_dev -models wrapper_models.txt",
        "ws_root": "/nobackup/o/polaris_dev/git/0520/polaris",
        "overall_status": "FAILED",
        "exit_code": 0,
        "contact_alias": "yang-coverage-support",
        "reason": "Completed Successfully",
        "num_file_analyzed": 3
        "baseline": [
            {
                "modelname": "Cisco-IOS-XE-aaa",
                "coverage": 4.2,
                "log": "/nobackup/o/0520/polaris/LOGS/baseline/...aaa.log"
            },
            {
                "modelname": "Cisco-IOS-XE-bfd",
                "coverage": 0.0,
                "log": "/nobackup/o/0520/polaris/LOGS/baseline/...bfd.log"
            },
            {
                "modelname": "Cisco-IOS-XE-ppp",
                "coverage": 16.9,
                "log": "/nobackup/o/0520/polaris/LOGS/baseline/...-ppp.log"
            }
        ],
        "withdiffs": [
            {
                "modelname": "Cisco-IOS-XE-aaa",
                "coverage": 4.2,
                "log": "/nobackup/o/0520/polaris/LOGS/Cisco-IOS-XE-aaa.log",
                "status": "FAILED"
            },
            {
                "modelname": "Cisco-IOS-XE-bfd",
                "coverage": 0.0,
                "log": "/nobackup/o/0520/polaris/LOGS/Cisco-IOS-XE-bfd.log",
                "status": "FAILED"
            },
            {
                "modelname": "Cisco-IOS-XE-ppp",
                "coverage": 16.9,
                "log": "/nobackup/o/0520/polaris/LOGS/Cisco-IOS-XE-ppp.log",
                "status": "FAILED"
            }
        ],
        "precommit": [
            {
                "status": "FAILED",
                "coverage": 0.0,
                "log": "/nobackup/o/0520/polaris/LOGS/precommit.log"
            }
        ]
    }
    """
    if not paw_results[parent] or create:
        paw_results[parent].append(OrderedDict([(key, value)]))
    else:
        if not modelname:
            if parent in paw_results and paw_results[parent]:
                paw_results[parent][0].update({key: value})
        else:
            # Loop through the list entries
            for entries in paw_results[parent]:
                new_entries = entries.copy()
                # Loop through the dictionary
                for entry in new_entries:
                    if new_entries[entry] == modelname:
                        entries.update({key: value})


def write_error_results(output):
    """Write error results to json file.

       Args:
           output (str): Path to the json output file
    """
    if (check_file_writable(output)):
        # Write results to json file
        with open(output, 'w') as outfile:
            json.dump(paw_results, outfile, sort_keys=False,
                      indent=4, separators=(',', ': '))


def write_results(baseline, output):
    """Write results to json file.

       Args:
           baseline (bool): True if it is a baseline run. False otherwise.
           output (str): Path to the json output file
    """
    if (check_file_writable(output)):
        if baseline:
            # Write results to json file
            with open(output, 'w') as outfile:
                json.dump(paw_results, outfile, sort_keys=False,
                          indent=4, separators=(',', ': '))
        else:
            with open(output) as outfile:
                data = json.load(outfile, object_pairs_hook=OrderedDict)

            data.update(paw_results)

            with open(output, 'w') as outfile:
                json.dump(data, outfile, sort_keys=False,
                          indent=4, separators=(',', ': '))


def set_json_header(ws, branch, models):
    """Set json file header.

       Args:
           ws (str): Workspace
           branch (str): Branch name
           models (str): File contains list of modified models
    """
    # Build the command string
    command_str = os.path.basename(__file__)
    "{0} -ws {1} -branch {2} -models {3}".format(command_str,
                                                 ws,
                                                 branch,
                                                 models)

    # Build command string
    paw_results["command"] = command_str
    # Build the ws root
    paw_results["ws_root"] = ws
    paw_results["overall_status"] = "SUCCESS"
    paw_results["exit_code"] = 0
    paw_results["contact_alias"] = "yang-coverage-support"
    paw_results["reason"] = "Completed Successfully"
    paw_results["num_file_analyzed"] = 0


def init_json_data(baseline):
    """Set json file header.

       Args:
           baseline (bool): True if it's a baseline run. False otherwise.

       Returns:
           (tuple): (str, str)
               WHERE
               parentname is the name of the parent dictionary
               logpath is the path to the log file
    """
    if baseline:
        paw_results["baseline"] = []
        parentname = "baseline"
        logpath = os.path.join(dirname, "baseline")
    else:
        paw_results["withdiffs"] = []
        parentname = "withdiffs"
        logpath = dirname

    return parentname, logpath


def get_model_coverage(ws, branch, models, modelnames,
                       baseline, run_precommit):
    """Get model coverage by calling precommit_check.

       Args:
           ws (str): Workspace
           branch (str): Branch name
           models: (str): Path to file contains list of modified models
           modelnames: (str): List of modified models
           baseline (bool): True if it's a baseline run. False otherwise.
           run_precommit (bool): True if precommit check needs to
                                 be done. False otherwise.

       Returns:
           (tuple): (bool, str)
               WHERE
               bool is TRUE if the precommit script compeleted
               successfully. False otherwise.
               str: Reason for the failure
    """
    parentname, logpath = init_json_data(baseline)

    # When there is a change in model or tests directory
    for modelname in modelnames:
        logfile = modelname + ".log"
        filepath = os.path.join(logpath, logfile)
        ret = precommit_check(ws, branch, modelname,
                              None, True, filepath, models)
        build_results(parentname, "modelname", modelname, True)
        if not ret:
            # Errors in running precommit_check
            # (i.e. Unable to unzip a zip file)
            build_results(parentname, "coverage", float(unknown_coverage),
                          modelname=modelname)
        else:
            build_results(parentname, "coverage", float(0),
                          modelname=modelname)

        set_coverage = False
        if os.path.isfile(filepath):
            for line in reversed(open(filepath).readlines()):
                if line.startswith("Test Coverage:"):
                    coverage = line.split('Test Coverage: ')[-1].strip('%\n')
                    build_results(parentname, "coverage", float(coverage),
                                  modelname=modelname)
                    build_results(parentname, "log", filepath,
                                  modelname=modelname)
                    set_coverage = True

                if set_coverage:
                    break

            # Test Coverage not calculated
            if not set_coverage:
                build_results(parentname, "coverage", float(unknown_coverage),
                              modelname=modelname)

    # when there is change in model directory in the updated workspace
    if not baseline and run_precommit:
        filepath = os.path.join(dirname, "precommit.log")
        ret = precommit_check(ws, branch, None, None, False, filepath, models)
        if not ret:
            build_results("precommit", "status", "FAILED")
            paw_results["overall_status"] = "FAILED"
            return False, "Precommit Failed"

        set_status = False
        set_coverage = False
        paw_results["precommit"] = []
        if os.path.isfile(filepath):
            for line in reversed(open(filepath).readlines()):
                if line.startswith("PRECOMMIT FAILED"):
                    build_results("precommit", "status", "FAILED")
                    paw_results["overall_status"] = "FAILED"
                    if not paw_results["exit_code"]:
                        paw_results["exit_code"] = 1
                        paw_results["reason"] = "Precommit failed"
                    set_status = True
                elif line.startswith("PRECOMMIT SUCCESS"):
                    build_results("precommit", "status", "SUCCESS")
                    set_status = True
                else:
                    if line.startswith("Test Coverage:"):
                        coverage = line.split('Test Coverage: ')[-1]
                        coverage = coverage.strip('%\n')
                        build_results("precommit", "coverage", float(coverage))
                        set_coverage = True

                if set_status and set_coverage:
                    break

        build_results("precommit", "log", filepath)

    return True, "Success"


def paw_wrapper_init():
    """Initialize the parser.

       Args:
           ---

       Returns:
           list: List of input arguments
    """
    # Get Command Parameters
    parse = setup_args()
    args = parse.parse_args()

    return args


def update_json_header(js, exit_code, reason):
    """Update json file header.

       Args:
           js (str): Path to the json output file
           exit_code (int): 0 if exits without error. Otherwise,
                            it is set to 1
           reason (str): Reason for exit
    """
    paw_results["exit_code"] = exit_code
    paw_results["reason"] = reason
    if exit_code:
        paw_results["overall_status"] = "FAILED"

    # Write results
    write_error_results(js)


def set_log_dirname(ws):
    """Set directory name.

       Args:
           ws (str): Path to the workspace
    """
    global dirname
    dirname = os.path.join(ws, "LOGS")


def paw_wrapper():
    """PAW wrapper entry point.

       It is called by PAW to generate model coverage for a model
       changeset. It compares the model coverage with the
       baseline results, then validates the covearge number is improving for
       a changeset.
    """

    args = paw_wrapper_init()

    ws = args.ws
    branch = args.branch
    models = args.models
    baseline = args.baseline
    js = args.js

    # Set the header in the json result file
    set_json_header(ws, branch, models)

    set_log_dirname(ws)
    baseline_path = os.path.join(dirname, "baseline")
    # Validation for the json file
    if js:
        if not os.path.exists(os.path.dirname(js)):
            sys.exit(1)
    else:
        js = os.path.join(ws, "LOGS", "precommit_paw.json")

    # Create the directory
    if os.path.exists(ws):
        os.makedirs(baseline_path, exist_ok=True)

    if not os.path.exists(dirname):
        # Unable to create result directories
        exit_code = 1
        reason = "Unable to create result directories."
        update_json_header(js, exit_code, reason)
        sys.exit(exit_code)

    # Json file must exist for non-baseline run
    if not baseline:
        if not os.path.isfile(js):
            exit_code = 1
            reason = "Unable to locate " + js + " for non-baseline run."
            update_json_header(js, exit_code, reason)
            sys.exit(exit_code)
        else:
            # Baseline data does not exist
            with open(js) as outfile:
                data = json.load(outfile, object_pairs_hook=OrderedDict)
                if data["reason"] == "Changeset contains no model changes.":
                    sys.exit(0)
                if "baseline" not in data or not data["baseline"]:
                    # Modules which have no tree to display
                    exit_code = 0
                    reason = "Missing baseline data for non-baseline run."
                    update_json_header(js, exit_code, reason)
                    sys.exit(exit_code)

    # Get model list
    modelnames, run_precommit = get_model_list(models)

    file_to_analyzed = len(modelnames)

    paw_results["num_file_analyzed"] = file_to_analyzed

    # Empty model file
    if not file_to_analyzed:
        exit_code = 0
        reason = "Changeset contains no model changes."
        update_json_header(js, exit_code, reason)
        sys.exit(exit_code)

    status, errstr = get_model_coverage(ws, branch, models, modelnames,
                                        baseline, run_precommit)

    if not status:
        # Error in running coverage script
        exit_code = 1
        reason = errstr
        update_json_header(js, exit_code, reason)
        sys.exit(exit_code)

    # Combine two json files
    write_results(baseline, js)

    if not args.baseline:
        validate_results(fcov, js)

    # cleanup the directory
    # shutil.rmtree(dirname)


if __name__ == '__main__':
    # Get Command Parameters
    paw_wrapper()
