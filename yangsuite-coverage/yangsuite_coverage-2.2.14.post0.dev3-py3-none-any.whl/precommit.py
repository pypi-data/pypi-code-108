# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Report Model Coverage"""
import os
import argparse
import glob
import subprocess
import shutil
import re
import tempfile
import json
import logging
import datetime
import lxml.etree as et
import zipfile

from yscoverage.dataset import dataset_for_directory
from yscoverage.yangdiff import getdiff
from ysyangtree.tasks import TaskHandler
from yangsuite.logs import get_logger

# Suppress verbose logging messages from being echoed to console when
# running as CLI script
get_logger('yangsuite.ysyangtree.context').setLevel(logging.ERROR)
get_logger('yangsuite.ysyangtree.ymodels').setLevel(logging.ERROR)
logger = get_logger('model-coverage')

# Template pattern
var_pattern = re.compile(r"{{.*}}|_-.*-_")
var_template = ['{{', '_-']

# Do not write log to console by default
console_log = False
# Dictionary for all test cases
all_tc_dict = dict()

# Model Paths
MODELPATH = '/mgmt/dmi/model/yang/src/'
TDLMODELPATH = '/mgmt/dmi/libyang/'
MODELDIRS = [MODELPATH + 'ned/',
             MODELPATH + 'openconfig/',
             TDLMODELPATH]


def setup_args():
    """Setup and return command line parameter parser object. """
    parse = argparse.ArgumentParser(description='DMI Precommit Check Tool',
                                    epilog="""
    Example:
    Precommit Check Tool:
    python precommit-check.py -ws path_to_workspace -dir working_dir
                              -label branch
    """)

    parse.add_argument('-ws', '--workspace', type=str, dest='workspace',
                       required=False,
                       help='Path to the workspace to run precommit against')

    parse.add_argument('-label', '--label', type=str, dest='label',
                       required=False,
                       help='Branch name')

    parse.add_argument('-reportname', '--reportname', type=str,
                       dest='reportname',
                       required=False,
                       help='Model name')

    parse.add_argument('-bugid', '--bugid', type=str, dest='bugid',
                       required=False,
                       help='Bugid')

    parse.add_argument('--report', action='store_true',
                       required=False,
                       help='Generate model coverage report')

    parse.add_argument('-logfile', '--logfile', type=str, dest='logfile',
                       required=False,
                       help='Log file')

    return parse


def report(msg, fd):
    """Write results to console and/or file."""
    if console_log:
        print(msg)
    fd.write(msg + '\n')


def print_invalid_testcases(testcases, header, f):
    """Print invalid test cases.

    Args:
        testcases (dict): A dictionary of test xpaths and its
                          corresponding test files
        header (str): report header
        f (int): file descriptor
    """
    print_header = False

    for k, v in testcases.items():
        if not print_header:
            report('  ' + header, f)
            report('  ' + len(header)*'=', f)
            print_header = True
        report('  ' + k, f)
        report('   ' + v, f)

    if testcases:
        report('\n', f)


def run_cmd(cmd, wdir=None):
    """Execute a command line.

    Args:
        cmd (str): the command to be executed
        wdir (str): path to the workspace

    Return:
        (str): output of the command
    """
    if not wdir:
        wdir = os.getcwd()
    logger.debug("Calling: %s", ''.join(cmd))
    return subprocess.check_output(cmd,
                                   cwd=wdir,
                                   stderr=subprocess.STDOUT).decode()


def get_git_changeset(logfile, wspath):
    """Retrive a list of modified model files from a git ws.

    Args:
        logfile (str): absolute path to the file to write output to
        wspath (str): path to the workspace

    Return:
        ret (int): return status
    """
    ret = 0
    command = ['git', 'diff', '--name-only', '--diff-filter=AM']
    with open(logfile, 'w') as f:
        ret = subprocess.call(command,
                              cwd=wspath,
                              stdout=f,
                              stderr=subprocess.PIPE)

    return ret


def copy_tdl_base_model(tdlpath, workspace, base_workspace):
    """Copy tdl models to the baseline git ws.

    Args:
        tdlpath (str): path to the tdl transform file
        workspace (str): path to the workspace
        base_workspace (str): path to the baseline workspace

    Return:
        ret (int): return status
    """
    # tdlpath: 'binos/mgmt/dmi/libyang/src/yang/Cisco-IOS-XE-bgp-oper.yang'
    modelpath = os.path.splitext(tdlpath)[0]
    # modelpath: 'binos/mgmt/dmi/libyang/src/yang/Cisco-IOS-XE-bgp-oper'
    mn = os.path.basename(modelpath)

    src_path = os.path.join('binos/mgmt/dmi/model/tests/tdl-oper',
                            mn,
                            'baseline')
    dst_path = os.path.join(strip_tdlmodelpath(), 'model')

    full_src_path = os.path.join(workspace, src_path, mn + '.yang')
    full_dst_path = os.path.join(base_workspace, dst_path)

    shutil.copy(full_src_path, full_dst_path)
    return


def copy_base_model(model_path, workspace, label, base_workspace):
    """Copy baseline models to the baseline git ws.

    Args:
        model_path (str): path to the model from binos directory
        workspace (str): path to the workspace
        base_workspace (str): path to the baseline workspace

    Return:
        ret (int): return status
    """
    ret = 0
    # copy model from origin/<label>
    origin_str = 'origin/' + label + ':' + model_path
    command = ['git', 'show', origin_str]

    sha = ''
    output = run_cmd(['git', 'branch', '-vv'], workspace)

    # output of 'git branch -vv'
    # * (HEAD detached at V1612_1SPRD3_FC1) dc999411eeeb CSCvr02304 Boot ...
    # s2c/polaris_dev                       8f31b9cf1285 [origin/s2c/polar ...
    if output.startswith('*'):
        # commit SHA is between column 38 and column 50
        sha = output[38:50]

        if sha:
            # copy model from sha
            origin_str = sha + ':' + model_path
            # git show dc999411eeeb:./Cisco-IOS-XE-wccp.yang
            command = ['git', 'show', origin_str]

    tmp_line = os.path.relpath(model_path, 'binos')
    with open(os.path.join(base_workspace, tmp_line), 'w') as f:
        ret = subprocess.call(command,
                              cwd=workspace,
                              stdout=f,
                              stderr=subprocess.PIPE)

    return ret


