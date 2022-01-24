# Copyright 2018 Red Hat, Inc.
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

import io
import json
import logging
import time
from contextlib import suppress

import cachetools
import kazoo
import paramiko

from zuul.lib import encryption, strings
from zuul.zk import ZooKeeperBase

RSA_KEY_SIZE = 2048


class KeyStorage(ZooKeeperBase):
    log = logging.getLogger("zuul.KeyStorage")
    # /keystorage/connection/orgname
    PREFIX_PATH = "/keystorage/{}/{}"
    # /keystorage/connection/orgname/projectuniqname
    PROJECT_PATH = PREFIX_PATH + "/{}"
    SECRETS_PATH = PROJECT_PATH + "/secrets"
    SSH_PATH = PROJECT_PATH + "/ssh"

    def __init__(self, zookeeper_client, password, backup=None):
        super().__init__(zookeeper_client)
        self.password = password
        self.password_bytes = password.encode("utf-8")

    def _walk(self, root):
        ret = []
        children = self.kazoo_client.get_children(root)
        if children:
            for child in children:
                path = '/'.join([root, child])
                ret.extend(self._walk(path))
        else:
            data, _ = self.kazoo_client.get(root)
            try:
                ret.append((root, json.loads(data)))
            except Exception:
                self.log.error(f"Unable to load keys at {root}")
                # Keep processing exports
        return ret

    def exportKeys(self):
        keys = {}
        for (path, data) in self._walk('/keystorage'):
            self.log.info(f"Exported: {path}")
            keys[path] = data
        return {'keys': keys}

    def importKeys(self, import_data, overwrite):
        for path, data in import_data['keys'].items():
            if not path.startswith('/keystorage'):
                self.log.error(f"Invalid path: {path}")
                return
            data = json.dumps(data, sort_keys=True).encode('utf8')
            try:
                self.kazoo_client.create(path, value=data, makepath=True)
                self.log.info(f"Created key at {path}")
            except kazoo.exceptions.NodeExistsError:
                if overwrite:
                    self.kazoo_client.set(path, value=data)
                    self.log.info(f"Updated key at {path}")
                else:
                    self.log.warning(f"Not overwriting existing key at {path}")

    def getSSHKeysPath(self, connection_name, project_name):
        prefix, name = strings.unique_project_name(project_name)
        key_path = self.SSH_PATH.format(connection_name, prefix, name)
        return key_path

    @cachetools.cached(cache={})
    def getProjectSSHKeys(self, connection_name, project_name):
        """Return the public and private keys"""
        key = self._getSSHKey(connection_name, project_name)
        if key is None:
            self.log.info("Generating a new SSH key for %s/%s",
                          connection_name, project_name)
            key = paramiko.RSAKey.generate(bits=RSA_KEY_SIZE)
            key_version = 0
            key_created = int(time.time())

            try:
                self._storeSSHKey(connection_name, project_name, key,
                                  key_version, key_created)
            except kazoo.exceptions.NodeExistsError:
                # Handle race condition between multiple schedulers
                # creating the same SSH key.
                key = self._getSSHKey(connection_name, project_name)

        with io.StringIO() as o:
            key.write_private_key(o)
            private_key = o.getvalue()
        public_key = "ssh-rsa {}".format(key.get_base64())

        return private_key, public_key

    def loadProjectSSHKeys(self, connection_name, project_name):
        """Return the complete internal data structure"""
        key_path = self.getSSHKeysPath(connection_name, project_name)
        try:
            data, _ = self.kazoo_client.get(key_path)
            return json.loads(data)
        except kazoo.exceptions.NoNodeError:
            return None

    def saveProjectSSHKeys(self, connection_name, project_name, keydata):
        """Store the complete internal data structure"""
        key_path = self.getSSHKeysPath(connection_name, project_name)
        data = json.dumps(keydata, sort_keys=True).encode("utf-8")
        self.kazoo_client.create(key_path, value=data, makepath=True)

    def deleteProjectSSHKeys(self, connection_name, project_name):
        """Delete the complete internal data structure"""
        key_path = self.getSSHKeysPath(connection_name, project_name)
        with suppress(kazoo.exceptions.NoNodeError):
            self.kazoo_client.delete(key_path)

    def _getSSHKey(self, connection_name, project_name):
        """Load and return the public and private keys"""
        keydata = self.loadProjectSSHKeys(connection_name, project_name)
        if keydata is None:
            return None
        encrypted_key = keydata['keys'][0]["private_key"]
        with io.StringIO(encrypted_key) as o:
            return paramiko.RSAKey.from_private_key(o, self.password)

    def _storeSSHKey(self, connection_name, project_name, key,
                     version, created):
        """Create the internal data structure from the key and store it"""
        # key is an rsa key object
        with io.StringIO() as o:
            key.write_private_key(o, self.password)
            private_key = o.getvalue()
        keys = [{
            "version": version,
            "created": created,
            "private_key": private_key,
        }]
        keydata = {
            'schema': 1,
            'keys': keys
        }
        self.saveProjectSSHKeys(connection_name, project_name, keydata)

    def getProjectSecretsKeysPath(self, connection_name, project_name):
        prefix, name = strings.unique_project_name(project_name)
        key_path = self.SECRETS_PATH.format(connection_name, prefix, name)
        return key_path

    @cachetools.cached(cache={})
    def getProjectSecretsKeys(self, connection_name, project_name):
        """Return the public and private keys"""
        pem_private_key = self._getSecretsKey(connection_name, project_name)
        if pem_private_key is None:
            self.log.info("Generating a new secrets key for %s/%s",
                          connection_name, project_name)
            private_key, public_key = encryption.generate_rsa_keypair()
            pem_private_key = encryption.serialize_rsa_private_key(
                private_key, self.password_bytes)
            key_version = 0
            key_created = int(time.time())

            try:
                self._storeSecretsKey(connection_name, project_name,
                                      pem_private_key, key_version,
                                      key_created)
            except kazoo.exceptions.NodeExistsError:
                # Handle race condition between multiple schedulers
                # creating the same secrets key.
                pem_private_key = self._getSecretsKey(
                    connection_name, project_name)

        private_key, public_key = encryption.deserialize_rsa_keypair(
            pem_private_key, self.password_bytes)

        return private_key, public_key

    def loadProjectsSecretsKeys(self, connection_name, project_name):
        """Return the complete internal data structure"""
        key_path = self.getProjectSecretsKeysPath(
            connection_name, project_name)
        try:
            data, _ = self.kazoo_client.get(key_path)
            return json.loads(data)
        except kazoo.exceptions.NoNodeError:
            return None

    def saveProjectsSecretsKeys(self, connection_name, project_name, keydata):
        """Store the complete internal data structure"""
        key_path = self.getProjectSecretsKeysPath(
            connection_name, project_name)
        data = json.dumps(keydata, sort_keys=True).encode("utf-8")
        self.kazoo_client.create(key_path, value=data, makepath=True)

    def deleteProjectsSecretsKeys(self, connection_name, project_name):
        """Delete the complete internal data structure"""
        key_path = self.getProjectSecretsKeysPath(
            connection_name, project_name)
        with suppress(kazoo.exceptions.NoNodeError):
            self.kazoo_client.delete(key_path)

    def _getSecretsKey(self, connection_name, project_name):
        """Load and return the private key"""
        keydata = self.loadProjectsSecretsKeys(
            connection_name, project_name)
        if keydata is None:
            return None
        return keydata['keys'][0]["private_key"].encode("utf-8")

    def _storeSecretsKey(self, connection_name, project_name, key,
                         version, created):
        """Create the internal data structure from the key and store it"""
        # key is a pem-encoded (base64) private key stored in bytes
        keys = [{
            "version": version,
            "created": created,
            "private_key": key.decode("utf-8"),
        }]
        keydata = {
            'schema': 1,
            'keys': keys
        }
        self.saveProjectsSecretsKeys(connection_name, project_name, keydata)

    def deleteProjectDir(self, connection_name, project_name):
        prefix, name = strings.unique_project_name(project_name)
        project_path = self.PROJECT_PATH.format(connection_name, prefix, name)
        prefix_path = self.PREFIX_PATH.format(connection_name, prefix)
        try:
            self.kazoo_client.delete(project_path)
        except kazoo.exceptions.NotEmptyError:
            # Rely on delete only deleting empty paths by default
            self.log.warning(f"Not deleting non empty path {project_path}")
        except kazoo.exceptions.NoNodeError:
            # Already deleted
            pass
        try:
            self.kazoo_client.delete(prefix_path)
        except kazoo.exceptions.NotEmptyError:
            # Normal for the org to remain due to other projects existing.
            pass
        except kazoo.exceptions.NoNodeError:
            # Already deleted
            pass
