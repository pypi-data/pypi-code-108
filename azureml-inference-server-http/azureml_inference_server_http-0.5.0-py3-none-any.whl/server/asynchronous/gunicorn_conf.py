import os

#
# Server socket
#
#   bind - The socket to bind.
#
#       A string of the form: 'HOST', 'HOST:PORT', 'unix:PATH'.
#       An IP is a valid HOST.
bind = '0.0.0.0:5001'

#
# Worker processes
#
#   workers - The number of worker processes that this server
#       should keep alive for handling requests.
#   worker_class - The type of worker to use. 'uvicorn.workers.UvicornWorker'
workers = int(os.environ.get("WORKER_COUNT", 1))
worker_class = "uvicorn.workers.UvicornWorker"
preload_app = os.environ.get("WORKER_PRELOAD", "false").lower() == "true"

#
# Server hooks
#   pre_fork - Called just prior to forking the worker subprocess
#

def pre_fork(server, worker):
    server.log.info("WORKER_COUNT is {0}".format(workers))
    if (preload_app):
        server.log.info("PRELOAD_APP is true")
