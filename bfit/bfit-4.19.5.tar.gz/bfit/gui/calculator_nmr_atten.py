# Calculate needed current from desired magnetic field. 
# Derek Fujimoto
# December 2017

from tkinter import *
from tkinter import ttk
import numpy as np
import pandas as pd
import logging
import bfit
import os
from bfit import logger_name
from bfit.backend import colors
from bdata.calc import nmr_atten, get_atten_data

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# =========================================================================== #
class calculator_nmr_atten(object):
    
    # ======================================================================= #
    def __init__(self, commandline=False):
        """Draw window for Iain's calculator"""
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
        # root 
        if commandline: root = Tk()
        else:           root = Toplevel()
        
        root.title("Iain's Caculator")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        root.minsize(100, 100)

        # icon
        try:
            img = PhotoImage(file=bfit.icon_path)
            root.tk.call('wm', 'iconphoto', root._w, img)
        except Exception as err:
            print(err)

        # variables
        self.power = StringVar()
        self.power.set("")
        self.dac = StringVar()
        self.dac.set("")
        
        # load data
        self.data = get_atten_data()
        
        # main frame
        mainframe = ttk.Frame(root, pad=5)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(1, weight=1)
        
        # Entry and other objects
        entry_frame = ttk.Frame(mainframe)
        title_line = ttk.Label(entry_frame,   
                text='B-NMR RF Power -- DAC Linear Interpolation', 
                justify=CENTER)
        self.entry_power = Entry(entry_frame, textvariable=self.power, width=10, 
                justify=RIGHT)
        percent = ttk.Label(entry_frame, text='RF Power (%)')
        equals = ttk.Label(entry_frame, text='=')
        self.entry_dac = Entry(entry_frame, 
                textvariable=self.dac, width=10, justify=RIGHT)
        dac = ttk.Label(entry_frame, text='DAC Setpoint')

        # Gridding
        c = 1
        title_line.grid(        column=1, row=0, padx=5, pady=5, columnspan=5)
        percent.grid(           column=c, row=1, padx=5, pady=5); c+=1
        self.entry_power.grid(  column=c, row=1, padx=5, pady=5); c+=1
        equals.grid(            column=c, row=1, padx=20, pady=5); c+=1
        self.entry_dac.grid(    column=c, row=1, padx=5, pady=5); c+=1
        dac.grid(               column=c, row=1, padx=5, pady=5); c+=1
        
        entry_frame.columnconfigure([0, c], weight=1)
        
        # embed the data figure in the tk window
        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        
        ax.plot(self.data['rf_level_control (DAC)'], self.data['power (%)'], 'o', 
                color=colors.foreground)
        ax.set_ylabel('Normalized Antenna Readback (%)', fontsize='small', 
                color=colors.foreground)
        ax.set_xlabel('rf_level_control (DAC Setpoint)', fontsize='small', 
                color=colors.foreground)
        
        # text
        ax.text(0, 5, 'Data taken Oct 2018, M1354', color=colors.foreground, 
                fontsize='small')
        
        # set plot elements
        ax.set_facecolor(colors.background)
        fig.set_facecolor(colors.background)
        for loc in ['bottom', 'top', 'right', 'left']:
            ax.spines[loc].set_color(colors.foreground)
        ax.tick_params(axis='both', labelsize='small', colors=colors.foreground)
        
        canvas = FigureCanvasTkAgg(fig, master=mainframe)  # A tk.DrawingArea.
        canvas.draw()
        
        # grid onto mainframe
        entry_frame.grid(column=0, row=0, sticky=(E, W))
        canvas.get_tk_widget().grid(column=0, row=1, padx=5, pady=5, 
                                    sticky=(E, W, N, S))
        
        self.root = root
        
        # tie key release to calculate 
        self.entry_power.bind('<KeyRelease>', self.calculate)
        self.entry_dac.bind('<KeyRelease>', self.calculate)
        
        # runloop
        self.logger.debug('Initialization success. Starting mainloop.')
        
        if commandline:
            root.update()
            root.update_idletasks()
        else:
            root.mainloop()
        
    # ======================================================================= #
    def calculate(self, *args):
        
        # check focus
        focus_id = str(self.root.focus_get())
        
        # convert power to dac
        if focus_id == str(self.entry_power):        
            try:
                power = float(self.power.get()) 
                value = nmr_atten(power=power)
                self.dac.set("%d" % value)
                self.logger.debug('Power of %g converted to dac setpoint of %d', 
                                 power, value)
            except ValueError:
                self.dac.set('')
            
        # convert dac to power
        elif focus_id == str(self.entry_dac):        
            try:
                dac = int(self.dac.get()) 
                value = nmr_atten(dac=dac)
                self.power.set("%.4f" % np.around(value, 4))
                self.dac.set("%d" % int(dac))
                self.logger.debug('dac setpoint of of %d converted to power of %g', 
                                 dac, value)
            except ValueError:
                self.power.set('')
