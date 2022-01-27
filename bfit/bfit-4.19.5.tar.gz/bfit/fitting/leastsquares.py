# Least squares class for minuit minimizer
# Derek Fujimoto
# Oct 2020

from scipy.misc import derivative 
import numpy as np


class LeastSquares:

    def __init__(self, fn, x, y, dy=None, dx=None, dy_low=None, dx_low=None, 
                 fn_prime=None, fn_prime_dx=1e-6):
        """
            fn: function handle. f(x, a, b, c, ...)
            x:              x data
            y:              y data
            dy:             error in y
            dx:             error in x
            dy_low:         used only if error in y is asymmetric. If not none, dy is upper error
            dx_low:         used only if error in y is asymmetric. If not none, dx is upper error
            fn_prime:       function handle for the first derivative of fn. f'(x, a, b, c, ...)
            fn_prime_dx:    spacing in x to calculate the derivative in the case of the default calculation
        """
        self.fn = fn
        self.x = np.asarray(x, dtype=np.float)
        self.y = np.asarray(y, dtype=np.float)
        self.n = len(x)
        
        # set derivative
        if fn_prime is None:
            self.fn_prime = lambda x, *pars : derivative(func=self.fn, x0=x, 
                                                         dx=fn_prime_dx, n=1, order=3, 
                                                         args=pars)
        else:
            self.fn_prime = fn_prime
        
        # set errors
        has_dy = False
        if dy is not None:
            has_dy = True
            self.dy = np.asarray(dy)
        
        has_dx = False    
        if dx is not None:
            has_dx = True
            self.dx = np.asarray(dx)
        
        # asymmetric errors
        has_dy_asym = False
        if dy_low is not None:
            
            if dy is None:
                has_dy = True
                self.dy = dy_low
            else:
                has_dy_asym = True
                self.dy_low = np.asarray(dy_low)
        
        has_dx_asym = False
        if dx_low is not None:
            if dx is None:
                has_dx = True
                self.dx = np.asarray(dx_low)
            else:
                has_dx_asym = True
                self.dx_low = np.asarray(dx_low)
        
        # set least squares function
        if not any((has_dy, has_dx)):
            self.__call__ = self.ls_no_errors
        
        elif has_dx_asym and has_dy_asym:
            self.__call__ = self.ls_dxa_dya
        
        elif all((has_dx_asym, has_dy)) and not has_dy_asym:
            self.__call__ = self.ls_dxa_dy
        
        elif all((has_dy_asym, has_dx)) and not has_dx_asym:
            self.__call__ = self.ls_dx_dya
        
        elif has_dx_asym and not has_dy:
            self.__call__ = self.ls_dxa
        
        elif has_dy_asym and not has_dx:
            self.__call__ = self.ls_dya
        
        elif all((has_dy, has_dx)) and not any((has_dx_asym, has_dy_asym)):
            self.__call__ = self.ls_dxdy
        
        elif has_dy and not has_dx:
            self.__call__ = self.ls_dy

        elif has_dx and not has_dy:
            self.__call__ = self.ls_dx    
        
        else:
            raise RuntimeError("Missing error assignment case")
     
    def __call__(self, *pars):
        return self.__call__(*pars)
        
    def ls_no_errors(self, *pars):
        return np.sum(np.square(self.y - self.fn(self.x, *pars)))
            
    def ls_dy(self, *pars):
        return np.sum(np.square((self.y -self.fn(self.x, *pars)) / self.dy))
    
    def ls_dx(self, *pars):
        fprime = self.fn_prime(self.x, *pars)
        num = np.square(self.y - self.fn(self.x, *pars))
        den = np.square(self.dx*fprime)
        
        return np.sum(num/den)        

    def ls_dxdy(self, *pars):
        fprime = self.fn_prime(self.x, *pars)
        num = np.square(self.y - self.fn(self.x, *pars))
        den = np.square(self.dx*fprime) + np.square(self.dy)
        return np.sum(num/den)   
             
    def ls_dya(self, *pars):
        
        # get errors on appropriate side of the function
        idx = self.y > self.fn(self.x, *pars)
        dy = np.array(self.dy)
        dy[idx] = self.dy_low[idx]
        
        num = np.square(self.y - self.fn(self.x, *pars))
        den = np.square(dy)
        return np.sum(num/den)        
  
    def ls_dxa(self, *pars):
        fprime = self.fn_prime(self.x, *pars)
        dx = 0.5*(self.dx+self.dx_low)
        num = np.square(self.y - self.fn(self.x, *pars))
        den = np.square(dx*fprime)
        return np.sum(num/den)        
       
    def ls_dx_dya(self, *pars):
        fprime = self.fn_prime(self.x, *pars)
        
        # get errors on appropriate side of the function
        idx = self.y > self.fn(self.x, *pars)
        dy = np.array(self.dy)
        dy[idx] = self.dy_low[idx]
        
        num = np.square(self.y - self.fn(self.x, *pars))
        den = np.square(self.dx*fprime) + np.square(dy)
        return np.sum(num/den)    
        
    def ls_dxa_dy(self, *pars):
        fprime = self.fn_prime(self.x, *pars)
        
        dx = 0.5*(self.dx+self.dx_low)
        
        num = np.square(self.y - self.fn(self.x, *pars))
        den = np.square(dx*fprime) + np.square(self.dy)
        return np.sum(num/den)    
        
    def ls_dxa_dya(self, *pars):
        fprime = self.fn_prime(self.x, *pars)
        dx = 0.5*(self.dx+self.dx_low)
        
        # get errors on appropriate side of the function
        idx = self.y > self.fn(self.x, *pars)
        dy = np.array(self.dy)
        dy[idx] = self.dy_low[idx]
        
        num = np.square(self.y - self.fn(self.x, *pars))
        den = np.square(dx*fprime) + np.square(dy)
        return np.sum(num/den)    
        
