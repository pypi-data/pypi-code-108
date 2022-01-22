import click
import atexit
import threading
import traceback
from time import sleep
from mlsteam.consumer import ApiClient, DiskCache, ConsumerThread


class Track(object):
    def __init__(self,
        track: dict,
        project_uuid: str,
        apiclient: ApiClient,
        background_jobs: list,
        debug: bool
    ):
        self._info = track
        self._project_uuid = project_uuid
        self._lock = threading.RLock()
        self._apiclient = apiclient
        self._background_jobs = background_jobs
        self._debug = debug
        self._waiting_cond = threading.Condition(lock=self._lock)
        self._cache = DiskCache(f"{project_uuid}/{track['name']}", debug=self._debug)
        self._consumer = ConsumerThread(
            self._lock,
            self._cache,
            self._apiclient,
            project_uuid,
            track['bucket_name'],
            sleep_time=1
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is not None:
            traceback.print_exception(exc_type, exc_val, exc_tb)
        self.stop()

    def __getitem__(self, key):
        return Handler(self, self._cache, key)

    def __setitem__(self, key, value):
        self.__getitem__(key).assign(value)

    def lock(self):
        return self._lock

    def start(self):
        atexit.register(self._shutdown_hook)
        self._consumer.start()

    def stop(self):
        if self._consumer.is_running():
            self._consumer.disable_sleep()
            self._consumer.wake_up()
            self._wait_queu_empty(self._cache)
            self._consumer.interrupt()
            click.echo("mlsteam-client stopped")
        self._consumer.join()

    def _wait_queu_empty(self, cache: "DiskCache"):
        while True:
            qsize = cache.queue_size()
            if qsize == 0:
                break
            sleep(1)

    def _shutdown_hook(self):
        self.stop()

    def tags_set(self, tags: list):
        self._apiclient.add_tags(self._project_uuid, self._info['id'], tags)


class Handler(object):
    def __init__(self, track: Track, cache: DiskCache, key: str):
        self._track = track
        self._cache = cache
        self._key = key

    def __getitem__(self, key):
        return Handler(self._track, self._cache, self._key)

    def __setitem__(self, key, value):
        self[key].assign(value)

    def assign(self, value):
        with self._track.lock():
            self._cache.assign(self._key, value)

    def log(self, value):
        with self._track.lock():
            self._cache.log(self._key, value)
