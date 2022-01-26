# -*- coding: utf-8 -*-
#
# @Author: Florian Briegel (briegel@mpia.de)
# @Date: 2021-08-18
# @Filename: proxy.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)


from __future__ import annotations

import asyncio
# import logging
import sys
from functools import partial
from itertools import chain
from typing import Callable, Optional
from shlex import quote
import json

from inspect import getcoroutinelocals, iscoroutine
from clu import AMQPReply, BaseClient

from .exceptions import ProxyPartialInvokeException



class Proxy():
    """A proxy client with actor commands.

import uuid
from clu import AMQPClient, CommandStatus
from cluplus.proxy import Proxy, invoke, unpack

actor = "proto"

amqpc = AMQPClient(name=f"proxy-{uuid.uuid4().hex[:8]}")

proto = Proxy(amqpc, actor)
proto.start()

async def start_now(proto):
    await amqpc.start()
    await proto.start()
    await amqpc.stop()

amqpc.loop.run_until_complete(start_now(proto))

print(proto.ping())

async def start_ping(proto):
    await amqpc.start()
    print(await proto.ping())
    await amqpc.stop()

amqpc.loop.run_until_complete(start_ping(proto))

async def start_async_ping(proto):
    await amqpc.start()
    print(await proto.async_ping())
    await amqpc.stop()

amqpc.loop.run_until_complete(start_async_ping(proto))


invoke(proto.async_setEnabled(True, axis0=True),
       proto.async_gotoRaDecJ2000(10,20))


unpack(proto.ping())

a, a0, b0, *coord = unpack(invoke(proto.async_setEnabled(True, axis0=True),
                                  proto.async_gotoRaDecJ2000(10,20)))
try:
   proto.errPassAsError()
   
except Exception as ex:
   print(f"got: {ex}")

try:
   amqpc.loop.run_until_complete(invoke(proto.ping(async_mode=True),
                                        proto.async_version(),
                                        proto.async_errPassAsError()))
except Exception as ex:
   print(ex)

try:
    async def start_async_invoke():
        await amqpc.start()
        await invoke(proto.ping(),
                     proto.version(),
                     proto.errPassAsError())
        await amqpc.stop()
    amqpc.loop.run_until_complete(start_async_invoke())
except Exception as ex:
   print(ex)


def callback(reply): 
    amqpc.log.warning(f"Reply: {CommandStatus.code_to_status(reply.message_code)} {reply.body}")

proto.setEnabled(True, callback=callback)


async def start_async_setEnabled():
        await amqpc.start()
        await proto.setEnabled(True, callback=callback)
        await amqpc.stop()

amqpc.loop.run_until_complete(start_async_setEnabled())
    """
    
    __commands = "__commands"
    __comkey = "help"
    
    def __init__(self, client: BaseClient, actor: str):
        self.client = client
        self.actor = actor
        self.async_mode = True
