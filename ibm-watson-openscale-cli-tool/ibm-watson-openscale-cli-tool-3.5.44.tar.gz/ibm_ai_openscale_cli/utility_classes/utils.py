# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8
from __future__ import print_function

from requests.auth import HTTPBasicAuth
from urllib3.util import parse_url
import os
import json
import subprocess
import sys
import requests
import random

def pip_install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])


def executeCommandWithResult(cmd):
    '''
    Run command and capture the output of the command
    '''
    status, result = subprocess.getstatusoutput(cmd)
    if status != 0:
        return None
    return result


def executeCommand(cmd):
    '''
    Run command
    '''
    status, result = subprocess.getstatusoutput(cmd)
    if status != 0:
        error_msg = 'Exited with {} status while trying to execute {}. Reason: {}'.format(status, cmd, result)
        raise Exception(error_msg)


def jsonFileToDict(filename):
    '''
    reads the json file specfied and returns it as a dictionary
    '''
    result = None
    if (filename is not None and filename.strip()):
        with open(filename.strip()) as f:
            result = json.load(f)
    if result is None:
        error_msg = 'Unable to read file "{}"'.format(filename)
        raise Exception(error_msg)
    return result


def remove_port_from_url(url):
    elements = parse_url(url)
    url_without_port = '{}://{}'.format(elements.scheme, elements.hostname)
    if elements.path and len(elements.path) > 1:
        url_without_port = '{}{}'.format(url_without_port, elements.path)
    #if elements.params:
    #    url_without_port = '{};{}'.format(url_without_port, elements.params)
    if elements.query:
        url_without_port = '{}?{}'.format(url_without_port, elements.query)
    if elements.fragment:
        url_without_port = '{}#{}'.format(url_without_port, elements.fragment)
    return url_without_port


# None means same value will be used
def update_url(url, new_hostname, new_port=None, new_scheme=None):
    elements = parse_url(url)
    host = new_hostname if new_hostname else elements.hostname
    port = new_port if new_port else elements.port
    scheme = new_scheme if new_scheme else elements.scheme
    new_url =  '{}://{}'.format(scheme, host)
    if port:
        new_url = '{}:{}'.format(new_url, port)
    if elements.path and len(elements.path) > 1:
        new_url = '{}{}'.format(new_url, elements.path)
    #if elements.params:
    #    new_url = '{};{}'.format(new_url, elements.params)
    if elements.query:
        new_url = '{}?{}'.format(new_url, elements.query)
    if elements.fragment:
        new_url = '{}#{}'.format(new_url, elements.fragment)
    return new_url


def get_url_elements(url):
    return parse_url(url)

def get_error_message(response):
    """
    Gets the error message from a JSON response.
    :return: the error message
    :rtype: string
    """
    error_message = 'Unknown error'
    try:
        error_json = response.json()
        if 'error' in error_json:
            if isinstance(error_json['error'], dict) and 'description' in \
                    error_json['error']:
                error_message = error_json['error']['description']
            else:
                error_message = error_json['error']
        elif 'error_message' in error_json:
            error_message = error_json['error_message']
        elif 'message' in error_json:
            error_message = error_json['message']
        elif 'description' in error_json:
            error_message = error_json['description']
        elif 'errorMessage' in error_json:
            error_message = error_json['errorMessage']
        elif 'msg' in error_json:
            error_message = error_json['msg']
        return error_message
    except:
        return response.text or error_message


# random.choices() not available before Python 3.6
# expects a [] list of the choices and an equal-length [] list of integer weights
def choices(population, weights):
    sum_weights = 0
    for i in weights:
        sum_weights += i
    r = random.randint(0, sum_weights)
    choice = population[0]
    sum_weights = 0
    for i in range(len(weights)):
        sum_weights += weights[i]
        if r <= sum_weights:
            choice = population[i]
            break
    return choice


def get_immediate_subdirectories(parent_dir):
    result = []
    contents = os.listdir(parent_dir)
    for item in contents:
        valid_name = not (str(item).startswith('.') or str(item).startswith('_'))
        directory = get_path(parent_dir, [parent_dir, item])
        if valid_name and os.path.isdir(directory):
            result.append(item)
    return result


def get_path(basedir, path_array):
    basedir = os.path.realpath(basedir)
    path = os.path.realpath(os.sep.join(path_array))
    if path.startswith(basedir):
        return path
    raise Exception('Requested path ({}) does not begin with base directory ({})'.format(path, basedir))


def load_pickle_file(pickle_file_path):
    # import pickle
    # with open(pickle_file_path, 'rb') as handle:
    #     return pickle.load(handle)
    pass

