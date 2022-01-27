# Model the fit results with a function
# Derek Fujimoto
# Nov 2019


from tkinter import *
from tkinter import ttk, messagebox
from functools import partial

import logging, re, os, warnings
import jax
import numpy as np
import jax.numpy as jnp
import pandas as pd
import bdata as bd

from bfit.global_variables import KEYVARS
from bfit.global_variables import KEYVARS
from bfit.gui.template_fit_popup import template_fit_popup
from bfit.gui.InputLine import InputLine

jax.config.update('jax_platform_name', 'cpu')
jax.config.update("jax_enable_x64", True)

# ========================================================================== #
class popup_fit_constraints(template_fit_popup):
    """
        Popup window for settings fit parameters according to a function
        
        bfit
        fittab
        logger
        
        constraints_are_set bool, if true, constraints should be in place
        defined             list of str, defined parameter names
        eqn                 list of str, equations for each defined parameter
        
        input_error         Bool, if true don't allow contrain to run
        
        label_new_var       Label, show new variables
        label_defined       Label, show which variables will be redefined
        
        new_par             list of list of str, new parameter found in each eqn
        new_par_unique      list of str, new parameters, sorted
        
        output_par_text     text, detected parameter names
        output_text         dict, keys: p0, blo, bhi, res, err, value: tkk.Text objects
       
        output_par_text_val string, contents of output_par_text
        output_text_val     dict of strings, contents of output_text
       
        parnames:           list, function inputs
        reserved_pars:      dict, define values in bdata that can be accessed
        win:                Toplevel
    """

    # names of modules the constraints have access to
    modules = {'np':'numpy'}
    window_title = 'Constrain parameters'
    
    # default values
    defaults = {'p0':       1,
                'blo':      -np.inf,
                'bhi':      np.inf,
                'res':      np.nan,
                'dres+':    np.nan,
                'dres-':    np.nan,
                'chi':      np.nan,
                'fixed':    False,
                'shared':   False,
                }
    
    # ====================================================================== #
    def __init__(self, bfit, fittab, input_fn_text=''):
        
        super().__init__(bfit, input_fn_text)
        
        # initialize
        self.defined = []
        self.eqn = []
        self.new_par = []
        self.new_par_unique = []
        self.fittab = fittab
        self.input_error = False
        self.constraints_are_set = False
        
    # ====================================================================== #
    def add_fn(self, data):
        """
            Make a lambda function to add to data
        """
        
        # trivial end
        if not self.constraints_are_set:
            data.constrained = {}
            return
        
        # get variables in decreasing order of length (no mistakes in replace)
        varlist = np.array(list(KEYVARS.keys()))
        varlist = varlist[np.argsort(list(map(len, varlist))[::-1])]
    
        # make functions
        fns = {}
        for defined, eqn, new_par in zip(self.defined, self.eqn, self.new_par):
            
            # find constant names in the string, replace with constant
            for var in varlist:
                if var in eqn:
                    value = data.get_values(KEYVARS[var])[0]
                    eqn = eqn.replace(var, str(value))
            
            new_par.sort()
            f = 'lambda {new_par} : {equation}'
            f = f.format(new_par=','.join(new_par), 
                         equation=eqn)
                                       
            # replace numpy functions with jax.numpy functions
            f = f.replace('np.', 'jnp.')
                                      
            # evaluate functions string to python handle
            fns[defined] = (eval(f), new_par)
            
        data.constrained = fns
        
    # ====================================================================== #
    def add_new_par(self, data):
        """
            Add constrained parameters to data.fitpar
        """
        
        # clean nan rows
        for p in self.new_par_unique:
            if p in data.fitpar.index and all(data.fitpar.loc[p, ['p0', 'blo', 'bhi']].isna()):
                data.fitpar.drop(index=p, inplace=True)
        
        # check if no changes to input list
        if not any((p not in data.fitpar.index for p in self.new_par_unique)):
            return 
            
        # check if constrained
        if not self.constraints_are_set:
            return
        
        # add new parameters, looking for present values
        cols = InputLine.columns
        new_fit_par = {}
        new_par_added = []
        
        # iterate parameter names
        for c in cols:
            
            # get values
            values = []
            for par in self.new_par_unique:
                if par in data.fitpar.index:                    
                    values.append(data.fitpar.loc[par, c])
                else:
                    if par not in new_par_added:
                        new_par_added.append(par)
                    values.append(self.defaults[c])
                    
            # set values
            new_fit_par[c] = values
            
        data.set_fitpar(pd.DataFrame(new_fit_par, 
                                     index=self.new_par_unique)
                        )

    # ====================================================================== #
    def do_after_parse(self, defined=None, eqn=None, new_par=None):
        """
            show inputs as readback and save
        """
        
        if defined and defined is not None:
        
            # check defined variables
            ncomp = self.bfit.fit_files.n_component.get()
            fn_name = self.bfit.fit_files.fit_function_title.get()
            par_names = self.bfit.fit_files.fitter.gen_param_names(fn_name, ncomp)
            s = [d if d else '<blank>' for d in sorted(defined)]
            s = [d if d in par_names else '%s [ERROR: Bad parameter]' % d for d in s]
            s = '\n'.join(s)
            
            # check for errors
            self.input_error = 'ERROR' in s
            
            # set label
            self.label_defined.config(text=s)
            
            # check new variables
            s = sorted(np.unique(np.concatenate(new_par)))
            s = [i for i in s if i and i not in self.parnames]
            
            # show input
            self.label_new_var.config(text='\n'.join(s))
        
        else:
            self.label_defined.config(text='')
            self.label_new_var.config(text='')
            defined = []
            eqn = []
            new_par = []
            self.input_error = False
        
        # save
        self.defined = defined
        self.eqn = eqn
        self.new_par = new_par
        
        try:
            self.new_par_unique = sorted(np.unique(np.concatenate(new_par)))
            self.new_par_unique = list(map(str, self.new_par_unique))
        except ValueError:
            self.new_par_unique = []
    
    # ====================================================================== #
    def do_return(self, *_):
        """
            Activated on press of return key
        """
        self.set_constraints()

    # ====================================================================== #
    def drop_unused_param(self, data):
        """
            Remove rows from fitdata.fitpar if not constrained new_par
        """
        # get function input names
        fit_files = self.bfit.fit_files
        ncomp = fit_files.n_component.get()
        fn_title = fit_files.fit_function_title.get()
        pnames = sorted(fit_files.fitter.gen_param_names(fn_title, ncomp))
        
        # check if constrained, get parnames
        if self.constraints_are_set:
            pnames.extend(self.new_par_unique)
        
        # drop unused
        data.drop_unused_param(pnames)
        
    # ====================================================================== #
    def set_constraints(self):
        """
            Set up constraining parameter functions
        """
        
        # check for input errors
        if self.input_error:
            msg = 'Input error'
            self.logger.exception(msg)
            messagebox.showerror('Error', msg)
            raise RuntimeError(msg)
        
        # no constraints: enable all lines
        if not self.defined:                
            self.constraints_are_set = False
            self.fittab.populate()
            self.cancel()
            return
            
        # check for missing equations
        if any([e=='' for e in self.eqn]):
            defi = self.defined[self.eqn.index('')]
            msg = 'Missing equation for {d}'.format(d=defi)
            self.logger.exception(msg)
            messagebox.showerror('Error', msg)
            raise RuntimeError(msg)
        
        # check for circular definitions
        for d, e in zip(self.defined, self.eqn):
            if d in e:
                msg = 'Circular parameter definitions not allowed:'+\
                      '\n{d} = f({d}) is not allowed'.format(d=d)
                messagebox.showerror('Error', msg)
                self.logger.exception(msg)
                raise RuntimeError(msg)
        
        # check for more circular definitions
        for d in self.parnames:
            for e in self.eqn:
                if d in e:
                    msg = 'Reserved parameter "{p}" cannot be used as an input'.format(p=d)
                    self.logger.exception(msg)
                    messagebox.showerror('Error', msg)
                    raise RuntimeError(msg)
        
        # set flag
        self.constraints_are_set = True
        
        # populate 
        self.fittab.populate()
        
        # close
        self.cancel()
    
    # ====================================================================== #
    def set_init_button_state(self, fline):
        """
            Set the state of the gui_param_buttons in fit_lines
        """
        if self.constraints_are_set:
            state = 'disabled'
        else:
            state = 'normal'
        
        fline.gui_param_button.config(state=state)
            
    # ====================================================================== #
    def show(self):
        """
            show window
        """
        
        # show base class
        if not hasattr(self, 'win') or not Toplevel.winfo_exists(self.win):
            super().show()
        
        # Keyword parameters
        key_param_frame = ttk.Frame(self.left_frame, relief='sunken', pad=5)
        s = 'Reserved variable names:\n\n'
        self.reserved_pars = KEYVARS
        
        keys = list(self.reserved_pars.keys())
        descr = [self.reserved_pars[k] for k in self.reserved_pars]
        maxk = max(list(map(len, keys)))
        
        s += '\n'.join(['%s:   %s' % (k.rjust(maxk), d) for k, d in zip(keys, descr)])
        s += '\n'
        key_param_label = ttk.Label(key_param_frame, text=s, justify=LEFT)
        
        # fit parameter names 
        fit_param_frame = ttk.Frame(self.left_frame, relief='sunken', pad=5)
        s = 'Reserved function parameter names:\n\n'
        self.parnames = self.fittab.fitter.gen_param_names(
                                        self.fittab.fit_function_title.get(), 
                                        self.fittab.n_component.get())
        
        s += '\n'.join([k for k in sorted(self.parnames)]) 
        s += '\n'
        fit_param_label = ttk.Label(fit_param_frame, text=s, justify=LEFT)

        # module names 
        module_frame = ttk.Frame(self.left_frame, relief='sunken', pad=5)
        s = 'Reserved module names:\n\n'
        
        keys = list(self.modules.keys())
        descr = [self.modules[k] for k in self.modules]
        maxk = max(list(map(len, keys)))
        
        s += '\n'.join(['%s:   %s' % (k.rjust(maxk), d) for k, d in zip(keys, descr)])
        s += '\n'
        modules_label = ttk.Label(module_frame, text=s, justify=LEFT)
        
        # Text entry
        self.entry_label['text'] = 'Enter one constraint equation per line.'+\
                                 '\nNon-reserved words are shared variables.'+\
                                 '\nEx: "1_T1 = a*np.exp(b*BIAS**0.5)+c"'                                 
                
        # detected new parameters
        frame_detected = ttk.Frame(self.right_frame)
        label_defined_title = ttk.Label(frame_detected, text='Constrained parameters')
        label_new_var_title = ttk.Label(frame_detected, text='New variables')
        
        self.label_new_var = ttk.Label(frame_detected, text='')
        self.label_defined = ttk.Label(frame_detected, text='')
                
        # add constrain button
        button_constrain = ttk.Button(self.right_frame, text='Constrain', 
                                      command=self.set_constraints)
                
        # gridding
        key_param_label.grid(column=0, row=0)
        fit_param_label.grid(column=0, row=0)
        modules_label.grid(column=0, row=0)
        
        key_param_frame.grid(column=0, row=0, rowspan=1, sticky='ew', padx=1, pady=1)
        module_frame.grid(column=0, row=1, sticky='ew', padx=1, pady=1, rowspan=2)
        fit_param_frame.grid(column=0, row=3, sticky='ewns', padx=1, pady=1)
        
        frame_detected.grid(column=0, row=4, sticky='ewn', padx=1, pady=1)
        frame_detected.grid_columnconfigure(0, weight=1)
        frame_detected.grid_columnconfigure(1, weight=1)
        label_defined_title.grid(column=0, row=0, sticky='n', padx=1, pady=1)
        label_new_var_title.grid(column=1, row=0, sticky='n', padx=1, pady=1)
        self.label_defined.grid( column=0, row=1, sticky='n', padx=1, pady=1)
        self.label_new_var.grid( column=1, row=1, sticky='n', padx=1, pady=1)
        
        
        self.right_frame.grid_rowconfigure(4, weight=1)
        button_constrain.grid(column=0, row=5, sticky='ews', padx=1, pady=1)
        
        self.get_input()
        
    
