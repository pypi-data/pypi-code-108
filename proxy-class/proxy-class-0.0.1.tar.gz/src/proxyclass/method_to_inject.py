import inspect


def init_method(self, *args, **kwargs):
    ''' Initialize adapted objects defined in class annotations
    '''
    for arg, (key, value) in zip(args, self.__class__.__dict__['__annotations__'].items()):
        if inspect.isclass(value):
            if not isinstance(arg, value):
                raise TypeError(f'{arg} must be an instance of {value.__name__}')
            setattr(self, key, arg)

    for key, value in kwargs.items():
        obj = self.__class__.__dict__['__annotations__'].get(key, None)
        if obj is None:
            raise TypeError(f'{key} must be an instance of registered object')                
        if not isinstance(value, obj):
            raise TypeError(f'{key} must be an instance of {obj}')
        setattr(self, key, value)

    for key, value in self.__class__.__dict__['__annotations__'].items():
        if not inspect.isclass(value) and not inspect.isroutine(value):
            setattr(self, key, value)