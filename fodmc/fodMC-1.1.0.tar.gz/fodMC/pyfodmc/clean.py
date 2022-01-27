#!/usr/bin/env python
# Copyright 2020-2022 The fodMC Developers. All Rights Reserved.
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
#
# Author: Kai Trepte <kai.trepte1987@gmail.com>
#
import os
from glob import glob 

""" Clean script """

delete = ['fodMC.out','system']
delete += glob('*.xyz')

for d in delete:
    try:
        os.remove(d)
        print("File Removed!")
    except BaseException:
        'Nothing'
