# Calculate needed Vpp from desired H1 magnetic field. 
# Derek Fujimoto
# December 2017

from tkinter import *
from tkinter import ttk
from bfit import logger_name
import numpy as np
import webbrowser
import logging
import bfit
from bdata.calc import nmr_B1

# =========================================================================== #
class calculator_nmr_B1(object):
    
    # ======================================================================= #
    def __init__(self, commandline=False):
        """Draw window for calculating needed Vpp from desired H1 magnetic field."""
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
        # root 
        if commandline: root = Tk()
        else:           root = Toplevel()
        
        root.title("Gerald's Caculator")
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
        self.volt = StringVar()
        self.volt.set("")
        self.nu = StringVar()
        
        self.nu.set('41.27') # MHz
        
        # main frame
        mainframe = ttk.Frame(root, pad=5)
        mainframe.grid(column=0, row=0, sticky=(N, W))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        
        # Entry and other objects
        title_line = ttk.Label(mainframe,   
                text='BNMR Magnetic Oscillating Field -- '+\
                     'Antenna Voltage (peak-peak)', 
                     justify=CENTER)
        self.entry_field = Entry(mainframe, textvariable=self.field, width=10, 
                justify=RIGHT)
        gauss = ttk.Label(mainframe, text='Gauss')
        equals = ttk.Label(mainframe, text='=')
        self.entry_voltage = Entry(mainframe, textvariable=self.volt, 
                width=10, justify=RIGHT)
        voltage = ttk.Label(mainframe, text='millivolts')
        
        # frequency input
        freq_frame = ttk.Frame(root, pad=5)
        
        freq1 = ttk.Label(freq_frame, text='Freq:')
        self.entry_freq = Entry(freq_frame, textvariable=self.nu, width=10, 
                                    justify=RIGHT)
        freq2 = ttk.Label(freq_frame, text='MHz')
        
        freq1.grid(column=0, row=0, padx=5)
        self.entry_freq.grid(column=1, row=0, padx=5)
        freq2.grid(column=2, row=0, padx=5)
        
        # caveat
        warning = ttk.Label(root, 
                            text='WARNING: Calculation only valid for runs \n'+\
                                 'with silver antenna (before Sept 2019)', 
                            justify=CENTER)
        
        # Gridding
        title_line.grid(        column=0, row=0, padx=5, pady=5, columnspan=5)
        freq_frame.grid(        column=0, row=1, padx=5, pady=5, columnspan=5)
        self.entry_field.grid(  column=0, row=2, padx=5, pady=5, sticky=E)
        gauss.grid(             column=1, row=2, padx=5, pady=5, sticky=E)
        equals.grid(            column=2, row=2, padx=20, pady=5, sticky=(E, W))
        self.entry_voltage.grid(column=3, row=2, padx=5, pady=5, sticky=W)
        voltage.grid(           column=4, row=2, padx=5, pady=5, sticky=W)
        warning.grid(           column=0, row=2, padx=5, pady=5, columnspan=5)
        
        self.root = root
        
        # tie key release to calculate 
        self.entry_field.bind('<KeyRelease>', self.calculate)
        self.entry_voltage.bind('<KeyRelease>', self.calculate)
        
        # mainloop
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
        
        # get freqeuency
        nu = float(self.nu.get())
        
        # convert field to voltage
        if focus_id == str(self.entry_field):        
            try:
                field = float(self.field.get())
                value, err = nmr_B1(gauss=field, freq=nu)
                self.volt.set("%9.6f" % np.around(value, 6))
                
                self.logger.debug('Field of %g G converted to voltage of %g mV', 
                                 field, value)
            except ValueError:
                self.volt.set('')
        
        # convert voltage to field
        elif focus_id == str(self.entry_voltage):        
            try:
                voltage = float(self.volt.get())
                value, err = nmr_B1(mV=voltage, freq=nu)
                self.field.set("%9.6f" % np.around(value, 6))
                
                self.logger.debug('Voltage of %g mV converted to field of %g G', 
                                 voltage, value)
            except ValueError:
                self.field.set('')
