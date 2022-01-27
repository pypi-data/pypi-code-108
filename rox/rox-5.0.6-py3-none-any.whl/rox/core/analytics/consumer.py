from threading import Thread
import monotonic
import backoff
import json

from rox.core.analytics.version import VERSION
from rox.core.analytics.request import post, APIError, DatetimeSerializer
from rox.core.consts import property_type
from rox.core.logging.logging import Logging
from rox.core.utils.time_utils import now_in_unix_milliseconds

try:
    from queue import Empty
except ImportError:
    from Queue import Empty

MAX_MSG_SIZE = 32 << 10

# Our servers only accept batches less than 500KB. Here limit is set slightly
# lower to leave space for extra data that will be added later, eg. "sentAt".
BATCH_SIZE_LIMIT = 475000


class Consumer(Thread):
    """Consumes the messages from the client's queue."""
    def __init__(self, device_properties, queue, write_key, upload_size=100, host=None, on_error=None,
                 upload_interval=0.5, gzip=False, retries=10):
        """Create a consumer thread."""
        Thread.__init__(self)
        # Make consumer a daemon thread so that it doesn't block program exit
        self.daemon = True
        self.upload_size = upload_size
        self.upload_interval = upload_interval
        self.write_key = write_key
        self.device_properties = device_properties
        self.host = host
        self.on_error = on_error
        self.queue = queue
        self.gzip = gzip
        # It's important to set running in the constructor: if we are asked to
        # pause immediately after construction, we might set running to True in
        # run() *after* we set it to False in pause... and keep running forever.
        self.running = True
        self.retries = retries

    def run(self):
        """Runs the consumer."""
        Logging.get_logger().debug('consumer is running...')
        while self.running:
            self.upload()

        Logging.get_logger().debug('consumer exited.')

    def pause(self):
        """Pause the consumer."""
        self.running = False

    def upload(self):
        """Upload the next batch of items, return whether successful."""
        success = False
        batch = self.next()
        if len(batch) == 0:
            return False

        try:
            self.request({
                'analyticsVersion': '1.0.0',
                'sdkVersion': self.device_properties.lib_version,
                'time': now_in_unix_milliseconds(),
                'platform': self.device_properties.get_all_properties()[property_type.PLATFORM.name],
                'rolloutKey': self.device_properties.rollout_key,
                'events': batch
            })
            success = True
        except Exception as e:
            Logging.get_logger().error('error uploading', e)
            success = False
            if self.on_error:
                self.on_error(e, batch)
        finally:
            # mark items as acknowledged from queue
            for item in batch:
                self.queue.task_done()
            return success

    def next(self):
        """Return the next batch of items to upload."""
        queue = self.queue
        items = []

        start_time = monotonic.monotonic()
        total_size = 0

        while len(items) < self.upload_size:
            elapsed = monotonic.monotonic() - start_time
            if elapsed >= self.upload_interval:
                break
            try:
                item = queue.get(block=True, timeout=self.upload_interval - elapsed)
                item_size = len(json.dumps(item, cls=DatetimeSerializer).encode())
                if item_size > MAX_MSG_SIZE:
                    Logging.get_logger().error('Item exceeds 32kb limit, dropping. (%s)' % str(item))
                    continue
                items.append(item)
                total_size += item_size
                if total_size >= BATCH_SIZE_LIMIT:
                    Logging.get_logger().debug('hit batch size limit (size: %d)' % total_size)
                    break
            except Empty:
                break

        return items

    def request(self, batch):
        """Attempt to upload the batch and retry before raising an error """

        def fatal_exception(exc):
            if isinstance(exc, APIError):
                # retry on server errors and client errors with 429 status code (rate limited),
                # don't retry on other client errors
                return (400 <= exc.status < 500) and exc.status != 429
            else:
                # retry on all other errors (eg. network)
                return False

        @backoff.on_exception(backoff.expo, Exception, max_tries=self.retries + 1, giveup=fatal_exception)
        def send_request():
            post(self.device_properties, self.write_key, self.host, gzip=self.gzip, batch=batch)

        send_request()
