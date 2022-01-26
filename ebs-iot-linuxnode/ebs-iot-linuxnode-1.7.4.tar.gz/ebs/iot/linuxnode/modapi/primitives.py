

import os
import shutil
import pickle
import pqueue
from twisted.internet.defer import succeed


class ApiPersistentActionQueue(object):
    def __init__(self, api_engine, prefix=None):
        self._prefix = prefix
        self._api_engine = api_engine
        self._api_queue = None

    def process(self):
        while True:
            try:
                api_func_name, args = self.api_queue.get_nowait()
                self._api_engine.log.info(
                    "Executing persistent API action : {func_name}, {args}",
                    func_name=api_func_name, args=args
                )
                getattr(self._api_engine, api_func_name)(*args)
            except pqueue.Empty:
                break
            except pickle.UnpicklingError:
                self._api_queue = None
                shutil.rmtree(self._api_queue_dir, ignore_errors=True)
                self._api_engine.log.warn("API persistent queue pickle corrupted. Clearing.")
                break
            except Exception as e:
                # TODO Remove this broad exception
                self._api_queue = None
                shutil.rmtree(self._api_queue_dir, ignore_errors=True)
                self._api_engine.log.warn("Unhandled error in api queue get. \n {} ".format(e))
                break
        return succeed(True)

    def enqueue_action(self, api_func_name, *args):
        self._api_engine.log.info(
            "Enqueuing API action to disk : {func_name}, {args}",
            func_name=api_func_name, args=args
        )
        self.api_queue.put((api_func_name, args))

    @property
    def api_queue(self):
        if not self._api_queue:
            self._api_queue = pqueue.Queue(
                self._api_queue_dir,
                tempdir=os.path.join(self._api_queue_dir, 'tmp')
            )
        return self._api_queue

    @property
    def _api_queue_dir(self):
        dir_name = 'apiqueue'
        if self._prefix:
            dir_name = '-'.join([self._prefix, dir_name])
        _api_queue_dir = os.path.join(self._api_engine.cache_dir, dir_name)
        _api_queue_tmp_dir = os.path.join(_api_queue_dir, 'tmp')
        os.makedirs(_api_queue_tmp_dir, exist_ok=True)
        return _api_queue_dir