def get_acme_changeset(logfile, wspath):
    """Retrive a list of modified model files from an acme ws.

    Args:
        logfile (str): the command to be executed
        wspath (str): path to the workspace

    Return:
        None
    """
    command = ['acme', 'lschangeset']
    with open(logfile, 'w') as f:
        # ignore return code
        subprocess.call(command,
                        cwd=wspath,
                        stdout=f,
                        stderr=subprocess.PIPE)

    with open(logfile, 'r') as f:
        for line in f.readlines():
            if line.startswith('Component: '):
                chgsetver = line.split('Component: ')[-1]
                return chgsetver

    return None


def pull_baseline_acme_ws(projlu_fullpath, comp_ver,
                          label, base_workspace):
    """Pull a baseline acme ws.

    Args:
        projlu_fullpath (str): path to .projlu for dmi component
        comp_ver (str): dmi component version
        label (str): branch name
        base_workspace (str): path to the baseline workspace

    Return:
        (boolean): True if the workspace is pulled successfully.
                   Otherwise, returns False.
    """
    if comp_ver is None:
        # get dmi version from source tree
        with open(projlu_fullpath, 'r') as fd:
            for line in fd.readlines():
                if 'mgmt/dmi' in line:
                    dmi_version = line.replace(" ", "@")
                    dmi_version = dmi_version.strip()
                    break
    else:
        # use version in acme lschangeset
        dmi_version = comp_ver.strip()

    c_dmi_version = 'mgmt/dmi@' + label
    logger.debug("dmi_version: " + dmi_version)
    if not dmi_version.startswith(c_dmi_version):
        logger.error("Invalid ws. Cannot get dmi version.")
        return False

    logger.info('Pulling baseline ws from ' + dmi_version + '......')
    # Pull a baseline ws
    ret = run_cmd(['acme', 'init', '-comp', dmi_version, '-sb', 'binos'],
                  base_workspace)

    logger.debug('acme init: ' + ret)

    if not any("The workspace is ready for use" in s for s
               in ret.splitlines()):
        logger.error("Cannot create baseline tree.")
        return False

    return True


def trim_broken_testset(del_xpaths, tc_xpaths):
    """Trim broken test cases.

        Example:

        Match the deleted xpaths against test case using template.

        deleted xpaths:
        "/ios:native/ios:interface/ios:GigabitEthernet0/ios:name"

        test case xpath using template:
        "/ios:native/ios:interface/ios:{{ interface_name }}/ios:name"

        Add the deleted xpaths to the set of trim broken test cases
        if a match is found.

    Args:
        del_xpaths (set): deleted xpaths
        tc_xpaths (set): test case xpaths with namespace prefixes removed

    Return:
        (set): A set of broken test paths
    """
    trim_broken_tc = set()

    for del_xpath in del_xpaths:
        for tc_xpath in tc_xpaths:
            if not any(var in tc_xpath for var in var_template):
                trim_broken_tc.add(del_xpath)
                continue
            # process the template
            match = re.match(var_pattern.sub('.*', tc_xpath), del_xpath)
            if match:
                trim_broken_tc.add(del_xpath)
                break

    return trim_broken_tc


def trim_missing_testset(missing_tcs, tc_xpaths):
    """Trim missing test cases.
       Check a missing test case against the teamplate {{.*}}.

    Args:
        missing_tcs (set): missing test cases
        tc_xpaths (set): test case xpaths with namespace prefixes removed

    Return:
        (set): A set of broken test paths
    """
    trim_missing_tc = set()

    for missing_tc in missing_tcs:
        for tc_xpath in tc_xpaths:
            if not any(var in tc_xpath for var in var_template):
                continue
            # process the template
            match = re.match(var_pattern.sub('.*', tc_xpath), missing_tc)
            if match:
                break
        else:
            trim_missing_tc.add(missing_tc)

    return trim_missing_tc


