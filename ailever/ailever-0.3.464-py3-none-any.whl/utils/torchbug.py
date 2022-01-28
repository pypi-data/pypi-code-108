import os, sys
from collections import OrderedDict
import re
import torch

Obj = type('Obj', (), {})

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
                if re.search(r'torchbugging\.log', log):
                    lognumbers.append(int(log[16:]))
            if len(lognumbers) == 0:
                num = 0
            else:
                num = max(lognumbers) + 1

        stdout_restore = sys.stdout                                         # Save the current stdout so that we can revert sys.stdou after we complete
        sys.stdout = open(f'.DebuggingLog/torch_debugging.log{num}', 'w')          # Redirect sys.stdout to the file
        """
        file info overview!
        """
        calllogs = kwargs['calllogs']
        callcount = kwargs['callcount']
        finallogs = kwargs['finallogs']           # logs : self.logs in Debugger

        print('* FILE NAME :', sys.argv[0])
        print('* BREAK POINT', set(finallogs.keys()))
        for key in finallogs:
            objs = finallogs[key]
            print(f'  * {key} : 0~{len(objs)-1}')
        
        print('\n* [1]------------------------------------------------FINAL INFO(attributes)--------------------------------------------*')
        
        """
        write, here!
        """
        for key, objs in finallogs.items():
            for i, obj in enumerate(objs):
                tensor = obj
                print(f'\n[{key}][{i}] - {i}th object')
                print(f'===========================')
                print(f'[{tensor.type()}][{tensor.size()}] : {tensor}')
        
        print('\n* [2]-------------------------------------------------CALL INFO(attributes)--------------------------------------------*')
        
        for callcount, logname, objs in calllogs:
            print(f'[{callcount}][{logname}] {[obj.type(torch.FloatTensor).mean() for obj in objs]}')

        sys.stdout.close()              # Close the file
        sys.stdout = stdout_restore     # Restore sys.stdout to our old saved file handler      
        print(f'.DebuggingLog/torch_debugging.log{num} file was sucessfully created!')
        return self.func(*args, **kwargs)


class Torchbug:
    def __init__(self):
        self.calllogs = list()
        self.callcount = -1
        self.finallogs = OrderedDict()

    def __call__(self, *objs, **kwargs):
        self.callcount += 1
        self.calllogs.append((self.callcount, kwargs['logname'], objs))
        self.finallogs[kwargs['logname']] = objs

    def __del__(self):
        self.logwriter(None,
                       calllogs=self.calllogs,
                       finallogs=self.finallogs,
                       callcount=self.callcount)
    
    @logtrace
    def logwriter(self, *args, **kwargs):
        pass


def main():
    x = torch.tensor(0)
    w = torch.nn.Linear(3,3)

    epochs = 20
    torchbug = Torchbug()
    torchbug(x, logname='logname1')
    for epoch in range(epochs):
        for batch_idx, data in enumerate(range(1000)):
            tensor = torch.tensor(data)
            torchbug(w.weight.data, tensor, tensor, logname='logname2')
    del torchbug


if __name__ == "__main__":
    main()
