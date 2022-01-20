import sys, os
import h5py
from collections import OrderedDict
import pprint
import inspect
import re


class Attribute:
    def __init__(self, attrviewer=True, itercount=None, iterdepth=None):
        self.attrviewer = attrviewer
        self.itercount = itercount
        self.iterdepth = iterdepth

    def rc_get(self, obj, memory='', depth=0):
        if not self.iterdepth:
            if isinstance(obj, (h5py._hl.files.File, h5py._hl.group.Group, h5py._hl.dataset.Dataset)):
                self._rc_get_hdf5(obj, memory, depth)
            elif hasattr(obj, '__dict__') and len(obj.__dict__) != 0:
                self._rc_get_obj(obj, memory, depth)
            elif isinstance(obj, list):
                self._rc_get_list(obj, memory, depth)
            elif isinstance(obj, (dict, OrderedDict)):
                self._rc_get_dict(obj, memory, depth)
        else:
            if depth < self.iterdepth:
                if isinstance(obj, (h5py._hl.files.File, h5py._hl.group.Group, h5py._hl.dataset.Dataset)):
                    self._rc_get_hdf5(obj, memory, depth)
                elif hasattr(obj, '__dict__') and len(obj.__dict__) != 0:
                    self._rc_get_obj(obj, memory, depth)
                elif isinstance(obj, list):
                    self._rc_get_list(obj, memory, depth)
                elif isinstance(obj, (dict, OrderedDict)):
                    self._rc_get_dict(obj, memory, depth)

            elif depth >= self.iterdepth:
                return None


    def _rc_get_obj(self, obj, memory='', depth=0):
        if hasattr(obj, '__dict__') and len(obj.__dict__) != 0:
            if not len(memory) : print(f'\n- LENGTH(obj) : {len(vars(obj))}')
            else               : print(f'\n- LENGTH(obj~{memory}) : {len(vars(obj))}')
            ic = -1
            for key, attr in vars(obj).items():
                if not self.itercount:
                    if self.attrviewer:
                        if not len(memory):
                            print(f'.{key} : {attr}')
                        else:
                            print(f'{memory}.{key} : {attr}')
                    else:
                        if not len(memory):
                            print(f'.{key}')
                        else:
                            print(f'{memory}.{key}')
                else:
                    ic += 1
                    if ic == self.itercount:
                        break

                    if self.attrviewer:
                        if not len(memory):
                            print(f'.{key} : {attr}')
                        else:
                            print(f'{memory}.{key} : {attr}')
                    else:
                        if not len(memory):
                            print(f'.{key}')
                        else:
                            print(f'{memory}.{key}')

            self.spliter(n=depth)
            for key, attr in vars(obj).items():
                self.rc_get(attr, memory=memory+'.'+str(key), depth=depth+1)
        
        else:
            return None



    def _rc_get_list(self, obj, memory='', depth=0):
        if isinstance(obj, list):
            if not len(memory) : print(f'\n- LENGTH(obj) : {len(obj)}')
            else               : print(f'\n- LENGTH(obj~{memory}) : {len(obj)}')
            ic = -1
            for key, attr in enumerate(obj):
                if not self.itercount:
                    if self.attrviewer:
                        if not len(memory):
                            print(f'[{key}] : {attr}')
                        else:
                            print(f'{memory}[{key}] : {attr}')
                    else:
                        if not len(memory):
                            print(f'[{key}]')
                        else:
                            print(f'{memory}[{key}]')

                else:
                    ic += 1
                    if ic == self.itercount:
                        break

                    if self.attrviewer:
                        if not len(memory):
                            print(f'[{key}] : {attr}')
                        else:
                            print(f'{memory}[{key}] : {attr}')
                    else:
                        if not len(memory):
                            print(f'[{key}]')
                        else:
                            print(f'{memory}[{key}]')

            self.spliter(n=depth)
            for key, attr in enumerate(obj):
                self.rc_get(attr, memory=memory+'['+str(key)+']', depth=depth+1)
        
        else:
            return None



    def _rc_get_dict(self, obj, memory='', depth=0):
        if isinstance(obj, (dict, OrderedDict)):
            if not len(memory) : print(f'\n- LENGTH(obj) : {len(obj)}')
            else               : print(f'\n- LENGTH(obj~{memory}) : {len(obj)}')
            ic = -1
            for key, attr in obj.items():
                if not self.itercount:
                    if self.attrviewer:
                        if not len(memory):
                            if isinstance(key, str):
                                print(f'["{key}"] : {attr}')
                            else:
                                print(f'[{key}] : {attr}')
                        else:
                            if isinstance(key, str):
                                print(f'{memory}["{key}"] : {attr}')
                            else:    
                                print(f'{memory}[{key}] : {attr}')
                    else:
                        if not len(memory):
                            if isinstance(key, str):
                                print(f'["{key}"]')
                            else:
                                print(f'[{key}]')
                        else:
                            if isinstance(key, str):
                                print(f'{memory}["{key}"]')
                            else:    
                                print(f'{memory}[{key}]')
                
                else:
                    ic += 1
                    if ic == self.itercount:
                        break
                    
                    if self.attrviewer:
                        if not len(memory):
                            if isinstance(key, str):
                                print(f'["{key}"] : {attr}')
                            else:
                                print(f'[{key}] : {attr}')
                        else:
                            if isinstance(key, str):
                                print(f'{memory}["{key}"] : {attr}')
                            else:    
                                print(f'{memory}[{key}] : {attr}')
                    else:
                        if not len(memory):
                            if isinstance(key, str):
                                print(f'["{key}"]')
                            else:
                                print(f'[{key}]')
                        else:
                            if isinstance(key, str):
                                print(f'{memory}["{key}"]')
                            else:    
                                print(f'{memory}[{key}]')


            self.spliter(n=depth)
            for key, attr in obj.items():
                if isinstance(key, str):
                    self.rc_get(attr, memory=memory+'["'+str(key)+'"]', depth=depth+1)
                else:
                    self.rc_get(attr, memory=memory+'['+str(key)+']', depth=depth+1)
        else:
            return None


    def _rc_get_hdf5(self, obj, memory='', depth=0):
        if isinstance(obj, (h5py._hl.files.File, h5py._hl.group.Group)):
            if not len(memory) : print(f'\n- LENGTH(obj) : {len(obj.keys())}')
            else               : print(f'\n- LENGTH(obj~{memory}) : {len(obj.keys())}')
            ic = -1
            for key in obj.keys():
                if not self.itercount:
                    if self.attrviewer:
                        if not len(memory):
                            if isinstance(key, str):
                                print(f'["{key}"] : {obj[key]}')
                            else:
                                print(f'[{key}] : {obj[key]}')
                        else:
                            if isinstance(key, str):
                                print(f'{memory}["{key}"] : {obj[key]}')
                            else:    
                                print(f'{memory}[{key}] : {obj[key]}')
                    else:
                        if not len(memory):
                            if isinstance(key, str):
                                print(f'["{key}"]')
                            else:
                                print(f'[{key}]')
                        else:
                            if isinstance(key, str):
                                print(f'{memory}["{key}"]')
                            else:    
                                print(f'{memory}[{key}]')
                
                else:
                    ic += 1
                    if ic == self.itercount:
                        break
                    
                    if self.attrviewer:
                        if not len(memory):
                            if isinstance(key, str):
                                print(f'["{key}"] : {obj[key]}')
                            else:
                                print(f'[{key}] : {obj[key]}')
                        else:
                            if isinstance(key, str):
                                print(f'{memory}["{key}"] : {obj[key]}')
                            else:    
                                print(f'{memory}[{key}] : {obj[key]}')
                    else:
                        if not len(memory):
                            if isinstance(key, str):
                                print(f'["{key}"]')
                            else:
                                print(f'[{key}]')
                        else:
                            if isinstance(key, str):
                                print(f'{memory}["{key}"]')
                            else:    
                                print(f'{memory}[{key}]')


            self.spliter(n=depth)
            for key in obj.keys():
                if isinstance(key, str):
                    self.rc_get(obj[key], memory=memory+'["'+str(key)+'"]', depth=depth+1)
                else:
                    self.rc_get(obj[key], memory=memory+'['+str(key)+']', depth=depth+1)


        elif isinstance(obj, h5py._hl.dataset.Dataset):
            if not len(memory) : print(f'\n- LENGTH(obj) : {len(obj)}')
            else               : print(f'\n- LENGTH(obj~{memory}) : {len(obj)}')
            ic = -1
            for key, attr in enumerate(obj):
                if not self.itercount:
                    if self.attrviewer:
                        if not len(memory):
                            print(f'[{key}] : {attr}')
                        else:
                            print(f'{memory}[{key}] : {attr}')
                    else:
                        if not len(memory):
                            print(f'[{key}]')
                        else:
                            print(f'{memory}[{key}]')
                
                else:
                    ic += 1
                    if ic == self.itercount:
                        break
                    
                    if self.attrviewer:
                        if not len(memory):
                            print(f'[{key}] : {attr}')
                        else:
                            print(f'{memory}[{key}] : {attr}')
                    else:
                        if not len(memory):
                            print(f'[{key}]')
                        else:
                            print(f'{memory}[{key}]')


            self.spliter(n=depth)
            for key, attr in enumerate(obj):
                if isinstance(key, str):
                    self.rc_get(attr, memory=memory+'["'+str(key)+'"]', depth=depth+1)
                else:
                    self.rc_get(attr, memory=memory+'['+str(key)+']', depth=depth+1)

        else:
            return None

        

    @staticmethod
    def spliter(n, turn=False):
        split_line = '-'*(100 - 5*n)
        if turn==True:
            print(split_line)



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
        
        attrviewer = kwargs['attrviewer']
        itercount = kwargs['itercount']
        iterdepth = kwargs['iterdepth']
        logs = kwargs['logs']           # logs : self.logs in Debugger
        lognames = kwargs['lognames']     # lognames : self.namespace in Debugger
        
        print('* FILE NAME :', sys.argv[0])
        print('* BREAK POINT', set(logs.keys()))
        for key in logs:
            obj = logs[key]
            print(f'  * {key} : 0~{len(obj)-1}')
        
        print('\n* [1]-----------------------------------------------DETAILS INFO(attributes)-------------------------------------------*')
        attribute = Attribute(attrviewer=attrviewer, itercount=itercount, iterdepth=iterdepth)

        for key, values in logs.items():
            for i, obj in enumerate(values):
                print(f'\n[{key}][{i}] - {i}th object')
                print(f'===========================')
                print(attribute.rc_get(obj))

        print('\n* [2]-------------------------------------------------DETAILS INFO(method)---------------------------------------------*')

        for key, values in logs.items():
            for i, obj in enumerate(values):
                print(f'\n[{key}][{i}] - {i}th object')
                print(f'===========================')
                for idx, method in enumerate(inspect.getmembers(obj, inspect.ismethod)):
                    print(f'\n[{key}][{i}][{idx}] : obj.{method[0]}(*args, **kwargs)')
                    print(method)
                    print(inspect.getsource(getattr(obj, f'{method[0]}')))

        


        print('\n* [3]------------------------------------------------------FINAL LOG---------------------------------------------------*')
        
        for key, values in logs.items():
            for i, obj in enumerate(values):
                print(f'\n[{key}][{i}] - {i}th object')
                print(f'===========================')
                pprint.pprint(obj)

        sys.stdout.close()              # Close the file
        sys.stdout = stdout_restore     # Restore sys.stdout to our old saved file handler      
        print(f'.DebuggingLog/debugging.log{num} file was sucessfully created!')
        return self.func(*args, **kwargs)



