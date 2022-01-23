import builtins
import sys
import os
import io
import boto3
from io import StringIO
from multiprocessing.connection import wait
from multiprocessing import Process, Pipe, Queue
from queue import Empty
import pandas as pd
from pandas import DataFrame
from tqdm import tqdm
import ast
import subprocess
import tempfile
import pickle
from infinstor import infin_ast
from datetime import datetime, timedelta, timezone
import time
import mlflow
from mlflow import start_run, end_run, log_metric, log_param, log_artifacts, set_experiment, log_artifact, set_tag
from mlflow.tracking.client import MlflowClient
from mlflow.entities import ViewType
from os.path import sep
import mlflow.projects
from contextlib import contextmanager,redirect_stderr,redirect_stdout
import pprint
import types
import shutil
from infinstor_mlflow_plugin.tokenfile import read_token_file
from os.path import expanduser
from requests.exceptions import HTTPError
import requests
import inspect
import glob
import json
from urllib.parse import urlparse
import string
import random
import traceback
import hashlib
import logging
import zipfile
import base64
from dataclasses import dataclass
from typing import Dict, List
import urllib.parse
from infinstor import infin_boto3
from infinstor import bootstrap

# import astpretty

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s")

TRANSFORM_RAW_PD = "infin_transform_raw_to_pd"
TRANSFORM_RAW_DS = "infin_transform_raw_to_ds"
TRANSFORM_CSV_PD = "infin_transform_csv_to_pd"
TRANSFORM_CSV_DS = "infin_transform_csv_to_ds"
TRANSFORM_ONE_OBJ = "infin_transform_one_object"
TRANSFORM_DIR_BY_DIR = "infin_transform_dir_by_dir"
TRANSFORM_ALL_OBJECTS = "infin_transform_all_objects"
TRANSFORM_MULTI_INPUTS = "infin_transform_all_objects_multi_inputs"

MLFLOW_TRACKING_URI = 'MLFLOW_TRACKING_URI'

def read_infinstor_config_json_key(jsonkey:str):
    keyval = None
    config_json_path = os.path.join(os.path.expanduser('~'),'.infinstor','config.json')
    if os.path.exists(config_json_path): 
        with open(config_json_path, 'r') as fh:
            config_json = json.load(fh)
            if (config_json.get('clientlib_verbose')): keyval = config_json.get(jsonkey)
    return keyval

def set_verbose() -> bool:
    return read_infinstor_config_json_key('clientlib_verbose')

verbose = False
if set_verbose(): verbose = set_verbose()

enable_infin_ast = False # right now infin_ast does not pick up classes defined in the cell

def log_file(filepath:str):
    with open(filepath, 'r') as fh:
        logger.info("Contents of file=%s: \n%s", filepath, fh.read())
        

def num_threads():
    return 8

def list_dir_recursively(root, array_of_files):
    for file in os.listdir(root):
        if (os.path.isfile(os.path.join(root, file))):
            array_of_files.append(os.path.join(root, file))
        else:
            list_dir_recursively(os.path.join(root, file), array_of_files)

class FuncLister(ast.NodeVisitor):
    def __init__(self, glbs):
        self.glbs = glbs;

    def visit_FunctionDef(self, node):
        self.glbs[node.name] = "'" + node.name + "'";
        # print('>> FunctionDef: ' + node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.glbs[node.name] = "'" + node.name + "'";
        # print('>> ClassDef: ' + node.name)
        self.generic_visit(node)


def get_label_info(label):
    tokfile = expanduser('~') + sep + '.infinstor' + sep + '/token'
    token, refresh_token, token_time, client_id, service, token_type, id_token = read_token_file(tokfile)

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': token
        }
    url = 'https://' + builtins.mlflowserver + '/api/2.0/mlflow/label/get?labelname=' + label
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        raise
    except Exception as err:
        print(f'Other error occurred: {err}')
        raise
    label = response.json()['label']
    return label['timespec']['S'], label['bucketname']['S'], label['prefix']['S'], service

def get_xform_info(xformname):
    if (xformname.find(':') != -1):
        return get_xform_info_git(xformname)
    else:
        return get_xform_info_ddb(xformname)

def get_xform_info_git(xformname):
    dst_dir = tempfile.mkdtemp()
    import git
    git.Git(dst_dir).clone(xformname, '.')
    with open(os.path.join(dst_dir, 'xformcode.py'), 'r') as xformcodefile:
        xformcode = xformcodefile.read()
    try:
        with open(os.path.join(dst_dir, 'Dockerfile'), 'r') as dockerfile:
            dockerfile_str = dockerfile.read()
    except:
        print('get_xform_info_git: No dockerfile. code=' + xformcode, flush=True)
        # TODO: implement xform_local_files_zip for git repositories
        return xformcode, None, None
    else:
        print('get_xform_info_git: dockerfile=' + dockerfile_str + ', code=' + xformcode, flush=True)
        # TODO: implement xform_local_files_zip for git repositories
        return xformcode, dockerfile_str, None

def get_xform_info_ddb(xformname):
    tokfile = expanduser('~') + sep + '.infinstor' + sep + '/token'
    token, refresh_token, token_time, client_id, service, token_type, id_token = read_token_file(tokfile)

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': token
        }
    url = 'https://' + builtins.mlflowserver + '/api/2.0/mlflow/xform/get?transform_name=' + xformname
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}', exc_info=sys.exc_info())
        raise
    except Exception as err:
        logger.error(f'Other error occurred: {err}', exc_info=sys.exc_info())
        raise
    xform = response.json()['transform']
        
    # get xform_local_files_zip if available
    zf = None
    xform_local_files_zip = xform.get('xform_local_files_zip')
    if xform_local_files_zip:   # if we have xform_local_files_zip
        info("xform_local_files_zip_base64=%s" % xform_local_files_zip)
        # encode received str to bytes/ascii; base64 decode this to get the original bytestream
        bytesio = io.BytesIO( base64.b64decode( xform_local_files_zip.encode("ascii") ) )
        zf = zipfile.ZipFile(bytesio, "r", compression=zipfile.ZIP_LZMA)

    if ('dockerfile' in xform and xform['dockerfile'] != None):
        return xform['xformcode']['S'], xform['dockerfile']['S'],zf
    else:
        return xform['xformcode']['S'], None, zf

def download_one_dir(label):
    timespec, bucketname, prefix, service = get_label_info(label)
    client = boto3.client('s3', infinstor_time_spec=timespec)

    dict_of_arrays_of_files = dict()
    list_dir_by_dir(client, bucketname, prefix, True, dict_of_arrays_of_files)
    tmpdir_root = tempfile.mkdtemp()
    for parentdir in dict_of_arrays_of_files:
        array_of_files = dict_of_arrays_of_files[parentdir]
        if (verbose == True):
            info('Number Of Objects in parentdir ' + parentdir + ': ' +str(len(array_of_files)))
        local_tmpdir = tmpdir_root + sep + parentdir
        if (verbose == True):
            info('Local temp dir is ' + local_tmpdir)
        os.makedirs(local_tmpdir, mode=0o755, exist_ok=True)
        objects = download_objects_inner(client, bucketname, parentdir, array_of_files,\
                    False, None, local_tmpdir)
    return tmpdir_root

# fills out array_of_files with all the files in this prefix
def list_one_dir(timespec, bucket, prefix_in, recurse, array_of_files):
    client = boto3.client('s3', infinstor_time_spec=timespec)
    paginator = client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix_in, Delimiter="/")
    for page in page_iterator:
        # print('Files:')
        contents = page.get('Contents')
        if (contents != None):
            # print('   ' + str(contents))
            count = 0;
            for one_content in contents:
                object_name = one_content['Key']
                full_object_name = object_name
                # print(full_object_name)
                array_of_files.append(full_object_name)
                count += 1
            if (count > 0):
                print(str(count) + " files in " + prefix_in)
        # print('Directories:')
        common_prefixes = page.get('CommonPrefixes')
        if (common_prefixes != None):
            for prefix in common_prefixes:
                this_prefix = str(prefix['Prefix'])
                # print('   ' + this_prefix)
                if (bool(recurse) and this_prefix != None and not_dot_infinstor(this_prefix)):
                    list_one_dir(timespec, bucket, this_prefix, recurse, array_of_files)

def get_parent_dir_and_fn(full_object_key):
    """returns parentdir (with no leading or trailing /) and filename"""
    components = full_object_key.split(sep)
    parentdir = ''
    for comp in components[0:len(components) -1]:
        if (parentdir == ''):
            parentdir = comp
        else:
            parentdir = parentdir + sep + comp
    return parentdir, components[len(components) - 1]

def not_dot_infinstor(prefix):
    components = prefix.rstrip('/').split(sep)
    if (len(components) > 1 and components[len(components) - 1].startswith('.infinstor')):
        return False
    else:
        return True

