#!/usr/bin/env python

# Copyright 2011-2015 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
import os
import tempfile
import shutil

import xnat
from xnat.exceptions import XNATLoginFailedError


def main():
    parser = argparse.ArgumentParser(description='Copy Xnat projects')
    parser.add_argument('--host', type=str, required=True, help='XNAT url')
    parser.add_argument('--folder', type=str, required=True, help='path to upload dir')

    parser.add_argument('--destination', type=str, required=False, default=None, help='archive/prearchive')
    parser.add_argument('--retries', type=str, required=False, default=None, help='number of retries for upload')
    parser.add_argument('--project', type=str, required=False, default=None, help='project id')
    parser.add_argument('--subject', type=str, required=False, default=None, help='subject label')
    parser.add_argument('--experiment', type=str, required=False, default=None,  help='experiment label')

    parser.add_argument('--import-handler', type=str, )
    parser.add_argument('--quarantine', type=bool, required=False, default=False, help='Quarantine data')
    parser.add_argument('--trigger-pipelines', type=bool, required=None, default=False, help='Trigger pipelines')

    args = parser.parse_args()
    try:
        with xnat.connect(args.host) as xnat_host:
            xnat_host.services.import_dir(args.folder, quarantine=args.quarantine, destination=args.destination,
                                          trigger_pipelines=args.trigger_pipelines, project=args.project, subject=args.subject,
                                          experiment=args.experiment, import_handler=None)
    except XNATLoginFailedError:
        print(f"ERROR Failed to login")


if __name__ == '__main__':
    main()
