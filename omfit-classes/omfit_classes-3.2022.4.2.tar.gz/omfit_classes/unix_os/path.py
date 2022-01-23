import os as _os
from os.path import *


def join(a, *p):
    return '/'.join([a] + list(p))


join.__doc__ = _os.path.join.__doc__


for _item in ['normpath', 'abspath']:
    _str = f'''
def {_item}(path):
    return _os.path.{_item}(path).replace('\\\\', '/')

{_item}.__doc__ = _os.path.{_item}.__doc__
'''
    exec(_str)