def list_dir_by_dir(client, bucket:str, prefix_in:str, recurse:bool, dict_dirname_to_arrays_of_files:dict):
    """ fills out dict_dirname_to_arrays_of_files with parentdir -> array_of_files_in_parent_dir.

    All S3 objects with keys that map to <bucket>/<prefix_in> or below are processed.

    client is the s3 client
    """
    if (verbose == True):
        info('list_dir_by_dir: Entered. bucket=' + bucket + ', prefix_in=' + prefix_in)
    paginator = client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix_in, Delimiter="/")
    for page in page_iterator:

        if (verbose == True):
            info('list_dir_by_dir: Files:')
        contents = page.get('Contents')
        if (contents != None):
            if (verbose == True):
                info('list_dir_by_dir:    ' + str(contents))
            count = 0;
            for one_content in contents:
                object_name = one_content['Key']     # 'Key' is the s3 key for the s3 object
                full_object_name = object_name
                if (verbose == True):
                    info('list_dir_by_dir: full_object_name=' + full_object_name)
                parent_dir, filename = get_parent_dir_and_fn(object_name)
                if (parent_dir in dict_dirname_to_arrays_of_files):
                    files_in_this_dir = dict_dirname_to_arrays_of_files[parent_dir]
                else:
                    files_in_this_dir = []
                    dict_dirname_to_arrays_of_files[parent_dir] = files_in_this_dir
                files_in_this_dir.append(filename)
                count += 1
            if (count > 0):
                print(str(count) + " files in " + prefix_in)

        if (verbose == True):
            info('list_dir_by_dir: Directories:')
        common_prefixes = page.get('CommonPrefixes')
        if (common_prefixes != None):
            for prefix in common_prefixes:
                this_prefix = str(prefix['Prefix'])        # get the 'Prefix' of the s3 object??
                if (verbose == True):
                    info('list_dir_by_dir:    ' + this_prefix)
                if (bool(recurse) and this_prefix != None and not_dot_infinstor(this_prefix)):
                    list_dir_by_dir(client, bucket, this_prefix, recurse, dict_dirname_to_arrays_of_files)

def info(msg,*args):
    now = datetime.now()
    #print(__name__ + '[' + str(os.getpid()) + '][' + now.strftime('%Y-%m-%d %H:%M:%S') + ']' + msg)
    logger.info(msg,*args)    # all of the above fields such as process id, module name and others, have been set automatically using logging.basicConfig() further above

def log_artifacts_recursively(temp_output_dir):
    for filename in glob.iglob(temp_output_dir + '**/**', recursive=True):
        if (os.path.isfile(filename)):
            bn = os.path.basename(filename)
            bn_minus_tmp = filename[len(temp_output_dir):].lstrip('/')
            key = 'infinstor/' + os.path.dirname(bn_minus_tmp).lstrip('/')
            log_artifact(filename, key)

class download_task:
    def __init__(self, command, bucketname, parentdir, prefix_trunc, filename):
        self.command = command
        self.bucketname = bucketname
        self.parentdir = parentdir
        self.prefix_trunc = prefix_trunc
        self.filename = filename

def s3downloader(**kwargs):
    """
    num_threads() processes are forked. Each child process executes this function

    This function reads operations(op) from the parent process through a Pipe.

    The only ops we support today are download and quit
    
    For download, we have three distnct modes we operate in:
    - Mode 1 is download into memory and write the bytes to the parent process through the Pipe
    - Mode 2 is for downloading to a temporary dir. Returns status to parent process through Pipe
    - Mode 3 is where we download one object and execute the function provided by the user, the xform_one_object function written by the Data Scientist
    
    Here is how we recognize the different modes this function operates in:
    - Mode 1. tmpfile_dir=None, glb=None: Read object into memory and return bytes to pipe
    - Mode 2. tmpfile_dir is present and glb=None: Read object into tmpfile_dir and return status
    - Mode 3. tmpfile_dir is present and glb is present: Read object into tmpfile_dir and call
        the function infin_transform_one_object using glb as globals. Send status back
        Note: If glb is present, tmpfile_dir must be present. We always call
        infin_transform_one_object by passing in a temporary file
    """
    download_task_q = kwargs.pop('command_q')
    write_pipe = kwargs.pop('write_pipe')
    client = kwargs.pop('client')
    glb = kwargs.pop('globals')
    tmpfile_dir = kwargs.pop('tmpfile_dir')

    if (glb != None):
        namespaced_infin_transform_one_object =\
                namespaced_function(glb['infin_transform_one_object'], glb, None, True)

    while (True):
        try:
            if (verbose == True):
                start = datetime.now()
            download_task = download_task_q.get()
            if (verbose == True):
                end = datetime.now()
                td = end - start
                ms = (td.days * 86400000) + (td.seconds * 1000) + (td.microseconds / 1000)
                if (ms > 10):
                    info('s3downloader: q.get took ' + str(ms) + ' ms')
        except Empty as e:
            if (verbose == True):
                info('s3downloader: No more entries in download_task_q. Exiting..')
            write_pipe.close()
            break
        op = download_task.command
        if (op == 'download'):
            bucketname = download_task.bucketname
            parentdir = download_task.parentdir
            prefix_trunc = download_task.prefix_trunc
            filename = download_task.filename
            if (verbose == True):
                info('s3downloader: Received download command. bucket='
                        + str(bucketname) + ', parentdir=' + str(parentdir)
                        + ', prefix_trunc=' + str(prefix_trunc)
                        + ', filename=' + str(filename))
            if (parentdir == ''):
                full_object_key = filename
            else:
                full_object_key = parentdir + sep + filename
            if (verbose == True):
                info('s3downloader: starting download of ' + full_object_key\
                        + ' from ' + bucketname)
                start = datetime.now()

            if (tmpfile_dir == None):
                obj = client.get_object(Bucket=bucketname, Key=full_object_key)
                content_length = obj['ContentLength']
                strbody = obj['Body']
                dtm = obj['LastModified']
                key = dtm.strftime('%Y-%m-%d %H:%M:%S') + ' ' + bucketname + '/' + full_object_key
            else:
                tmpf_name = tmpfile_dir + sep + filename
                if (verbose == True):
                    info('s3downloader: Downloading s3://' + str(bucketname) + '/'
                            + str(full_object_key) + ' to ' + str(tmpf_name))
                try:
                    client.download_file(bucketname, full_object_key, tmpf_name)
                except Exception as e:
                    info('s3downloader: Caught ' + str(e) + ' downloading s3://'
                            + str(bucketname) + '/' + str(full_object_key)
                            + ' to ' + str(tmpf_name) + ", traceback = \n" + traceback.format_exc())

                content_length = os.stat(tmpf_name).st_size
                key = bucketname + '/' + full_object_key

            if (glb == None):
                while (not write_pipe.writable):
                    info('s3downloader: WARNING write pipe not writable')
                    time.sleep(2)
                try:
                    write_pipe.send(key)
                    write_pipe.send(filename)
                    if (tmpfile_dir == None):
                        write_pipe.send(content_length)
                        for chunk in strbody.iter_chunks(8192):
                            write_pipe.send(chunk)
                    else:
                        status_as_byte_array = bytes('Success', 'utf-8')
                        write_pipe.send(len(status_as_byte_array))
                        write_pipe.send(status_as_byte_array)
                except Exception as e:
                    status_str = str(e)
                    info("Error sending bytes back: " + status_str + ", traceback = \n" + traceback.format_exc())
            else:
                try:
                    temp_output_dir = tempfile.mkdtemp()
                    #namespaced_infin_transform_one_object(bucketname, parentdir,\
                    #        filename, tmpf_name, **kwargs)
                    namespaced_infin_transform_one_object(tmpf_name, temp_output_dir,\
                            parentdir[len(prefix_trunc):], **kwargs)
                except Exception as e1:
                    status_str = str(e1)
                    info("Error executing infin_transform_one_object_tmpfile: " + status_str + ", traceback = \n" + traceback.format_exc())
                else:
                    log_artifacts_recursively(temp_output_dir)
                    status_str = 'Success'
                finally:
                    shutil.rmtree(temp_output_dir)
                os.remove(tmpf_name)
                write_pipe.send(key)
                write_pipe.send(filename)
                status_as_byte_array = bytes(status_str, 'utf-8')
                write_pipe.send(len(status_as_byte_array))
                write_pipe.send(status_as_byte_array)
        elif (op == 'quit'):
            if (verbose == True):
                info('s3downloader: Received quit command')
            write_pipe.close()
            break
        else:
            info('s3downloader: Unknown command ' + op)
            write_pipe.close()
            break

def namespaced_function(function, global_dict, defaults=None, preserve_context=False):
    '''
    Redefine (clone) a function under a different globals() namespace scope

        preserve_context:
            Allow keeping the context taken from orignal namespace,
            and extend it with globals() taken from
            new targetted namespace.
    '''
    if defaults is None:
        defaults = function.__defaults__

    if preserve_context:
        _global_dict = function.__globals__.copy()
        _global_dict.update(global_dict)
        global_dict = _global_dict
    new_namespaced_function = types.FunctionType(
        function.__code__,
        global_dict,
        name=function.__name__,
        argdefs=defaults,
        closure=function.__closure__
    )
    new_namespaced_function.__dict__.update(function.__dict__)
    return new_namespaced_function

