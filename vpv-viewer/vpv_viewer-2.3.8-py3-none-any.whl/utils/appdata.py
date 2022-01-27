# Copyright 2016 Medical Research Council Harwell.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# @author Neil Horner <n.horner@har.mrc.ac.uk>

import appdirs
import yaml
from os.path import expanduser
import os
import collections
from vpv import common
import logging

VPV_APPDATA_VERSION = 2.2
ANNOTATION_CRICLE_RADIUS_DEFAULT = 40


class AppData(object):
    def __init__(self):
        self.using_appdata = True # Set to false if we weren't able to find a sirectory to save the appdata
        appname = 'vpv_viewer'
        appdata_dir = appdirs.user_data_dir(appname)

        if not os.path.isdir(appdata_dir):
            try:
                os.mkdir(appdata_dir)
            except WindowsError:
                #Can't find the AppData directory. So just make one in home directory
                appdata_dir = os.path.join(expanduser("~"), '.' + appname)
                if not os.path.isdir(appdata_dir):
                    os.mkdir(appdata_dir)

        self.app_data_file = os.path.join(appdata_dir, 'vpv_viewer.yaml')

        if os.path.isfile(self.app_data_file):

            self.data = common.load_yaml(self.app_data_file)
            if not self.data:
                logging.error(f'Warning: could not load app data file\nTry deleting {self.app_data_file}')
                self.data = {}
        else:
            self.data = {}

        # Appdata versioning was not always in place. If a we find some appdata without a version, reset the data
        # Also reset the data if we find a previous version

        # This breaks for JIm on v2.02. Complains about NoneType not having a get(). Catch attribute error
        try:
            if self.data.get('version') is None or self.data['version'] < VPV_APPDATA_VERSION:
                print("resetting appdata")
                self.data = {}
        except AttributeError:
            self.data = {}

        if self.data == {}:
            self.data['version'] = VPV_APPDATA_VERSION

        if 'recent_files' not in self.data:
            self.data['recent_files'] = collections.deque(maxlen=10)

    def set_flips(self, flip_options: dict):
        self.data['flips'] = flip_options

    def get_flips(self):
        flips = self.data.get('flips')

        if not flips:
            self.data['flips'] = {'axial':    {'x': False, 'z': False, 'y': False},
                                      'coronal':  {'x': False, 'z': False, 'y': False},
                                      'sagittal': {'x': False, 'z': False, 'y': False},
                                      'impc_view': False}

        return self.data['flips']

    @property
    def last_qc_dir(self):
        return self.data.get('last_qc_dir')

    @last_qc_dir.setter
    def last_qc_dir(self, dir_):
        self.data['last_qc_dir'] = dir_

    @property
    def last_qc_output_dir(self):
        return self.data.get('last_qc_output_dir')

    @last_qc_output_dir.setter
    def last_qc_output_dir(self, dir_):
        self.data['last_qc_output_dir'] = dir_

    @property
    def last_atlas_metadata_file(self):
        return self.data.get('last_atlas_metadata_file')

    @last_atlas_metadata_file.setter
    def last_atlas_metadata_file(self, file_):
        self.data['last_atlas_metadata_file'] = file_

    @property
    def annotation_circle_radius(self):
        return self.data.get('annotation_cricle_radius', ANNOTATION_CRICLE_RADIUS_DEFAULT)

    @annotation_circle_radius.setter
    def annotation_circle_radius(self, radius):
        self.data['annotation_cricle_radius'] = radius

    @property
    def annotation_centre(self):
        return self.data.get('annotation_centre')

    @annotation_centre.setter
    def annotation_centre(self, centre):
        self.data['annotation_centre'] = centre

    @property
    def annotation_stage(self):
        return self.data.get('annotation_stage')

    @annotation_stage.setter
    def annotation_stage(self, stage):
       self.data['annotation_stage'] = stage

    @property
    def annotator_id(self):
        return self.data.get('annotator_id')

    @annotator_id.setter
    def annotator_id(self, id_):
        self.data['annotator_id'] = id_

    @property
    def last_screen_shot_dir(self):
        if not self.data.get('last_screenshot_dir'):
            self.data['last_screenshot_dir'] = expanduser("~")
        return self.data['last_screenshot_dir']

    @last_screen_shot_dir.setter
    def last_screen_shot_dir(self, dir_):
        self.data['last_screenshot_dir'] = dir_

    def write_app_data(self):
        #first convert yaml-incompatible stuff
        self.data['recent_files'] = [str(x) for x in self.data['recent_files']]

        with open(self.app_data_file, 'w') as fh:
            fh.write(yaml.dump(self.data))

    def get_last_dir_browsed(self):
        if not self.data.get('last_dir_browsed'):
            self.data['last_dir_browsed'] = expanduser("~")
        return self.data['last_dir_browsed']

    def set_last_dir_browsed(self, path):
        self.data['last_dir_browsed'] = path

    def add_used_volume(self, volpath):
        if volpath not in self.data['recent_files']:
            self.data['recent_files'].append(volpath)

    def get_recent_files(self):
        return self.data['recent_files']

    def set_include_filter_patterns(self, patterns):
        self.data['include_patterns'] = patterns

    def get_include_filter_patterns(self):
        if not self.data.get('include_patterns'):
            return []
        else:
            return self.data.get('include_patterns')

    def set_exclude_filter_patterns(self, patterns):
        self.data['exclude_patterns'] = patterns

    def get_exclude_filter_patterns(self):
        if not self.data.get('exclude_patterns'):
            return []
        else:
            return self.data.get('exclude_patterns')

    def clear_recent(self):
        self.data['recent_files'].clear()

