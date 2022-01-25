from .core import PyThread, synchronized
from .promise import Promise
from threading import Timer
import subprocess

def to_str(b):
    if isinstance(b, str):
        return b
    elif isinstance(b, bytes):
        return b.decode("utf-8")
    else:
        return b

class Subprocess(PyThread):
    
    def __init__(self, *params, tag=None, input=None, daemon=None, timeout=None, **kv):
        PyThread.__init__(self, daemon=daemon)    # timeout will be passed to the run()
        self.Params = params
        self.KV = kv
        self.Killed = False
        self.Subrocess = None
        self.Daemon = daemon
        self.Promise = None
        self.Input = input
        self.Timeout = timeout
        self.Tag = tag          # used to identify the Promise
        
    def run(self):
        timeout = self.Timeout
        #print("Subprocess.run(): timeout:", timeout)
        kv = self.KV.copy()
        kv["stderr"] = subprocess.PIPE
        kv["stdout"] = subprocess.PIPE
        
        self.Subprocess = subprocess.Popen(*self.Params, **kv)
        if self.Input is not None:
            self.Subprocess.stdin.write(self.Input)

        killer = None
        if timeout is not None:
            killer = Timer(timeout, self.killme)
            killer.start()          # do not start killer until self.Subprocess is set
            #print("killer started")

        out, err = self.Subprocess.communicate()
        out = to_str(out)
        err = to_str(err)
        retcode = self.Subprocess.returncode

        with self:
                # make this a critical section so the killer process does not intercept us
                if killer is not None:  
                    try:    killer.cancel()
                    except: pass
                self.Subprocess = None
                
        if self.Killed:
            exc = RuntimeError("timeout")
            if self.Promise is not None:
                self.Promise.exception(RuntimeError, exc, None)
                self.Promise = None
            raise exc

        if self.Promise:
            self.Promise.complete((retcode, out, err))
            self.Promise = None
        return retcode, out, err

    def start(self):
        self.Promise = Promise(self.Tag)
        PyThread.start(self)
        return self.Promise
        
    @synchronized
    def killme(self):
        if self.Subprocess is not None and self.Subprocess.returncode is None:
            self.Subprocess.terminate()
            self.Killed = True
        
class ShellCommand(Subprocess):

    def __init__(self, command, tag=None, cwd=None, env=None, input=None, daemon=None, timeout=None):
        Subprocess.__init__(self, command, tag=tag,
            input=input, timeout=timeout, 
            shell=True, close_fds=True,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            stdin=None if input is None else suprocess.PIPE,
            cwd=cwd, env=env, daemon=daemon)

    @staticmethod
    def execute(command, cwd=None, env=None, input=None, timeout=None, daemon=True):
        s = ShellCommand(command, cwd=cwd, env=env, input=input, daemon=daemon, timeout=timeout)
        return s.run()
    
        