def load_one_csv_from_bytearray(bts):
    s = str(bts, 'utf-8')
    sio = StringIO(s)
    return pd.read_csv(sio)

def download_objects_inner(client, bucketname, parentdir, prefix_trunc, array_of_files, is_csv,
        glb, tmpfile_dir, **kwargs):
    """
    from s3downloader() documentation: downloads the objects from bucketname://parentdir.  Downloaded s3 objects can be stored in tmpfile_dir or memory (dataframe) or can be provided as an input to user provided transform.

    returns a pandas DataFrame with index 'YY-MM-dd HH:MM:SS bucketname/filename'
    and one column named RawBytes that contains the raw bytes from the object
    """
    command_q = Queue(len(array_of_files) + num_threads())
    for onefile in array_of_files:
        command_q.put(download_task('download', bucketname, parentdir, prefix_trunc, onefile))
    for i in range(num_threads()):
        command_q.put(download_task('quit', '', '', '', ''))

    pipe_from_child = []
    processes = []
    for i in range(num_threads()):
        r1, w1 = Pipe(False)
        pipe_from_child.append(r1)
        newkwargs = dict(kwargs)
        newkwargs['command_q'] = command_q
        newkwargs['write_pipe'] = w1
        newkwargs['client'] = client
        newkwargs['globals'] = glb
        newkwargs['tmpfile_dir'] = tmpfile_dir
        p = Process(target=s3downloader, args=(), kwargs=newkwargs)
        p.start()
        processes.append(p)
        w1.close()

    filebytes = []
    filenames = []
    filekeys = []
    step = 0
    with tqdm(total=len(array_of_files)) as pbar:
        files_read = 0
        while pipe_from_child:
            ready = wait(pipe_from_child, timeout=10)
            for read_pipe in ready:
                key = None
                fn = None
                length = None
                this_file_bytes = None
                try:
                    read_pipe.poll(None)
                    key = read_pipe.recv()
                    read_pipe.poll(None)
                    fn = read_pipe.recv()
                    read_pipe.poll(None)
                    length = read_pipe.recv()
                    this_file_bytes = bytearray()
                    if length:
                        bytes_read = 0
                        while (read_pipe.poll(None)):
                            bts = read_pipe.recv()
                            bytes_read = bytes_read + len(bts)
                            this_file_bytes.extend(bts)
                            if (bytes_read == length):
                                break
                except EOFError:
                    pipe_from_child.remove(read_pipe)
                if (key and fn):
                    filekeys.append(key)
                    filenames.append(fn)
                    filebytes.append(this_file_bytes)
                    pbar.update(1)
                    files_read += 1
                    if ((files_read % 10) == 0):
                        log_metric("downloaded", files_read, step=step)
                        step += 1

    for i in range(num_threads()):
        processes[i].join()
    if (is_csv == True):
        rv = pd.concat(map(load_one_csv_from_bytearray, filebytes))
    else:
        data = {'FileName': filenames, 'RawBytes': filebytes}
        rv = DataFrame(data, index=filekeys)
    log_metric("downloaded", files_read, step=step)
    return rv

def actually_run_transformation(client, is_pandas_df, bucketname,\
        prefix_in, prefix_trunc, is_csv, transformation_string, **kwargs):
    array_of_files = []
    list_one_dir(client, bucketname, prefix_in, True, array_of_files)
    print('actually_run_transformation: total number Of objects: ' + str(len(array_of_files)))
    objects = download_objects_inner(client, bucketname, '', prefix_trunc, array_of_files, is_csv,\
                None, None, **kwargs)
    if (enable_infin_ast == True):
        transformAst = infin_ast.extract_transform(TRANSFORM_RAW_PD, src_str=transformation_string)
        # XXX we should use the following statement to figure out what
        # kind of an object the infin_transform function returns
        # infin_ast.add_type_statements(transformAst)
        transformSrc = infin_ast.get_source(transformAst)
    else:
        transformSrc = transformation_string

    if (verbose == True):
        info('transformSrc=' + transformSrc);

    if (is_csv):
        if (is_pandas_df):
            xn = TRANSFORM_CSV_PD
        else:
            xn = TRANSFORM_CSV_DS
    else:
        if (is_pandas_df):
            xn = TRANSFORM_RAW_PD
        else:
            xn = TRANSFORM_RAW_DS

    tree = ast.parse(transformSrc)

    compiledcode2 = compile(tree, "<string>", "exec")

    # Add all functions in xformcode to the globals dictionary
    glb = {}
    fl = FuncLister(glb)
    fl.visit(tree)
    try:
        exec(compiledcode2, glb)
    except Exception as e:
        status_str = str(e)
        info("Execution of global statics failed. status_str=" + status_str + ", traceback = \n" + traceback.format_exc())
        raise
    else:
        status_str = 'Success'
    # print('Globals=')
    # pprint.pprint(glb)
    # info("Execution of global statics complete. status_str=" + status_str)

    namespaced_infin_transform_fnx = namespaced_function(glb[xn], glb, None, True)
    try:
        namespaced_infin_transform_fnx(objects, **kwargs)
    except Exception as e:
        status_str = str(e)
        info("Error executing " + xn + ", status=" + status_str + ", traceback = \n" + traceback.format_exc())
    else:
        status_str = 'Success'

    if (is_pandas_df == True):
        fd, tmpf_name = tempfile.mkstemp(suffix='.pkl')
        os.close(fd)
        objects.to_pickle(tmpf_name)
        log_artifact(tmpf_name, 'infinstor/pd.DataFrame')
        os.remove(tmpf_name)
    else:
        print('saving tf.data.Dataset unimplemented')
    return objects

class RunTransformContext:
    """used to store details of the transform that is currently being run"""
    def __init__(self, xform_input_dirs:list, xform_output_dir:str, **xform_kwargs):
        self.xform_input_dirs = xform_input_dirs
        self.xform_output_dir = xform_output_dir
        self.xform_kwargs = xform_kwargs

# declare a module global.  Assumption is that there is a single thread of execution accessing this module in a python process (which is true since python is not multi-threaded.)
global g_run_xform_ctx
g_run_xform_ctx = None

def setup_infinstor_inject_context_globals(glb:dict):
    """
    populates the argument 'glb' with the needed globals, so that code in wrapper() below can execute.  If wrapper() below is modified, this function also needs to be modified.
    """
    # set the global only if it isn't already defined; use glb.get() to avoid KeyError
    if not glb.get('os'): glb['os'] = os
    if not glb.get('logging'): glb['logging'] = logging

# TODO: add function parameter type hint.  'function' as hint did not work.
from functools import wraps
def infinstor_inject_context(func):
    """function decorator. apply the decorator to functions with signature functionName(input_dirs:list, output_dir:str, **kwargs:dict)

    when running in the infinstor platform, decorator will inject the correct values for the arguments input_dirs, output_dir and kwargs during the invocation of functionName()

    when not running in the infinstor platform, the decorator is a noop: it will not inject any values for the arguments and instead will just be a pass through.
    """
    funcname = "infinstor_inject_context()"

    @wraps(func)
    def wrapper(*args, **kwargs):
        # note that the wrapper is executed in the execution context of the exec()ed transfor.  So import these as they may not exist in this execution context.  'import' is idempotent, so no harm if imported more than once.
        import os
        import logging

        # if not running in infinstor platform
        if not g_run_xform_ctx:
            # Use 'logging' (logging module level methods) since 'logger' most likely will not be defined during the exec() of 'transform' python script.
            logging.info(f'{funcname}: Not running in infinstor platform: pass through. No overrides of function {func.__name__}()''s arguments done')
            return func(*args, **kwargs)
        
        # call the method with input_dirs, output_dir and kwargs; Use 'logging' (logging module level methods) since 'logger' most likely will not be defined during the exec() of 'transform' python script.
        logging.info(f'{funcname}: injecting function arguments: invoking {func.__name__}(input_dirs={g_run_xform_ctx.xform_input_dirs}, output_dir={g_run_xform_ctx.xform_output_dir}, kwargs={g_run_xform_ctx.xform_kwargs})')
        return func(g_run_xform_ctx.xform_input_dirs, g_run_xform_ctx.xform_output_dir, **g_run_xform_ctx.xform_kwargs)

    return wrapper

def run_dag_script(transformation_string:str, run_id, **kwargs:dict):
    transformSrc = transformation_string
    if (verbose == True):
        info('run_dag_script: transformSrc=' + transformSrc);

    if (len(kwargs.items()) > 0):
        tr_src = 'import sys\n'
        lis = "['infin_transform'"
        for key, value in kwargs.items():
            lis = lis + ", '--" + key + "=" + value + "'"
        tr_src = tr_src + 'sys.argv = ' + lis + "]\n" + transformSrc
    else:
        tr_src = transformSrc

    tree = ast.parse(tr_src)

    compiledcode2 = compile(tree, "<string>", "exec")

    try:
        mlflow_run_prefix = "import mlflow \n" + "mlflow.start_run(run_id='{0}')".format(run_id) + "\n"
        srcstr = mlflow_run_prefix + tr_src
        exec_file = "transform_exec.py"
        with open("transform_exec.py", "w") as fd:
            fd.write(srcstr)
        subprocess.run(["python", exec_file], stdout=sys.stdout, stderr=subprocess.STDOUT)
    except Exception as e:
        status_str = str(e)
        info("Execution of transform failed. status_str=" + status_str + ", traceback = \n" + traceback.format_exc())
        raise
    else:
        status_str = 'Success'


