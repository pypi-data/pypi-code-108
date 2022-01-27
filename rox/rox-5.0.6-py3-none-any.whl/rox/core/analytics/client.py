import numbers
import atexit
import os

from dateutil.tz import tzutc
from six import string_types

from rox.core.analytics.utils import guess_timezone, clean
from rox.core.analytics.consumer import Consumer
from rox.core.analytics.version import VERSION
from rox.core.logging.logging import Logging

try:
    import queue
except:
    import Queue as queue


ID_TYPES = (numbers.Number, string_types)


class Client(object):
    """Create a new Segment client."""
    def __init__(self, device_properties, write_key=None, host=None, debug=False, max_queue_size=100000,
                 send=True, on_error=None, upload_size=200, upload_interval=0.5,
                 gzip=False, max_retries=10):
        require('write_key', write_key, string_types)

        try:
            max_queue_size = int(os.getenv('rox.analytics.max_queue_size'))
        except ValueError:
            pass
        except TypeError:
            pass

        try:
            upload_size = int(os.getenv('rox.analytics.max_batch_size'))
        except ValueError:
            pass
        except TypeError:
            pass

        self.queue = queue.Queue(max_queue_size)
        self.consumer = Consumer(device_properties, self.queue, write_key, host=host, on_error=on_error,
                                 upload_size=upload_size, upload_interval=upload_interval,
                                 gzip=gzip, retries=max_retries)
        self.write_key = write_key
        self.on_error = on_error
        self.debug = debug
        self.send = send

        # if we've disabled sending, just don't start the consumer
        if send:
            # On program exit, allow the consumer thread to exit cleanly.
            # This prevents exceptions and a messy shutdown when the interpreter is
            # destroyed before the daemon thread finishes execution. However, it
            # is *not* the same as flushing the queue! To guarantee all messages
            # have been delivered, you'll still need to call flush().
            # atexit.register(self.join)
            self.consumer.start()

    def track(self, event):
        return self._enqueue(event)

    def _enqueue(self, msg):
        """Push a new `msg` onto the queue, return `(success, msg)`"""

        msg = clean(msg)
        Logging.get_logger().debug('queueing: %s' % msg)

        # if send is False, return msg as if it was successfully queued
        if not self.send:
            return True, msg

        try:
            self.queue.put(msg, block=False)
            Logging.get_logger().debug('enqueued %s.' % msg['type'])
            return True, msg
        except queue.Full:
            Logging.get_logger().warn('analytics-python queue is full')
            return False, msg

    def flush(self):
        """Forces a flush from the internal queue to the server"""
        queue = self.queue
        size = queue.qsize()
        queue.join()
        # Note that this message may not be precise, because of threading.
        Logging.get_logger().debug('successfully flushed about %s items.' % size)

    def join(self):
        """Ends the consumer thread once the queue is empty. Blocks execution until finished"""
        self.consumer.pause()
        try:
            self.consumer.join()
        except RuntimeError:
            # consumer thread has not started
            pass

    def shutdown(self):
        """Flush all messages and cleanly shutdown the client"""
        self.flush()
        self.join()


def require(name, field, data_type):
    """Require that the named `field` has the right `data_type`"""
    if not isinstance(field, data_type):
        msg = '{0} must have {1}, got: {2}'.format(name, data_type, field)
        raise AssertionError(msg)

def stringify_id(val):
    if val is None:
        return None
    if isinstance(val, string_types):
        return val
    return str(val)
