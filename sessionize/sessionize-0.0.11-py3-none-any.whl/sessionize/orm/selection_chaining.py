def getitem_chaining(cls):
    """
    Class decorator that adds __getitem__ chaining.
    
    Example
    -------
    ChainList = getitem_chaining(list)
    cl = ChainList([[1, 2, 3], [4, 5, 6]])
    cl[1, 2] -> 6
    """
    class InnerCls(cls):
        def __getitem__(self, key):
            if isinstance(key, tuple):
                result = self
                for item in key:
                    result = result[item]
                return result
            return super().__getitem__(key)
    return InnerCls


def delitem_chaining(cls):
    """
    Class decorator that adds __delitem__ chaining.
    
    Example
    -------
    ChainList = delitem_chaining(list)
    cl = ChainList([[1, 2, 3], [4, 5, 6]])
    del cl[1, 2]
    cl -> [[1, 2, 3], [4, 5]]
    """
    class InnerCls(cls):
        def __delitem__(self, key):
            if isinstance(key, tuple):
                result = self
                for i, item in enumerate(key):
                    if i == len(key) - 1:
                        del result[item]
                        break
                    result = result[item]
            else:
                super().__delitem__(key)
    return InnerCls


def setitem_chaining(cls):
    """
    Class decorator that adds __setitem__ chaining.
    
    Example
    -------
    ChainList = setitem_chaining(list)
    cl = ChainList([[1, 2, 3], [4, 5, 6]])
    cl[1, 2] = 100
    cl -> [[1, 2, 3], [4, 5, 100]]
    
    """
    class InnerCls(cls):
        def __setitem__(self, key, value):
            if isinstance(key, tuple):
                result = self
                for i, item in enumerate(key):
                    if i == len(key) - 1:
                        result[item] = value
                        break
                    result = result[item]
            else:
                super().__setitem__(key, value)
    return InnerCls


def selection_chaining(cls):
    """
    Class decorator that adds __setitem__, __getitem__, and __delitem__ chaining.
    
    Example
    -------
    ChainList = selection_chaining(list)
    cl = ChainList([[1, 2, 3], [4, 5, 6]])
    cl[1, 2] -> 6
    
    cl[1, 2] = 100
    cl -> [[1, 2, 3], [4, 5, 100]]
    
    del cl[1, 1]
    cl -> [[1, 2, 3], [4, 100]]
    
    """
    cls = getitem_chaining(cls)
    cls = delitem_chaining(cls)
    return setitem_chaining(cls)