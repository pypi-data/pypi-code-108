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

import json
import time
import contextlib
import zlib

from kazoo.exceptions import (
    KazooException, NodeExistsError, NoNodeError, ZookeeperError)

from zuul.zk import sharding
from zuul.zk.exceptions import InvalidObjectError


class ZKContext:
    def __init__(self, zk_client, lock, stop_event, log):
        self.client = zk_client.client
        self.lock = lock
        self.stop_event = stop_event
        self.log = log

    def sessionIsValid(self):
        return ((not self.lock or self.lock.is_still_valid()) and
                (not self.stop_event or not self.stop_event.is_set()))


class LocalZKContext:
    """A Local ZKContext that means don't actually write anything to ZK"""

    def __init__(self, log):
        self.client = None
        self.lock = None
        self.stop_event = None
        self.log = log

    def sessionIsValid(self):
        return True


class ZKObject:
    _retry_interval = 5

    # Implementations of these two methods are required
    def getPath(self):
        """Return the path to save this object in ZK

        :returns: A string representation of the Znode path
        """
        raise NotImplementedError()

    def serialize(self):
        """Implement this method to return the data to save in ZK.

        :returns: A byte string
        """
        raise NotImplementedError()

    # This should work for most classes
    def deserialize(self, data, context):
        """Implement this method to convert serialized data into object
        attributes.

        :param bytes data: A byte string to deserialize
        :param ZKContext context: A ZKContext object with the current
            ZK session and lock.

        :returns: A dictionary of attributes and values to be set on
        the object.
        """
        return json.loads(data.decode('utf-8'))

    # These methods are public and shouldn't need to be overridden
    def updateAttributes(self, context, **kw):
        """Update attributes on this object and save to ZooKeeper

        Instead of using attribute assignment, call this method to
        update attributes on this object.  It will update the local
        values and also write out the updated object to ZooKeeper.

        :param ZKContext context: A ZKContext object with the current
            ZK session and lock.  Be sure to acquire the lock before
            calling methods on this object.  This object will validate
            that the lock is still valid before writing to ZooKeeper.

        All other parameters are keyword arguments which are
        attributes to be set.  Set as many attributes in one method
        call as possible for efficient network use.
        """
        old = self.__dict__.copy()
        self._set(**kw)
        serial = self._trySerialize(context)
        if hash(serial) != getattr(self, '_zkobject_hash', None):
            try:
                self._save(context, serial)
            except Exception:
                # Roll back our old values if we aren't able to update ZK.
                self._set(**old)
                raise

    @contextlib.contextmanager
    def activeContext(self, context):
        if self._active_context:
            raise RuntimeError(
                f"Another context is already active {self._active_context}")
        try:
            old = self.__dict__.copy()
            self._set(_active_context=context)
            yield
            serial = self._trySerialize(context)
            if hash(serial) != getattr(self, '_zkobject_hash', None):
                try:
                    self._save(context, serial)
                except Exception:
                    # Roll back our old values if we aren't able to update ZK.
                    self._set(**old)
                    raise
        finally:
            self._set(_active_context=None)

    @classmethod
    def new(klass, context, **kw):
        """Create a new instance and save it in ZooKeeper"""
        obj = klass()
        obj._set(**kw)
        data = obj._trySerialize(context)
        obj._save(context, data, create=True)
        return obj

    @classmethod
    def fromZK(klass, context, path, **kw):
        """Instantiate a new object from data in ZK"""
        obj = klass()
        obj._set(**kw)
        obj._load(context, path=path)
        return obj

    def refresh(self, context):
        """Update data from ZK"""
        self._load(context)

    def _trySerialize(self, context):
        if isinstance(context, LocalZKContext):
            return b''
        try:
            return self.serialize()
        except Exception:
            # A higher level must handle this exception, but log
            # ourself here so we know what object triggered it.
            context.log.error(
                "Exception serializing ZKObject %s", self)
            raise

    def delete(self, context):
        path = self.getPath()
        while context.sessionIsValid():
            try:
                context.client.delete(path, recursive=True)
                return
            except ZookeeperError:
                # These errors come from the server and are not
                # retryable.  Connection errors are KazooExceptions so
                # they aren't caught here and we will retry.
                context.log.error(
                    "Exception deleting ZKObject %s at %s", self, path)
                raise
            except KazooException:
                context.log.exception(
                    "Exception deleting ZKObject %s, will retry", self)
                time.sleep(self._retry_interval)
        raise Exception("ZooKeeper session or lock not valid")

    # Private methods below

    def __init__(self):
        # Don't support any arguments in constructor to force us to go
        # through a save or restore path.
        super().__init__()
        self._set(_active_context=None)

    def _load(self, context, path=None):
        if path is None:
            path = self.getPath()
        while context.sessionIsValid():
            try:
                compressed_data, zstat = context.client.get(path)
                self._set(_zkobject_hash=None)
                try:
                    data = zlib.decompress(compressed_data)
                except zlib.error:
                    # Fallback for old, uncompressed data
                    data = compressed_data
                self._set(**self.deserialize(data, context))
                self._set(_zstat=zstat,
                          _zkobject_hash=hash(data))
                return
            except ZookeeperError:
                # These errors come from the server and are not
                # retryable.  Connection errors are KazooExceptions so
                # they aren't caught here and we will retry.
                context.log.error(
                    "Exception loading ZKObject %s at %s", self, path)
                raise
            except KazooException:
                context.log.exception(
                    "Exception loading ZKObject %s at %s, will retry",
                    self, path)
                time.sleep(5)
            except Exception:
                # A higher level must handle this exception, but log
                # ourself here so we know what object triggered it.
                context.log.error(
                    "Exception loading ZKObject %s at %s", self, path)
                raise
        raise Exception("ZooKeeper session or lock not valid")

    def _save(self, context, data, create=False):
        if isinstance(context, LocalZKContext):
            return
        path = self.getPath()
        while context.sessionIsValid():
            try:
                compressed_data = zlib.compress(data)
                if create:
                    real_path, zstat = context.client.create(
                        path, compressed_data, makepath=True,
                        include_data=True)
                else:
                    zstat = context.client.set(path, compressed_data,
                                               version=self._zstat.version)
                self._set(_zstat=zstat,
                          _zkobject_hash=hash(data))
                return
            except ZookeeperError:
                # These errors come from the server and are not
                # retryable.  Connection errors are KazooExceptions so
                # they aren't caught here and we will retry.
                context.log.error(
                    "Exception saving ZKObject %s at %s", self, path)
                raise
            except KazooException:
                context.log.exception(
                    "Exception saving ZKObject %s at %s, will retry",
                    self, path)
                time.sleep(self._retry_interval)
        raise Exception("ZooKeeper session or lock not valid")

    def __setattr__(self, name, value):
        if self._active_context:
            super().__setattr__(name, value)
        else:
            raise Exception("Unable to modify ZKObject %s" %
                            (repr(self),))

    def _set(self, **kw):
        for name, value in kw.items():
            super().__setattr__(name, value)


