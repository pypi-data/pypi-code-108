# Calculate needed current from desired magnetic field. 
# Derek Fujimoto
# December 2017

from tkinter import *
from tkinter import ttk
import numpy as np
import webbrowser
import logging
import bfit
from bfit import logger_name
from bdata.calc import nqr_B0_hh3

# =========================================================================== #
class calculator_nqr_B0(object):
    
    # ======================================================================= #
    def __init__(self, commandline=False):
        """Draw window for Zaher's calculator"""
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
        # root 
        if commandline: root = Tk()
        else:           root = Toplevel()
        
        root.title("Zaher's Calculator")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # icon
        try:
            img = PhotoImage(file=bfit.icon_path)
            root.tk.call('wm', 'iconphoto', root._w, img)
        except Exception as err:
            print(err)

        # variables
        self.field = StringVar()
        self.field.set("")
        self.current = StringVar()
        self.current.set("")
        
        # main frame
        mainframe = ttk.Frame(root, pad=5)
        mainframe.grid(column=0, row=0, sticky=(N, W))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        
        # Entry and other objects
        title_line = ttk.Label(mainframe,   
                text='BNQR Magnetic Static Field -- Current Converter\nFor ILE2A1:HH3 (the older one)', 
                justify=CENTER)
        self.entry_field = Entry(mainframe, textvariable=self.field, width=10, 
                justify=RIGHT)
        gauss = ttk.Label(mainframe, text='Gauss')
        equals = ttk.Label(mainframe, text='=')
        self.entry_current = Entry(mainframe, 
                textvariable=self.current, width=10, justify=RIGHT)
        amperes = ttk.Label(mainframe, text='Amperes')
                
        link = ttk.Button(mainframe, 
                          text='Calibration Data Here', 
                          command=lambda : webbrowser.open(\
                                  'http://bnmr.triumf.ca/?file=HH_Calibration'))
        
        # Gridding
        title_line.grid(        column=0, row=0, padx=5, pady=5, columnspan=5)
        self.entry_field.grid(  column=0, row=1, padx=5, pady=5)
        gauss.grid(             column=1, row=1, padx=5, pady=5)
        equals.grid(            column=2, row=1, padx=20, pady=5)
        self.entry_current.grid(column=3, row=1, padx=5, pady=5)
        amperes.grid(           column=4, row=1, padx=5, pady=5)
        link.grid(              column=0, row=3, padx=5, pady=5, columnspan=5)
        
        self.root = root
        
        # tie key release to calculate 
        self.entry_current.bind('<KeyRelease>', self.calculate)
        self.entry_field.bind('<KeyRelease>', self.calculate)
        
        # runloop
        if commandline: 
            root.update()
            root.update_idletasks()
        else:
            self.logger.debug('Initialization success. Starting mainloop.')
            root.mainloop()
            
    # ======================================================================= #
    def calculate(self, *args):
        
        # check focus
        focus_id = str(self.root.focus_get())
        
        # convert field to current
        if focus_id == str(self.entry_field):        
            try:
                field = float(self.field.get()) 
                value, err = nqr_B0_hh3(gauss=field)
                self.current.set("%.4f" % np.around(value, 4))
                self.logger.debug('Field of %g G converted to current of %g A (HH3)', 
                                 field, value)
            except ValueError:
                self.current.set('')
            
        # convert current to field
        elif focus_id == str(self.entry_current):        
            try:
                current = float(self.current.get()) 
                value, err = nqr_B0_hh3(amps=current)
                self.field.set("%.4f" % np.around(value, 4))
                self.logger.debug('Current of %g A converted to field of %g G (HH3)', 
                                 current, value)
            except ValueError:
                self.field.set('debug')
