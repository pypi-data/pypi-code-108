# -*- coding: future_fstrings -*-

import os
import shutil
import sys
import six
import re

if __name__ == "__main__":
    cur_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, cur_dir)

from sumoappclient.common.utils import get_normalized_path, create_dir
from sumoappclient.pkggenerator.base import PkgGenerator


class SetupGen(PkgGenerator):

    def __init__(self, target_folder, configpath=None, *args, **kwargs):
        self.target_folder = target_folder
        if not configpath:
            configpath = self.generate_config()
        super(SetupGen, self).__init__(configpath, *args, **kwargs)

    def _is_valid(self, val, pattern):
        return re.match(pattern, val)

    def _get_input(self, field_name, regex):
        # if six.PY2:
        #     input = raw_input

        value = input('Enter %s: >' % field_name)
        while not (value and self._is_valid(value, regex)):
            value = input('Enter %s: >' % field_name)

        return value

    def get_deploy_metadata(self):
        deploy_metadata = {}
        inputs = [("PACKAGENAME", r'^[a-z\-]+$'), ("APPNAME", r'^[a-zA-Z ]+$'), ("SRC_FOLDER_NAME", r'^[a-z]+$')]
        for field, pattern in inputs:
            deploy_metadata[field] = self._get_input(field, pattern)
        print("User input %s" % deploy_metadata)
        return deploy_metadata

    def generate_config(self):
        base_configpath = os.path.join(self.RESOURCE_FOLDER, "setup", "baseconfig.yaml")
        deploy_metadata = self.get_deploy_metadata()
        src_folder_path = os.path.join(self.target_folder, deploy_metadata["SRC_FOLDER_NAME"])
        create_dir(src_folder_path)
        filename = "%s.yaml" % deploy_metadata["SRC_FOLDER_NAME"]
        configpath = os.path.join(src_folder_path, filename)
        print("generating yaml config file %s" % configpath)
        deploy_config = {
            "APPNAME": deploy_metadata["APPNAME"],
            "PACKAGENAME": deploy_metadata["PACKAGENAME"],
            "SRC_FOLDER_NAME": deploy_metadata["SRC_FOLDER_NAME"],
            "COLLECTION_CONFIG": filename,
            "ENABLE_LAYER": deploy_metadata.get("ENABLE_LAYER", False),
            "APPNAME_SINGLE": deploy_metadata["APPNAME"].replace(" ", '').replace("_", "")
        }

        self.generate_file(base_configpath, deploy_config, configpath)
        return configpath

    def setup_env(self):
        self.remove_unwanted_files(self.project_dir)

    def generate_setup_files(self):
        target_folder = get_normalized_path(self.target_folder)
        for filename in ["setup.py", "README.md", "MANIFEST.in"]:
            self.generate_file(os.path.join(self.RESOURCE_FOLDER, "setup", filename), self.deploy_config, os.path.join(target_folder, filename))
        for filename in ["LICENSE", "VERSION"]:
            shutil.copyfile(os.path.join(self.RESOURCE_FOLDER, "setup", filename), os.path.join(target_folder, filename))

if __name__ == '__main__':
    sobj = SetupGen("/Users/username/sumologic-workday")
    sobj.generate_setup_files()
