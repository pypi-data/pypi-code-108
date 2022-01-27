# Deadtime set and calculate
# Derek Fujimoto
# Feb 2021

from tkinter import *
from tkinter import ttk, messagebox
from bfit import logger_name
import logging, webbrowser, textwrap, datetime
import bdata as bd
import numpy as np
import matplotlib.pyplot as plt

# ========================================================================== #
class popup_deadtime(object):
    """
        Popup window for finding and setting deadtime corrections. 
        
        Attributes: 
        
        bfit:       bfit object
        c:          Float, calculated helicity output
        chi:        StringVar, display chi2
        dt:         Float, calculated deadtime output
        logger:     logger 
        run:        IntVar, run number of run to fetch
        bfit.deadtime_switch:   BooleanVar, if true use calculated dt value
        win:        root Tk object
        year:       IntVar, year of run to fetch
        
    """

    # ====================================================================== #
    def __init__(self, bfit):
        self.bfit = bfit
        
        # set default deadtimes
        if bfit.deadtime_global.get():
            self.dt = bfit.deadtime*1e9
            self.c = 1
        else:
            self.dt = 0
            self.c = bfit.deadtime
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing')
        
         # make a new window
        self.win = Toplevel(bfit.mainframe)
        self.win.title('Find and set deadtime')
        frame = ttk.Frame(self.win, relief='sunken', pad=5)
        
        # icon
        bfit.set_icon(self.win)
        
        # Key bindings
        self.win.bind('<Return>', self.find)        
        self.win.bind('<KP_Enter>', self.find)
        self.win.bind('<Shift-Key-Return>', self.draw)        
        self.win.bind('<Shift-Key-KP_Enter>', self.draw)
        
        # Run entry ----------------------------------------------------------
        frame_run = ttk.Frame(frame, pad=5)
        
        label_year = ttk.Label(frame_run, text="Year:", pad=5, justify=LEFT)
        label_run  = ttk.Label(frame_run, text="Run:", pad=5, justify=LEFT)
        
        self.year = IntVar()
        self.run = IntVar()
        
        # set year and run
        self.year.set(self.bfit.fileviewer.year.get())
        self.run.set(self.bfit.fileviewer.runn.get())
        
        spin_year = Spinbox(frame_run, from_=2000, to=datetime.datetime.today().year, 
                            textvariable=self.year, width=7)
        spin_run = Spinbox(frame_run, from_=0, to=50000, textvariable=self.run, width=7)
        
        button_find = ttk.Button(frame_run, text='Find', command=self.find)
        button_draw = ttk.Button(frame_run, text='Draw', command=self.draw)
        
        # grid
        frame_run.grid(column=0, row=0, sticky='new', padx=2, pady=2)
        label_year.grid(column=0, row=1, sticky='nse', padx=2, pady=0)
        label_run.grid(column=0, row=2, sticky='nse', padx=2, pady=0)
        spin_year.grid(column=1, row=1, sticky='nse', padx=2, pady=2)
        spin_run.grid(column=1, row=2, sticky='nse', padx=2, pady=2)
        button_find.grid(column=3, row=1, rowspan=2, sticky='nws', padx=6, pady=2)
        button_draw.grid(column=4, row=1, rowspan=2, sticky='nws', padx=6, pady=2)
        
        frame_run.columnconfigure(2, weight=1)
        
        # input ---------------------------------------------------------------
        frame_input = ttk.Frame(frame, pad=5)
        
        label_dt = ttk.Label(frame_input, text='Deadtime (ns)', pad=2, justify=LEFT)
        label_c = ttk.Label(frame_input, text='Helicity Scaling (-)', pad=2, justify=LEFT)
        
        self.dt_inpt = StringVar()
        self.c_inpt = StringVar()
        
        self.dt_inpt.set('%g' % self.dt)
        self.c_inpt.set('%g' % self.c)
        
        entry_dt = Entry(frame_input, textvariable=self.dt_inpt, width=10, justify=RIGHT)
        entry_c =  Entry(frame_input, textvariable=self.c_inpt,  width=10, justify=RIGHT)
        
        entry_dt.bind('<KeyRelease>', self.read_dt)
        entry_c.bind('<KeyRelease>',  self.read_c)
        
        self.fix_dt = BooleanVar()
        self.fix_c = BooleanVar()
        
        self.fix_dt.set(False)
        self.fix_c.set(True)
        
        check_fix_dt = ttk.Checkbutton(frame_input, text='Fix', pad=5,
                            variable=self.fix_dt, onvalue=True, offvalue=False) 
        check_fix_c = ttk.Checkbutton(frame_input, text='Fix', pad=5,
                            variable=self.fix_c, onvalue=True, offvalue=False) 
        
        # gridding
        frame_input.grid(column=0, row=1, sticky='new', padx=2, pady=2)
        
        label_dt.grid(column=0, row=0, sticky='sew', padx=2)
        entry_dt.grid(column=1, row=0, sticky='sew', padx=2)
        check_fix_dt.grid(column=2, row=0, sticky='sew', padx=2)
        
        label_c.grid(column=0, row=1, sticky='sew', padx=2)
        entry_c.grid(column=1, row=1, sticky='sew', padx=2)
        check_fix_c.grid(column=2, row=1, sticky='sew', padx=2)
        
        # chi2 ----------------------------------------------------------------
        self.chi = StringVar()
        self.chi.set('')
        label_chi = ttk.Label(frame, textvariable=self.chi, pad=2, justify=LEFT)
        label_chi.grid(column=0, row=2, sticky='new', padx=2, pady=2)
        
        # global/local switch -------------------------------------------------
        self.check_global = ttk.Checkbutton(frame, 
                text='Using deadtime of %.3f ns\nglobally' % self.dt, 
                variable=self.bfit.deadtime_global, onvalue=True, offvalue=False, 
                pad=5, command=self.toggle_scope)
        self.check_global.grid(column=0, row=3, sticky='new', padx=2, pady=2)
            
        # apply correction ---------------------------------------------------
        self.check_corr = ttk.Checkbutton(frame, 
                text='Activate deadtime correction', 
                variable=self.bfit.deadtime_switch, onvalue=True, offvalue=False, 
                pad=5)
        self.check_corr.grid(column=0, row=4, sticky='new', padx=2, pady=0)
            
        # grid frames --------------------------------------------------------
        frame.grid(column=0, row=0)
        self.logger.debug('Initialization success. Starting mainloop.')
        
    # ====================================================================== #
    def draw(self, *args):
        """
            Draw deadtime corrected data
        """
        
        # get data
        try:
            data = bd.bdata(self.run.get(), self.year.get())
        except bd.InputError as msg:
            messagebox.showerror('Bad run input', str(msg))
            raise msg
        
        asym = data.asym('hel')
        asym_dt = data.asym('hel', deadtime=self.dt*1e-9)
        
        asym_dt['n'] = list(asym_dt['n'])
        asym_dt['n'][0] *= self.c
        asym_dt['n'][1] *= self.c
        
        
        # draw split helicity ------------------------------------------------
        plt.figure()
        plt.errorbar(asym['time_s'], *asym['p'], fmt='.C0', zorder=0, 
                     label='Uncorrected')
        plt.errorbar(asym['time_s'], *asym['n'], fmt='.C0', zorder=0)
        plt.errorbar(asym_dt['time_s'], *asym_dt['p'], fmt='.C3', zorder=5, alpha=0.4, 
                     label='Corrected')
        plt.errorbar(asym_dt['time_s'], *asym_dt['n'], fmt='.C3', zorder=5, alpha=0.4 )
        
        # plot elements
        plt.ylabel('Asymmetry')
        plt.xlabel('Time (s)')
        plt.title('Run %d.%d\nDeadtime correction of %.3f ns' % \
            (self.year.get(), self.run.get(), self.dt) +\
            '\nNeg Helicity Scaling of %.3f' % self.c,
            fontsize='x-small')
        plt.legend(fontsize='small')
        plt.tight_layout()
        
        # draw helicity difference -------------------------------------------
        dasym = 0.5*(asym['p'][0] + asym['n'][0])
        ddasym = 0.5*(asym['p'][1]**2 + asym['n'][1]**2)**0.5
        
        dasym_sub = dasym - np.mean(dasym)
        ddasym_sub = (dasym**2 + np.std(dasym)**2/len(dasym))**2
        
        dasym_dt = 0.5*(asym_dt['p'][0] + asym_dt['n'][0])
        ddasym_dt = 0.5*(asym_dt['p'][1]**2 + asym_dt['n'][1]**2)**0.5
        
        dasym_dt_sub = dasym_dt - np.mean(dasym_dt)
        ddasym_dt_sub = (dasym_dt**2 + np.std(dasym_dt)**2/len(dasym_dt))**2
        
        plt.figure()
        
        plt.errorbar(asym['time_s'], dasym_sub, ddasym_sub, fmt='.C0', zorder=0, 
                     label='Uncorrected')
        plt.errorbar(asym_dt['time_s'], dasym_dt_sub, ddasym_dt_sub, fmt='.C3', 
                     zorder=5, alpha=0.4, label='Corrected')
        
        plt.axhline(0, ls='-', color='k', zorder=10)
        
        # plot elements
        plt.ylabel(r'$\frac{1}{2}(\mathcal{A}_+ + c\mathcal{A}_-) - ' +\
                     r'\frac{1}{2} \overline{(\mathcal{A}_+ + c\mathcal{A}_-)}$', 
                     fontsize='small')
        plt.xlabel('Time (s)')
        plt.title('Run %d.%d\nDeadtime correction of %.3f ns' % \
            (self.year.get(), self.run.get(), self.dt) +\
            '\nNeg Helicity Scaling: c = %.3f' % self.c,
            fontsize='x-small')
        plt.legend(fontsize='small')
        plt.tight_layout()
        
    # ====================================================================== #
    def find(self, *args):
        """
            Find deadtime of entered run
        """
        
        # get data
        try:
            data = bd.bdata(self.run.get(), self.year.get())
        except RuntimeError as msg:
            messagebox.showerror('Bad run input', str(msg))
            raise msg
        
        # get fix state
        fixed = []
        if self.fix_dt.get():   fixed.append('dt')
        if self.fix_c.get():    fixed.append('c')
        
        # get initial values
        p0 = {'dt': self.dt*1e-9,
              'c':  self.c}
        
        # find the correction
        try:
            m = data.get_deadtime(**p0, fixed=fixed, return_minuit=True)
        except RuntimeError as msg:
            messagebox.showerror('Bad run input', str(msg))
            raise msg
        except bd.exceptions.MinimizationError as msg:
            messagebox.showerror('Minimization failed',str(msg))
            raise msg
        
        self.dt = m.values['dt_ns']
        self.c = m.values['c']
        chi2 = m.fval
        
        # set the strings
        self.dt_inpt.set('%f' % self.dt)
        self.c_inpt.set('%f' % self.c)
        self.chi.set('Flattening χ2 = %.3f' % chi2)
        
        # set the value
        self.toggle_scope()    
        
        # activate deadtime usage
        self.bfit.deadtime_switch.set(True)
        
    # ====================================================================== #
    def read_c(self, *args):
        """
            read float scaling factor values from text input
        """
        
        try:
            self.c = float(self.c_inpt.get())
        except ValueError:
            return
        
        self.toggle_scope()
        
    # ====================================================================== #
    def read_dt(self, *args):
        """
            read float deadtime values from text input
        """
        
        try:
            self.dt = float(self.dt_inpt.get())
        except ValueError:
            return
        
        self.toggle_scope()
    
    # ====================================================================== #
    def set_deadtime(self, *args):
        """
            Set the bfit deadtime value depending on the state of 
            bfit.deadtime_global
        """
        
        # set deadtime value for globally applied deadtime
        if self.bfit.deadtime_global.get():
            self.bfit.deadtime = self.dt*1e-9
        
        # set scaling factor for locally calculated deadtimes
        else:
            self.bfit.deadtime = self.c
            
    # ====================================================================== #
    def toggle_scope(self, *args):
        """
            Change the deadtime from globally applied to locally calculated for 
            each run
        """
        
        self.set_deadtime()
        
        if self.bfit.deadtime_global.get():            
            outstring = 'Using deadtime of %.3f ns\nglobally' % (self.bfit.deadtime*1e9)
            self.logger.info('Set bfit.deadtime to global %f s', self.bfit.deadtime)
        else:
            outstring = 'Using scaling of %.3f to find\ndeadtimes for each run' % self.bfit.deadtime    
            self.logger.info('Set bfit.deadtime to %f for local deadtime calculations', \
                             self.bfit.deadtime)
        
        self.check_global.config(text=outstring)
        
