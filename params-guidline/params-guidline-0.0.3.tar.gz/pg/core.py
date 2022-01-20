import os
import sys
import json

class RootParam:
    def __init__(self):
        self.data = {}
        for p in sys.argv[1:]:
            
            if p[:2] != "--":
                raise Exception(f"Parameter {p} must start with '--'!")
            
            if not '=' in p:
                raise Exception(f"Parameter {p} must contain '='!")

            key, value = p[2:].split('=')
            self.data[key] = value


class Param:
    def __init__(self, key, kwargs):

        if key[:2] != "--":
            raise Exception(f"Parameter {key} must start with '--'!")
            
        self.key = key[2:]
        self.kwargs = kwargs
        self.value = None
        self.is_parent = False

    def __repr__(self):
        return self.value

    def check_value(self):
        if 'type' in self.kwargs:
            if not isinstance(self.value, self.kwargs['type']):
                try:
                    if self.kwargs['type'] == list:
                        self.value = self.value.split(',')
                    elif self.kwargs['type'] == bool:
                        if self.value in ['0', 'False', 'false', '']:
                            self.value = False
                        elif self.value in ['1', 'True', 'true']:
                            self.value = True
                        else:
                            raise
                    else: 
                        self.value = self.kwargs['type'](self.value)
                except:
                    raise TypeError(f"The value of attribute {self.key} must be of type {self.kwargs['type']}.")

        if 'condition' in self.kwargs:
            #print(str(inspect.getsourcelines(self.kwargs['condition'])[0][0]))
            if not self.kwargs['condition'](self.value):
                raise ValueError(f"The value of attribute {self.key} does not satisfy the condition.")

    def update_value(self, data=None):
        for a in data:
            if a == self.key:
                self.value = data[a]
                break
        else:
            if self.value is None and 'default' in self.kwargs:
                self.value = self.kwargs['default']
            else:
                raise Exception(f"{self.key} property requires a value.")

        self.check_value()
        return self.value


class JsonParam(Param):
    def __init__(self, key, kwargs):
        super().__init__(key, kwargs)
        self.is_parent = True


    def update_value(self, data=None):
        file_path = super().update_value(data=data)
        if not os.path.exists(file_path):
            raise FileExistsError(f"{file_path} is the wrong path.")
        
        with open(file_path, 'r') as f:
            self.data = json.load(f)

class TorchParam(Param):
    def __init__(self, key, kwargs):
        super().__init__(key, kwargs)
        self.is_parent = True

    def update_value(self, data=None):
        file_path = super().update_value(data=data)
        if not os.path.exists(file_path):
            raise FileExistsError(f"{file_path} is the wrong path.")
        
        import torch
        self.data = torch.load(file_path)


class Manager:
    def __init__(self):
        self.stack = []

    def add(self, param):
        self.stack.append(param)

    def __len__(self):
        return len(self.stack)

    def update(self):
        for p in self.stack:
            if p.is_parent:
                setattr(p.kwargs['parent'], p.key, p)
            else:
                setattr(p.kwargs['parent'], p.key, p.value)

        
        root = self.stack[0]
        while hasattr(root, 'kwargs'):
            root = root.kwargs['parent']
        
        return root


def decorator(param):
    
    def _decorator(args):
        if isinstance(args, tuple):
            args[1].add(param)
            return args[0], args[1]
        else:
            manager = Manager()
            manager.add(param)
            return args, manager
    return _decorator


def static_vars(**kwargs):
    def _decorater(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return _decorater

class pg:

    def parsing():
        pg.root = RootParam()
        pg.parent = pg.root
        def _decorator(args):
            if len(args[1]):
                params = args[1].update()
                return lambda: args[0](params) # main(args)
            else:
                return lambda: args[0]()       # main

        return _decorator

    def arg(name, **kwargs):
        kwargs['parent'] = pg.parent
        param = Param(name, kwargs)
        param.update_value(data=pg.parent.data)
        return decorator(param)

    class json:
        def parsing(name, **kwargs):
            kwargs['parent'] = pg.root
            param = JsonParam(name, kwargs)
            param.update_value(data=pg.root.data)
            setattr(pg, 'parent', param)
            return decorator(param)

    class torch:
        def parsing(name, **kwargs):
            kwargs['parent'] = pg.root
            param = TorchParam(name, kwargs)
            param.update_value(data=pg.root.data)
            setattr(pg, 'parent', param)
            return decorator(param)
