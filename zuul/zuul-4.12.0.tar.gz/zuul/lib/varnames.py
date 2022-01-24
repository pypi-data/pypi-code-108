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
import re


VARNAME_RE = re.compile(r'^[A-Za-z0-9_]+$')


def check_varnames(var):
    # We block these in configloader, but block it here too to make
    # sure that a job doesn't pass variables named zuul or nodepool.
    if 'zuul' in var:
        raise Exception("Defining variables named 'zuul' is not allowed")
    if 'nodepool' in var:
        raise Exception("Defining variables named 'nodepool' is not allowed")
    if 'unsafe_vars' in var:
        raise Exception("Defining variables named 'unsafe_vars' "
                        "is not allowed")
    for varname in var.keys():
        if not VARNAME_RE.match(varname):
            raise Exception("Variable names may only contain letters, "
                            "numbers, and underscores")
    # Block some connection related variables so they cannot be
    # overridden by jobs to bypass security mechanisms.
    connection_vars = [
        'ansible_connection',
        'ansible_host',
        'ansible_python_interpreter',
        'ansible_shell_executable',
        'ansible_user',
    ]
    for conn_var in connection_vars:
        if conn_var in var:
            raise Exception(f"Variable name '{conn_var}' is not allowed.")
