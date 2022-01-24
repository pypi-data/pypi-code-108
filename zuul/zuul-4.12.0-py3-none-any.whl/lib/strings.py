# Copyright 2021 Acme Gating, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import base64
import os.path
from urllib.parse import quote_plus

import zuul.model


def unique_project_name(project_name):
    parts = project_name.split('/')
    prefix = parts[0]
    name = quote_plus(project_name)
    return (prefix, name)


def workspace_project_path(hostname, project_name, scheme):
    """Return the project path based on the specified scheme"""
    if scheme == zuul.model.SCHEME_UNIQUE:
        prefix, project_name = unique_project_name(project_name)
        return os.path.join(hostname, prefix, project_name)
    elif scheme == zuul.model.SCHEME_GOLANG:
        return os.path.join(hostname, project_name)
    elif scheme == zuul.model.SCHEME_FLAT:
        parts = project_name.split('/')
        return os.path.join(parts[-1])


def b64encode(string):
    # Return a base64 encoded string (the module operates on bytes)
    return base64.b64encode(string.encode('utf8')).decode('utf8')
