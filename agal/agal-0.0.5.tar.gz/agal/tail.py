import sys
import os
import time
import asyncio
import collections
import threading
import concurrent.futures

pool = concurrent.futures.ThreadPoolExecutor()

SEP = '\n'
LINES = collections.deque()


def fd_list_to_dict(fd_list):
    fd_dict = {}
    for idx, fd in enumerate(fd_list):
        fd_dict[idx] = {
            'fd': fd,
            'buf': '',
            'idx': idx
        }
    return fd_dict


async def readlines(fd_info):
    global LINES
    def _readline():
        try:
            return fd_info['fd'].readline()
        except Exception as e:
            return ''
    loop = asyncio.get_running_loop()
    line = await loop.run_in_executor(pool, _readline)
    if not line:
        await asyncio.sleep(0.1)
        return
    LINES.append(line)


async def tail(fd_list):
    fd_dict = fd_list_to_dict(fd_list)
    while True:
        for idx, fd_info in fd_dict.items():
            await readlines(fd_info)


async def handle_lines(handler=None):
    global LINES
    while True:
        try:
            line = LINES.popleft()
            if handler:
                await handler(line)
            else:
                sys.stdout.write(line)
        except:
            await asyncio.sleep(0.1)


def start_loop(futures):
    def _start_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(futures)
        loop.close()
    t = threading.Thread(target=_start_loop, daemon=True)
    t.start()
    return t


def start(filename_list, handler=None):
    fd_list = []
    for i in filename_list:
        if os.path.exists(i):
            fd = open(i)
            fd.seek(0, 2)
            fd_list.append(fd)
    if not sys.stdin.isatty():
        fd_list.append(sys.stdin)
    t_read = start_loop(tail(fd_list))
    t_handle = start_loop(handle_lines(handler))
    t_read.join()
    t_handle.join()
