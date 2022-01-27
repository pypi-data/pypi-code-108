# Drawing style window
# Derek Fujimoto
# July 2018

from tkinter import *
from tkinter import ttk
from bfit import logger_name
import webbrowser
import logging

# ========================================================================== #
class popup_units(object):
    """
        Popup window for setting redraw period. 
        
        input:      dict:[StringVar, StringVar]
                    keyed by run mode, [conversion #, unit string]
    """

    # ====================================================================== #
    def __init__(self, parent):
        self.parent = parent    # fit_files pointer
        units = parent.units    # units dict from fit_files
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
        # make a new window
        self.win = Toplevel(parent.mainframe)
        self.win.title('Set Units')
        frame = ttk.Frame(self.win, relief='sunken', pad=5)
        topframe = ttk.Frame(frame, pad=5)

        # icon
        self.parent.set_icon(self.win)

        # Key bindings
        self.win.bind('<Return>', self.set)             
        self.win.bind('<KP_Enter>', self.set)

        # headers
        l_header = ttk.Label(topframe, text='Conversion', pad=5, justify=LEFT)
        l_header2 = ttk.Label(topframe, text='Unit', pad=5, justify=LEFT)

        # grid
        l_header.grid(column=1, row=0)
        l_header2.grid(column=2, row=0)

        # make entries
        self.input = {}    # [value StringVar, unit StringVar]
        r = 1
        for key in units.keys():
            
            l_val = ttk.Label(topframe, text=key, pad=5, justify=LEFT)
            self.input[key] = [StringVar(), StringVar()]
            
            for i in range(2):
                self.input[key][i].set(units[key][i])
                
            entry_val = Entry(topframe, textvariable=self.input[key][0], width=10, justify=RIGHT)        
            entry_uni = Entry(topframe, textvariable=self.input[key][1], width=7, justify=RIGHT)
            
            l_val.grid(column=0, row=r)
            entry_val.grid(column=1, row=r, padx=5)
            entry_uni.grid(column=2, row=r, padx=5)
            r += 1
            
        # instructions
        insr = ttk.Label(topframe, text='Set unit as "default" to disable', pad=5, justify=LEFT)
        
        # make objects: buttons
        set_button = ttk.Button(frame, text='Set', command=self.set)
        close_button = ttk.Button(frame, text='Cancel', command=self.cancel)
        
        # grid
        topframe.grid(column=0, row=0, columnspan=2, pady=10)
        insr.grid(column=0, row=r, columnspan=4); r+= 1
        
        set_button.grid(column=0, row=r, pady=10)
        close_button.grid(column=1, row=r, pady=10)
            
        # grid frame
        frame.grid(column=0, row=0)
        self.logger.debug('Initialization success. Starting mainloop.')
    
    # ====================================================================== #
    def set(self, *args):
        """Set entered values"""     
           
        self.logger.info('Setting')
        for key, value in self.input.items():
            self.parent.units[key] = [float(value[0].get()), value[1].get()]
        self.win.destroy()
        
    # ====================================================================== #
    def cancel(self):
        self.win.destroy()
