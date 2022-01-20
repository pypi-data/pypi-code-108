#!/usr/bin/env python3

from __future__ import print_function
import threading
import asyncio
import traceback
import inspect

Log = print


#==================================================================================================
''' class ThreadMsg

    Provides a thread safe message queue.

'''
class ThreadMsg():


    ''' class ThreadMsgReply
        Brokers thread reply
    '''
    class ThreadMsgReply():

        def __init__(self, loop):
            self.err = None
            self.data = None
            self.loop = loop
            self.event = asyncio.Event(loop=loop)

        async def wait(self, to):
            try:
                if not self.event.is_set():
                    await asyncio.wait_for(self.event.wait(), to)
            except asyncio.TimeoutError as e:
                return False
            return self.event.is_set()

        def setData(self, data):
            self.data = data
            self.loop.call_soon_threadsafe(self.event.set)

        def setError(self, err):
            self.err = err
            self.loop.call_soon_threadsafe(self.event.set)

        def getData(self):
            return self.data if self.event.is_set() else None

        def getError(self):
            return self.err if self.event.is_set() else None



    ''' Constructor
        @param [in] f       - Pointer to the function to run
                                The function will receive a pointer to this
                                class as the first parameter.
                                The function can return an integer representing
                                the amount of time in seconds to delay before
                                calling the function again.  If a number less than
                                zero is returned, the thread will exit.
        @param [in] p       - Tuple containing other parameters to pass to the function
        @param [in] start   - True if the thread should start right away.
        @param [in] deffk   - Default function key for function mapping
    '''
    def __init__(self, f, p=(), start=True, deffk=None):

        self.msgs = []
        self.msgcnt = 0
        self.msgwait = 0
        self.run = True
        self.loops = 0
        self.lock = threading.Lock()
        self.event = None
        self.loop = None

        self.defFunKey = deffk

        # Thread
        self.thread = threading.Thread(target=self.threadLoop, args=(f, p,))
        if start:
            self.start()


    ''' Destructor
    '''
    def __del__(self):
        self.join()


    ''' Sets a default function key to use with function mapping
        @param [in] fk  - Function key name
    '''
    def setDefaultFunctionKey(self, fk):
        self.defFunKey = fk

    ''' Maps a call to set functions

            You can use this message to map messages to a function.

        @param [in] f       - Function or key in the function map
        @param [in] fm      - Map of functions to call
        @param [in] params  - dict containing function parameters to pass to function
        @param [in] kwargs  - keyword arguments to pass to function

        @begincode

            fm = {
                    'open'  : self.open,
                    'close' : self.close
                }

            @staticmethod
            async def mainThread(ctx):
                while msg := ctx.getMsg()
                    ctx.mapCall('_funName', fm, msg['data'])

        @endcode

    '''
    def mapCall(self, _f, _fm, _params={}, **kwargs):

        # Merge arguments
        _params.update(kwargs)

        # Look up function name if not callable
        if not callable(_f):
            if not isinstance(_f, str) or not _f:
                _f = self.defFunKey
            if not isinstance(_f, str) or not _f or _f not in _params:
                raise Exception('Function not found : %s' % _f)
            _f = _params[_f]
            if not isinstance(_f, str) or not _f or _f not in _fm:
                raise Exception('Function map not found : %s' % _f)
            _f = _fm[_f]

        # Map the parameters
        p = []
        sig = inspect.signature(_f).parameters
        for v in sig:
            if v not in _params:
                raise Exception('Function parameter not found : %s' % v)
            p.append(_params[v])

        # Make the call
        return _f(*p)


    ''' Asynchronously maps a call to set functions

            You can use this message to map messages to a function.

        @param [in] f       - Function or key in the function map
        @param [in] fm      - Map of functions to call
        @param [in] params  - dict containing function parameters to pass to function
        @param [in] kwargs  - keyword arguments to pass to function

        @begincode

            fm = {
                    'open'  : self.open,
                    'close' : self.close
                }

            @staticmethod
            async def mainThread(ctx):
                while msg := ctx.getMsg()
                    await ctx.mapCall('_funName', fm, msg['data'])

        @endcode

    '''
    async def mapCallAsync(self, _f, _fm, _params={}, **kwargs):

        # Merge arguments
        _params.update(kwargs)

        # Look up function name if not callable
        if not callable(_f):
            if not isinstance(_f, str) or not _f:
                _f = self.defFunKey
            if not isinstance(_f, str) or not _f or _f not in _params:
                raise Exception('Function not found : %s' % _f)
            _f = _params[_f]
            if not isinstance(_f, str) or not _f or _f not in _fm:
                raise Exception('Function map not found : %s' % _f)
            _f = _fm[_f]

        # Map the parameters
        p = []
        sig = inspect.signature(_f).parameters
        for v in sig:
            if v not in _params:
                raise Exception('Function parameter not found : %s' % v)
            p.append(_params[v])

        # Make the call
        r = _f(*p)
        if inspect.isawaitable(r):
            r = await r
        return r


    ''' Maps a message to set functions

            You can use this message to map a thread message to a function.
            This function will ensure any callback function is called.

        @param [in] f       - Function or key in the function map
        @param [in] fm      - Map of functions to call
        @param [in] msg     - dict containing function parameters to pass to function

        @begincode

            fm = {
                    'open'  : self.open,
                    'close' : self.close
                }

            @staticmethod
            async def mainThread(ctx):
                while msg := ctx.getMsg()
                    ctx.mapMsg('_funName', fm, msg)

        @endcode

    '''
    def mapMsg(self, f, fm, msg):
        try:
            r = self.mapCall(f, fm, msg['data'])
        except Exception as e:
            if callable(msg['cb']):
                msg['cb'](self, None, e)
            else:
                raise e
            return
        if callable(msg['cb']):
            msg['cb'](self, r, None)
        return r


    ''' Asynchronously maps a message to set functions

            You can use this message to map a thread message to a function.
            This function will ensure any callback function is called.

        @param [in] f       - Function or key in the function map
        @param [in] fm      - Map of functions to call
        @param [in] msg     - dict containing function parameters to pass to function

        @begincode

            fm = {
                    'open'  : self.open,
                    'close' : self.close
                }

            @staticmethod
            async def mainThread(ctx):
                while msg := ctx.getMsg()
                    ctx.mapMsg('_funName', fm, msg)

        @endcode

    '''
    async def mapMsgAsync(self, f, fm, msg):
        try:
            r = self.mapCall(f, fm, msg['data'])
            if inspect.isawaitable(r):
                r = await r
        except Exception as e:
            if callable(msg['cb']):
                cbr = msg['cb'](self, None, e)
                if inspect.isawaitable(cbr):
                    cbr = await cbr
            else:
                raise e
            return
        if callable(msg['cb']):
            cbr = msg['cb'](self, r, None)
            if inspect.isawaitable(cbr):
                cbr = await cbr
        return r


    ''' Find argument by type or return default
        @param [in] i       - Index of argument
        @param [in] t       - Type to find or list of types to find
        @param [in] d       - Default value to return if not found
        @param [in] args    - Argument lists to search
    '''
    @staticmethod
    def findByType(i, t, d, args):
        for v in args:
            match = False
            if type(t) == list:
                if (callable in t and callable(v)) or type(v) in t:
                    match = True
            elif (callable == t and callable(v)) or type(v) == t:
                match = True
            if match:
                if not i:
                    return v
                i -= 1
        return d


    ''' Make a call via the thread message loop
        @params [in] args  - In any order
                                fn[0]   - Callback function
                                            cb(returnVal, errorObj)
                                str[0]  - Name of function to call
                                dict[0] - Parameters to pass to function
        @params [in] kwargs - Keyword arguments to pass to function

        Return value will be passed to the callback if specified
    '''
    def call(self, *args, **kwargs):
        cb = self.findByType(0, callable, None, args)
        fn = self.findByType(0, str, '', args)
        params = self.findByType(0, dict, {}, args)
        params.update(kwargs)
        if fn:
            if not self.defFunKey:
                raise Exception('Default function key not set')
            params[self.defFunKey] = fn

        tmr = None

        # Callback object
        if not cb:
            # Use the callers loop context
            tmr = self.ThreadMsgReply(asyncio.get_event_loop())
            def cbCall(ctx, r, e):
                if e:
                    tmr.setError(e)
                else:
                    tmr.setData(r)
            cb = cbCall

        self.addMsg(params, cb)

        return tmr


    ''' Static function that handles thread
    '''
    @staticmethod
    async def threadRun(ctx, f, p):

        # Insert a pointer to our object
        pp = list(p)
        pp.insert(0, ctx)
        p = tuple(pp)

        # Create sync event
        ctx.lock.acquire()
        ctx.event = asyncio.Event(loop=ctx.loop)
        ctx.lock.release()

        # Allows the exit thread to keep things alive
        while ctx.wantRun():

            # While run flag is set
            while ctx.wantRun():

                try:
                    delay = f(*p)
                    if inspect.isawaitable(delay):
                        delay = await delay
                except Exception as e:
                    ctx.run = False
                    Log(e)
                    break

                if delay and 0 > delay:
                    ctx.run = False
                    break

                ctx.loops += 1

                # Maximum wait time if user didn't specify
                if None == delay:
                    delay = threading.TIMEOUT_MAX

                if delay:
                    await ctx.wait(delay)

            # Run again with the run flag set to false
            try:
                r = f(*p)
                if inspect.isawaitable(r):
                    r = await r
            except Exception as e:
                ctx.run = False
                Log(e)

        ctx.lock.acquire()
        ctx.event = None
        ctx.lock.release()


    ''' Sets up the async loop for the thread
    '''
    def threadLoop(self, f, p):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.threadRun(self, f, p))
        self.loop = None


    ''' Notify's the thread, i.e. breaks the wait state
    '''
    def notify(self):
        self.lock.acquire()
        if self.event:
            self.loop.call_soon_threadsafe(self.event.set)
        self.lock.release()


    ''' Enters an efficient interruptable wait state for the specified time.
        @param [in] t   - Time in milliseconds to wait.

        If notify is called, the wait state will end.

    '''
    async def wait(self, t):
        if not self.run or (len(self.msgs) and self.msgwait != self.msgcnt):
            return

        try:
            self.lock.acquire()
            event = self.event
            self.lock.release()

            if event:
                event.clear()
                if self.run and (not len(self.msgs) or self.msgwait == self.msgcnt):
                    await asyncio.wait_for(event.wait(), t)

        except asyncio.TimeoutError as e:
            pass


    ''' Notifies the thread it should quit
    '''
    def stop(self):
        self.run = False
        self.notify()


    ''' Start the thread
    '''
    def start(self):
        self.run = True
        self.thread.start()


    ''' Notifies the thread it should quit and waits for the thread to terminate
    '''
    def join(self, stop=False):
        if stop:
            self.run = False
            self.notify()
        if self.thread.is_alive():
            self.thread.join()


    ''' Adds a message to the threads queue
    '''
    def addMsg(self, msg, cb=None):
        self.lock.acquire()
        self.msgs.insert(0, {'data':msg, 'cb':cb})
        self.msgcnt += 1
        if self.event:
            self.loop.call_soon_threadsafe(self.event.set)
        self.lock.release()


    ''' Returns a message from the threads queue
    '''
    def getMsg(self):
        if not len(self.msgs):
            return None
        self.lock.acquire()
        msg = self.msgs.pop()
        self.lock.release()
        return msg


    ''' Returns message data from the threads queue
    '''
    def getMsgData(self):
        if not len(self.msgs):
            return None
        self.lock.acquire()
        msg = self.msgs.pop()
        self.lock.release()
        return msg['data']


    ''' Returns True if the thread should keep running
    '''
    def wantRun(self):
        return self.run
