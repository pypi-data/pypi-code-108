import os, sys
from collections import OrderedDict
import re

class logtrace:
    def __init__(self, func):
        self.func = func
    
    def __call__(self, *args, **kwargs):
        if not os.path.isdir('.DebuggingLog'):
            os.mkdir('.DebuggingLog')
            num = 0
        elif not os.listdir('.DebuggingLog/'):
            num = 0
        else:
            loglist = os.listdir('.DebuggingLog/')
            
            lognumbers = []
            for log in loglist:
                if re.search(r'debugging\.log', log):
                    lognumbers.append(int(log[13:]))
            if len(lognumbers) == 0:
                num = 0
            else:
                num = max(lognumbers) + 1

        stdout_restore = sys.stdout                                         # Save the current stdout so that we can revert sys.stdou after we complete
        sys.stdout = open(f'.DebuggingLog/debugging.log{num}', 'w')          # Redirect sys.stdout to the file
        """
        file info overview!
        """
        forlooplog = kwargs['forlooplog']
        logs = kwargs['logs']           # logs : self.logs in Debugger
        lognames = kwargs['lognames']     # lognames : self.namespace in Debugger
        
        print('* FILE NAME :', sys.argv[0])
        print('* BREAK POINT', set(logs.keys()))
        for key in logs:
            obj = logs[key]
            print(f'  * {key} : 0~{len(obj)-1}')
        
        print('\n* [1]-----------------------------------------------DETAILS INFO(attributes)-------------------------------------------*')
        
        """
        write, here!
        """
        for key, values in logs.items():
            for i, obj in enumerate(values):
                print(f'\n[{key}][{i}] - {i}th object')
                print(f'===========================')

        sys.stdout.close()              # Close the file
        sys.stdout = stdout_restore     # Restore sys.stdout to our old saved file handler      
        print(f'.DebuggingLog/debugging.log{num} file was sucessfully created!')
        return self.func(*args, **kwargs)


class Debugger:
    def __init__(self):
        self.forlooplog = list()
        self.namespace = list()
        self.logs = OrderedDict()
        self.callcount = -1

    def __call__(self, *objs, **kwargs):
        self.callcount += 1
        self.logs[kwargs['logname']] = objs

        self.forlooplog.append(objs)
        if 'logname' in kwargs:
            self.namespace.append(f'[debug{self.callcount}] '+kwargs['logname'])
        else:
            self.namespace.append(f'[debug{self.callcount}] Untitled')

    def __del__(self):
        self.logwriter(None,
                       forlooplog=self.forlooplog,
                       lognames=self.namespace,
                       logs=self.logs)
    
    @logtrace
    def logwriter(self, *args, **kwargs):
        pass


def main():
    dic = {1:1, 2:2, 3:3, 4:[1,2,3,4,5], 5:{'a':1, 'b':2, 'c':{3:3, 'a':1, 'b':2, 'ed':23}}}
    
    debugger = Debugger()
    debugger(dic, logname='here')
    del debugger


if __name__ == "__main__":
    main()