def run_script(transformation_string:str, zf:zipfile.ZipFile, run_id, **kwargs:dict):
    transformSrc = transformation_string
    if (verbose == True):
        info('run_script: transformSrc=' + transformSrc);

    if (len(kwargs.items()) > 0):
        tr_src = 'import sys\n'
        lis = "['infin_transform'"
        for key, value in kwargs.items():
            lis = lis + ", '--" + key + "=" + value + "'"
        tr_src = tr_src + 'sys.argv = ' + lis + "]\n" + transformSrc
    else:
        tr_src = transformSrc

    # unzip the local files captured with the transform
    if zf: extract_zip_file(zf)

    try:
        mlflow_run_prefix = "import mlflow \n" + "mlflow.start_run(run_id='{0}')".format(run_id) + "\n"
        srcstr = mlflow_run_prefix + tr_src
        exec_file = "transform_exec.py"
        with open("transform_exec.py", "w") as fd:
            fd.write(srcstr)
        proc = subprocess.Popen(["python", exec_file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in proc.stdout:
            print(line.rstrip().decode('utf-8'))

    except Exception as e:
        status_str = str(e)
        info("Execution of transform failed. status_str=" + status_str + ", traceback = \n" + traceback.format_exc())
        raise

def extract_zip_file(zf:zipfile.ZipFile):
    """
    extract the specified zip file into the current directory.
    """
    # if function called with an invalid argument
    if not zf:
        # print the stack trace of the caller.
        logger.error( ''.join(traceback.format_stack()) )
        return
        
    # unzip the zip archive with local files
    for zipinfo in zf.infolist():
        logger.info("file in zipfile: zipinfo=%s" % zipinfo) # + zf.read(zipinfo).decode('ascii'))
        # if file exists
        if os.path.exists(zipinfo.filename):
            logger.info(f"Not extracting file {zipinfo.filename} since it already exists")
        else:
            logger.info(f"Extracting file {zipinfo.filename} to {os.getcwd()}")
            zf.extract(zipinfo)
            
def exec_with_infinstor_inject_context(temp_input_dir_roots:list, temp_output_dir:str, compiledcode2):
    glb = {}
    try:
        #setup the needed data for the decorator '@infinstor_inject_context' so that it can inject the right values
        global g_run_xform_ctx 
        # g_run_xform_ctx set to non None signals that transform code is running in infinstor platform; 
        # g_run_xform_ctx is also used by infinstor_inject_context(), using data stored in this instance, to inject function argument overrides
        g_run_xform_ctx = RunTransformContext(temp_input_dir_roots,temp_output_dir)
        # below global is needed by infinstor_inject_context() decorator
        glb['g_run_xform_ctx'] = g_run_xform_ctx

        exec(compiledcode2, glb)
    except Exception as e:
        status_str = str(e)
        info("Execution of transform failed. status_str=" + status_str + ", traceback = \n" + traceback.format_exc())
        raise
    else:
        status_str = 'Success'
    finally:
        # g_run_xform_ctx set to non None signals that transform code is running in infinstor platform; 
        g_run_xform_ctx = None  

def new_dict_with_just_one(dict_in):
    one_dir = list(dict_in.keys())[0]
    newdict = dict()
    newdict[one_dir] = dict_in[one_dir]
    return newdict

def read_and_xform_one_object(client, bucketname,\
        prefix_in, prefix_trunc, transform_string, zf:zipfile.ZipFile, **kwargs):
    if (verbose == True):
        info('read_and_xform_one_object: Entered. bucketname=' + str(bucketname)\
            + ', prefix=' + str(prefix_in) + ', prefix_trunc=' + str(prefix_trunc))
    if (enable_infin_ast == True):
        transformAst = infin_ast.extract_transform(TRANSFORM_ONE_OBJ, src_str=transform_string)
        transformSrc = infin_ast.get_source(transformAst)
    else:
        transformSrc = transform_string
    tree = ast.parse(transformSrc)
    # astpretty.pprint(tree)
    compiledcode1 = compile(tree, "<string>", "exec")

    dict_of_arrays_of_files = dict()
    list_dir_by_dir(client, bucketname, prefix_in, True, dict_of_arrays_of_files)
    if (verbose == True):
        info('read_and_xform_one_object: num entries in dict_of_arrays_of_files='\
            + str(len(dict_of_arrays_of_files)))

    # unzip the local files captured with the transform
    if zf: extract_zip_file(zf)

    objects = None
    for parentdir in dict_of_arrays_of_files:
        array_of_files = dict_of_arrays_of_files[parentdir]
        info('Number Of Objects in parentdir ' + parentdir + ' = ' + str(len(array_of_files)))
        # Add all functions in xformcode to the globals dictionary
        glb = {}
        fl = FuncLister(glb)
        fl.visit(tree)
        try:
            exec(compiledcode1, glb)
        except Exception as e:
            status_str = str(e)
            info("Execution of global statics failed for " + parentdir\
                    + ". status_str=" + status_str + ", traceback = \n" + traceback.format_exc())
            raise
        else:
            status_str = 'Success'
        # print('Globals=')
        # pprint.pprint(glb)
        info("Execution of global statics for parentdir " + parentdir\
                + " complete. status_str=" + status_str)
        tdir = tempfile.mkdtemp()
        objects = download_objects_inner(client, bucketname, parentdir, prefix_trunc, array_of_files,
                        False, glb, tdir, **kwargs)
        shutil.rmtree(tdir)
    return objects

def read_and_xform_dir_by_dir(client, bucketname, prefix_in, prefix_trunc, transform_string, zf:zipfile.ZipFile, **kwargs):
    if (enable_infin_ast == True):
        transformAst = infin_ast.extract_transform(TRANSFORM_DIR_BY_DIR, src_str=transform_string)
        transformSrc = infin_ast.get_source(transformAst)
    else:
        transformSrc = transform_string
    tree = ast.parse(transformSrc)
    # astpretty.pprint(tree)
    # compiledcode1 = compile(tree, "<string>", "exec")
    
    # unzip the local files captured with the transform
    if zf: extract_zip_file(zf)

    dict_of_arrays_of_files = dict()
    list_dir_by_dir(client, bucketname, prefix_in, True, dict_of_arrays_of_files)
    if (len(dict_of_arrays_of_files) == 0):
        info('No directories to process')
        return
    for parentdir in dict_of_arrays_of_files:
        array_of_files = dict_of_arrays_of_files[parentdir]
        temp_input_dir = tempfile.mkdtemp()
        temp_output_dir = tempfile.mkdtemp()
        info('Processing parentdir ' + parentdir + ' with ' + str(len(array_of_files))\
                + ' objects, temp_input_dir=' + str(temp_input_dir)\
                + ', temp_output_dir=' + str(temp_output_dir))
        objects = download_objects_inner(client, bucketname, parentdir, prefix_trunc, array_of_files,
                False, None, temp_input_dir, **kwargs)

        if (enable_infin_ast == True):
            transformAst = infin_ast.extract_transform(TRANSFORM_DIR_BY_DIR,\
                src_str=transform_string)
            transformSrc = infin_ast.get_source(transformAst)
        else:
            transformSrc = transform_string
        xn = TRANSFORM_DIR_BY_DIR
        tree = ast.parse(transformSrc)
        compiledcode3 = compile(tree, "<string>", "exec")

        # Add all functions in xformcode to the globals dictionary
        glb = {}
        fl = FuncLister(glb)
        fl.visit(tree)
        try:
            exec(compiledcode3, glb)
        except Exception as e:
            status_str = str(e)
            shutil.rmtree(temp_input_dir)
            info("Execution of global statics failed for " + parentdir\
                    + ". status_str=" + status_str + ", traceback = \n" + traceback.format_exc())
            continue # process next directory
        else:
            status_str = 'Success'
        # print('Globals=')
        # pprint.pprint(glb)
        info("Execution of global statics complete. status_str=" + status_str)

        namespaced_infin_transform_fnx = namespaced_function(glb[xn], glb, None, True)
        try:
            namespaced_infin_transform_fnx(temp_input_dir, temp_output_dir, parentdir[len(prefix_trunc):], **kwargs)
        except Exception as e:
            status_str = str(e)
            info("Error executing " + xn + ", status=" + status_str + ", traceback = \n" + traceback.format_exc())
        else:
            info("Successfully executed transform " + xn + " for parentdir " + parentdir[len(prefix_trunc):])
        finally:
            shutil.rmtree(temp_input_dir)

        try:
            # lstrip() ensures that parentdir[....] expression does not start with a '/'.  this is needed to ensure that we don't have a '//' like 'infinstor//...'
            dest_path = 'infinstor/' + parentdir[len(prefix_trunc):].lstrip('/')
            for one_output_file in os.listdir(temp_output_dir):
                fq_local = os.path.join(temp_output_dir, one_output_file)
                log_artifact(fq_local, dest_path)
        except Exception as e:
            status_str = str(e)
            info("Error logging artifacts for parentdir " + str(parentdir)\
                    + ": " + status_str + ", traceback = \n" + traceback.format_exc())
        else:
            info("Successfully logged artifacts for parentdir " + str(parentdir))
        finally:
            shutil.rmtree(temp_output_dir)

def download_all_objects(client, bucketname, prefix_in, prefix_trunc, transform_string, zf:zipfile.ZipFile,
                         temp_input_dir_root, temp_output_dir, **kwargs):
    if (enable_infin_ast == True):
        transformAst = infin_ast.extract_transform(TRANSFORM_DIR_BY_DIR, src_str=transform_string)
        transformSrc = infin_ast.get_source(transformAst)
    else:
        transformSrc = transform_string
    tree = ast.parse(transformSrc)
    # astpretty.pprint(tree)

    dict_dirname_to_arrays_of_files = dict()
    list_dir_by_dir(client, bucketname, prefix_in, True, dict_dirname_to_arrays_of_files)
    if (len(dict_dirname_to_arrays_of_files) == 0):
        info('No directories to process')
        return

    if not temp_input_dir_root:
        temp_input_dir_root = tempfile.mkdtemp()
    if not temp_output_dir:
        temp_output_dir = tempfile.mkdtemp()

    download_all_s3_objects_to_download_dir(client, bucketname, dict_dirname_to_arrays_of_files, prefix_trunc,
                                            temp_input_dir_root, kwargs, temp_output_dir)
    ##unzip the local files captured with the transform
    if zf: extract_zip_file(zf)
    return temp_input_dir_root, temp_output_dir

def execute_xform_all_objects(temp_input_dir_root, temp_output_dir, transform_string, **kwargs):
    if (enable_infin_ast == True):
        transformAst = infin_ast.extract_transform(TRANSFORM_ALL_OBJECTS,\
            src_str=transform_string)
        transformSrc = infin_ast.get_source(transformAst)
    else:
        transformSrc = transform_string
    xn = TRANSFORM_ALL_OBJECTS
    tree = ast.parse(transformSrc)
    compiledcode3 = compile(tree, "<string>", "exec")

    # Add all functions in xformcode to the globals dictionary
    glb = {}
    fl = FuncLister(glb)
    fl.visit(tree)
    try:
        exec(compiledcode3, glb)
    except Exception as e:
        status_str = str(e)
        shutil.rmtree(temp_input_dir_root)
        info("Execution of global statics failed. status_str=" + status_str + ", traceback = \n" + traceback.format_exc())
        raise
    else:
        status_str = 'Success'
    # print('Globals=')
    # pprint.pprint(glb)
    info("Execution of global statics complete. status_str=" + status_str)

    namespaced_infin_transform_fnx = namespaced_function(glb[xn], glb, None, True)
    try:
        namespaced_infin_transform_fnx(temp_input_dir_root, temp_output_dir, **kwargs)
    except Exception as e:
        status_str = str(e)
        info("Error executing " + xn + ", status=" + status_str + ", traceback = \n" + traceback.format_exc())
    else:
        info("Successfully executed transform " + xn)
    finally:
        shutil.rmtree(temp_input_dir_root)

def read_and_xform_all_objects(client, bucketname, prefix_in, prefix_trunc, transform_string, zf:zipfile.ZipFile, **kwargs):
    temp_input_dir_root, temp_output_dir = download_all_objects(
        client, bucketname, prefix_in, prefix_trunc, transform_string, zf, None, None, ** kwargs)

    execute_xform_all_objects(temp_input_dir_root, temp_output_dir, transform_string, **kwargs)

    log_all_artifacts_in_dir(prefix_in, prefix_trunc, temp_output_dir)

def download_all_s3_objects_to_download_dir(client, bucketname:str, dict_dirname_to_arrays_of_files:dict, prefix_trunc:str, temp_input_dir_root:str, kwargs:dict, temp_output_dir:str):
    """download all s3 objects specified by <bucketname>+<prefix>, where each prefix is a key in the dict 'dict_dirname_to_arrays_of_files', to a local directory (temp_input_dir_root).
    
    for each s3 object, lstrip(prefix,prefix_trunc) of the object is preserved in 'temp_input_dir_root': if s3 object is s3://dir1/dir2/dir3/artifact, prefix_trunc is dir1, 
    then object is stored <temp_input_dir_root>/dir2/dir3/artifact

    temp_output_dir is only used for logging.  TODO: Remove this parameter
    """
    for parentdir in dict_dirname_to_arrays_of_files:
        temp_input_dir = os.path.join(temp_input_dir_root, parentdir[len(prefix_trunc):])
        os.makedirs(temp_input_dir, mode=0o755, exist_ok=True)
        array_of_files = dict_dirname_to_arrays_of_files[parentdir]
        info('Processing parentdir ' + parentdir + ' with ' + str(len(array_of_files))\
                + ' objects, temp_input_dir=' + str(temp_input_dir)\
                + ', temp_output_dir=' + str(temp_output_dir))
        objects = download_objects_inner(client, bucketname, parentdir, prefix_trunc,
                array_of_files, False, None, temp_input_dir, **kwargs)
    return temp_input_dir

def log_all_artifacts_in_dir(prefix_in:str, prefix_trunc:str, temp_output_dir:str, delete_output=True):
    """log all artifacts in the directory temp_out_dir as mlflow artifacts.  when logging, the artifacts are logged to lstrip(<prefix_in>,<prefix_trunc>) + <artifact_path>.  The subdirectory under temp_out_dir, where the artifact lives, is included in the logged mlflow artifact's path
    
    for example, the artifact <temp_out_dir>/dir1/artifact1 is logged to infinstor/lstrip(<prefix_in>,<prefix_trunc>)/dir1/artifact1.  
    """
    try:
        # lstrip() ensures that prefix_in[...] expression does not start with a '/'.  this is needed to ensure that we don't have a '//' like 'infinstor//...'
        dest_path = 'infinstor/' 
        # if 'no input' is selected for the transform, then prefix_in and prefix_trunc will be None
        if prefix_in != None and prefix_trunc != None: 
            dest_path = dest_path + prefix_in[len(prefix_trunc):].lstrip('/')
        for one_output_file in os.listdir(temp_output_dir):
            fq_local = os.path.join(temp_output_dir, one_output_file)
            log_artifact(fq_local, dest_path)
    except Exception as e:
        status_str = str(e)
        info("Error logging artifacts: " + status_str + ", traceback = \n" + traceback.format_exc())
    else:
        info("Successfully logged artifacts")
    finally:
        if delete_output:
            shutil.rmtree(temp_output_dir)

def look_for_transform(transform_string, transform_symbol):
    if (enable_infin_ast == True):
        transformAst = infin_ast.extract_transform(transform_symbol, src_str=transform_string)
        transformSrc = infin_ast.get_source(transformAst)
    else:
        transformSrc = transform_string
    if (verbose == True):
        info('transformSrc=' + transformSrc);
    tree = ast.parse(transformSrc)
    glb = {}
    fl = FuncLister(glb)
    fl.visit(tree)
    for key, value in glb.items():
        if (key == transform_symbol):
            return True
    return False

def get_mlflow_run_artifacts_info(input_spec):
    run_id = input_spec['run_id']
    client = mlflow.tracking.MlflowClient()
    run = client.get_run(run_id)
    # run.info = <RunInfo: artifact_uri='s3://infinstor-mlflow-artifacts-rrajendran-isstage2/mlflow-artifacts/rrajendran/0/0-a3eae5ebd76b4f35bb0cf1ef0162564f', end_time=1613664747468, experiment_id='0', lifecycle_stage='active', run_id='0-a3eae5ebd76b4f35bb0cf1ef0162564f', run_uuid='0-a3eae5ebd76b4f35bb0cf1ef0162564f', start_time=1613664685420, status='FINISHED', user_id='rrajendran'>
    artifact_uri = run.info.artifact_uri
    parse_result = urlparse(artifact_uri)
    if (parse_result.scheme != 's3'):
        raise ValueError('Error. Do not know how to deal with artifacts in scheme '\
                + parse_result.scheme)
    bucketname = parse_result.netloc
    if 'prefix' in input_spec:
        prefix = input_spec['prefix']
    else:
        prefix = parse_result.path.lstrip('/') + '/'     # parse_result.path= '/mlflow-artifacts/rrajendran/0/0-a3eae5ebd76b4f35bb0cf1ef0162564f' ; prefix='mlflow-artifacts/rrajendran/0/0-a3eae5ebd76b4f35bb0cf1ef0162564f/'
    return bucketname, prefix

def generate_input_data_spec_string(input_data_spec):
    if (input_data_spec['type'] == 'infinsnap'):
        if 'time_spec' in input_data_spec:
            rv = 'infinsnap/' + input_data_spec['time_spec'] + '/' + input_data_spec['bucketname']\
                    + '/' + input_data_spec['prefix']
        else:
            rv = 'infinsnap/' + input_data_spec['bucketname'] + '/' + input_data_spec['prefix']
    elif (input_data_spec['type'] == 'infinslice'):
        rv = 'infinslice/' + input_data_spec['time_spec'] + '/' + input_data_spec['bucketname']\
                + '/' + input_data_spec['prefix']
    elif (input_data_spec['type'] == 'label'):
        rv = 'label/' + input_data_spec['label']
    elif (input_data_spec['type'] == 'mlflow-run-artifacts'):
        rv = 'run_id/' + input_data_spec['run_id']
    elif (input_data_spec['type'] == 'no-input-data'):
        rv = 'no-input-data'
    else:
        raise ValueError('Error. Unknown input_data_spec type ' + input_data_spec['type'])
    return rv

def get_data_connection_details(service_name:str, input_data_spec:dict, xformname:str):
    """
    Returns the tuple (endpoint, prefix_in, prefix_trunc, bucketname, session, client, input_spec_string)
    
    Except for input_spec_string, one or more of the others can be None
    """
    endpoint = None
    prefix_in = None
    prefix_trunc = ''
    bucketname = None
    session = None
    client = None
    if (input_data_spec['type'] == 'infinsnap' or input_data_spec['type'] == 'infinslice'):
        if 'time_spec' in input_data_spec:
            client = boto3.client('s3', infinstor_time_spec=input_data_spec['time_spec'])
        else:
            client = boto3.client('s3')
        prefix_in = input_data_spec['prefix']
        prefix_trunc = ''
        bucketname = input_data_spec['bucketname']
    elif (input_data_spec['type'] == 'label'):
        timespec, bckt, pfx, service = get_label_info(input_data_spec['label'])
        prefix_in = pfx
        prefix_trunc = ''
        bucketname = bckt
        client = boto3.client('s3', infinstor_time_spec=timespec)
    elif (input_data_spec['type'] == 'mlflow-run-artifacts'):
        bucketname, prefix_in = get_mlflow_run_artifacts_info(input_data_spec)
        prefix_trunc = prefix_in
        session = boto3.session.Session()
        client = session.client('s3')
    elif (input_data_spec['type'] == 'no-input-data'):
        endpoint = None
        prefix_in = None
        prefix_trunc = ''
        bucketname = None
        session = None
        client = None
    else:
        raise ValueError('Error. Unknown input_data_spec type ' + input_data_spec['type'])

    input_spec_string = generate_input_data_spec_string(input_data_spec)

    return endpoint, prefix_in, prefix_trunc, \
           bucketname, session, client, input_spec_string


def run_transform_inline(service_name:str, run_id:str, input_data_spec_or_specs, xformname:str, **kwargs):
    bootstrap._bootstrap_config_values_from_mlflow_rest_if_needed()
    """
    input_data_spec_or_specs: can be a list of dicts or a dict    
    """
    transform_string, dockerfile, zf = get_xform_info(xformname)
    if (transform_string == None):
        raise ValueError('Error. Cannot find xform ' + xformname)

    log_param('run_id', run_id)

    if type(input_data_spec_or_specs) == list:
        info("transform with multiple input_data_specs detected: " + str(input_data_spec_or_specs))
        input_spec_string_list = []
        clients = []
        bucketnames = []
        prefix_ins = []
        prefix_truncs = []
        for spec in input_data_spec_or_specs:
            endpoint, prefix_in, prefix_trunc, bucketname, session, client, input_spec_string\
                = get_data_connection_details(service_name, spec, xformname)
            input_spec_string_list.append(input_spec_string)
            clients.append(client)
            bucketnames.append(bucketname)
            prefix_ins.append(prefix_in)
            prefix_truncs.append(prefix_trunc)
        try:
            log_param('input_data_spec', json.dumps(input_spec_string_list))
        except Exception:
            pass
        xobjects = run_transform_string_inline_multi_input(clients, bucketnames, prefix_ins, prefix_truncs,
                    transform_string, zf, run_id, **kwargs)
    else:
        info("transform with single input_data_specs detected: " + str(input_data_spec_or_specs))
        endpoint, prefix_in, prefix_trunc, bucketname, session, client, input_spec_string\
            = get_data_connection_details(service_name, input_data_spec_or_specs, xformname)
        try:
            log_param('input_data_spec', input_spec_string)
        except Exception:
            pass
        xobjects = run_transform_string_inline(client, bucketname, prefix_in, prefix_trunc,
                transform_string, zf, run_id, **kwargs)

    return xobjects

def run_transform_string_inline_multi_input(clients:list, bucketnames:list, prefix_ins:list, prefix_truncs:list,
                    transform_string:str, zf:zipfile.ZipFile, run_id, **kwargs):
    print("Multiple input specs")
    if look_for_transform(transform_string, TRANSFORM_DIR_BY_DIR):
        if not clients:
            raise ValueError('Error. Transform type ' + str(TRANSFORM_DIR_BY_DIR) + ' needs input_data')
        print("Running transform " + str(TRANSFORM_DIR_BY_DIR))
        num_clients = len(clients)
        for index in range(num_clients):
            client = clients[index]
            bucketname = bucketnames[index]
            prefix_in = prefix_ins[index]
            prefix_trunc = prefix_truncs[index]
            read_and_xform_dir_by_dir(client, bucketname, prefix_in, prefix_trunc,
                                      transform_string, zf, **kwargs)
    elif look_for_transform(transform_string, TRANSFORM_ALL_OBJECTS):
        if not clients:
            raise ValueError('Error. Transform type ' + str(TRANSFORM_ALL_OBJECTS) + ' needs input_data')
        print("Running transform " + str(TRANSFORM_ALL_OBJECTS))
        num_clients = len(clients)
        temp_input_dir_root = tempfile.mkdtemp()
        temp_output_dir = tempfile.mkdtemp()
        for index in range(num_clients):
            client = clients[index]
            bucketname = bucketnames[index]
            prefix_in = prefix_ins[index]
            prefix_trunc = prefix_truncs[index]
            download_all_objects(client, bucketname, prefix_in, prefix_trunc, transform_string, zf,
                                 temp_input_dir_root, temp_output_dir, **kwargs)
        execute_xform_all_objects(temp_input_dir_root, temp_output_dir, transform_string, **kwargs)
        log_all_artifacts_in_dir(None, None, temp_output_dir)
    elif look_for_transform(transform_string, TRANSFORM_MULTI_INPUTS):
        if (enable_infin_ast == True):
            transformAst = infin_ast.extract_transform(TRANSFORM_MULTI_INPUTS, src_str=transform_string)
            transformSrc = infin_ast.get_source(transformAst)
        else:
            transformSrc = transform_string
        tree = ast.parse(transformSrc)
        # astpretty.pprint(tree)
        # compiledcode1 = compile(tree, "<string>", "exec")

        temp_output_dir = tempfile.mkdtemp()
        temp_input_roots = list()
        total_dirs_to_process = 0
        for i in range(len(clients)):
            client = clients[i]
            bucketname = bucketnames[i]
            prefix_in = prefix_ins[i]
            prefix_trunc = prefix_truncs[i]

            dict_dirname_to_arrays_of_files = dict()
            list_dir_by_dir(client, bucketname, prefix_in, True, dict_dirname_to_arrays_of_files)
            if (len(dict_dirname_to_arrays_of_files) == 0):
                info('No directories to process')
                continue
            total_dirs_to_process = total_dirs_to_process + len(dict_dirname_to_arrays_of_files)

            temp_input_dir_root = tempfile.mkdtemp()
            temp_input_roots.append(temp_input_dir_root)

            download_all_s3_objects_to_download_dir(client, bucketname, dict_dirname_to_arrays_of_files, prefix_trunc, temp_input_dir_root, kwargs, temp_output_dir)

        if total_dirs_to_process == 0:
            info('No directories to process')
            return
        else:
            info("Total " + str(total_dirs_to_process) + " to process")
            for debugdir in temp_input_roots:
                print("DEBUG dir name " + debugdir + ",  exists="+str(os.path.exists(debugdir)))

        # unzip the local files captured with the transform
        if zf: extract_zip_file(zf)

        if (enable_infin_ast == True):
            transformAst = infin_ast.extract_transform(TRANSFORM_MULTI_INPUTS,\
                src_str=transform_string)
            transformSrc = infin_ast.get_source(transformAst)
        else:
            transformSrc = transform_string
        xn = TRANSFORM_MULTI_INPUTS
        tree = ast.parse(transformSrc)
        compiledcode3 = compile(tree, "<string>", "exec")

        # Add all functions in xformcode to the globals dictionary
        glb = {}
        fl = FuncLister(glb)
        fl.visit(tree)

        # if infin_transform_all_objects_multi_input() exists, use it..  use dict.get() to avoid KeyError
        if (glb.get(xn)):
            try:
                exec(compiledcode3, glb)
            except Exception as e:
                status_str = str(e)
                info("Execution of global statics failed. status_str=" + status_str)
                delete_dirs(temp_input_roots)
                raise
            else:
                status_str = 'Success'

            # print('Globals=')
            # pprint.pprint(glb)
            info("Execution of global statics complete. status_str=" + status_str)

            namespaced_infin_transform_fnx = namespaced_function(glb[xn], glb, None, True)
            try:
                namespaced_infin_transform_fnx(temp_input_roots, temp_output_dir, **kwargs)
            except Exception as e:
                status_str = str(e)
                info("Error executing " + xn + ", status=" + status_str)
            else:
                info("Successfully executed transform " + xn)
            finally:
                delete_dirs(temp_input_roots)
        else:
            exec_with_infinstor_inject_context(temp_input_roots, temp_output_dir,compiledcode3)

        log_all_artifacts_in_dir(None, None, temp_output_dir)
    else:
        run_dag_script(transform_string, run_id, **kwargs)

def run_transform_string_inline(client, bucketname, prefix_in, prefix_trunc,
        transform_string, zf:zipfile.ZipFile, run_id, **kwargs):
    if (look_for_transform(transform_string, TRANSFORM_RAW_PD)):
        if (client == None):
            raise ValueError('Error. Transform type ' + str(TRANSFORM_RAW_PD) + ' needs input_data')
        logger.info("Running transform " + str(TRANSFORM_RAW_PD))
        # TODO: is xform_local_files_zip needed for this?
        return actually_run_transformation(client, True,\
                bucketname, prefix_in, prefix_trunc, False, transform_string, zf,\
                **kwargs)
    elif (look_for_transform(transform_string, TRANSFORM_RAW_DS)):
        if (client == None):
            raise ValueError('Error. Transform type ' + str(TRANSFORM_RAW_DS) + ' needs input_data')
        logger.info("Running transform " + str(TRANSFORM_RAW_DS))
        # TODO: is xform_local_files_zip needed for this?
        return actually_run_transformation(client, False,\
                bucketname, prefix_in, prefix_trunc, False, transform_string, zf,\
                **kwargs)
    elif (look_for_transform(transform_string, TRANSFORM_CSV_PD)):
        if (client == None):
            raise ValueError('Error. Transform type ' + str(TRANSFORM_CSV_PD) + ' needs input_data')
        logger.info("Running transform " + str(TRANSFORM_CSV_PD))
        # TODO: is xform_local_files_zip needed for this?
        return actually_run_transformation(client, True,\
                bucketname, prefix_in, prefix_trunc, True, transform_string, zf,\
                **kwargs)
    elif (look_for_transform(transform_string, TRANSFORM_CSV_DS)):
        if (client == None):
            raise ValueError('Error. Transform type ' + str(TRANSFORM_CSV_DS) + ' needs input_data')
        logger.info("Running transform " + str(TRANSFORM_CSV_DS))
        # TODO: is xform_local_files_zip needed for this?
        return actually_run_transformation(client, False,\
                bucketname, prefix_in, prefix_trunc, True, transform_string, zf,\
                **kwargs)
    elif (look_for_transform(transform_string, TRANSFORM_ONE_OBJ)):
        if (client == None):
            raise ValueError('Error. Transform type ' + str(TRANSFORM_ONE_OBJ) + ' needs input_data')
        logger.info("Running transform " + str(TRANSFORM_ONE_OBJ))
        return read_and_xform_one_object(client, bucketname, prefix_in, prefix_trunc,
                transform_string, zf, **kwargs)
    elif (look_for_transform(transform_string, TRANSFORM_DIR_BY_DIR)):
        if (client == None):
            raise ValueError('Error. Transform type ' + str(TRANSFORM_DIR_BY_DIR) + ' needs input_data')
        logger.info("Running transform " + str(TRANSFORM_DIR_BY_DIR))
        return read_and_xform_dir_by_dir(client, bucketname, prefix_in, prefix_trunc,
                transform_string, zf, **kwargs)
    elif (look_for_transform(transform_string, TRANSFORM_ALL_OBJECTS)):
        if (client == None):
            raise ValueError('Error. Transform type ' + str(TRANSFORM_ALL_OBJECTS) + ' needs input_data')
        logger.info("Running transform " + str(TRANSFORM_ALL_OBJECTS))
        return read_and_xform_all_objects(client, bucketname, prefix_in, prefix_trunc,
                transform_string, zf, **kwargs)
    else:
        #run_script(client, bucketname, prefix_in, prefix_trunc, transform_string, zf, run_id, **kwargs)
        run_script(transform_string, zf, run_id, **kwargs)

def log_file(filepath:str):
    with open(filepath, 'r') as fh:
        logger.info("Contents of file=%s: \n%s", filepath, fh.read())

def run_transform_singlevm(service_name, experiment_id, parent_run_id, last_in_chain_of_xforms,
        input_data_spec, xformname, instance_type, **kwargs):
    # save the conda environment
    projdir = tempfile.mkdtemp()
    if (verbose):
        info('Project dir: ' + projdir)
    # create an empty conda.yaml file. mlflow requires it, but our backend does not use it
    # The actual xform environment (docker or conda) is stored along with the xform
    os.close(os.open(projdir + sep + 'conda.yaml', os.O_CREAT|os.O_WRONLY, mode=0o644))

    with open(projdir + sep + 'MLproject', "w") as projfile:
        kwp = ''
        for key, value in kwargs.items():
            kwp = kwp + (' --' + key + '={' + key + '}')
        projfile.write('Name: run-' + xformname + '\n')
        projfile.write('conda_env: conda.yaml\n')
        projfile.write('\n')
        projfile.write('entry_points:' + '\n')
        projfile.write('  main:' + '\n')
        projfile.write('    parameters:\n')
        projfile.write('      service: string\n')
        projfile.write('      input_data_spec: string\n')
        projfile.write('      xformname: string\n')
        for key, value in kwargs.items():
            projfile.write('      ' + key + ': string\n')
        projfile.write(
            '    command: "python -c \'from infinstor import mlflow_run; mlflow_run.main()\'\
                    --input_data_spec={input_data_spec} --service={service}\
                    --xformname={xformname}' + kwp + '"\n')
                    
    if verbose: log_file(os.path.join(projdir,'MLproject'))

    child_env = os.environ.copy()
    child_env[MLFLOW_TRACKING_URI] = os.environ.get(MLFLOW_TRACKING_URI)

    if (parent_run_id != None):
        child_env['INFINSTOR_PARENT_RUN_ID'] = parent_run_id
        child_env['INFINSTOR_LAST_IN_CHAIN_OF_XFORMS'] = last_in_chain_of_xforms
        backend_config = '{"instance_type": "' + instance_type \
            + '", "parent_run_id": "' + parent_run_id \
            + '", "last_in_chain_of_xforms": "' + last_in_chain_of_xforms + '"}'
    else:
        backend_config = '{"instance_type": "' + instance_type \
            + '", "last_in_chain_of_xforms": "' + last_in_chain_of_xforms + '"}'

    cmd = ['mlflow', 'run',
            '-b', 'infinstor-backend',
            '--backend-config', backend_config,
            '--experiment-id', str(experiment_id),
            projdir,
            '-P', 'service=' + service_name,
            '-P', 'input_data_spec=' + json.dumps(input_data_spec),
            '-P', 'xformname=' + xformname ]
    for key, value in kwargs.items():
        cmd.append('-P')
        cmd.append(key + '=' + value)
    logger.info("run_transform_singlevm(): Running cmd " + str(cmd))
    process = subprocess.Popen(cmd, env=child_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, close_fds=True)
    run_id = ''
    for line in process.stdout:
        line_s = line.decode('utf-8')
        logger.info("run_transform_singlevm(): " + line_s.rstrip('\n'))
        if (line_s.startswith('run_id=')):
            run_id = line_s[len('run_id='):].rstrip('\n')
    process.wait()

    return run_id

def run_transform_emr(time_spec, service_name, bucketname, prefix_in, xformname, **kwargs) -> str:
    print('Error: Unimplemented')
    return None

@ dataclass
class InputDataSpec:
    type: str                   # no-input-data | infinsnap | infinslice | mlflow-run-artifacts
    run_id: str = None          # mlflow run-id to read input from when type=='mlflow-run-artifacts'
    bucketname: str = None      # the bucketname when type == infinsnap | infinslice
    prefix: str = None          # the S3 prefix when type == infinsnap | infinslice
    time_spec: str = None       # the time_spec when type == infinsnap | infinslice
    
@ dataclass
class RunOptions:
    xformname: str
    service_name: str
    run_location: str                    # single-vm | inline | emr
    input_data_spec: InputDataSpec
    experiment_id: str = None            # the mlflow experiment_id for this run
    instance_type: str = None            # the VM type for this run if run_location == single-vm
    parent_run_id = None                 # applicable when running more than one transform
    last_in_chain_of_xforms = None
    
@dataclass
class Transform:
    kwargs: Dict[str, str]
    run_options: RunOptions
    

def run_transform(run_options:dict, **kwargs) -> str:
    """ Runs the specified transforms.  Returns the run_id """
    if ('parent_run_id' in run_options):
        parent_run_id = run_options.get('parent_run_id')
    else:
        parent_run_id = None
    if ('last_in_chain_of_xforms' in run_options):
        last_in_chain_of_xforms = run_options.get('last_in_chain_of_xforms')
    else:
        last_in_chain_of_xforms = 'False'
    input_data_spec = run_options.get('input_data_spec')
    xformname = run_options.get('xformname')
    service_name = run_options.get('service_name')
    run_location = run_options.get('run_location')
    if (run_location == "inline"):
        if (parent_run_id != None):
            nes = True
        else:
            nes = False
        with start_run(nested=nes, experiment_id=run_options['experiment_id']) as run:
            run_options['run_id'] = run.info.run_id
            logger.info("run_transform(): Starting inline run of transform = %s with kwargs = %s", run_options, kwargs)
            xobjects = run_transform_inline(service_name, run.info.run_id,
                    input_data_spec, xformname, **kwargs)
            logger.info("run_transform(): Ended inline run of transform = %s with kwargs = %s", run_options, kwargs)
            return run.info.run_id
    elif (run_location == "singlevm"):
        instance_type = run_options.get('instance_type')
        logger.info("run_transform(): Starting single-vm run of transform = %s with kwargs = %s", run_options, kwargs)
        run_id: str = run_transform_singlevm(service_name, run_options['experiment_id'], parent_run_id,
                last_in_chain_of_xforms, input_data_spec, xformname, instance_type, **kwargs)
        run_options['run_id'] = run_id
        logger.info("run_transform(): Finished submitting single-vm run of transform = %s with kwargs = %s", run_options, kwargs)
        return run_id
    elif (run_location == "emr"):
        time_spec = run_options.get('time_spec')
        service_name = run_options.get('service_name')
        bucketname = run_options.get('bucketname')
        prefix_in = run_options.get('prefix')
        xformname = run_options.get('xformname')
        return run_transform_emr(time_spec, service_name, bucketname, prefix_in, xformname,\
                **kwargs)

def run_transforms(transforms):
    try:
        logger.info("run_transforms(): start = %s ", transforms)
        global verbose 
        verbose = set_verbose()

        # populate builtins.region, builtins.mlflowserver and others, if needed
        bootstrap._bootstrap_config_values_from_mlflow_rest_if_needed()
        
        if ('MLFLOW_EXPERIMENT_ID' in os.environ):
            experiment_id = os.environ['MLFLOW_EXPERIMENT_ID']
        else:
            experiment_id = '0'
        if (len(transforms) == 1):
            transform = transforms[0]
            transform['run_options']['experiment_id'] = experiment_id
            if ('kwargs' in transform and transform['kwargs'] != None):
                run_id:str = run_transform(transform['run_options'], **transform['kwargs'])
            else:
                run_id:str = run_transform(transform['run_options'])
            logger.info("run_transforms(): end = %s ", transforms)
            return run_id

        run = start_run(experiment_id = experiment_id)
        parent_run_id = run.info.run_id
        print('parent_run_id = ' + str(parent_run_id))

        run_id = None
        for ind in range(len(transforms)):
            transform = transforms[ind]
            run_options = transform['run_options']
            run_options['experiment_id'] = experiment_id

            do_reset_mlflow_active_run_stack = False
            do_end_parent_run = False
            if (ind == (len(transforms) - 1)): # last xform
                run_options['last_in_chain_of_xforms'] = 'True'
                if (run_options['run_location'] == 'inline'):
                    do_end_parent_run = True # we end the parent run for inline runs
                elif (run_options['run_location'] == 'singlevm'):
                    do_reset_mlflow_active_run_stack = True
            else:
                run_options['last_in_chain_of_xforms'] = 'False'

            if (ind > 0): # set the input_data_spec for all but the first transform
                if (run_id == None or len(run_id) == 0):
                    print('Error. run_id not available for chained transform')
                    return
                else:
                    input_data_spec = {}
                    input_data_spec['type'] = 'mlflow-run-artifacts'
                    input_data_spec['run_id'] = run_id
                    run_options['input_data_spec'] = input_data_spec

            run_options['parent_run_id'] = parent_run_id
            kwargs = transform['kwargs']
            if (kwargs != None):
                run_id = run_transform(run_options, **kwargs)
            else:
                run_id = run_transform(run_options)
            if (do_end_parent_run):
                end_run()
            if (do_reset_mlflow_active_run_stack):
                mlflow.tracking.fluent._active_run_stack = []
        
        logger.info("run_transforms(): end = %s ", transforms)
    except Exception as e:
        logger.error("run_transforms(): error: caught exception: %s \ntransforms = %s", traceback.format_exc(), transforms)

# returns a pandas DataFrame with index 'YY-MM-dd HH:MM:SS bucketname/filename'
# and one column named RawBytes that contains the raw bytes from the object
def download_objects(timespec, bucketname, array_of_files, is_csv):
    client = boto3.client('s3', infinstor_time_spec=timespec)
    with start_run() as run:
        return download_objects_inner(client, bucketname, '', '', array_of_files, is_csv,\
                None, None)

def delete_dirs(dirs):
    for dir in dirs:
        if os.path.exists(dir):
            shutil.rmtree(dir)

def test_infin_transform(service_name, input_data_spec, **kwargs):
    caller_globals = dict(inspect.getmembers(inspect.stack()[1][0]))["f_globals"]
    code_str = ''
    for one_line in caller_globals['In']:
        code_str = one_line # pick last cell's code
    # print(code_str)

    clean_code = ''
    code_str_lines = code_str.splitlines()
    for one_line in code_str_lines:
        if (one_line == '%reset -f'):
            continue
        if (one_line == 'from infinstor import test_infin_transform # infinstor'):
            continue
        if (one_line.startswith('input_data_spec') and one_line.endswith('# infinstor')):
            continue
        if (one_line.startswith('rv = test_infin_transform') and one_line.endswith('# infinstor')):
            continue
        clean_code += (one_line + '\n')
    # print(clean_code)

    if (input_data_spec['type'] == 'infinsnap' or input_data_spec['type'] == 'infinslice'):
        if 'time_spec' in input_data_spec:
            client = boto3.client('s3', infinstor_time_spec=input_data_spec['time_spec'])
        else:
            client = boto3.client('s3')
        prefix_in = input_data_spec['prefix']
        prefix_trunc = ''
        bucketname = input_data_spec['bucketname']
    elif (input_data_spec['type'] == 'label'):
        timespec, bckt, pfx, service = get_label_info(input_data_spec['label'])
        prefix_in = pfx
        prefix_trunc = ''
        bucketname = bckt
        client = boto3.client('s3', infinstor_time_spec=timespec)
    elif (input_data_spec['type'] == 'mlflow-run-artifacts'):
        bucketname, prefix_in = get_mlflow_run_artifacts_info(input_data_spec)
        prefix_trunc = prefix_in
        session = boto3.session.Session()
        client = session.client('s3')
    elif (input_data_spec['type'] == 'no-input-data'):
        endpoint = None
        prefix_in = None
        prefix_trunc = ''
        bucketname = None
        session = None
        client = None
    else:
        raise ValueError('Error. Unknown input_data_spec type ' + input_data_spec['type'])


    with start_run() as run:
        run_transform_string_inline(client, bucketname, prefix_in, prefix_trunc, clean_code, run.info.run_id, **kwargs)
        return run.info.run_id

def infinsnap(snaptime=datetime.now()):
    # add timezone info to naive snaptime
    if (snaptime.tzinfo == None or snaptime.tzinfo.utcoffset(snaptime) == None):
        snaptime = snaptime.replace(tzinfo=datetime.now(timezone.utc).astimezone().tzinfo)
    snaptime = snaptime.astimezone(timezone.utc)
    return snaptime.strftime('tm%Y%m%d%H%M%S')

def infinslice(start_time, end_time):
    # add timezone info to naive start_time
    if (start_time.tzinfo == None or start_time.tzinfo.utcoffset(start_time) == None):
        start_time = start_time.replace(tzinfo=datetime.now(timezone.utc).astimezone().tzinfo)
    start_time = start_time.astimezone(timezone.utc)
    # add timezone info to naive end_time
    if (end_time.tzinfo == None or end_time.tzinfo.utcoffset(end_time) == None):
        end_time = end_time.replace(tzinfo=datetime.now(timezone.utc).astimezone().tzinfo)
    end_time = end_time.astimezone(timezone.utc)
    return start_time.strftime('tm%Y%m%d%H%M%S') + '-' + end_time.strftime('tm%Y%m%d%H%M%S')
