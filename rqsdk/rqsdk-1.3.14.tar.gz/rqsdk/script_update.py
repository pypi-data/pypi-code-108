# -*- coding: utf-8 -*-
#
# Copyright 2016 Ricequant, Inc
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
import os
import subprocess
import sys

import click

from rqsdk.const import BASH_FILE, EXTRA_INDEX_URL


def pip_install(full_name, index_url):
    proxy_url = os.environ.get('RQSDK_PROXY', "")
    proxy_cmd = ""
    if proxy_url:
        proxy_cmd = "--proxy {}".format(proxy_url)
    command = "install -U -i {} --extra-index-url {} {} {}".format(index_url, EXTRA_INDEX_URL, full_name, proxy_cmd)
    if os.environ.get("RQSDK_PYPI"):
        command = "install -U -i {} {} {}".format(os.environ["RQSDK_PYPI"], full_name, proxy_cmd)
        click.echo("pip {}".format(command))
    python_path = "\"{}\"".format(sys.executable)
    if sys.platform == "win32":
        end_help_msg = "& echo 请按下 Enter（回车）键继续..."
        subprocess.Popen("{} -m pip {} ".format(python_path, command) + end_help_msg, shell=True)
        sys.exit(1)
    else:
        subprocess.check_call(["{} -m pip {} ".format(python_path, command)], shell=True)


def update_bash_file(variables, value):
    for _file in BASH_FILE:
        _path = os.path.join(os.path.expanduser("~"), _file)
        if not os.path.exists(_path):
            continue
        lines = open(_path, "r", encoding="utf8").readlines()
        changed = set()

        def update_bash(line):
            nonlocal changed
            for i in variables:
                if "export {}=".format(i) in line:
                    changed.add(i)
                    return "export {}={} \n".format(i, value)
            return line

        lines = [update_bash(i) for i in lines.copy()]

        for i in variables:
            if not i in changed:
                lines.append("export {}={} \n".format(i, value))
        with open(_path, "w", encoding="utf8")as f:
            f.writelines(lines)
