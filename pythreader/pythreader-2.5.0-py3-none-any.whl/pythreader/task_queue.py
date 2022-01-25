import time, traceback, sys
from .core import Primitive, PyThread, synchronized
from .dequeue import DEQueue
from threading import Timer

class TaskQueueDelegate(object):
    
    # abstract class
    
    def taskIsStarting(self, queue, task):
        pass

    def taskStarted(self, queue, task):
        pass

    def taskEnded(self, queue, task, result):
        pass

    def taskFailed(self, queue, task, exc_type, exc_value, tback):
        pass

class Task(Primitive):

    def __init__(self, name=None):
        Primitive.__init__(self, name=name)
        self.Created = time.time()
        self.Queued = None
        self.Started = None
        self.Ended = None
    
    #def __call__(self):
    #    pass

    def run(self):
        raise NotImplementedError
        
    @property
    def has_started(self):
        return self.Started is not None
        
    @synchronized
    @property
    def is_running(self):
        return self.Started is not None and self.Ended is None
        
    @synchronized
    @property
    def has_ended(self):
        return self.Started is not None and self.Ended is not None
        
    def start(self):
        self.Started = time.time()
        
    def end(self):
        self.Ended = time.time()
        
    def enqueue(self):
        self.Queued = time.time()

class FunctionTask(Task):

    def __init__(self, fcn, *params, **args):
        Task.__init__(self)
        self.F = fcn
        self.Params = params
        self.Args = args
        
    def run(self):
        return self.F(*self.Params, **self.Args)
        
class TaskQueue(Primitive):
    
    class ExecutorThread(PyThread):
        def __init__(self, queue, task):
            PyThread.__init__(self, daemon=True)
            self.Queue = queue
            self.Task = task
            
        def run(self):
            task = self.Task
            task.start()
            try:
                if callable(task):
                    result = task()
                else:
                    result = task.run()
                task.end()
                self.Queue.taskEnded(self.Task, result)
            except:
                task.end()
                exc_type, value, tb = sys.exc_info()
                self.Queue.taskFailed(self.Task, exc_type, value, tb)
            finally:
                self.Queue.threadEnded(self)
                self.Queue = None
                    
    def __init__(self, nworkers, capacity=None, stagger=None, tasks = [], delegate=None, name=None):
        Primitive.__init__(self, name=name)
        self.NWorkers = nworkers
        self.Threads = []
        self.Queue = DEQueue(capacity)
        self.Held = False
        self.Stagger = stagger or 0.0
        self.LastStart = 0.0
        self.StartTimer = None
        self.Delegate = delegate
        for t in tasks:
            self.addTask(t)

    def addTask(self, task, timeout = None):
        #print "addTask() entry"
        self.Queue.append(task, timeout=timeout)
        #print("queue.append done", self.counts())
        task.enqueue()
        self.startThreads()
        return self
        
    def __iadd__(self, task):
        return self.addTask(task)
        
    def __lshift__(self, task):
        return self.addTask(task)
        
    def insertTask(self, task, timeout = None):
        self.Queue.insert(task, timeout = timeout)
        task.enqueue()
        self.startThreads()
        return self
        
    def __rshift__(self, task):
        return self.insertTask(task)
        
    @synchronized
    def timer_fired(self):
        self.StartTimer = None
        self.startThreads()
        
    @synchronized
    def startThreads(self):
        #print "startThreads() entry"
        if not self.Held:
            while self.Queue \
                    and (self.NWorkers is None or len(self.Threads) < self.NWorkers) \
                    and not self.Held:
                if self.Stagger > 0.0:
                    delta = self.LastStart + self.Stagger - time.time()
                    #print "arming timer..."
                    if delta > 0.0:
                        if self.StartTimer is None:
                            self.StartTimer = Timer(delta, self.timer_fired)
                            self.StartTimer.daemon = True
                            self.StartTimer.start()
                        break
                self.LastStart = time.time()
                task = self.Queue.pop()
                t = self.ExecutorThread(self, task)
                t.kind = "%s.task" % (self.kind,)
                self.Threads.append(t)
                self.call_delegate("taskIsStarting", self, task)
                t.start()
                self.call_delegate("taskStarted", self, task)
                #print("thread started")
            
    @synchronized
    def threadEnded(self, t):
        #print("queue.threadEnded: ", t)
        if t in self.Threads:
            self.Threads.remove(t)
        self.startThreads()
        self.wakeup()
        
    def call_delegate(self, cb, *params):
        if self.Delegate is not None and hasattr(self.Delegate, cb):
            try:    getattr(self.Delegate, cb)(*params)
            except:
                traceback.print_exc(file=sys.stderr)
            
    def taskEnded(self, task, result):
        self.call_delegate("taskEnded", self, task, result)
        
    def taskFailed(self, task, exc_type, exc_value, tb):
        if self.Delegate is None:
            sys.stdout.write("Exception in task %s:\n" % (task, ))
            traceback.print_exception(exc_type, exc_value, tb, file=sys.stderr)
        else:
            self.call_delegate("taskFailed", self, task,  exc_type, exc_value, tb)
            
    @synchronized
    def waitingTasks(self):
        return list(self.Queue.items())
        
    @synchronized
    def activeTasks(self):
        return [t.Task for t in self.Threads]
        
    @synchronized
    def tasks(self):
        return self.waitingTasks(), self.activeTasks()
        
    def nrunning(self):
        return len(self.Threads)
        
    def nwaiting(self):
        return len(self.Queue)
        
    @synchronized
    def counts(self):
        return self.nwaiting(), self.nrunning()
        
    @synchronized
    def hold(self):
        self.Held = True
        
    @synchronized
    def release(self):
        self.Held = False
        self.startThreads()
        
    @synchronized
    def isEmpty(self):
        return len(self.Queue) == 0 and len(self.Threads) == 0
                
    def waitUntilEmpty(self):
        # wait until all tasks are done and the queue is empty
        if not self.isEmpty():
            while not self.sleep(function=self.isEmpty):
                pass
                
    join = waitUntilEmpty
                
    def drain(self):
        self.hold()
        self.waitUntilEmpty()
                
    @synchronized
    def flush(self):
        self.Queue.flush()
        self.wakeup()
            
    def __len__(self):
        return len(self.Queue)