class Debugger:
    def __init__(self, attrviewer=False, itercount=None, iterdepth=None):
        self.attrviewer = attrviewer
        self.itercount = itercount
        self.iterdepth = iterdepth
        self.attribute = list()
        self.forlooplog = list()
        self.namespace = list()
        self.logs = OrderedDict()
        self.callcount = -1

    def __call__(self, *obj, **kwargs):
        self.callcount += 1
        self.logs[kwargs['logname']] = obj

        self.forlooplog.append(obj)
        if 'logname' in kwargs:
            self.namespace.append(f'[debug{self.callcount}] '+kwargs['logname'])
        else:
            self.namespace.append(f'[debug{self.callcount}] Untitled')

    def __del__(self):
        self.logwriter(self.forlooplog,
                       lognames=self.namespace,
                       logs=self.logs,
                       attrviewer=self.attrviewer,
                       itercount=self.itercount,
                       iterdepth=self.iterdepth)

    @logtrace
    def logwriter(self, *args, **kwargs):
        pass



def main():
    obj = {1:1, 2:2, 3:3, 4:[1,2,3,4,5], 5:{'a':1, 'b':2, 'c':{3:3, 'a':1, 'b':2, 'ed':23}}}
    debugger = Debugger(attrviewer=True, itercount=3, iterdepth=3)
    debugger(obj, logname='dic')
    del debugger


if __name__ == "__main__":
    main()
