#  (C) Copyright IBM Corp. 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import subprocess
import os


def get_openshift_token(username, password, server):
    try:
        cmd = subprocess.run(["./oc login -u {} -p {} --server={} --insecure-skip-tls-verify=true > /dev/null && ./oc whoami --show-token=true".format(
            username,
            password,
            server
        )],
            cwd=os.path.dirname(os.path.realpath(__file__)),
            shell=True, capture_output=True, check=True)
        token = str(cmd.stdout, 'utf-8').strip()
        print("Token: {}".format(token))
    except subprocess.CalledProcessError as ex:
        print("Command execution failed with code: {}, reason:\n{}".format(ex.returncode, ex.stderr))
        token = None

    return token

