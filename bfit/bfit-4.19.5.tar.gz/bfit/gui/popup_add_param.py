# Model the fit results with a function
# Derek Fujimoto
# Nov 2019


from tkinter import *
from tkinter import ttk
from functools import partial

import logging, re, os, warnings
import numpy as np
import pandas as pd
import bdata as bd
import weakref as wref

from bfit import logger_name
from bfit.backend.entry_color_set import on_focusout, on_entry_click
from bfit.backend.raise_window import raise_window
from bfit.fitting.fit_bdata import fit_bdata
from bfit.backend.ParameterFunction import ParameterFunction as ParFnGenerator
from bfit.global_variables import KEYVARS
from bfit.gui.template_fit_popup import template_fit_popup
import bfit.backend.colors as colors

# ========================================================================== #
class popup_add_param(template_fit_popup):
    """
        Popup window for adding parameters for fitting or drawing
        
        bfit
        fittab
        logger
        
        input_fn_text       string: input lines
        
        new_par:            dict: {parname, string: par equation}
        set_par:            dict: {parname, fn handle: lambda : return new_par}
        parnames:           list, function inputs
        reserved_pars:      dict, define values in bdata that can be accessed
        win:                Toplevel
    """

    # names of modules the constraints have access to
    modules = {'np':'numpy'}
    
    window_title = 'Add parameter for fitting or drawing'
    
    # ====================================================================== #
    def __init__(self, bfit, input_fn_text=''):
        
        
        super().__init__(bfit, input_fn_text)
        super().show()
        
        self.fittab = bfit.fit_files
        self.set_par = {}
        self.new_par = {}
        
        # add button 
        add_button = ttk.Button(self.right_frame, text='Set Parameters', command=self.do_add)
        
        add_button.grid(column=0, row=1, sticky=(N, E, W, S), padx=20, pady=20)
        
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
        s = 'Reserved parameter names:\n\n'
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
        self.entry_label['text'] = 'Enter one parameter equation per line.'+\
                '\nLHS must use only reserved words, constants, or functions'+\
                '\nfrom the reserved modules in the parameter definition.'+\
                '\nEx: "mypar = 1/(1_T1*TEMP)"'+\
                '\n\nAccepts LaTeX input for the new parameter.'+\
                '\nEx: "$\eta_\mathrm{f}$ (Tesla) = B0 * np.exp(-amp**2)"' +\
                '\n\nValues taken as shown in fit results, with no unit scaling.'
                
        # gridding
        key_param_label.grid(column=0, row=0)
        fit_param_label.grid(column=0, row=0)
        modules_label.grid(column=0, row=0)
        
        key_param_frame.grid(column=0, row=0, rowspan=1, sticky=(E, W), padx=1, pady=1)
        module_frame.grid(column=0, row=1, sticky=(E, W), padx=1, pady=1, rowspan=2)
        fit_param_frame.grid(column=0, row=3, sticky=(E, W, N, S), padx=1, pady=1)
        
        self.logger.debug('Initialization success. Starting mainloop.')

    # ====================================================================== #
    def do_add(self, *_):
        """
            Add the parameter and the corresponding function
        """
        # reset draw comp
        self.bfit.fit_files.draw_components = list(self.bfit.draw_components)
        
        # set the parameters
        self.set_par = {}
        try:
            self.set_par = {p: ParFnGenerator(p, e, self.parnames, self.bfit) \
                        for p, e in self.new_par.items()}
        except SyntaxError: # on empty set
            pass
            
        self.logger.info('Added new parameters ', self.set_par)
        
        # update the lists
        self.bfit.fit_files.populate_param()
            
        # close the window
        self.cancel()
        
        # ====================================================================== #
    def do_after_parse(self, defined=None, eqn=None, new_par=None):
        
        # no input
        if defined is None:
            return
        
        # add result
        self.new_par = {k:e for k, e in zip(defined, eqn)}
        
    # ====================================================================== #
    def do_return(self, *_):
        return self.do_add()
    
