# Copyright 2021 Syeam Bin Abdullah <syeamtechdemon@gmail.com>
#
# This file is part of duplicity.
#
# Duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# Duplicity is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with duplicity; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

from builtins import str
import os
import shutil
import requests
import json
import urllib.request
from pathlib import Path
import time

import duplicity.backend
from duplicity import log
from duplicity import util
from duplicity.errors import BackendException


class SlateBackend(duplicity.backend.Backend):
    u"""
    Backend for Slate
    """
    def __init__(self, parsed_url):
        duplicity.backend.Backend.__init__(self, parsed_url)
        log.Debug(u"loading slate backend...")
        if u'SLATE_API_KEY' not in os.environ.keys():
            raise BackendException(
                u'''You must set an environment variable SLATE_API_KEY
                as the value of your slate API key''')
        else:
            self.key = os.environ[u'SLATE_API_KEY']

        if u'SLATE_SSL_VERIFY' not in os.environ.keys():
            self.verify = True
        else:
            if u'SLATE_SSL_VERIFY' == u'0':
                self.verify = False
            else:
                self.verify = True

        data = json.dumps({u'data': {u'private': u'true'}})
        headers = {
            u'Content-Type': u'application/json',
            u'Authorization': u'Basic ' + self.key
        }

        response = requests.post(
            u'https://slate.host/api/v1/get',
            data=data,
            headers=headers,
            verify=self.verify)
        if not response.ok:
            raise BackendException(u"Slate backend requires a valid API key")

        self.slate_id = parsed_url.geturl().split(u'/')[-1]

    def _put(self, source_path, remote_filename):
        data = json.dumps({u'data': {u'private': u'true'}})
        headers = {
            u'Content-Type': u'application/json',
            u'Authorization': u'Basic ' + self.key
        }

        log.Debug(u"source_path.name: " + str(source_path.name))
        log.Debug(u"remote_filename: " + remote_filename.decode(u"utf8"))
        rem_filename = str(util.fsdecode(remote_filename))

        src = Path(util.fsdecode(source_path.name))
        if str(src.name).startswith(u"mktemp"):
            log.Debug(u"copying temp file for upload")
            src = shutil.move(str(src), str(src.with_name(rem_filename)))

        log.Debug(u"response")
        headers = {
            u'Authorization': u'Basic ' + self.key
        }
        files = {rem_filename: open(str(src), u'rb')}
        log.Debug(u"-------------------FILECHECK: " + str(files.keys()))
        response = requests.post(
            url=u'https://uploads.slate.host/api/public/' + self.slate_id,
            files=files,
            headers=headers)
        log.Debug(u"response handled")

        if not response.ok:
            raise BackendException(u"An error occured whilst attempting to upload a file: %s" % (response))
        else:
            log.Debug(u"File successfully uploaded to slate with id:" + self.slate_id)

        if str(src).endswith(u"difftar.gpg"):
            os.remove(str(src))

    def _list(self):

        # Checks if a specific slate has been selected, otherwise lists all slates
        log.Debug(u"Slate ID: %s" % (self.slate_id))
        data = json.dumps({u'data': {u'private': u'true'}})
        headers = {
            u'Content-Type': u'application/json',
            u'Authorization': u'Basic ' + self.key
        }
        response = requests.post(
            u'https://slate.host/api/v1/get',
            data=data,
            headers=headers,
            verify=self.verify)

        if not response.ok:
            raise BackendException(u"Slate backend requires a valid API key")

        slates = response.json()[u'slates']
        # log.Debug("SLATES:\n%s"%(slates))
        file_list = []
        for slate in slates:
            if slate[u'id'] == self.slate_id:
                files = slate[u'data'][u'objects']
                for f in files:
                    file_list.append(f[u'name'])
            else:
                log.Debug(u"Could not find slate with id: " + self.slate_id)

        return file_list

    def _get(self, remote_filename, local_path):
        # Downloads chosen file from IPFS by parsing its cid
        found = False
        data = json.dumps({u'data': {u'private': u'true'}})
        headers = {
            u'Content-Type': u'application/json',
            u'Authorization': u'Basic ' + self.key
        }

        response = requests.post(
            u'https://slate.host/api/v1/get',
            data=data,
            headers=headers,
            verify=self.verify)

        slates = response.json()[u'slates']
        # file_list = self._list()

        # if remote_filename not in file_list:
        #     raise BackendException(u"The chosen file does not exist in the chosen slate")

        for slate in slates:
            if slate[u'id'] == self.slate_id:
                found = True
                for obj in slate[u'data'][u'objects']:
                    if obj[u'name'] == remote_filename.decode(u"utf8"):
                        cid = obj[u'url'].split(u"/")[-1]
                        break
                    else:
                        raise BackendException(
                            u"The file '"
                            + remote_filename.decode(u"utf8")
                            + u"' could not be found in the specified slate")

        if not found:
            raise BackendException(u"A slate with id " + self.slate_id + u" does not exist")

        try:
            urllib.request.urlretrieve(u'http://ipfs.io/ipfs/%s' % (cid), util.fsdecode(local_path.name))
            log.Debug(u'Downloaded file with cid: %s' % (cid))
        except NameError as e:
            raise BackendException(u"Couldn't download file")


duplicity.backend.register_backend(u'slate', SlateBackend)
