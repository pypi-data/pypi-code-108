import os
import sys

#
# Server socket
#
#   bind - The socket to bind.
#
#       A string of the form: 'HOST', 'HOST:PORT', 'unix:PATH'.
#       An IP is a valid HOST.
bind = '127.0.0.1:31311'

#
# Worker processes
#
#   workers - The number of worker processes that this server
#       should keep alive for handling requests.
#   timeout - If a worker does not notify the master process in this
#       number of seconds it is killed and a new worker is spawned
#       to replace it.
workers = int(os.environ.get("WORKER_COUNT", 1))
timeout = int(os.environ.get("WORKER_TIMEOUT", 300))
preload_app = os.environ.get("WORKER_PRELOAD", "false").lower() == "true"

#
# Logging Configuration
# log-config - the config file which tells gunicorn how to log

logconfig = os.path.join(os.environ.get('AML_SERVER_ROOT', '/var/azureml-server'), 'synchronous', 'gunicorn_logging.conf')

#
# Server hooks
# worker_abort - called when a worker received the SIGABRT signal
#   pre_fork - Called just prior to forking the worker subprocess.
#


def pre_fork(server, worker):
    server.log.info("worker timeout is set to {0}".format(timeout))
    if (workers > 1):
        server.log.warning("WORKER_COUNT is {}, this can cause issues with memory and CPU consumption.".format(workers))
    if (preload_app):
        server.log.warning("PRELOAD_APP is true, this will use shared memory and may lead to issues with certain frameworks.")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")
    sys.exit(3)


def worker_abort(worker):
    worker.log.error("worker timed out, killing gunicorn")
    sys.exit(3)