#        super().__init__(client, actor)

    def start(self):
        """Query and set actor commands."""

        def set_commands(reply):
            commands = reply[Proxy.__comkey] if isinstance(reply, dict) else reply.help

            for c in commands:
                setattr(self, c, partial(self._hybrid_call_command, c))
                setattr(self, f"async_{c}", partial(self.call_command, c))
                setattr(self, f"nowait_{c}", partial(self.call_command, c, nowait=True))


        if self.client.loop.is_running():
            async def start_async():
                set_commands(await self.call_command(Proxy.__commands))
            return start_async()
        else:
            self.async_mode = False
            coro = self._sync_call_command(Proxy.__commands)
            set_commands(self.client.loop.run_until_complete(coro))
            self.client.loop.run_until_complete(self.client.stop())
            return self


    def isClientConnected(self):
        if not self.client.connection.connection:
            return False
        return not self.client.connection.connection.is_closed

    async def _sync_call_command(self,
                                 command,
                                 *args,
                                 callback: Optional[Callable[[AMQPReply], None]] = None,
                                 object_hook: Optional[Callable[[AMQPReply], None]] = None,
                                 **kwargs):

        await self.client.start()

        try:
            ret = await self.call_command(command,
                                        *args,
                                        callback=callback,
                                        object_hook=object_hook,
                                        **kwargs)
        except Exception as ex:
            await self.client.stop()
            raise ex

        await self.client.stop()
        return ret

    def _hybrid_call_command(self,
                             command,
                             *args,
                             nowait:Bool = False,
                             callback: Optional[Callable[[AMQPReply], None]] = None,
                             object_hook: Optional[Callable[[AMQPReply], None]] = None,
                             **kwargs):

        if self.async_mode:
            return self.call_command(command,
                                     *args,
                                     nowait=nowait,
                                     callback=callback,
                                     object_hook=object_hook,
                                     **kwargs)
        else:
            return self.client.loop.run_until_complete(
                self._sync_call_command(command,
                                        *args,
                                        callback=callback,
                                        object_hook=object_hook,
                                        **kwargs))

    async def call_command(self,
                           command: str,
                           *args,
                           callback: Optional[Callable[[AMQPReply], None]] = None,
                           nowait:Bool = False,
                           object_hook: Optional[Callable[[AMQPReply], None]] = None,
                           **kwargs):

        def encode(v):
            if isinstance(v, (int, float, bool)): return v
            elif isinstance(v, str): return v if v[0] in "'\"" and v[-1] in "'\"" else quote(v)
            return f"'{json.dumps(v)}'"

        args = [encode(v) for v in args] \
             + list(chain.from_iterable(('--' + k, encode(v))
                                        for k, v in kwargs.items()))

        fu = await self.client.send_command(self.actor,
                                                command,
                                                *args,
                                                callback=callback)
        
        if nowait: return fu

        ret = await fu

        if hasattr(ret, "status") and ret.status.did_fail:
            raise self._errorMapToException(ret.replies[-1].body['error'])

        return ret.replies[-1].body




    @staticmethod
    def _errorMapToException(em):
        if isinstance(em, dict):
            return Proxy._stringToException(em['exception_message'],
                                            em['exception_type'],
                                            em['exception_module'])
        return Exception(em)


    @staticmethod
    def _stringToException(sval, tn='Exception', mn='builtins'):
        try:
            module = sys.modules[mn] if mn in sys.modules \
                                     else __import__(mn, fromlist=tn)
            return getattr(module, tn)(sval)

        except AttributeError:
            return Exception(f'Unknown exception type {tn}-{sval}')

        except ImportError:
            return Exception(f'Unknown module type {mn}-{tn}:{sval}')


def invoke(*cmds):
    """invokes one or many commands in parallel

    On error it throws an exception if one of the commands fails as a dict
    with an exception and return values for every command.
    """
    async def invoke_now(proxy, *cmds, return_exceptions=False):
        if proxy and not proxy.isClientConnected():
            await proxy.client.start()
        
        ret = await asyncio.gather(*[asyncio.create_task(cmd) for cmd in cmds], 
                                   return_exceptions=True)

        if proxy:
            await proxy.client.stop()

        if not return_exceptions:
            for r in ret:
                if isinstance(r, Exception):
                    raise ProxyPartialInvokeException(*ret)
        return ret


    first_coro = cmds[0]
    assert(iscoroutine(first_coro))

    proxy = getcoroutinelocals(first_coro)['self']
    loop = proxy.client.loop
    
    if loop.is_running():
        return invoke_now(None, *cmds)
    else:
        return loop.run_until_complete(invoke_now(proxy, *cmds))


def unpack(ret, *keys):
    """ unpacks every parameter from the body of the finish reply or list of replies.

        Pythons list unpacking mechanism PEP3132 can be used to assign the value(s)
        
        Be warned if you dont use it the correct way, 
        whould also be a good place to check the reply body format with schemas.

        >>> a, b, c = [1, 2, 3]
        >>> a
        1

        >>> a = [1, 2, 3]
        >>> a
        [1, 2, 3]

        >>> a, b = [1, 2, 3]
        Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        ValueError: too many values to unpack (expected 2)

        >>> a, *b = [1, 2, 3]
        >>> a
        1
        >>> b
        [2, 3]

        Parameters
        ----------
        keys
        return only the parameters from keys
    """

    if len(ret) == 0:
        return
    
    if isinstance(ret, list):
        if len(keys) > 0:
            return [d[i] for d in ret for i in keys if i in d]
        else:
            return [val for d in ret for val in list(d.values())]

    if len(ret) == 1:
        return list(ret.values())[0]
    elif len(keys) > 1:
        return [ret[i] for i in keys]
    else:
        return list(ret.values())

