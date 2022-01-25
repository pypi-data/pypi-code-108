from .core import Primitive, synchronized, Timeout
from threading import get_ident, RLock

class DebugLock(object):
    
    def __init__(self):
        self.R = RLock()
        
    def acquire(self, *params, **args):
        print(self, "acquire by ", get_ident(), "...")
        self.R.acquire(*params, **args)
        print(self, "acquired by ", get_ident())
        
    def release(self):
        print(self, "released by ", get_ident())
        self.R.release()
        
    def __enter__(self):
        return self.acquire()
        
    def __exit__(self, *params):
        return self.release()
    

class Promise(Primitive):
    
    def __init__(self, data=None, callbacks = [], name=None):
        Primitive.__init__(self, name=name)    #, lock=DebugLock())
        self.Data = data
        self.Callbacks = callbacks[:]
        self.Complete = False
        self.Canceled = False
        self.Result = None
        self.ExceptionInfo = None     # or tuple (exc_type, exc_value, exc_traceback)
        self.OnDone = self.OnCancel = self.OnException = None
        self.Chained = []
        self.Name = name
        
    @synchronized
    def ondone(self, cb):
        self.OnDone = cb
        
    @synchronized
    def oncancel(self, cb):
        self.OnCancel = cb
        
    @synchronized
    def oncexception(self, cb):
        self.OnException = cb
        
    @synchronized
    def addCallback(self, cb):
        if self.Complete and not self.Canceled:
            cb(self)
        self.Callbacks.append(cb)        
        
    @synchronized
    def exception(self, exc_type, exc_value, exc_traceback):
        self.ExceptionInfo = (exc_type, exc_value, exc_traceback)
        if self.OnException is not None:
            self.OnExceptipn(self)
        for p in self.Chained:
            p.exception(exc_type, exc_value, exc_traceback)
        self.wakeup()
        self._cleanup()

    @synchronized
    def chain(self, *promises):
        if self.ExceptionInfo:
            exc_type, exc_value, exc_traceback = self.ExceptionInfo
            for p in promises:
                p.exception(exc_type, exc_value, exc_traceback)
        elif self.Complete:
            for p in promises:
                p.complete(self.Result)
        elif self.Canceled:
            for p in promises:
                p.complete(None)
        else:
            self.Chained += list(promises)
        return self
        
    @synchronized
    def complete(self, result=None):
        self.Result = result
        self.Complete = True
        if not self.Canceled:
            if self.OnDone is not None:
                self.OnDone(self.Result,)
            for cb in self.Callbacks:
                if cb(self) == "stop":
                    break
        for p in self.Chained:
            #print("%s: complete(%s) ..." % (self, p))
            p.complete(result)
            #print("%s: complete(%s) done" % (self, p))
        self.wakeup()
        self._cleanup()
    
    def is_complete(self):
        return self.Complete
        
    @synchronized
    def wait(self, timeout=None):
        #print("thread %s: wait(%s)..." % (get_ident(), self))
        pred = lambda x: x.Complete or x.Canceled or self.ExceptionInfo is not None
        self.sleep_until(pred, self, timeout=timeout)
        try:
            if self.Complete:
                return self.Result
            elif self.Canceled:
                return None
            elif self.ExceptionInfo:
                _, e, _ = self.ExceptionInfo
                raise e 
            else:
                raise Timeout()
        finally:
            self._cleanup()
            
            
    def _cleanup(self):
        self.Chained = []
        self.Callbacks = []
        self.OnCancel = self.OnException = self.OnDone = None
    
class ORPromise(Primitive):
    
    def __init__(self, promises):
        Primitive.__init__(self)
        self.Fulfilled = None
        for p in promises:
            p.addCallback(self, promise_callback)

    @synchronized
    def promise_callback(self, promise):
        self.Fulfilled = promise
        self.wakeup()
    
    @synchronized
    def wait(self, timeout = None):
        while self.Fulfilled is None:
            self.sleep(timeout)
        return sef.Fulfilled

class ANDPromise(Primitive):
    
    def __init__(self, promises):
        Primitive.__init__(self)
        self.Promises = promises
        
    def wait(self, timeout=None):
        return [p.wait(timeout) for p in self.Promises]
