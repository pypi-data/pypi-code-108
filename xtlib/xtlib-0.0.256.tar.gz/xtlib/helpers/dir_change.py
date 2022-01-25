#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# dir_change.py: does a structured dir changed
import os
import shutil

class DirChange:
    def __init__(self, new_dir):
        self.orig_dir = os.getcwd()
        self.new_dir = new_dir
        
    def __enter__(self):
        os.chdir(self.new_dir)
        # copy xt_config file into new test dir
        #shutil.copyfile(self.orig_dir + "/xt_config.yaml", "xt_config.yaml")

    def __exit__(self, type, value, traceback):        
        # remove xt_config file from test dir
        #os.remove("xt_config.yaml")
        os.chdir(self.orig_dir)
