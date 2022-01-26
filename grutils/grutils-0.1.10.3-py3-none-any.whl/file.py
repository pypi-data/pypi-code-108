#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from .error import Error


def should_exists(err: Error, file_path=''):
    if err.has_error():
        return False
    if not os.path.exists(file_path):
        err.append('file or folder "' + file_path + '" is not exists')
        return False
    return True


def new_path_with_postfix(file_path: str, postfix: str):
    folder = os.path.dirname(file_path)
    old_filename = os.path.basename(file_path)
    old_filename_items = os.path.splitext(old_filename)
    if len(old_filename_items) > 1:
        new_filename = old_filename_items[0] + postfix + old_filename_items[1]
    else:
        new_filename = old_filename + postfix
    return os.path.join(folder, new_filename)


def load_csv(err: Error, file_path=''):
    data = {
        'fields': [],
        'rows': []
    }

    if err.has_error():
        return data

    if not should_exists(err, file_path):
        return data

    with open(file_path, "rt") as f:
        for line in f:
            items = list(map(lambda x: x.strip(), line.split(',')))
            if len(items) == 0:
                continue

            if len(data.get('fields')) == 0:
                data['fields'] = items
            else:
                data['rows'].append(items)

    return data


def create_folder_if_not_exists(folder):
    if not os.path.exists(folder):
        os.mkdir(folder)
