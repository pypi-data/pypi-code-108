# -*- coding: future_fstrings -*-
import json
import threading
import datetime
import urllib

from sumoappclient.common.errors import StoreException
from sumoappclient.sumoclient.httputils import ClientMixin
from sumoappclient.provider.factory import ProviderFactory
from sumoappclient.omnistorage.base import KeyValueStorage


class CToCKVStorage(KeyValueStorage):

    def setup(self, name, force_create=False, c2c_base_url='', *args, **kwargs):
        self.ctoc_state_endpoint = c2c_base_url + "/state"
        self.lock = threading.RLock()
        # https://stackoverflow.com/questions/18188044/is-the-session-object-from-pythons-requests-library-thread-safe
        # Session are thread safe if threads do not modify session object
        self.session = ClientMixin.get_new_session()
        if force_create:
            self.destroy()
        self.inmemory_store = self._get()

    def _get_actual_key(self, key):
        ''' in shelve keys needs to be string therefore converting them to strings
            could have used not instance(key, str) but it's better to be explicit(need to test what will happen in case of objects as keys)
        '''
        if isinstance(key, (float, int, datetime.datetime)):
            return str(key)
        return key

    def get(self, key, default=None):
        key = self._get_actual_key(key)
        value = None
        has_key = False
        with self.lock:
            value = self.inmemory_store.get(key, None)
        if not value:
            self.log.warning("Key %s not Found" % key)
            return default
        self.log.debug(f'''Fetched Item {key}''')
        return value

    def set(self, key, value):
        key = self._get_actual_key(key)
        with self.lock:
            self.inmemory_store[key] = value
            self._save()
        self.log.debug(f'''Saved Item {key}''')

    def delete(self, key):
        key = self._get_actual_key(key)
        with self.lock:
            if key in self.inmemory_store:
                del self.inmemory_store[key]
                self._save()
        self.log.debug(f'''Deleted Item {key}''')

    def has_key(self, key):
        key = self._get_actual_key(key)
        with self.lock:
            flag = key in self.inmemory_store
        return flag

    def destroy(self):
        self.log.debug("resetting state")
        with self.lock:
            self.inmemory_store = {}
            self._save()

    def _get(self):

        status, data = ClientMixin.make_request(self.ctoc_state_endpoint, "get", session=self.session, logger=self.log)

        if status:
            if data["state"]:
                cfg = json.loads(data["state"])
                self.log.debug(f"Initialized state {cfg}")
            else:
                cfg = {}
            del data
            # Todo whether int/float/decimal conversion are handled
            return cfg
        else:
            raise StoreException(f'''GETStateAPIError: {data}''')

    def _save(self):

        status, data = ClientMixin.make_request(self.ctoc_state_endpoint, "post", session=self.session, logger=self.log,
                                                data=json.dumps({"state": json.dumps(self.inmemory_store)}),
                                                headers={"Content-Type": "application/json"})
        if not status:
            raise StoreException(f'''POSTStateAPIError: {data}''')

    def acquire_lock(self, key):
        return True

    def release_lock(self, key):
        return True

    def release_lock_on_expired_key(self, key, expiry_min=15):
        return True

    @property
    def env(self):
        return "ctoc"

    def close(self):
        self.session.close()


if __name__ == "__main__":

    key = "abc"
    value = {"name": "Himanshu"}
    cli = ProviderFactory.get_provider("ctoc")
    kvstore = cli.get_storage("keyvalue", name='kvstore', force_create=True)

    cli2 = ProviderFactory.get_provider("onprem")
    kvstore2 = cli.get_storage("keyvalue", name='kvstore', force_create=True)

    kvstore.set(key, value)
    assert(kvstore.get(key) == value)
    assert(kvstore.has_key(key) == True)
    kvstore.delete(key)
    assert(kvstore.has_key(key) == False)
    assert(kvstore.acquire_lock(key) == True)
    assert(kvstore2.acquire_lock(key) == True)
    assert(kvstore.acquire_lock("blah") == True)
    assert(kvstore.release_lock(key) == True)
    assert(kvstore.release_lock(key) == False)
    assert(kvstore.release_lock("blahblah") == False)
    kvstore.destroy()
