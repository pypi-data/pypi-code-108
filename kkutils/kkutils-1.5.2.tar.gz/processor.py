#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Last modified: 2020-06-29 10:18:14
'''

import asyncio
import inspect
import sys
import time
from concurrent.futures._base import CancelledError
from functools import partial
from importlib import import_module
from inspect import isclass
from signal import SIGINT, SIGTERM

import uvloop
from utils import Config, Dict, Logger

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class Processor:

    def __init__(self, **kwargs):
        self.opt = Dict(kwargs)
        self.loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue()
        self.result = asyncio.Queue()
        self.logger = Logger()
        self._ckpt = 0, time.time()
        if hasattr(self, 'init'):
            ret = self.init()
            if inspect.isawaitable(ret):
                self.loop.run_until_complete(ret)

    async def producer(self):
        raise NotImplementedError

    async def consumer(self, args):
        raise NotImplementedError

    async def collector(self):
        raise NotImplementedError

    def _log_stats(self):
        qsize = self.queue.qsize()
        curr_time = time.time()
        if self._ckpt[0] == 0:
            self._ckpt = qsize, curr_time
        else:
            speed = (self._ckpt[0] - qsize) / (curr_time - self._ckpt[1])
            if curr_time - self._ckpt[1] >= 60:
                self._ckpt = qsize, curr_time
            seconds = int(qsize / speed)
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            eta = ''
            if hours:
                eta += f'{hours}h '
            if minutes:
                eta += f'{minutes}m '
            if seconds:
                eta += f'{seconds}s '
            self.logger.info(f'queue size: {qsize}, speed: {speed:.2f} it/s, eta: {eta.strip()}')

    async def _consumer(self):
        while True:
            try:
                args = await self.queue.get()
                self._log_stats()
                if isinstance(args, (tuple, list)):
                    ret = await self.consumer(*args)
                else:
                    ret = await self.consumer(args)
                if ret is not None:
                    await self.result.put(ret)
                self.queue.task_done()
            except CancelledError:
                return self.logger.error('Cancelled consumer')
            except Exception as e:
                self.logger.exception(e)
                self.queue.task_done()

    async def finish(self):
        await self.queue.join()
        if self.result.qsize() > 0:
            await self.collector()

    async def shutdown(self, sig):
        self.logger.warning(f'received signal {sig.name}')
        self.loop.stop()

    def start(self):
        for sig in (SIGINT, SIGTERM):
            self.loop.add_signal_handler(sig, partial(self.loop.create_task, self.shutdown(sig)))

        for _ in range(self.opt.workers):
            self.loop.create_task(self._consumer())

        if self.opt.forever:
            self.loop.create_task(self.producer())
            self.loop.run_forever()
        else:
            self.loop.run_until_complete(self.producer())
            self.loop.run_until_complete(self.finish())


def main():
    opt = Config(dict(workers=10, forever=False))
    arr = sys.argv[1].split('.')
    module = import_module(arr[0])
    if len(arr) == 1:
        for k, v in module.__dict__.items():
            if not k.startswith('__') and isclass(v) and any([x.__module__ == 'processor' and x.__name__ == 'Processor' for x in v.__bases__]):
                app = v(**opt)
                app.start()
    else:
        app = getattr(module, arr[1])(**opt)
        app.start()


if __name__ == '__main__':
    main()
