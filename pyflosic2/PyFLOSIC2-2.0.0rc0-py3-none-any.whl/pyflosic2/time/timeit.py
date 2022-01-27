#!/usr/bin/env python
# Copyright 2020-2022 The PyFLOSIC Developers. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Sebastian Schwalbe <theonov13@gmail.com>
#
from time import time

# Decorator functions: timer


def timeit(f):
    """
        Decorator write to stdout
        -------------------------

        Input
        -----
        f : function
    """
    def f0(*args, **kwargs):
        before = time()
        res = f(*args, **kwargs)
        after = time()
        print('elapsed time ({}) = {:+.15f} [s]'.format(f.__qualname__, after - before))
        return res
    return f0


def tictoc(p):
    """
        Decorator write to log file
        ----------------------------
        Decorator depends on parameter instance (p)

        Input
        -----
        f : function
    """
    def timeit(f):
        def f0(*args, **kwargs):
            before = time()
            res = f(*args, **kwargs)
            after = time()
            p.log.write('elapsed time ({}) = {:+.15f} [s]'.format(f.__qualname__, after - before))
            return res
        return f0
    return timeit


class history():
    """
        magic
        -----
        Magically transforms a function 
        to a class instance. 
    """
    def __init__(self,f):
        self.f = f
        # Current values 
        self.rv = None
        self.t = None
        # History of values 
        self.RV = []
        self.T = []
        self.count = 0

    def __call__(self,*args,**kwargs):
        """
            __call__
            ---------
            Make a class instance callable. 
        """
        self._callme(self.f,*args,**kwargs)
        self._log(self.f,*args,**kwargs)
        return self.rv

    def _callme(self,f,*args,**kwargs):
        """
            _callme
            -------
            Perform the actual functional call 
            plus timing and counting. 
        """
        self.count += 1
        before = time()
        self.rv = f(*args,**kwargs)
        after = time()
        self.t = after - before
        self.RV.append(self.rv)
        self.T.append(self.t)

    def _log(self,f,*args,**kwargs):
        """
            _log
            ----
            Log the all information.
        """
        print('Function name: {}'.format(self.f.__qualname__))
        print('Doc string: {}'.format(self.f.__doc__))
        print('Function calls: {}'.format(self.count))
        #print('Input: {} {}'.format(*args,**kwargs))
        print('elapsed time ({}) = {:+.15f} [s]'.format(self.f.__qualname__, self.t))
        print('Output: {}'.format(self.rv))
        print(self.RV,self.T)


if __name__ == '__main__':
    from pyflosic2.parameters.flosic_parameters import parameters
    p = parameters()

    @tictoc(p)
    def f(x):
        return 1 + x
    f(2)
