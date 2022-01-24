# Copyright 2021 BMW Group
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

import logging
from contextlib import contextmanager
from urllib.parse import quote_plus

from kazoo.protocol.states import KazooState

from zuul.zk.exceptions import LockException
from zuul.zk.vendor.lock import Lock, ReadLock, WriteLock

LOCK_ROOT = "/zuul/locks"
TENANT_LOCK_ROOT = f"{LOCK_ROOT}/tenant"
CONNECTION_LOCK_ROOT = f"{LOCK_ROOT}/connection"


class SessionAwareMixin:
    def __init__(self, client, path, identifier=None, extra_lock_patterns=()):
        self._zuul_ephemeral = None
        self._zuul_session_expired = False
        self._zuul_watching_session = False
        super().__init__(client, path, identifier, extra_lock_patterns)

    def acquire(self, blocking=True, timeout=None, ephemeral=True):
        ret = super().acquire(blocking, timeout, ephemeral)
        self._zuul_session_expired = False
        if ret and ephemeral:
            self._zuul_ephemeral = ephemeral
            self.client.add_listener(self._zuul_session_watcher)
            self._zuul_watching_session = True
        return ret

    def release(self):
        if self._zuul_watching_session:
            self.client.remove_listener(self._zuul_session_watcher)
            self._zuul_watching_session = False
        return super().release()

    def _zuul_session_watcher(self, state):
        if state == KazooState.LOST:
            self._zuul_session_expired = True

            # Return true to de-register
            return True

    def is_still_valid(self):
        if not self._zuul_ephemeral:
            return True
        return not self._zuul_session_expired


class SessionAwareLock(SessionAwareMixin, Lock):
    pass


class SessionAwareWriteLock(SessionAwareMixin, WriteLock):
    pass


class SessionAwareReadLock(SessionAwareMixin, ReadLock):
    pass


@contextmanager
def locked(lock, blocking=True, timeout=None):
    if not lock.acquire(blocking=blocking, timeout=timeout):
        raise LockException(f"Failed to acquire lock {lock}")
    try:
        yield lock
    finally:
        try:
            lock.release()
        except Exception:
            log = logging.getLogger("zuul.zk.locks")
            log.exception("Failed to release lock %s", lock)


@contextmanager
def tenant_read_lock(client, tenant_name, blocking=True):
    safe_tenant = quote_plus(tenant_name)
    with locked(
        SessionAwareReadLock(
            client.client,
            f"{TENANT_LOCK_ROOT}/{safe_tenant}"),
        blocking=blocking
    ) as lock:
        yield lock


@contextmanager
def tenant_write_lock(client, tenant_name, blocking=True):
    safe_tenant = quote_plus(tenant_name)
    with locked(
        SessionAwareWriteLock(
            client.client,
            f"{TENANT_LOCK_ROOT}/{safe_tenant}"),
        blocking=blocking
    ) as lock:
        yield lock


@contextmanager
def pipeline_lock(client, tenant_name, pipeline_name, blocking=True):
    safe_tenant = quote_plus(tenant_name)
    safe_pipeline = quote_plus(pipeline_name)
    with locked(
        SessionAwareLock(
            client.client,
            f"/zuul/locks/pipeline/{safe_tenant}/{safe_pipeline}"),
        blocking=blocking
    ) as lock:
        yield lock


@contextmanager
def management_queue_lock(client, tenant_name, blocking=True):
    safe_tenant = quote_plus(tenant_name)
    with locked(
        SessionAwareLock(
            client.client,
            f"/zuul/locks/events/management/{safe_tenant}"),
        blocking=blocking
    ) as lock:
        yield lock


@contextmanager
def trigger_queue_lock(client, tenant_name, blocking=True):
    safe_tenant = quote_plus(tenant_name)
    with locked(
        SessionAwareLock(
            client.client,
            f"/zuul/locks/events/trigger/{safe_tenant}"),
        blocking=blocking
    ) as lock:
        yield lock
