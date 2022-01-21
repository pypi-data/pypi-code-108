#!/usr/bin/env python
"""
Since entr always requires 2 terminals, one for entr, one for the reloader,
we've put filewatching capabilities into the devapp itself - spawned as back
ground process - this one.

Usage:
    See devapp.app.py, search dirwatch

"""

import os
import sys
import time
from fnmatch import fnmatch
from functools import partial

WD = 'WATCHDOG: '

out = partial(print, file=sys.stderr)


def start_dir_watch(dir_pid_match_rec):
    # print(dir_pid_match_rec)
    dir, pid, match, recursive = dir_pid_match_rec.split(':')
    recursive = bool(recursive)
    pid = int(pid)
    if not '*' in match:
        match = ('*' + match + '*').replace('**', '*')
    l = dict(locals())
    l.pop('dir_pid_match_rec')

    out(WD + 'starting. %s' % str(l)[1:-1].replace("'", ''))
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class H(FileSystemEventHandler):
        def on_modified(self, event, pid=pid):
            out(WD + f'event: {event.event_type}  path : {event.src_path}')
            # out(WD + 'match' + self.match + '.')
            if self.match:
                if not fnmatch(event.src_path, self.match):
                    return
            out(WD + 'match => Sending reload')
            os.kill(int(pid), 1)

    o, h = Observer(), H()
    if isinstance(match, str):
        h.match = match
    else:
        raise Exception('spec not supported')

    o.schedule(h, path=dir, recursive=recursive)
    o.start()
    while 1:
        time.sleep(100000)


if __name__ == '__main__':
    start_dir_watch(sys.argv[1])
