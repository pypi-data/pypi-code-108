# Function for calculating new user-defined parameters
# Derek Fujimoto
# Nov 2020

import jax
import jax.numpy as jnp
import numpy as np
from bfit.global_variables import KEYVARS
from bfit.backend.get_derror import get_derror

jax.config.update('jax_platform_name', 'cpu')
jax.config.update("jax_enable_x64", True)

# =========================================================================== # 
class ParameterFunction(object):
    """
        name:           name of the parameter being defined
        inputs:         list of strings for parameter inputs to equation
        equation:       function handle, the equation defining the parameter
    """
    
    # ======================================================================= # 
    def __init__(self, name, equation, parnames, bfit):
        """
            bfit:           pointer to bfit object
            name:           name of parameter which we are defining (LHS)
            equation:       string corresponding to equation RHS
            parnames:       list of strings for fit parameter names
        """
        self.bfit = bfit
        
        # equations and names
        self.name = name
        
        # get variables in decreasing order of length (no mistakes in replace)
        varlist = np.array(list(KEYVARS.keys()))
        varlist = varlist[np.argsort(list(map(len, varlist))[::-1])]
    
        # replace 1_T1 with lambda
        equation = equation.replace('1_T1', 'lambda1')
        
        self.parnames = list(parnames)
        for i, p in enumerate(self.parnames):
            self.parnames[i] = p.replace('1_T1', 'lambda1')
    
        # make list of input names from meta data
        self.inputs = []
        
        for var in varlist:
            if var in equation:
                self.inputs.append(var)
                
        # make list of input names from parameter names
        for var in self.parnames:
            if var in equation:
                self.inputs.append(var)
                
        # make equation
        input_str = ', '.join(self.inputs)
        equation = equation.replace('np.', 'jnp.')
        self.equation = eval('lambda %s : %s' % (input_str, equation))
        
        # add name to draw_components
        draw_comp = self.bfit.fit_files.draw_components
        if name in draw_comp:
            draw_comp.remove(name)
        draw_comp.append(name)
        
    # ======================================================================= # 
    def __call__(self, run_id):
        """ 
            Get data and calculate the parameter
        """
        
        inputs_val = {}
        inputs_err = {}
        for var in self.inputs:
            
            # get value for all data
            if var in KEYVARS:
                value, error = self._get_value(self.bfit.data[run_id], var)
            elif var in self.parnames:
                
                var_par = var.replace('lambda1', '1_T1')
                value = self.bfit.data[run_id].fitpar['res'][var_par]
                error1 = self.bfit.data[run_id].fitpar['dres+'][var_par]
                error2 = self.bfit.data[run_id].fitpar['dres-'][var_par]
                error = (error1+error2)/2
                    
            # set up inputs
            inputs_val[var] = value
            inputs_err[var] = error
                            
        # calculate the parameter
        val = self.equation(**inputs_val)
        
        order = self.equation.__code__.co_varnames
        inputs_val = [inputs_val[k] for k in order]
        inputs_err = [inputs_err[k] for k in order]
        err = get_derror(self.equation, inputs_val, inputs_err)
        
        return (val, err)
        
    # ======================================================================= # 
    def _get_value(self, data, name):
        """
            Tranlate typed constant to numerical value
        """
        new_name = KEYVARS[name]
        return data.get_values(new_name)
