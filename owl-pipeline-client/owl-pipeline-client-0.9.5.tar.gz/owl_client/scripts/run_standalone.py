import logging
import logging.config
import os
import signal
import sys
import tempfile
import time
import traceback
from argparse import Namespace
from contextlib import closing

from distributed import Client, LocalCluster
from owl_client.utils import find_free_port, get_pipeline, read_config

logconf = """
version: 1
handlers:
  console:
    class: logging.StreamHandler
    formatter: standard
    stream: 'ext://sys.stderr'
  file:
    class: logging.FileHandler
    filename: owl.log
    mode: w
    formatter: standard
formatters:
  standard:
    format: '%(asctime)s PIPELINE %(levelname)s %(name)s %(funcName)s | %(message)s'
loggers:
  owl.daemon.pipeline:
    handlers: [console, file]
    level: ${LOGLEVEL}
"""

log = logging.getLogger("owl.daemon.pipeline")

os.environ["LOGLEVEL"] = os.environ.get("LOGLEVEL", "DEBUG")
os.environ["OMP_NUM_THREADS"] = "1"


def terminate(*args):  # pragma: nocover
    log.info("Terminating...")
    try:
        client = Client.current()
        client.close()
        client.cluster.close()
    except:  # noqa: E722
        pass
    sys.exit(1)


def run_standalone(args: Namespace) -> None:  # pragma: nocover
    """Run worker pipeline.

    Parameters
    ----------
    arg
        Argparse namespace containing command line flags.
    """

    global logconf

    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)

    conf = read_config(args.conf)

    log_config = read_config(logconf)
    logging.config.dictConfig(log_config)

    func = get_pipeline(conf["name"])

    port = find_free_port()

    resources = conf["resources"]
    n_workers = resources.get("workers", 2)
    threads = resources.get("cores", 2)
    memory = resources.get("memory", 7)

    tmpdir = os.environ.get("TMP_DIR", "/tmp")
    with tempfile.TemporaryDirectory(dir=tmpdir) as local_directory:
        with closing(
            LocalCluster(
                n_workers=n_workers,
                threads_per_worker=threads,
                scheduler_port=port,
                dashboard_address="localhost:{}".format(port + 1),
                memory_limit="{}GB".format(memory),
                local_directory=local_directory,
            )
        ) as cluster:
            log.info("Running diagnostics interface in http://localhost:%s", port + 1)
            log.info("Starting pipeline %r", conf["name"])
            log.debug("Configuration %s", conf)
            watch = time.monotonic()
            if args.debug:
                log.info("Running in debug mode")
                import dask.config

                dask.config.set(scheduler="single-threaded")
            try:
                func(conf, log_config, cluster=cluster)
            except Exception:
                tb = traceback.format_exc()
                log.critical(f"{tb!r}")
                raise
    log.info("Elapsed time %fs", time.monotonic() - watch)
