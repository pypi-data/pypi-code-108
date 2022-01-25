# Copyright (c) 2019, IRIS-HEP
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import json
from datetime import datetime
import requests
import logging


MAX_RETRIES = 3


class ServiceXAdapter:
    def __init__(self, endpoint, file_prefix=None):
        self.endpoint = endpoint
        self.file_prefix = file_prefix

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())

    def post_status_update(self, status_msg, severity="info"):
        success = False
        attempts = 0
        while not success and attempts < MAX_RETRIES:
            try:
                requests.post(self.endpoint + "/status", data={
                    "timestamp": datetime.now().isoformat(),
                    "source": "DID Finder",
                    "severity": severity,
                    "info": status_msg
                })
                success = True
            except requests.exceptions.ConnectionError:
                self.logger.exception(f'Connection error to ServiceX App. Will retry '
                                      f'(try {attempts} out of {MAX_RETRIES}')
                attempts += 1
        if not success:
            self.logger.error(f'After {attempts} tries, failed to send ServiceX App a status '
                              f'message: {str(status_msg)} - Ignoring error.')

    def _prefix_file(self, file_path):
        return file_path if not self.file_prefix else self.file_prefix+file_path

    def put_file_add(self, file_info):
        success = False
        attempts = 0
        while not success and attempts < MAX_RETRIES:
            try:
                mesg = {
                    "timestamp": datetime.now().isoformat(),
                    "file_path": self._prefix_file(file_info['file_path']),
                    'adler32': file_info['adler32'],
                    'file_size': file_info['file_size'],
                    'file_events': file_info['file_events']
                }
                requests.put(self.endpoint + "/files", json=mesg)
                self.logger.info(f"Metric: {json.dumps(mesg)}")
                success = True
            except requests.exceptions.ConnectionError:
                self.logger.exception(f'Connection error to ServiceX App. Will retry '
                                      f'(try {attempts} out of {MAX_RETRIES}')
                attempts += 1
        if not success:
            self.logger.error(f'After {attempts} tries, failed to send ServiceX App a put_file '
                              f'message: {str(file_info)} - Ignoring error.')

    def post_transform_start(self):
        success = False
        attempts = 0
        while not success and attempts < MAX_RETRIES:
            try:
                requests.post(self.endpoint + "/start")
                success = True
            except requests.exceptions.ConnectionError:
                self.logger.exception(f'Connection error to ServiceX App. Will retry '
                                      f'(try {attempts} out of {MAX_RETRIES}')
                attempts += 1
        if not success:
            self.logger.error(f'After {attempts} tries, failed to send ServiceX App a  '
                              f'transform start message - Ignoring error.')

    def put_fileset_complete(self, summary):
        success = False
        attempts = 0
        while not success and attempts < MAX_RETRIES:
            try:
                requests.put(self.endpoint + "/complete", json=summary)
                success = True
            except requests.exceptions.ConnectionError:
                self.logger.exception(f'Connection error to ServiceX App. Will retry '
                                      f'(try {attempts} out of {MAX_RETRIES}')
                attempts += 1
        if not success:
            self.logger.error(f'After {attempts} tries, failed to send ServiceX App a put_file '
                              f'message: {str(summary)} - Ignoring error.')
