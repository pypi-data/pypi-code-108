# Wrapper for easy usage of the iminuit Minuit object
# Derek Fujimoto
# Nov 2020

import inspect
import numpy as np
from iminuit import Minuit
from bfit.fitting.leastsquares import LeastSquares

class minuit(Minuit):
    """
        Chi squared minimization for function of best fit using iminuit
    """
    
    # ====================================================================== #
    def __init__(self, fn, x, y, dy=None, dx=None, dy_low=None, dx_low=None, 
                 fn_prime=None, fn_prime_dx=1e-6, name=None, start=None, 
                 error=None, limit=None, fix=None, print_level=1, **kwargs):
        """
            fn: function handle. f(x, a, b, c, ...)
            x:              x data
            y:              y data
            dy:             error in y
            dx:             error in x
            dy_low:         Optional, if error in y is asymmetric. If not none, dy is upper error
            dx_low:         Optional, if error in y is asymmetric. If not none, dx is upper error
            fn_prime:       Optional, function handle for the first derivative of fn. f'(x, a, b, c, ...)
            fn_prime_dx:    Spacing in x to calculate the derivative for default calculation
            name:           Optional sequence of strings. If set, use this for setting parameter names
            start:          Optional sequence of numbers. Required if the 
                                function takes an array as input or if it has 
                                the form f(x, *pars), and name is not defined. 
                                Default: 1, broadcasted to all inputs
            error           Optional sequence of numbers. Initial step sizes. 
            limit           Optional sequence of limits that restrict the range 
                                format: [[low, high], [low, high], ...]
                                in which a parameter is varied by minuit. 
                                with None, +/- inf used to disable limit
            fix             Optional sequence of booleans. Default: False
            print_level Set the print_level
                            0 is quiet. 
                            1 print out at the end of MIGRAD/HESSE/MINOS. 
                            2 prints debug messages.
                
            kwargs:         passed to Minuit.from_array_func.
                
                To set for parameter "a" one can also assign the following 
                keywords instead of the array inputs
                    
                    a = initial_value
                    error_a = start_error
                    limit_a = (low, high)
                    fix_a = True
        """
        
        # construct least squares object
        ls = LeastSquares(fn = fn, 
                        x = x, 
                        y = y, 
                        dy = dy, 
                        dx = dx, 
                        dy_low = dy_low, 
                        dx_low = dx_low, 
                        fn_prime = fn_prime, 
                        fn_prime_dx = fn_prime_dx)
        self.ls = ls

        # get number of data points
        self.npts = len(x)

        # detect function names
        if name is None:
            
            # get names from code
            name = inspect.getfullargspec(fn).args
            
            # remove self
            if 'self' in name: name.remove('self')
            
            # remove data input
            name = name[1:]
            
            # check for starting parameters
            if start is not None:
                
                # if they don't match assume array input to function
                try:
                    if len(start) != len(name):
                        name = ['x%d'%d for d in range(len(start))]
                
                # start is a scalar to be broadcasted
                except TypeError:
                    pass
                
            # check for bad input
            else:
                for n in name:
                    if '*' in n:
                        raise RuntimeError("If array input must define name or start")
                  
        # set starting values, limits, fixed, errors
        error, kwargs = self._set_start(array=error, 
                                        namestr='error_', 
                                        name=name, 
                                        kwargs=kwargs, 
                                        default=1)
                                        
        limit, kwargs = self._set_start(array=limit, 
                                        namestr='limit_', 
                                        name=name, 
                                        kwargs=kwargs, 
                                        default=[-np.inf, np.inf])
        
        fix, kwargs = self._set_start(  array=fix, 
                                        namestr='fix_', 
                                        name=name, 
                                        kwargs=kwargs, 
                                        default=False)
        
        # are there starting values, limits, fixed, errors?
        is_start = start is not None
        is_error = error is not None
        is_limit = limit is not None
        is_fix   = fix   is not None
        
        keys = kwargs.keys()
        
        # check limit depth 
        if is_start:    
            broadcast_start = get_depth(start) < 1
        
        # iterate parameter names
        for n in name:
            
            # index of name 
            nidx = list(name).index(n)
            
            # start
            if n not in keys:
                
                if is_start:
                    
                    if broadcast_start: kwargs[n] = start
                    else:               kwargs[n] = start[nidx]
                        
                else:
                    kwargs[n] = 1
                
        # make minuit object
        super().__init__(ls, 
                         name = name, 
                         **kwargs)
        
        # set errors, limits, fix
        if is_error:
            self.errors = error
        if is_limit:
            self.limits = limit
        if is_fix:
            self.fixed = fix
                        
        # set errordef for least squares minimization
        self.errordef = 1
        
        # set print level
        self.print_level = print_level
        
    # ====================================================================== #
    def _set_start(self, array, namestr, name, kwargs, default):
        """
            Set starting values, or broadcast if needed
        """
        
        depth = np.array(default).size
        
        # check kwargs for needed values
        items = list(kwargs.items())
        for key, value in items:
            if namestr in key:
                
                idx = list(name).index(key.split('_')[1])
                
                # make new array
                if array is None:   
                    array = [default]*len(name)
                    
                # try to assign if not list, broadcast
                if get_depth(array) < depth:
                    array = [array]*len(name)
                array[idx] = value
                    
                # remove value from kwargs
                del kwargs[key]
                
        return (array, kwargs)
        
    # ====================================================================== #
    @property
    def chi2(self):
        """
            Get the chi2 value
        """
        nfixed = sum(self.fixed)
        narg = len(self.values)
        dof = self.npts - narg + nfixed
        
        if dof <= 0:
            return np.nan
        else:
            return self.fval/dof
    
    # ====================================================================== #
    def get_merrors(self, attribute):
        """
            Get attributes from self.merrors as an array
            
            Valid attributes:
                at_lower_limit
                at_lower_max_fcn
                at upper_limit
                at_upper_max_fcn
                is_valid
                lower
                lower_new_min
                lower_valid
                min
                name
                nfcn
                number
                upper
                upper_new_min
                upper_valid
        """
        
        keylist = tuple(self.merrors.keys())
        
        # check attribute
        if attribute not in self.merrors[keylist[0]].__slots__:
            raise AttributeError('Attribute "%s" not found. Must be one of %s.'%\
                    (attribute, self.merrors[keylist[0]].__slots__))
        
        # get
        return np.array([getattr(self.merrors[k], attribute) for k in keylist])
        
    @property
    def mat_lower_limit(self): return self.get_merrors('at_lower_limit')
    @property
    def mat_lower_max_fcn(self): return self.get_merrors('at_lower_max_fcn')
    @property
    def mat_upper_limit(self): return self.get_merrors('at_upper_limit')
    @property
    def mat_upper_max_fcn(self): return self.get_merrors('at_upper_max_fcn')
    @property
    def mis_valid(self): return self.get_merrors('is_valid')
    @property
    def mlower(self): return self.get_merrors('lower')
    @property
    def mlower_new_min(self): return self.get_merrors('lower_new_min')
    @property
    def mlower_valid(self): return self.get_merrors('lower_valid')
    @property
    def mmin(self): return self.get_merrors('min')
    @property
    def mname(self): return self.get_merrors('name')
    @property
    def mnfcn(self): return self.get_merrors('nfcn')
    @property
    def mnumber(self): return self.get_merrors('number')
    @property
    def mupper(self): return self.get_merrors('upper')
    @property
    def mupper_new_min(self): return self.get_merrors('upper_new_min')
    @property
    def mupper_valid(self): return self.get_merrors('upper_valid')
        
def get_depth(lst, depth=0):
    try: 
        lst[0]
    except (IndexError, TypeError):
        return depth
    else:
        return get_depth(lst[0], depth+1)
        
        
        
        