def get_excluded_xpaths(workspace,
                        model_test_path,
                        modelname,
                        excluded_xpath_filename,
                        modelpath):

    """Get the list of excluded xpaths from the model directory.

    Args:
        workspace (str): path to the workspace
        model_test_path (str): path to the model test directory
        modelname (str): model name
        excluded_xpaths_filename(str): file which stores the
                                       excluded xpaths
        modelpath (str): model path

    Return:
        (set): A set of trim missing test paths
    """

    exclusion_xpaths = []
    if not modelname:
        return exclusion_xpaths

    testpath = os.path.join(workspace, model_test_path)
    excluded_path = get_excluded_xpaths_path(modelname,
                                             testpath,
                                             excluded_xpath_filename,
                                             modelpath)

    if os.path.isfile(excluded_path):
        with open(excluded_path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                exclusion_xpaths.append(line)

    return exclusion_xpaths


def remove_excluded_xpaths(trim_missing_tc,
                           modelname,
                           excluded_xpaths):
    """Remove exception xpaths from missing test cases.
       Check a missing test case against the exclusion list.

    Args:
        trim_missing_tc (set): missing test cases
        modelname (str): model name
        excluded_xpaths(list): excluded xpaths

    Return:
        (set): A set of trim missing test paths
    """
    trim_exception_tc = set()

    for xpath in excluded_xpaths:
        for missing_tc in trim_missing_tc:
            if missing_tc.startswith(xpath):
                trim_exception_tc.add(missing_tc)

    final_set = trim_missing_tc - trim_exception_tc
    return final_set


def report_excluded_xpaths(reportname,
                           trim_missing_tc,
                           modelname,
                           model_tests_path):
    """ Report missing xpaths which are not in the exclusion list.
        Exclude the missing xpaths in model_tests_path from the report

    Args:
        reportname (str): report name
        trim_missing_tc (set): missing test cases
        modelname (str): model name
        model_tests_path(list): xpaths in excluded list

    Return:
        (set): missing test cases with excluded xpaths
    """

    if not model_tests_path:
        return None

    with open(reportname, "a") as f:
        if not trim_missing_tc:
            return None
        report('Missing test cases', f)
        report(17*'=', f)
        trim_exception_tc = remove_excluded_xpaths(trim_missing_tc,
                                                   modelname,
                                                   model_tests_path)
        if not trim_exception_tc:
            report('None', f)
        else:
            for i in trim_exception_tc:
                report(i, f)

        report('\n', f)

    return trim_exception_tc


def get_test_xpaths(tc_dict_list):
    """Retrieve test case xpaths.

    Args:
        tc_dict_list (list): a list of test case dictionaries

    Return:
        (set): A set of test case paths
    """
    tc_xpaths = set()
    for tc_dict in tc_dict_list:
        for i in tuple(tc_dict['xpaths']):
            tc_xpaths.add(i)

    return tc_xpaths


def get_tc_dict_from_xpath(xpath, tc_data_list):
    """Given an xpath, return the test case dictionary.

    Args:
        xpath (str): a xpath
        tc_dict_list (list): a list of test case dictionaries

    Return:
        (dict): A test case dictionary
    """
    found = False
    """get task directory from xpath"""
    for tc_dict in tc_data_list:
        for xp in tc_dict['xpaths']:
            if not any(var in xp for var in var_template):
                if xp == xpath:
                    found = True
                    break
                else:
                    continue
            # remove all the prefixes
            converted_xp = re.sub('[^/]+:', '', xp)
            # replace {{ interface_name }} and '_-var-_' to .*
            match = re.match(var_pattern.sub('.*', converted_xp), xpath)
            if match:
                found = True
                break

        if found:
            break

    if found:
        if 'category' in tc_dict:
            # Validate cli or oper verification
            check_tc(tc_dict)
        return tc_dict
    else:
        return None


def check_tc(tc_dict):
    """Validate if ssh verify or oper data exists given a test directory.

    Args:
        tc_dict (dict): a test case dictionary

    Return:
        None
    """
    # Build dictionary for all test cases
    # The key is the (category, task name).
    # The value is the filepath of the test case.
    if not all_tc_dict:
        for path, dirs, files in os.walk(os.path.join(tc_dict['path'])):
            for name in files:
                if name.endswith(".tst"):
                    with open(os.path.join(path, name), 'r') as f:
                        tst_data = json.load(f)
                    if 'tasks' in tst_data:
                        for task in tst_data['tasks']:
                            category = task[0]
                            task_name = task[1]
                            all_tc_dict[(category, task_name)] = \
                                os.path.join(path, name)

    # Look up the dict for the filepath of a test case using its category
    # and task name
    tn = tc_dict['task_name']
    cat = tc_dict['category']
    if (cat, tn) in all_tc_dict:
        test_filepath = all_tc_dict[(cat, tn)]
        name = os.path.basename(os.path.normpath(test_filepath))
        with open(test_filepath, 'r') as f:
            tst_data = json.load(f)
            tc_dict['test_name'].add(name)
            if 'ssh' in tst_data:
                if 'verify' in tst_data.get('ssh'):
                    ssh_verify = tst_data.get('ssh').get('verify')
                    if ssh_verify:
                        tc_dict['cli_verified'] = True

            if 'oper' in tst_data:
                oper_verify = tst_data.get('oper')
                if oper_verify:
                    tc_dict['oper_verified'] = True


def get_rpc_tag(elem):
    """Get RPC tag, minus any XML namespace.

    Args:
        elem (element): a custom rpc element
    Return:
        tag (str): a rpc tag
    """
    if elem.tag.startswith('{'):
        return elem.tag.split('}')[1]

    return elem.tag


def build_xpaths_from_rpc(rpc, path, result):
    """Build xpaths from custome rpc.

    Args:
        rpc (str): a custom rpc
        path (str): an xpath
        result (set): a set of xpaths
    Return:
        None
    """
    for child in rpc.getchildren():
        build_xpaths_from_rpc(child, path + '/' + get_rpc_tag(child), result)

    if not len(rpc):
        result.add(path)


def process_custom_rpc(name, rpc):
    """Process custom rpc in the test case.

    Args:
        rpc (str): a custom rpc

    Return:
        result (set): a set of xpaths retrived from custom rpc
    """
    result = set()
    try:
        obj = et.fromstring(rpc)
    except et.XMLSyntaxError as e:
        logger.error("XML syntax error in rpc\n%s", str(e))
        logger.error("Please fix the test case %s", name)
        return result

    root = obj.getroottree()

    ns = 'urn:ietf:params:xml:ns:netconf:base:1.0'
    config = root.find('{%s}edit-config/{%s}config' % (ns, ns))
    if config is not None:
        build_xpaths_from_rpc(config[0],
                              '/' + get_rpc_tag(config[0]),
                              result)

    return result


def extract_zipfile(source_filename, dest_dir):
    """Extract test cases from a zip file

    Args:
        source_filename (str): zip file name
        dest_dir (dest_dir): destination directory

    Return:
        ---
    """
    with zipfile.ZipFile(source_filename) as zf:
        zf.extractall(dest_dir)


def store_test_data(testdir):
    """Store test case data

    Args:
        testdir (str): test case directory

    Return:
        (list): List of test case dictionaries
    """
    tc_data_list = []
    for path, dirs, files in os.walk(testdir):
        for name in files:
            tc_xpaths = set()
            if name.endswith(".tsk"):
                replay = TaskHandler.get_replay(
                        os.path.dirname(path),
                        os.path.basename(path),
                        name[:name.index(".")])
                # Retrieving the xpaths
                for segment in replay.get('segments'):
                    modules = segment.get('yang').get('modules')
                    if modules is None:
                        # check for custom RPC
                        rpc = segment.get('yang').get('rpc')
                        if rpc is None:
                            continue
                        # process custom rpc
                        result = process_custom_rpc(name, rpc)
                        tc_xpaths = tc_xpaths | result
                    else:
                        for module in modules:
                            configs = modules.get(module).get('configs')
                            if configs is None:
                                continue
                            for config in configs:
                                # Strip out the list key entries
                                converted_xpath = re.sub(r"\[[^[]*]", "",
                                                         config['xpath'])
                                # Strip out namespace prefixes
                                np_xpath = re.sub('[^/]+:', '',
                                                  converted_xpath)
                                tc_xpaths.add(np_xpath)

                    tc_dict = dict()
                    tc_dict['task_name'] = replay.get('name')
                    tc_dict['category'] = replay.get('category')
                    # xpaths with namespace prefixes removed
                    tc_dict['xpaths'] = tc_xpaths
                    tc_dict['cli_verified'] = False
                    tc_dict['oper_verified'] = False
                    # absolute path to two levels up
                    parent_path = os.path.dirname(path)
                    tc_dict['path'] = os.path.dirname(parent_path)
                    tc_dict['test_name'] = set()

                    tc_data_list.append(tc_dict)

            if name.endswith(".tst"):
                # Get xpaths from oper test cases
                with open(os.path.join(path, name), 'r') as f:
                    tst_data = json.load(f)
                for operlist in tst_data.get('oper', []):
                    oper_opfields = operlist.get('opfields', [])
                    for op in oper_opfields:
                        if 'xpath' in op:
                            tc_xpaths.add(op.get('xpath'))

                if 'name' in tst_data:
                    tc_dict = dict()
                    tc_dict['task_name'] = tst_data.get('name')
                    # xpaths with namespace prefixes removed
                    tc_dict['xpaths'] = tc_xpaths
                    # absolute path to two levels up
                    parent_path = os.path.dirname(path)
                    tc_dict['path'] = os.path.dirname(parent_path)

                    tc_data_list.append(tc_dict)

    return tc_data_list


def get_zipfile_test_data(srcdir, destdir, modelname):
    """Get test data from zip file.

    Args:
        srcdir (str): zip file soruce directory
        destdir (str): directory to extract the zip file
        modelname (str): model name

    Return:
        (bool, bool): True if zip file exists. Otherwise, return False
                      True if errors are found
    """
    found = False
    error = False
    for path, dirs, files in os.walk(srcdir):
        for name in files:
            if zipfile.is_zipfile(os.path.join(path, name)):
                extract_path = os.path.join(destdir, modelname, name)
                if not os.path.exists(extract_path):
                    try:
                        os.makedirs(extract_path)
                    except OSError:
                        error = True
                        logger.error("Failed to create directory for zip "
                                     "files")
                        break
                extract_zipfile(os.path.join(path, name), extract_path)
                found = True

    return found, error


def get_test_data(model_tests_fullpath, modelist, zipfdir):
    """Scan through the test case directories in ws.
       Store task details in a dictionary.

    Args:
        model_tests_fullpath (str): full path to model test cases in a ws
        modelist (list): a list of model names
        zipfdir (str): zip file temp directory

        Example:
        model_tests_fullpath:
        '/nobackup/graceho/polaris_dev/git/0919/polaris/'
        'binos/mgmt/dmi/model/tests'
        modellist:
        [('/mgmt/dmi/libyang/_gen_yang-src-x86_64_cge7-vxe',
          'Cisco-IOS-XE-bgp-oper')]
        zipfdir
        '/tmp/tmpy47uyfbg/zip_tmpdir'

    Return:
        (list, bool): A list of test case dictionaries and a bool to indicate
                      if errors are found
    """
    tc_data_list = []

    for modelpath, modelname in modelist:
        # test_model_subdir: 'ned' or 'openconfig' or 'tdl-oper'
        test_model_subdir = get_model_subdir(modelname, modelpath)
        # test_model_fullpath:
        # i.e. <ws>/binos/mgmt/dmi/model/tests/ned/Cisco-IOS-XE-cdp
        test_model_fullpath = os.path.join(model_tests_fullpath,
                                           test_model_subdir,
                                           modelname)

        tc_data_list = store_test_data(test_model_fullpath)

        found, error = get_zipfile_test_data(test_model_fullpath,
                                             zipfdir,
                                             modelname)
        if found and not error:
            # Store test cases from zip file
            zipfile_data_list = store_test_data(os.path.join(
                                                zipfdir, modelname))
            tc_data_list += zipfile_data_list

    return tc_data_list, error


def find_tdlmodel(workspace, mn):
    """Find tdl model.

    Args:
        workspace (str): Path to the workspace
        mn (str): model name

    Return:
        (str): model path
    """
    # Find the tdl model. Return the path.
    libyangdir = [x[0] for x in
                  os.walk(os.path.join(workspace,
                                       'binos',
                                       'mgmt/dmi/libyang'))]
    for path in libyangdir:
        # Look for all tdl models in mgmt/dmi/libyang/_gen_yang-src*
        if 'mgmt/dmi/libyang/_gen_yang-src' in path:
            # Copy only .yang files
            files = glob.iglob(os.path.join(path, "*.yang"))
            for f in files:
                if mn in f:
                    return path.strip().split('binos')[-1].lstrip('/')

    return ""


def strip_tdlmodelpath():
    """Strip tdl model path.

    Return:
        (str): model path
    """
    return TDLMODELPATH.lstrip('/')


def get_model_subdir(modelname, modelpath):
    """Get model subdirectory.

    Args:
        modelname (str): Name of the model
        modelpath (str): model path

    Return:
        (str): type of model
    """
    if strip_tdlmodelpath() in modelpath:
        return "tdl-oper"

    if modelname.startswith('Cisco-IOS-XE'):
        return "ned"

    if "openconfig" in modelname:
        return "openconfig"

    return ''


def get_excluded_xpaths_path(modelname,
                             model_tests_fullpath,
                             excluded_xpaths_filename,
                             modelpath):
    """Get the location of the excluded xpaths file in a workspace.

    Args:
        modelname (str): model name
        model_tests_fullpath (str): path to the model test directory
        excluded_xpaths_filename(str): name of the file which contains the
                                       excluded xpaths

    Return:
        (str): path to the excluded xpaths file
    """

    test_model_subdir = get_model_subdir(modelname, modelpath)
    excluded_xpaths_path = os.path.join(model_tests_fullpath,
                                        test_model_subdir,
                                        modelname,
                                        excluded_xpaths_filename)

    return excluded_xpaths_path


def create_git_ws(chgsetfile, workspace, model_path,
                  label, base_workspace, modelnames):
    """Create a git ws.

    Args:
        chgsetfile (str): temp file contains the list of modified models
        workspace (str): user workspace
        model_path (str): model directory in ws
        label (str): branch name
        base_workspace (str): baseline workspace
        modelnames (str): Path to file contains list of modified models

        Example:
        chgsetfile: '/tmp/tmp1_xx_p_s/changeset.txt'
        workspace: '/nobackup/graceho/polaris_dev/git/0919/polaris'
        model_path: 'mgmt/dmi/model/yang/src'
        label: polaris_dev
        base_workspace: '/tmp/tmp1_xx_p_s/base_workspace'
        modelnames: None

    Return:
        (set): a set of modified models
    """
    modelist = list()
    if not modelnames:
        # No model list pass in
        ret = get_git_changeset(chgsetfile,
                                os.path.join(workspace,
                                             'binos',
                                             model_path))
        if ret:
            logger.error("Unable to get changeset")
            return modelist

    # Step 1: Copy the reference models i.e. ned, openconfig
    # src: /nobackup/graceho/polaris_dev/git/0912/polaris/ +
    #      binos/mgmt/dmi/model/yang/src
    # dst: /tmp/tmpf5hotcqw/base_workspace/mgmt/dmi/model/yang/src
    src = os.path.join(workspace, 'binos', model_path)
    dst = os.path.join(base_workspace, model_path)
    # copy the tree
    shutil.copytree(src, dst)

    # Step 2: Copy the reference tdl models
    # Loop through directory
    # /nobackup/graceho/polaris_dev/git/0912/polaris/binos/ +
    # mgmt/dmi/libyang
    libyangdir = [x[0] for x in
                  os.walk(os.path.join(workspace,
                                       'binos',
                                       'mgmt/dmi/libyang'))]
    tdl_model_path = os.path.join(strip_tdlmodelpath(), 'model')
    tdldst = os.path.join(base_workspace, tdl_model_path)

    # tdldst: /tmp/tmp1_xx_p_s/base_workspace/mgmt/dmi/libyang/model
    os.makedirs(tdldst)

    for path in libyangdir:
        # Look for all tdl models in mgmt/dmi/libyang/_gen_yang-src*
        if 'mgmt/dmi/libyang/_gen_yang-src' in path:
            # Copy only .yang files
            files = glob.iglob(os.path.join(path, "*.yang"))
            for f in files:
                if os.path.isfile(f):
                    shutil.copy2(f, tdldst)

    # copy the baseline models
    if not modelnames:
        filepath = chgsetfile
    else:
        filepath = modelnames

    with open(filepath, 'r') as f:
        for line in f.readlines():
            line = line.strip().split('binos')
            line = 'binos' + line[-1]
            if line.endswith('.yang') and any(md in line for md in MODELDIRS):
                # When there is a change in transform file
                if line.endswith('transform.yang'):
                    line = line.replace('-transform', '')
                    copy_tdl_base_model(line, workspace, base_workspace)
                else:
                    # Note: For NED and openconfig model
                    ret = copy_base_model(line, workspace,
                                          label, base_workspace)
                    if ret:
                        logger.error('Unable to copy base model ', line)
                        continue
                # change_path:
                # 'binos/mgmt/dmi/libyang/src/yang/Cisco-IOS-XE-bgp-oper'
                change_path = os.path.splitext(line)[0]
                # Path to the model
                # modelpath: 'binos/mgmt/dmi/libyang/src/yang'
                modelpath = os.path.dirname(change_path)
                # modelname: 'Cisco-IOS-XE-bgp-oper'
                modelname = os.path.basename(change_path)
                modelist.append((modelpath, modelname))

    return modelist


def create_acme_ws(chgsetfile, workspace, model_path,
                   label, base_workspace, precommit_tmpdir):
    """Create an acme ws.

    Args:
        chgsetfile (str): temp file contains the list of modified models
        workspace (str): user workspace
        model_path (str): model directory in ws
        label (str): branch name
        base_workspace (str): baseline workspace
        precommit_tmpdir (str): precommit temporary directory

    Return:
        (set): a set of modified models
    """

    projlu_path = 'binos/.acme_project/proj.lu'

    # Get changeset
    chgset_version = get_acme_changeset(chgsetfile,
                                        os.path.join(workspace,
                                                     'binos',
                                                     model_path))

    # Pull baseline ws
    if not pull_baseline_acme_ws(os.path.join(workspace, projlu_path),
                                 chgset_version,
                                 label,
                                 base_workspace):
        shutil.rmtree(precommit_tmpdir)
        return None

    # xpath processing
    logger.info("Processing xpaths......")

    plist = ['M', 'A']
    fset = set()
    with open(chgsetfile, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if line[0] in plist and line.endswith('.yang'):
                filename = os.path.basename(line[3:])
                modelname = os.path.splitext(filename)[0]
                fset.add(modelname)

    return fset


def create_baseline_ws(chgsetfile, workspace, model_path,
                       label, base_workspace, precommit_tmpdir, modelnames):
    """Create baseline ws.

    Args:
        chgsetfile (str): temp file contains the list of modified models
        workspace (str): user workspace
        model_path (str): model directory in ws
        label (str): branch name
        base_workspace (str): baseline workspace
        precommit_tmpdir (str): precommit temporary directory
        modelnames (str): Path to file contains list of modified models

    Return:
        (set): a set of modified models
    """
    if (os.path.isdir(os.path.join(workspace, ".git"))):
        modelist = create_git_ws(chgsetfile, workspace, model_path,
                                 label, base_workspace, modelnames)
    else:
        modelist = create_acme_ws(chgsetfile, workspace,
                                  model_path, label,
                                  base_workspace,
                                  precommit_tmpdir)

    return modelist


def is_data_node(entry):
    """Validate if this is a data node.

    Args:
        entry (list): an entry

    Return:
        (boolean): True if entry is a data node
    """
    # Check for presence container
    lentry = len(entry)
    if lentry >= 5 and entry[3] == 'container' and entry[4] == 'true':
        return True
    else:
        return entry[3] not in [
            'case',
            'choice',
            'container',
            'grouping',
            'identity',
            'typedef',
            'input',
            'output',
        ]


def get_all_xpaths(workspace, model_path, fset):
    """Get all xpaths from a model.

    Args:
        workspace (str): path to a ws
        model_path (list): model directory in ws
        fset (set): model name

    Return:
        (set): a set of xpaths
        (bool): True if it is a submodule
                Otherwise, return False
    """
    addons = ['status', 'module', 'nodetype', 'presence']

    new_xpaths = set()
    obsolete_containers = set()
    remove_obsolete_xpaths = set()
    for modelname in fset:
        model_subdir = get_model_subdir(modelname, model_path)

        if not model_subdir:
            logger.info('Model: ' + modelname + 'not supported')
            continue

        if model_subdir == "tdl-oper":
            # TDL generated model.
            model_subdir = ""

        to_dataset = dataset_for_directory(
            os.path.join(workspace,
                         'binos',
                         model_path.lstrip('/'),
                         model_subdir),
            modelname,
            addons
        )

        is_submod = False
        for row in to_dataset['data']:
            if not is_submod and row[-1] == 'submodule':
                is_submod = True
            # Filter out obsolete nodes
            if row[1] == 'obsolete':
                if row[3] in ['container', 'list']:
                    trim_obsolete_xpath = re.sub('[^/]+.:', '', row[0])
                    obsolete_containers.add(trim_obsolete_xpath)
                continue
            if not is_data_node(row):
                continue
            converted_new_xpath = re.sub('[^/]+.:', '', row[0])
            new_xpaths.add(converted_new_xpath)

    # This is a check added to catch those models which are not
    # following RFC standard for obsolete nodes
    # Filter out all xpaths whose parents are marked absolete
    for obsolete_container in obsolete_containers:
        for new_xpath in new_xpaths:
            if new_xpath.startswith(obsolete_container + '/'):
                remove_obsolete_xpaths.add(new_xpath)

    new_xpaths = new_xpaths - remove_obsolete_xpaths
    return new_xpaths, remove_obsolete_xpaths, is_submod


def get_changed_xpaths(workspace, model_path, base_workspace, modelist):
    """Get changed xpaths from ws.

    Args:
        workspace (str): path to a ws
        model_path (list): model directory in ws
        base_workspace: path to a baseline ws
        fset (set): a set of model names

    Return:
        new_xpaths (set): a set of newly added xpaths
        del_xpaths (set): a set of deleted xpaths
    """
    addons = ['datatype', 'module', 'nodetype']

    new_xpaths = set()
    del_xpaths = set()
    for modelpath, modelname in modelist:
        model_subdir = get_model_subdir(modelname, modelpath)

        if not model_subdir:
            logger.info('Model: ' + modelname + 'not supported')
            continue

        if model_subdir == "tdl-oper":
            # tdl generated model
            model_subdir = ""
            model_path_base = os.path.join(strip_tdlmodelpath(), 'model')
            # model_path_current:
            # 'mgmt/dmi/libyang/_gen_yang-src-x86_64_cge7-vxe'
            model_path_current = find_tdlmodel(workspace, modelname)
        else:
            model_path_base = model_path
            model_path_current = model_path

        # /tmp/tmpf5hotcqw/base_workspace/mgmt/dmi/model/yang/src/ned
        from_dataset = dataset_for_directory(
            os.path.join(base_workspace,
                         model_path_base,
                         model_subdir.lstrip('/')),
            modelname,
            addons
        )

        to_dataset = dataset_for_directory(
            os.path.join(workspace,
                         'binos',
                         model_path_current,
                         model_subdir.lstrip('/')),
            modelname,
            addons
        )

        dscmp = getdiff(from_dataset, to_dataset)

        for row in dscmp['data']:
            converted_new_xpath = re.sub('[^/]+.:', '', row[1])
            if row[0] == '+' or row[0] == '>':
                new_xpaths.add(converted_new_xpath)

            if row[0] == '-' or row[0] == '<':
                del_xpaths.add(converted_new_xpath)

    return new_xpaths, del_xpaths


def report_new_xpaths(reportname, new_xpaths, tdl):
    """Report newly added xpaths.

    Args:
        reportname (str): report name
        new_xpaths (set): a set of newly added xpaths
        tdl (list): a list of test case directories

    Return:
        missing_cli (boolean): True if no cli is defined.
                               Otherwise, return False
        missing_cli_verify (boolean): True if cli verification is not defined.
                                      Otherwise, return False.
        missing_oper_verify (boolean): True if operation verifiaction is not
                                       defined. Otherwise, return False.
    """
    with open(reportname, "a") as f:
        report('\nNew xpaths', f)
        report('==========', f)
        missing_cli = False
        missing_cli_verify = False
        missing_oper_verify = False
        for i in new_xpaths:
            tc_dict = get_tc_dict_from_xpath(i, tdl)
            if not tc_dict:
                missing_cli = True
                report(i, f)
                report('  WARNING: MISSING TESTCASE', f)
            else:
                if 'cli_verified' in tc_dict and not tc_dict['cli_verified']:
                    missing_cli_verify = True
                    report(i, f)
                    if tc_dict['test_name']:
                        report('  WARNING: MISSING CLI Verification ' +
                               str(tc_dict['test_name']), f)
                    else:
                        report('  WARNING: MISSING CLI Verification ' +
                               '  task(s): ' + str(tc_dict['task_name']),
                               f)
                else:
                    if ('oper_verified' in tc_dict and not
                            tc_dict['oper_verified']):
                        missing_oper_verify = True
                        report(i, f)
                        if tc_dict['test_name']:
                            report('  WARNING: MISSING Operational ' +
                                   'Verification ' +
                                   str(tc_dict['test_name']), f)
                        else:
                            report('  WARNING: MISSING Operational ' +
                                   '  task(s): ' +
                                   str(tc_dict['task_name']), f)
                    else:
                        report(i, f)

        if not new_xpaths:
            report('None', f)

        report('\n', f)

    return missing_cli, missing_cli_verify, missing_oper_verify


def report_deleted_xpaths(reportname, del_xpaths):
    """Report deleted xpaths.

    Args:
        reportname (str): report name
        del_xpaths (set): a set of deleted xpaths

    Return:
        None
    """
    with open(reportname, "a") as f:
        report('Removed xpaths', f)
        report('==============', f)
        if not del_xpaths:
            report('None', f)
        else:
            for i in del_xpaths:
                report(i, f)

        report('\n', f)


def report_missing_xpaths(reportname, new_xpaths, tc_xpaths, excluded_xpaths,
                          is_submod):
    """ Report missing xpaths.

    Args:
        reportname (str): report name
        new_xpaths (set): a set of newly added xpaths
        tc_xpaths (list): a set of test case xpaths
        is_submod (bool): True if it is a submodule
                          Otherwise, set to False

    Return:
        (bool): True if missing test case exists
                Otherwise, returns False
    """

    missing_tc = set()
    trim_missing_tc = set()
    if is_submod:
        # process xpaths from submodule
        for new_xpath in new_xpaths:
            if not any(new_xpath in tc_xpath for tc_xpath in tc_xpaths):
                missing_tc.add(new_xpath)
    else:
        missing_tc = new_xpaths - tc_xpaths
    trim_missing_tc = trim_missing_testset(missing_tc, tc_xpaths)

    if excluded_xpaths:
        return trim_missing_tc

    with open(reportname, "a") as f:
        report('Missing test cases', f)
        report('==================', f)
        if not missing_tc:
            report('None', f)
        else:
            if not trim_missing_tc:
                report('None', f)
            else:
                for i in trim_missing_tc:
                    report(i, f)

        report('\n', f)

    return trim_missing_tc


def report_broken_xpaths(reportname, del_xpaths, tc_xpaths):
    """Report broken xpaths.

    Args:
        reportname (str): report name
        del_xpaths (set): a set of deleted xpaths
        tc_xpaths (list): a set of test case xpaths

    Return:
        (boolean): True if broken test case exists.
                   Otherwise, returns False.
    """
    with open(reportname, "a") as f:
        trim_broken_tc = trim_broken_testset(del_xpaths, tc_xpaths)
        report('Broken test cases', f)
        report('==================', f)
        if not trim_broken_tc:
            report('None', f)
        else:
            for i in trim_broken_tc:
                report(i, f)

        report('\n', f)

    if (len(trim_broken_tc) > 0):
        return True

    return False


def report_obsolete_xpaths(reportname, obsolete_xpaths):
    """Report obsolete xpaths.

    Args:
        reportname (str): report name
        obsolete_xpaths (set): a set of obsolete xpaths

    Return:
        None
    """
    if not obsolete_xpaths:
        return
    with open(reportname, "a") as f:
        report('Below xpaths should mark obsolete in the model', f)
        report(46*'=', f)
        for i in obsolete_xpaths:
            report(i, f)

        report('\n', f)

    return


def report_invalid_testcases(reportname,
                             obsolete_xpaths,
                             tc_xpaths,
                             tdl,
                             excluded_xpaths):
    """Report invalid testcases.

    Args:
        reportname (str): report name
        obsolete_xpaths (set): a set of obsolete xpaths
        tc_xpaths (set): a set of test case xpaths
        tdl (list): a list of test case directories
        excluded_xpaths (set): excluded_xpaths

    Return:
        (set): invalid test cases which are part of the excluded xpaths
    """
    invalid_tc_no_exception = set()
    invalid_tc_with_exception = set()

    for xpath in excluded_xpaths:
        for tc_xpath in tc_xpaths:
            if tc_xpath.startswith(xpath):
                invalid_tc_with_exception.add(tc_xpath)

    invalid_tc_no_exception = tc_xpaths - invalid_tc_with_exception

    obsolete_dict = dict()
    cli_dict = dict()
    oper_dict = dict()

    for i in invalid_tc_no_exception:
        tc_dict = get_tc_dict_from_xpath(i, tdl)
        if not tc_dict:
            continue
        if i in obsolete_xpaths:
            obsolete_dict[i] = str(tc_dict['test_name'])
        else:
            if 'cli_verified' in tc_dict and not tc_dict['cli_verified']:
                if tc_dict['test_name']:
                    cli_dict[i] = str(tc_dict['test_name'])
                else:
                    cli_dict[i] = str(tc_dict['task_name'])

            if 'oper_verified' in tc_dict and not tc_dict['oper_verified']:
                if tc_dict['test_name']:
                    oper_dict[i] = str(tc_dict['test_name'])
                else:
                    oper_dict[i] = str(tc_dict['task_name'])

    with open(reportname, "a") as f:
        if obsolete_dict or cli_dict or oper_dict:
            report('Invalid/Incomplete test cases', f)
            report(30*'=' + '\n', f)

        msg = 'OBSOLETE test cases'
        print_invalid_testcases(obsolete_dict, msg, f)

        msg = 'MISSING CLI Verification'
        print_invalid_testcases(cli_dict, msg, f)

        msg = 'MISSING Operational Verification'
        print_invalid_testcases(oper_dict, msg, f)

    return invalid_tc_with_exception


def calculate_test_coverage(reportname,
                            total_xpaths,
                            missing_tc,
                            exception_tc,
                            exception_list,
                            invalid_testcase):
    """Calculate test coverage.

    Args:
        reportname (str): report name
        total_xpaths (set): all xpaths
        missing_tc (set): missing test cases
        exception_tc (set): missing test cases that are not part of the
                            excluded xpaths
        exception_list (list): excluded xpaths
        invalid_testcase (set): invalid testcases which are part of the
                                excluded xpaths

    Return:
        ---
    """
    with open(reportname, "a") as f:
        if total_xpaths:
            test_coverage = ((len(total_xpaths) -
                              len(missing_tc)) / len(total_xpaths))

            if exception_list:
                with_exception = ((len(total_xpaths) -
                                  len(exception_tc)) /
                                  len(total_xpaths))

                report('Test Coverage (no paths excluded): ' +
                       '{:.1%}\n'.format(test_coverage), f)
                report('Excluding xpaths', f)
                report(16*'=', f)
                for exception_xpath in exception_list:
                    report(exception_xpath, f)

                test_coverage = with_exception

                if invalid_testcase:
                    report('\nInvalid/Incomplete test cases ' +
                           'that are part of excluded paths ' +
                           '(please remove these tests)', f)
                    report(90*'=', f)
                    for invalid_tc in invalid_testcase:
                        report(invalid_tc, f)

                    report('\n', f)

            report('Test Coverage: {:.1%}'.format(test_coverage), f)

            report('\n', f)


def print_precommit_report(reportname, missing_tc,
                           missing_cli, broken_tc,
                           missing_cli_verify, missing_oper_verify):
    """Print precommit report.

    Args:
        reportname (str): report name
        missing_tc (boolean): True if missing test cases are found.
                                   Otherwise, this is set to False.
        missing_cli (boolean): True if no cli is found in test case.
                               Otherwise, this is set to False.
        broken_tc (boolean): True if broken test cases are found.
                                  Otherwise, this is set to False.
        missing_cli_verify (boolean): True if missing cli verification.
                                      Otherwise, this is set to False.
        missing_oper_verify (boolean): True if missing oper verfication.
                                       Otherwise, this is set to False

    Return:
        ---
    """
    with open(reportname, "a") as f:
        # Report PASS or FAIL
        if (missing_tc or missing_cli or broken_tc or
                missing_cli_verify or missing_oper_verify):
            report('PRECOMMIT FAILED', f)
            report('-----------------', f)
            if missing_tc or missing_cli:
                report('MISSING TESTCASES', f)
            if broken_tc:
                report('BROKEN TESTCASES', f)
            if missing_cli_verify:
                report('MISSING CLI VERIFICATION', f)
            if missing_oper_verify:
                report('MISSING OPER VERIFICATION', f)
            report('\n', f)
        else:
            report('PRECOMMIT SUCCESS\n', f)


def add_cdets_enclosure(reportname, bugid, label):
    """Add enclosure to cdets.

    Args:
        reportname (str): report name
        bugid (str): bug id
        label (str): branch name

    Return:
        ---
    """

    if bugid:
        logger.info('Adding ned precommit result to ' + bugid)
        logger.info('Please wait.......')
        timestamp = datetime.datetime.utcnow().strftime("%y%m%d-%H%M%S")
        enclosure_prefix = 'precommit-result-' + label + '-' + timestamp

        # write results to DDTS
        ret = run_cmd(['/usr/cisco/bin/addfile',
                       '-o',
                       bugid,
                       enclosure_prefix,
                       reportname])
        print('Done: ' + ret)


def save_log(full_report, logfile):
    """Save the log.

    Args:
       full_report (string): Path to the full log
       logfile (string): Path to copy the log file to

    """

    if full_report is None or logfile is None:
        return

    if not os.path.isfile(full_report):
        # Create an empty file if not exists
        open(full_report, 'a').close()

    if os.path.exists(os.path.dirname(logfile)):
        # Copy the file
        shutil.copyfile(full_report, logfile)


def turn_on_console_log(logfile):
    """Turn on console log.

    Args:
       logfile (string): Path to the logfile
    """
    global console_log

    if not logfile:
        console_log = True


def precommit_check(workspace=None,
                    label=None,
                    reportname=None,
                    bugid=None,
                    report=None,
                    logfile=None,
                    modelnames=None,
                    modelpath=None):
    """Precommit check entry point.
       This is called by model coverage script, precommit
       script and paw_wrapper script.

       Input parameters for model coverage script:
         workspace (mandatory)
         label (mandatory)
         bugid (optional)
         logfile (optional)

       Input parameters for precommit script:
         workspace (mandatory)
         label (mandatory)
         reportname (mandatory)
         report (mandatory)
         logfile (optional)
         modelnames (optional)
         modelpath (optional)

       paw_wrapper script also calls this function to perform model coverage.

    Args:
       workspace (string): Workspace
       label (string): Branch name
       reportname: (string): Report name
       bugid: (string): DDTS number
       report (boolean): True if generated the report for the model
                         Otherwise, it is set to False
       logfile (string): Path to copy the log file to
       modelnames (string): Path to file contains list of modified models
       modelpath (string): Path to generated models

    """
    interactive_mode = False
    if not workspace:
        ws = input('Full directory path to your workspace: ')
        workspace = ws
        interactive_mode = True
    if not label:
        lbl = input('Workspace label: ')
        label = lbl
    # Generate code coverage report
    if report:
        if not reportname:
            reportname = input('Enter model name: ')
        if not modelpath:
            modelpath = input('Model path: ')
    else:
        if interactive_mode and not bugid:
            bid = input('bugid: ')
            bugid = bid
            reportname = ''

    # Turn on console log if no log file is specified
    turn_on_console_log(logfile)

    excluded_xpath_filename = 'excluded_xpaths'
    if not modelpath:
        # Set model path
        modelpath = 'mgmt/dmi/model/yang/src'
    else:
        tdl_modelpath = TDLMODELPATH.lstrip('/')
        if tdl_modelpath not in modelpath:
            modelpath = 'mgmt/dmi/model/yang/src'
    model_test_path = 'binos/mgmt/dmi/model/tests'
    # Set up directories and paths
    precommit_tmpdir = tempfile.mkdtemp()
    # File to store for precommit result
    full_report = os.path.join(precommit_tmpdir, 'full_report.txt')
    # Create top directory for zip files
    zipfile_path = os.path.join(precommit_tmpdir, 'zip_tmpdir')
    os.mkdir(zipfile_path)
    modelist = list()

    if not reportname:
        chgsetfile = os.path.join(precommit_tmpdir, 'changeset.txt')
        # directory holding base models to compare against
        base_workspace = os.path.join(precommit_tmpdir, 'base_workspace')
        os.mkdir(base_workspace)

    try:
        is_submod = False
        if not reportname:
            modelist = create_baseline_ws(chgsetfile, workspace,
                                          modelpath, label, base_workspace,
                                          precommit_tmpdir, modelnames)
            if not modelist:
                if console_log:
                    logger.warning("Empty model set")
                else:
                    save_log(full_report, logfile)
                return True

            new_xpaths, del_xpaths = get_changed_xpaths(workspace,
                                                        modelpath,
                                                        base_workspace,
                                                        modelist)
        else:
            fset = []
            fset.append(reportname)
            new_xpaths, obsolete_xpaths, is_submod = get_all_xpaths(workspace,
                                                                    modelpath,
                                                                    fset)
        if not modelist:
            modelist.append((modelpath, fset[0]))

        tdl, error = get_test_data(os.path.join(workspace, model_test_path),
                                   modelist,
                                   zipfile_path)
        if error:
            # Unable to retrieve test data
            return False

        tc_xpaths = get_test_xpaths(tdl)

        if not reportname:
            no_cli, no_cliver, no_operver = report_new_xpaths(full_report,
                                                              new_xpaths,
                                                              tdl)

            report_deleted_xpaths(full_report, del_xpaths)

        excluded_xpaths = get_excluded_xpaths(workspace,
                                              model_test_path,
                                              reportname,
                                              excluded_xpath_filename,
                                              modelpath)

        trim_missing_tc = report_missing_xpaths(full_report,
                                                new_xpaths,
                                                tc_xpaths,
                                                excluded_xpaths,
                                                is_submod)

        # Filter out all xpaths in the exclusion list
        trim_exception_tc = report_excluded_xpaths(full_report,
                                                   trim_missing_tc,
                                                   reportname,
                                                   excluded_xpaths)

        invalid_testcase = set()
        if not reportname:
            trim_broken_tc = report_broken_xpaths(full_report,
                                                  del_xpaths,
                                                  tc_xpaths)
        else:
            report_obsolete_xpaths(full_report,
                                   obsolete_xpaths)
            invalid_testcase = report_invalid_testcases(full_report,
                                                        obsolete_xpaths,
                                                        tc_xpaths,
                                                        tdl,
                                                        excluded_xpaths)

        calculate_test_coverage(full_report,
                                new_xpaths,
                                trim_missing_tc,
                                trim_exception_tc,
                                excluded_xpaths,
                                invalid_testcase)

        if not reportname:
            print_precommit_report(full_report,
                                   trim_missing_tc,
                                   no_cli,
                                   trim_broken_tc,
                                   no_cliver,
                                   no_operver)

            add_cdets_enclosure(full_report, bugid, label)

    finally:
        save_log(full_report, logfile)
        shutil.rmtree(precommit_tmpdir)

    return True


def precommit_init():
    # Get Command Parameters
    parse = setup_args()
    args = parse.parse_args()

    return args


def main():
    """Entry Point for console script precommit.

       This is called by model coverage and precommit script.
       Model coverage script is for reporting coverage
       for a YANG model. Precommit script is for reporting
       coverage based off a model changeset.
    """
    # Get Command Parameters
    args = precommit_init()

    precommit_check(args.workspace, args.label, args.reportname,
                    args.bugid, args.report, args.logfile, None)


if __name__ == '__main__':
    # Get Command Parameters
    main()
