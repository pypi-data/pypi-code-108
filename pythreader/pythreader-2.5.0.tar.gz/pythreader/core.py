from threading import RLock, Thread, Event, Condition, Semaphore, currentThread, get_ident
import time
import sys

Waiting = []
In = []

class Timeout(Exception):
    pass

def threadName():
    t = currentThread()
    return str(t)

def synchronized(method):
    def smethod(self, *params, **args):
        me = get_ident()
        #print("entering synchronized", self, me)
        with self:
            out = method(self, *params, **args)
        #print("exiting synchronized", self, me)
        return out
    smethod.__doc__ = method.__doc__
    return smethod

def gated(method):
    def smethod(self, *params, **args):
        with self._Gate:
            out = method(self, *params, **args)
        return out
    smethod.__doc__ = method.__doc__
    return smethod


def printWaiting():
    print("waiting:----")
    for w in Waiting:
        print(w)
    print("in:---------")
    for w in In:
        print(w)

class UnlockContext(object):
    
    def __init__(self, prim):
        self.Prim = prim
        
    def __enter__(self):
        self.Prim._Lock.__exit__(None, None, None)
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.Prim._Lock.__enter__()    

class Primitive:
    def __init__(self, gate=1, lock=None, name=None):
        self._Kind = self.__class__.__name__
        self._Lock = lock if lock is not None else RLock()
        #print ("Primitive:", self, " _Lock:", self._Lock)
        self._WakeUp = Condition(self._Lock)
        self._Gate = Semaphore(gate)
        self.Name = name
        
    def __str__(self):
        ident = ('"%s"' % (self.Name,)) if self.Name else ("@%s" % (("%x" % (id(self),))[-4:],))
        return "[%s %s]" % (self._Kind, ident)

    def __get_kind(self):
        return self._Kind

    def __set_kind(self, kind):
        self._Kind = kind

    kind = property(__get_kind, __set_kind)

    def getLock(self):
        return self._Lock
        
    def __enter__(self):
        #t = currentThread()
        #print ">>>entry by thread %s %x: %s %x..." % (t.__class__.__name__, id(t), self.kind, id(self))
        return self._Lock.__enter__()
        
    def __exit__(self, exc_type, exc_value, traceback):
        #t = currentThread()
        #print "<<<<exit by thread %s %x: %s %x" % (t.__class__.__name__, id(t), self.kind, id(self))
        return self._Lock.__exit__(exc_type, exc_value, traceback)
    
    @property
    def unlock(self):
        return UnlockContext(self)

    @synchronized
    def sleep(self, timeout = None, function=None, arguments=()):
        #print("sleep", self, get_ident(), "   condition lock:", self._WakeUp._lock, "...")
        self._WakeUp.wait(timeout)
        if function is not None:
            return function(*arguments)

    @synchronized
    def sleep_until(self, predicate, *params, timeout = None, **args):
        #print("sleep", self, get_ident(), "   condition lock:", self._WakeUp._lock, "...")
        t1 = None if timeout is None else time.time() + timeout
        while (t1 is None or time.time() < t1):
            if predicate(*params, **args):
                return
            delta = None
            if t1 is not None:
                delta = max(0.0, t1 - time.time())
            self.sleep(delta)
        else:
            raise Timeout()
            
    # await is a reserved word in Python 3, use "wakeup" instead
    @synchronized
    def wakeup(self, n=1, all=True, function=None, arguments=()):
        if function is not None:
            function(*arguments)
        if all:
            self._WakeUp.notifyAll()
        else:
            self._WakeUp.notify(n)

if sys.version_info < (3,0):
    # await is a reserved word in Python 3, keep it for backward compatibility
    # in Python 2.
    setattr(Primitive, "await", Primitive.sleep)


class PyThread(Thread, Primitive):
    def __init__(self, *params, name=None, **args):
        Thread.__init__(self, *params, **args)
        Primitive.__init__(self, name=name)

class TimerThread(PyThread):
    def __init__(self, function, interval, *params, **args):
        PyThread.__init__(self, daemon=True)
        self.Interval = interval
        self.Func = function
        self.Params = params
        self.Args = args
        self.Pause = False

    def run(self):
        while True:
            while self.Pause:
                self.sleep()
            self.Func(*self.Params, **self.Args)
            time.sleep(self.Interval)
    
    def pause(self):
        self.Pause = True
        
    def resume(self):
        self.Pause = False
        self.wakeup()
                
            
            
