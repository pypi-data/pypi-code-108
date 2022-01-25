import os
import signal
import logging

from daemonize import Daemonize

logger = logging.getLogger('oshino')

DEFAULT_PID = '/var/run/oshino'


def start_daemon(config_path, pid=DEFAULT_PID, verbose=False, logfile=None):
    from oshino.config import load
    from oshino.core.heart import start_loop

    keep_fds = []
    if logfile:
        level = DEBUG if verbose else INFO
        fh = FileHandler(logfile, level=level)
        logger.handlers.append(fh)
        fh.push_application()
        keep_fds.append(fh.stream.fileno())

    def wrapped():
        cfg = load(config_path)
        return start_loop(cfg)

    daemon = Daemonize(
            app='oshino',
            pid=pid,
            action=wrapped,
            verbose=verbose,
            keep_fds=keep_fds,
            logger=logger,
            chdir=os.getcwd()
    )
    daemon.start()
    return daemon

def stop_daemon(pid=DEFAULT_PID):
    with open(pid, 'r') as f:
        os.kill(int(f.read()), signal.SIGTERM)

def status(pid=DEFAULT_PID):
    if os.path.exists(pid):
        with open(pid, 'r') as f:
            logger.info('Process is running on: {0}'.format(f.read()))
    else:
        logger.error('Process is not running')
