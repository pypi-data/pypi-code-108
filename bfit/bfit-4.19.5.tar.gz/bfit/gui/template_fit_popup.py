
# Model the fit results with a function
# Derek Fujimoto
# August 2019

from tkinter import *
from tkinter import ttk, messagebox

import logging, re, os, warnings
import weakref as wref
import numpy as np
import pandas as pd

from bfit import logger_name
from bfit.backend.entry_color_set import on_focusout, on_entry_click
from bfit.backend.raise_window import raise_window
import bfit.backend.colors as colors

# ========================================================================== #
class template_fit_popup(object):
    """
        Base class for fitting popup windows 
        
        bfit
        fittab
        logger
        
        entry:              Text, text entry for user
        entry_label:        Label, instructions above input text box
        input_fn_text:      string, text defining input functions
        left_frame:         Frame, for additional details 
        
        
        output_par_text     text, detected parameter names
        output_text         dict, keys: p0, blo, bhi, res, err, value: tkk.Text objects
       
        output_par_text_val string, contents of output_par_text
        
        reserved_pars:      dict, define values in bdata that can be accessed
        right_frame:        Frame, for input and actions
        win:                Toplevel
    """
    
    # default parameter values on new parameter
    default_parvals = { 'p0':1, 
                        'blo':-np.inf, 
                        'bhi':np.inf, 
                        'res':np.nan, 
                        'err':np.nan}
    
    window_title = 'Base class popup window'

    # ====================================================================== #
    def __init__(self, bfit, input_fn_text=''):
        
        self.bfit = bfit
        self.input_fn_text = input_fn_text
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
        # draw window
        self.logger.debug('Initialization success. Starting mainloop.')
    
    # ====================================================================== #
    def show(self):
        """
            Show window
        """
        bfit = self.bfit
        
        # make a new window
        self.win = Toplevel(bfit.mainframe)
        self.win.title(self.window_title)
        frame = ttk.Frame(self.win, relief='sunken', pad=5)
        left_frame = ttk.Frame(frame)
        right_frame = ttk.Frame(frame)

        # set icon
        self.bfit.set_icon(self.win)

        # Key bindings
        self.win.bind('<Control-Key-Return>', self.do_return)
        self.win.bind('<Control-Key-KP_Enter>', self.do_return)
        
        # Text entry
        entry_frame = ttk.Frame(right_frame, relief='sunken', pad=5)
        self.entry_label = ttk.Label(entry_frame, justify=LEFT, 
                                text='')
        self.entry = Text(entry_frame, width=60, height=13, state='normal')
        self.entry.bind('<KeyRelease>', self.get_input)
        scrollb = Scrollbar(entry_frame, command=self.entry.yview)
        self.entry['yscrollcommand'] = scrollb.set
        
        # Insert default text
        self.entry.insert('1.0', self.input_fn_text.strip())
         
        # gridding
        scrollb.grid(row=1, column=1, sticky='nsew')
        self.entry_label.grid(column=0, row=0, sticky=W)
        self.entry.grid(column=0, row=1)
        
        # grid to frame
        frame.grid(column=0, row=0)
        left_frame.grid(column=0, row=0, sticky=(N, S))
        right_frame.grid(column=1, row=0, sticky=(N, S))
        entry_frame.grid(column=0, row=0, sticky=(N, E, W), padx=1, pady=1)
        
        # initialize 
        self.left_frame = left_frame
        self.right_frame = right_frame
        
    # ====================================================================== #
    def cancel(self):
        self.win.destroy()
    
    # ====================================================================== #
    def do_return(self, *_):
        """
            Activated on press of return key
        """
        pass
        
    # ====================================================================== #
    def do_parse(self, *_):
        """
            Detect new global variables
            returns split lines, new parameter names 
        """
        
        # clean input
        text = self.input_fn_text.split('\n')
        text = [t.strip() for t in text if '=' in t]
        
        # check for no input
        if not text:
            return (None, None, None)
        
        # get equations and defined variables
        defined = [t.split('=')[0].strip() for t in text]
        eqn = [t.split('=')[1].strip() for t in text]
        
        # check for new parameters
        new_par = []
        for eq in eqn:
            lst = re.split('\W+', eq)    # split list non characters
            
            # throw out known things: numbers numpy equations
            delist = []
            for i, l in enumerate(lst):
                
                # check numpy functions
                if l == 'np':
                    delist.append(i)
                    delist.append(i+1)
                    continue
                
                # check integer
                try: 
                    int(l)
                except ValueError:
                    pass
                else:
                    delist.append(i)
                    continue
                
                # check variables
                if l in self.reserved_pars:  
                    delist.append(i)
                    continue
                    
            delist.sort()
            for i in delist[::-1]:
                try:
                    del lst[i]
                except IndexError:  # error raised on incomplete math: ex "np."
                    pass
                
            # look for non-parameters
            lst = [i for i in lst if i]
                
            new_par.append(lst)

        # logging
        self.logger.info('Parse found constraints for %s, and defined %s', 
                         sorted(defined), 
                         new_par)
                         
        return (defined, eqn, new_par)
    
    # ====================================================================== #
    def do_after_parse(self, defined=None, eqn=None, new_par=None):
        pass
        
    # ====================================================================== #
    def get_input(self, *_):
        """Get input from text box."""
        self.input_fn_text = self.entry.get('1.0', END)
        out = self.do_parse()
        self.do_after_parse(*out)
            
    # ====================================================================== #
    def yview(self, *args):
        """
            Scrollbar for all output text fields
        """
        self.output_par_text.yview(*args)
        for k in self.output_text:
            self.output_text[k].yview(*args)