class ShardedZKObject(ZKObject):
    # If the node exists when we create we normally error, unless this
    # is set, in which case we proceed and truncate.
    truncate_on_create = False
    # Normally we delete nodes which have syntax errors, but the
    # pipeline summary is read without a write lock, so those are
    # expected.  Don't delete them in that case.
    delete_on_error = True

    def _load(self, context, path=None):
        if path is None:
            path = self.getPath()
        while context.sessionIsValid():
            try:
                self._set(_zkobject_hash=None)
                with sharding.BufferedShardReader(
                        context.client, path) as stream:
                    data = stream.read()
                if not data and context.client.exists(path) is None:
                    raise NoNodeError
                self._set(**self.deserialize(data, context))
                self._set(_zkobject_hash=hash(data))
                return
            except ZookeeperError:
                # These errors come from the server and are not
                # retryable.  Connection errors are KazooExceptions so
                # they aren't caught here and we will retry.
                context.log.error(
                    "Exception loading ZKObject %s at %s", self, path)
                raise
            except KazooException:
                context.log.exception(
                    "Exception loading ZKObject %s at %s, will retry",
                    self, path)
                time.sleep(5)
            except Exception as exc:
                # A higher level must handle this exception, but log
                # ourself here so we know what object triggered it.
                context.log.error(
                    "Exception loading ZKObject %s at %s", self, path)
                if self.delete_on_error:
                    self.delete(context)
                raise InvalidObjectError from exc
        raise Exception("ZooKeeper session or lock not valid")

    def _save(self, context, data, create=False):
        if isinstance(context, LocalZKContext):
            return
        path = self.getPath()
        while context.sessionIsValid():
            try:
                if (create and
                    not self.truncate_on_create and
                    context.client.exists(path) is not None):
                    raise NodeExistsError
                with sharding.BufferedShardWriter(
                        context.client, path) as stream:
                    stream.truncate(0)
                    stream.write(data)
                self._set(_zkobject_hash=hash(data))
                return
            except ZookeeperError:
                # These errors come from the server and are not
                # retryable.  Connection errors are KazooExceptions so
                # they aren't caught here and we will retry.
                context.log.error(
                    "Exception saving ZKObject %s at %s", self, path)
                raise
            except KazooException:
                context.log.exception(
                    "Exception saving ZKObject %s at %s, will retry",
                    self, path)
                time.sleep(self._retry_interval)
        raise Exception("ZooKeeper session or lock not valid")
