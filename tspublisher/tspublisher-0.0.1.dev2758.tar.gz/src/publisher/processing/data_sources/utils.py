from __future__ import absolute_import, division, print_function

import csv
import os
from distutils.dir_util import copy_tree

from ruamel.yaml import YAML


class YamlObject(YAML):
    def __init__(self):
        YAML.__init__(self)
        self.default_flow_style = False
        self.block_seq_indent = 2
        self.indent = 4
        self.encoding = "utf-8"


def read_csv_file(csv_file):
    with open(csv_file, "rU") as f:
        reader = csv.DictReader(f, delimiter='|')

        rows = [{key: sanitise_new_lines(value) for key, value in row.items()} for row in reader]
        headers = reader.fieldnames

        return headers, rows


def sanitise_new_lines(string):
    if string is not None:
        string = string.replace("\r", "\n").rstrip("\n")
        string = string.decode("utf-8") if type(string) == bytes else string

    return string


def copy_assets(source_directory, destination_directory):
    if os.path.isdir(source_directory):
        copy_tree(source_directory, destination_directory)
        delete_misc_files(destination_directory)


def delete_misc_files(directory_name):
    thumbs_file = os.path.join(directory_name, "Thumbs.db")
    ds_store_file = os.path.join(directory_name, ".DS_Store")

    if os.path.isfile(thumbs_file):
        os.remove(thumbs_file)
    if os.path.isfile(ds_store_file):
        os.remove(ds_store_file)
