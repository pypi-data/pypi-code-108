
import time
import json
import inspect
import random
import threading
import aiohttp
from aiohttp import web, WSCloseCode
import asyncio

import threadmsg as tm
import propertybag as pb
import sparen
Log = sparen.log


class WebShoesApp():


    ''' Constructor
        @param [in] addr    - Address to listen on
        @param [in] port    - Port to listen on
        @param [in] opts    - Options, passed to callbacks in ctx.opts
                                verbose = True for verbose console messages
    '''
    def __init__(self, addr, port, opts={}):

        self.addr = addr
        self.port = port
        self.opts = pb.Bag(opts)

        self.thread = None
        self.ws = None
        self.handlers = {}
        self.evh = pb.Bag()

        # Setup thread and function broker
        self.thread = tm.ThreadMsg(self.msgThread, start=False)
        self.thread.setDefaultFunctionKey('_funName')
        self.callMap = {
            'triggerEventSync': self.triggerEventSync
        }


    ''' Register request handler
        @param [in] sub     - Sub path for http requests, can be * for any
        @param [in] cmd     - Name of parameter in websocket requests containing command
        @param [in] q       - Name of parameter in websocket requests containing paraameters
                                If this is '', then the top level object contains parameters
        @param [in] evt     - Name of parameter containing event name
        @param [in] rep     - Name of parameter in reply that should contain reply object
                                If this is '', then the top level object will contain reply values
        @param [fm] fm      - The function map

        @begincode

            # Test function
            def cmdAdd(ctx, q):
                return {'result': int(q.a) + int(q.b)}

            # Create the server
            import webshoes as ws
            wsa = ws.WebShoesApp('127.0.0.1', 15801, {'verbose': True})

            # Register the callback function
            #             -----------------------------> The root for http requests
            #             |      ----------------------> The variable in websocket requests
            #             |      |                          containing the command name
            #             |      |      ---------------> The variable in websocket requests
            #             |      |      |                   containing the function arguments
            #             |      |      |    ----------> The variable in websocket requests
            #             |      |      |    |              containing the event name
            #             |      |      |    |      ---> Variable in replys to put return data
            #             |      |      |    |      |
            wsa.register('cmd', 'cmd', 'q', 'evt', 'r', {
                    'add': cmdAdd
                })

            # Start the server
            wsa.start()


            # Call add function with http request
            import requests
            reply = requests.get('http://127.0.0.1:15801/cmd/add?a=2&b=3')
            Log(reply.text)


            # Call the add function with websockets
            import websockets
            async with websockets.connect('ws://127.0.0.1:15801') as wsc:
                await wsc.send(json.dumps({'cmd':'add', 'q':{'a':2, 'b':3}}))
                reply = await wsc.recv()
                Log(reply)

            wsa.stop()

        @endcode

    '''
    def register(self, sub, cmd, q, evt, rep, fm):
        self.handlers[sub] = {'sub':sub, 'cmd':cmd, 'q':q, 'evt':evt, 'rep':rep, 'fm':fm}


    ''' Unregister the specified request handler
        @param [in] sub     - Sub name to unregister
    '''
    def unregister(self, sub):
        if p in self.handlers:
            del self.handlers[sub]


    ''' Send message to socket
        @param [in] ws      - Websocket overwhich to send the message
        @param [in] msg     - Message to send
    '''
    async def sendMsg(self, ws, msg):

        if self.opts.verbose:
            Log(f"Sending --> {msg}")

        try:
            if isinstance(msg, pb.Bag):
                await ws.send_str(msg.toJson())
            elif isinstance(msg, dict) or isinstance(msg, list):
                await ws.send_str(json.dumps(msg))
            else:
                await ws.send_str(msg)
        except Exception as e:
            Log(e)
            return False

        return True


    '''
        @param [in] ev  - Event to register
        @param [in] uid - Unique id for event handler
        @param [in] ws  - Websocket over which to send events
    '''
    async def addEventHanlder(self, ev, uid, ws):

        if self.opts.verbose:
            Log(f'Registering: {ev} -> {uid}')

        # Add the event if it doesn't exist yet
        if ev not in self.evh:
            self.evh[ev] = {'evt': ev, 'cb':{}, 'ver': 0}

        # Adding new handler
        if uid not in self.evh[ev]['cb']:
            self.evh[ev]['cb'][uid] = {'uid': uid, 'ws': ws, 'ver': 0, 'last': {}}

        # Just mark existing handler as out of date
        else:
            self.evh[ev]['cb'][uid]['ver'] = 0


    ''' Send event to websocket connections
        @param [in] ev  - Event to send
    '''
    async def sendEvent(self, ev):

        if self.opts.verbose:
            Log(f'Send Event: {ev}')

        if ev not in self.evh:
            return False

        t = time.time()
        ver = self.evh[ev]['ver']
        r = self.evh[ev]['last']
        if isinstance(r, pb.Bag):
            r = self.evh[ev]['last'].as_dict()
        ruids = []
        for k,v in self.evh[ev]['cb'].items():
            if v['ver'] != ver:
                v['ver'] = ver
                if not await self.sendMsg(v['ws'], {
                                        'evt':ev,
                                        'uid': k,
                                        'ver':ver,
                                        't':t,
                                        'r':r
                                    }):
                    ruids.append(k)

        # Remove failed uids
        for v in ruids:
            self.removeUid(v)


    ''' Trigger the specified event
        @param [in] event  - Event to trigger
        @param [in] data   - Data associated with the event
    '''
    async def triggerEventSync(self, event, data):

        if self.opts.verbose:
            Log(f'Trigger event: {event}')

        # If it doesn't exist
        if event not in self.evh:
            self.evh[event] = {'evt': event, 'cb':{}, 'ver': 1, 'last': data}

        # Update existing event
        else:
            self.evh[event]['last'] = data
            self.evh[event]['ver'] += 1
            await self.sendEvent(event)


    ''' Thread safe function to trigger the specified event
        @param [in] event  - Event to trigger
        @param [in] data   - Data associated with the event
    '''
    def triggerEvent(self, event, data):
        return self.thread.call('triggerEventSync', event=event, data=data)


    ''' Remove specified uid from the event handler list
        @param [in] uid - Unique id of event handler
    '''
    def removeUid(self, uid):
        for k,v in self.evh.items():
            if uid in v['cb']:
                if self.opts.verbose:
                    Log(f'Removing event target: {uid}')
                del v['cb'][uid]


    ''' Called to handle a websocket message
        @param [in] req     - The original websocket request object
        @param [in] ws      - The websocket handler object
    '''
    async def handleWs(self, req, ws):

        if self.opts.verbose:
            Log('websocket connected')

        # List of events created by this websocket
        evts = []

        # For each message from the web socket
        async for msg in ws:

            # Transaction id
            tid = ''

            # If it's a text message
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data:
                    try:
                        # Message
                        j = pb.Bag(json.loads(msg.data), '')

                        if self.opts.verbose:
                            Log(f'Message: {j}')

                        # Save away the latest transaction id
                        if j.tid:
                            tid = j.tid

                        # Find handler
                        for c,h in self.handlers.items():

                            r = None
                            sendEvent = None

                            # Event handler registration?
                            if h['evt'] and h['evt'] in j:
                                uid = j.uid
                                if not uid:
                                    letters = '1324567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                                    uid = ''.join(random.choice(letters) for i in range(32))
                                evt = j[h['evt']]
                                evts.append(uid)
                                await self.addEventHanlder(evt, uid, ws)
                                r = {'uid': uid, 'status': 'Event added'}
                                sendEvent = evt

                            # Check for command
                            elif h['cmd'] and j.exists(h['cmd']):

                                # Command
                                cmd = j[h['cmd']]

                                # Params
                                q = {}
                                if h['q'] in j:
                                    q = j[h['q']]
                                else:
                                    q = j

                                # Split the command
                                p = cmd.split('/')
                                while len(p) and not p[0]:
                                    p = p[1:]

                                # Skip sub path if needed
                                if 1 < len(p) and h['sub'] and p[0] == h['sub']:
                                    p = p[1:]

                                # Ensure a handler
                                if p[0] not in h['fm']:
                                    if '*' not in h['fm']:
                                        raise Exception(f'No handler for {cmd}')
                                    p[0] = '*'

                                # Find function
                                f = h['fm'][p[0]]
                                if not callable(f):
                                    raise Exception(f'No callable handler for {cmd}')

                                # Context for user functions
                                ctx = pb.Bag({'p': cmd, 'req': req, 'opts': self.opts, 'wsa': self, 'ws': ws})

                                try:
                                    # Call user handler
                                    r = f(ctx, pb.Bag(q))
                                    if inspect.isawaitable(r):
                                        r = await r
                                except Exception as e:
                                    Log(e)
                                    raise Exception('Server Error')

                            else:
                                continue

                            # Send response if needed
                            if r:
                                if isinstance(r, pb.Bag):
                                    r = r.as_dict()

                                if 'rep' in h and h['rep']:
                                    res = {h['rep']:r}
                                else:
                                    res = r
                                if j.tid:
                                    res['tid'] = tid
                                if 't' not in res:
                                    res['t'] = time.time()
                                await self.sendMsg(ws, res)

                            # Send event if needed
                            if sendEvent:
                                await self.sendEvent(sendEvent)

                            break


                    except Exception as e:
                        Log(e)
                        res = {'error': str(e)}
                        if tid:
                            res['tid'] = tid
                        await self.sendMsg(ws, res)

            elif msg.type == aiohttp.WSMsgType.ERROR:
                Log(f'websocket error: {ws.exception()}')

        if self.opts.verbose:
            Log('websocket disconnected')

        # Remove events
        for e in evts:
            self.removeUid(e)


    ''' HTTP request handler
        @param [in] req     - Request object
    '''
    async def handleHttp(self, req):

        if self.opts.verbose:
            Log(f'HTTP Request {req.path}')

        p = req.path.split('/')
        while len(p) and not p[0]:
            p = p[1:]

        if 0 >= len(p):
            p = ['*']

        if 1 == len(p):
            p = [p[0], '*']

        # Find handler group
        if p[0] not in self.handlers:
            if '*' not in self.handlers:
                raise Exception(f'No handler group for {req.path}')
            p[0] = '*'

        # Find handler
        h = self.handlers[p[0]]
        if p[1] not in h['fm']:
            if '*' not in h['fm']:
                raise Exception(f'No handler for {req.path}')
            p[1] = '*'

        # Find function
        f = h['fm'][p[1]]
        if not callable(f):
            raise Exception(f'No callable handler for {req.path}')

        # Get parameters
        q = {}
        if 0 < len(req.query):
            q = dict(req.query)

        # Context for user functions
        ctx = pb.Bag({'p': req.path, 'req': req, 'opts': self.opts, 'wsa': self})

        # Call user handler
        try:
            r = f(ctx, pb.Bag(q))
            if inspect.isawaitable(r):
                r = await r
        except Exception as e:
            Log(e)
            raise Exception('Server error')

        # application/json
        if isinstance(r, dict) or isinstance(r, pb.Bag):
            res = web.Response(text=json.dumps(r))
            res.headers['Content-Type'] = 'application/json'
            return res

        return r


    ''' Connection handler
        @param [in] req - Request object
    '''
    async def reqHandler(self, req):

        # Try websocket
        try:
            ws = web.WebSocketResponse()
            await ws.prepare(req)
            try:
                await self.handleWs(req, ws)
                return ws
            except Exception as e:
                Log(e)

        # Http
        except Exception as e:
            try:
                return await self.handleHttp(req)
            except Exception as e:
                return web.Response(text=json.dumps({'error': str(e)}))


    ''' Main thread function
        @param [in] ctx - Thread context object
    '''
    async def msgThread(self, ctx):

        # Initialize
        if not ctx.loops:
            # https://docs.aiohttp.org/en/stable/web_reference.html
            self.server = web.Server(self.reqHandler)
            self.runner = web.ServerRunner(self.server)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, self.addr, self.port)
            await self.site.start()

        # Shutdown
        if not ctx.run:
            await self.site.stop()
            await self.runner.cleanup()
            self.site = None
            self.runner = None
            self.server = None
            return

        # Service message loop
        while msg := ctx.getMsg():
            await ctx.mapMsgAsync(None, self.callMap, msg)


    ''' Starts the server thread
    '''
    def start(self):
        self.stop()
        self.thread.start()


    ''' Stops the server thread
    '''
    def stop(self):
        if self.thread:
            self.thread.join(True)

