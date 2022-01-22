import os
import logging
import socket
import flask

# get ip address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('8.8.8.8', 53))
ip = s.getsockname()[0]
s.close()

# gunicorn worker class
worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "sync")


class HostAddressFilter(logging.Filter):
    """Add host address to logging.format
    """

    def filter(self, record):
        if "HOSTNAME" in os.environ:
            record.hostname = os.environ.get("HOSTNAME")
            return True
        record.hostname = ip
        return True


class RequestAddressFilter(logging.Filter):
    """Add request address to logging.format, "127.0.0.1" for non-flask scenario
    """

    def filter(self, record):
        try:
            if flask.request.headers.getlist("X-Forwarded-For"):
                source_ip = flask.request.headers.getlist("X-Forwarded-For")[0]
            else:
                source_ip = flask.request.remote_addr
        except:
            # not in Flask scope
            source_ip = "127.0.0.1"
        record.source_ip = source_ip
        return True


class ConcurrentIdFilter(logging.Filter):
    """Add concurrent id to logging.format
    """

    def filter(self, record):
        from threading import get_ident
        concurrent_id = get_ident()
        record.concurrent_id = concurrent_id
        return True


class NameFilter(logging.Filter):
    def filter(self, record):
        import getpass
        if getpass.getuser() == record.name:
            return True
        return False
