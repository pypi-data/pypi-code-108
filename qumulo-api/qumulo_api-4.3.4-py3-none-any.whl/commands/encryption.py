# Copyright (c) 2020 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# Copyright (c) 2020 Qumulo, Inc. All rights reserved.
#
# NOTICE: All information and intellectual property contained herein is the
# confidential property of Qumulo, Inc. Reproduction or dissemination of the
# information or intellectual property contained herein is strictly forbidden,
# unless separate prior written permission has been obtained from Qumulo, Inc.

import argparse

from typing import Optional

import qumulo.lib.opts
import qumulo.rest.encryption as encryption

from qumulo.lib.auth import Credentials
from qumulo.lib.request import Connection


class RotateEncryptionKeysCommand(qumulo.lib.opts.Subcommand):
    NAME = 'rotate_encryption_keys'
    SYNOPSIS = 'Rotate the at-rest encryption master keys.'

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], _args: argparse.Namespace
    ) -> None:
        resp = encryption.rotate_keys(conninfo, credentials)
        assert resp.data is None, f'Unexpected response from key rotation API: {resp}'
        print('Key rotation complete')


class EncryptionGetStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = 'encryption_get_status'
    SYNOPSIS = 'Get at-rest encryption status.'

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], _args: argparse.Namespace
    ) -> None:
        resp = encryption.status(conninfo, credentials)
        print(resp)
