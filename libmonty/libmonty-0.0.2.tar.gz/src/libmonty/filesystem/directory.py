#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# imports ######################################################################

import os
import re

# fields and initial values ####################################################

BASE_DIR = "~"
DATA_FILE_DICT_DELIMITER = "="

global exec_dir


# operations ###################################################################

def join(path1, path2):
    return os.path.join(path1, path2)


# current directory information ################################################

def get_current_dir():
    return os.path.basename(os.getcwd())


def get_current_dir_path():
    return os.getcwd()


def get_current_dir_content():
    content_list = os.listdir(os.getcwd())
    return {
        'list': content_list,
        'count': len(content_list)
    }


def get_current_dir_content_list():
    return os.listdir(os.getcwd())


def get_current_dir_content_count():
    return len(os.listdir(os.getcwd()))


def save_exec_dir():
    global exec_dir
    exec_dir = os.getcwd()


# checks #######################################################################

def is_dir(arg_path):
    return os.path.isdir(arg_path)


def is_file(arg_path):
    return os.path.isfile(arg_path)


# navigation ###################################################################

def navigate(arg_path):
    os.chdir(arg_path)


def nav_parent():
    os.chdir("../")


def nav_base_dir():
    os.chdir(BASE_DIR)


# creation #####################################################################

def create_dir(name):
    os.mkdir(name)


def create_file(name):
    newfile = open(name, 'x')
    newfile.close()


# special getters ##############################################################

def get_int_from_file(arg_path):

    valuefile = open(arg_path, 'rt')
    return int(valuefile.readlines()[0].splitlines()[0])


def get_string_from_file(arg_path):

    valuefile = open(arg_path, 'rt')
    return valuefile.readlines()[0].splitlines()[0]


def get_list_from_file(arg_path):

    valuefile = open(arg_path, 'rt')
    lines = valuefile.readlines()
    return_list = list()

    for line in lines:
        line_content = line.splitlines()[0]

        non_data_content = re.fullmatch('^[.*]?$', line_content)

        if not non_data_content and line_content is not '':
            return_list.append( line.splitlines()[0].strip() )

    return return_list


def get_dict_from_file(arg_path):

    valuefile = open(arg_path, "rt")
    lines = valuefile.readlines()
    return_dict = dict()

    for line in lines:
        line_content = line.splitlines()[0]

        non_data_content = re.fullmatch('^[.*]?$', line_content)

        if not non_data_content and line_content is not '':

            new_kv_pair = line_content.split( DATA_FILE_DICT_DELIMITER )
            new_key = new_kv_pair[0].strip()
            new_value = new_kv_pair[1].strip()
            return_dict[new_key] = new_value

    return return_dict

# END ##########################################################################
