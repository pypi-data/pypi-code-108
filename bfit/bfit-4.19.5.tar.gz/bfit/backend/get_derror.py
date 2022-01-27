# Do numeral derivative error propagation
# Derek Fujimoto
# Nov 2021

import numpy as np
import jax
jax.config.update('jax_platform_name', 'cpu')

def get_derror(fn, par, err):
    """
        Propagate errors through a function with the Monte Carlo method
        
        fn: function handle with prototype fn(*par), returns scalar
            note: the function must call jax.numpy functions, not numpy functions
        par: list of parameters passed to fn
        err: list of errors for each parameter (same length and order)
    """
    
    # get gradient functions
    grad_fns = [jax.grad(fn, i) for i in range(len(par))]
    
    # evaluate gradients
    par = np.array(par, dtype=float)
    grad_val = np.array([g(*par) for g in grad_fns])
    
    # calculate error
    err = np.sqrt(np.sum((grad_val*err)**2))
    
    return err
