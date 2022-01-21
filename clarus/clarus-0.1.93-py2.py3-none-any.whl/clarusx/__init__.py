from __future__ import print_function

import sys

from clarus import services

class Ext(object):
    category=None
    
    def __init__(self, category):
      self.category = category
    
    def __getattr__(self,name):
        def fn(output=None, **params):
            return services.api_request(self.category, name, output=output, **params)
        return fn

extcache = {}

class Wrapper(object):
    def __init__(self, wrapped):
        self.wrapped = wrapped
    
    def __getattr__(self, name):
      # Perform custom logic here
        try:
            return getattr(self.wrapped, name)
        except AttributeError:
            if name in extcache:
                return extcache[name]
            ext = Ext(name)
            extcache[name] = ext
            return ext
        
sys.modules[__name__] = Wrapper(sys.modules[__name__])