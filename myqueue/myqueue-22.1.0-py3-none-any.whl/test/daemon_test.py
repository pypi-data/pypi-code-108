from __future__ import annotations
import functools
import socket
import time

from myqueue.daemon import perform_daemon_action


def test_daemon(mq, capsys):
    cmd = functools.partial(perform_daemon_action,
                            mq.config.home / '.myqueue')
    cmd('status')
    cmd('stop')
    pid = cmd('start')
    cmd('start')
    cmd('status')
    cmd('stop')
    time.sleep(0.2)
    cmd('status')

    host = socket.gethostname()
    assert capsys.readouterr().out == '\n'.join(
        ['Not running',
         'Not running',
         f'PID: {pid}',
         'Already running',
         f'Running on {host} with pid={pid}',
         'Not running',
         ''])
