# Set function paramters from gui window
# Derek Fujimoto
# April 2019

from tkinter import *
from tkinter import ttk
from bfit import logger_name
from bfit.backend.FunctionPlacer import FunctionPlacer
from bfit.fitting.decay_31mg import fa_31Mg
import bfit.fitting.functions as fns

import matplotlib.pyplot as plt
import logging
import bdata as bd
import numpy as np

# ========================================================================== #
class popup_param(object):
    """
        Popup window for graphically finding input parameters. 
        
        bhi:            dictionary of StringVar objects to link parameters
        blo:            dictionary of StringVar objects to link parameters
        data:           bdata object 
        fig:            maplotlib figure object
        fitter:         fit_tab.fitter obje (defined in default_routines.py)
        first:          if True, first time through fixing parameters
        fname:          name of the function 
        lines:          dict of InputLine objects to link parameters
        logger:         logging variable
        mode:           1 or 2 to switch between run modes
        n_components:   number of components in the fit function
        parnames:       tuple of names of the parameters
        p0:             dictionary of StringVar objects to link parameters
        selection:      StringVar, track run selection
        win:            TopLevel window
        xy:             (x, asym, dasym) tuple
    """

    # parameter mapping
    parmap = {  '1_T1':'lam', 
                '1_T1b':'lamb', 
                'amp':'amp', 
                'beta':'beta', 
                'fraction_b':'fraction_b', 
                'baseline':'base', 
                'peak':'peak', 
                'fwhmA':'fwhm', 
                'fwhmB':'fwhm', 
                'height':'amp', 
                'heightA':'amp', 
                'heightB':'amp', 
                'sigma':'fwhm', 
                'mean':'peak', 
                'amp0':'amp0', 
                'amp1':'amp1', 
                'amp2':'amp2', 
                'amp3':'amp3', 
                'nu_0':'nu_0', 
                'nu_q':'nu_q', 
                'efgAsym':'eta', 
                'efgPhi':'phi', 
                'efgTheta':'theta', 
                'fwhm':'fwhm', 
             }

    # ====================================================================== #
    def __init__(self, bfit, id=''):
        self.bfit = bfit
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.info('Initializing gui param popup')
        
        # make a new window
        self.win = Toplevel(bfit.mainframe)
        self.win.title('Find P0')
        frame = ttk.Frame(self.win, relief='sunken', pad=5)
        
        # icon 
        self.bfit.set_icon(self.win)
        
        # Labels
        ttk.Label(frame, text="Select Run").grid(column=0, row=0, sticky=E)
        
        # box for run select
        self.selection = StringVar()
        select_box = ttk.Combobox(frame, textvariable=self.selection, 
                                  state='readonly')
        select_box.bind('<<ComboboxSelected>>', self.setup)
        
        # get run list
        runlist = list(self.bfit.fit_files.fit_lines.keys())
        runlist.sort()
        # ~ runlist = ['('+r.split('.')[0]+') '+r.split('.')[1] for r in runlist]
        select_box['values'] = runlist
        
        # gridding
        frame.grid(column=0, row=1, sticky=(N, W, E, S))
        select_box.grid(column=0, row=1, sticky=E)
        
        # start looking automatically
        if id:
            self.selection.set(id)
            self.setup()
            self.win.withdraw()
                
    # ====================================================================== #
    def setup(self, *args):
        """Get parameters for placing function and start the run squence"""
        
        # get run selection 
        run_id = self.selection.get()
        self.logger.info('Running P0 GUI finder on run %s', run_id)
        
        # get data
        self.data = self.bfit.data[run_id]
        mode = self.data.mode
        
        # mode switching
        if mode in ('20', '2h'):         self.mode = 2
        elif mode in ('1f', '2e', '1w', '1x'):  self.mode = 1
        else:
            self.logger.warning('P0 Finder not configured for run mode %s', mode)
            print('P0 Finder not configured for run mode %s'%mode)
        
        # make new window 
        self.fig = plt.figure()
        ax = self.fig.add_subplot(111)
        
        # draw data
        omit = self.data.omit.get()
        if omit == self.bfit.fetch_files.bin_remove_starter_line:
            omit = ''
        self.xy = self.data.asym(self.bfit.get_asym_mode(self.bfit.fit_files), 
                                 rebin=self.data.rebin.get(), omit=omit)
        ax.errorbar(*self.xy, fmt='.', color='k', ecolor='k')
        
        # plot elements - don't do tight_layout here - blocks matplotlib signals
        ax.set_ylabel('Asymmetry')
        if self.mode == 2:     ax.set_xlabel('Time')
        elif self.mode == 1:   ax.set_xlabel('Frequency')
        self.fig.show()
        
        # get parameters list and run finder 
        fit_tab = self.bfit.fit_files
        self.fitter = fit_tab.fitter
        self.n_components = fit_tab.n_component.get()
        self.fname = fit_tab.fit_function_title.get()
        self.parnames = self.fitter.gen_param_names(fn_name=self.fname, 
                                          ncomp=self.n_components)
        
        lines = fit_tab.fit_lines[run_id].lines
        self.lines = {line.pname:line  for line in lines}
        
        # make initial parameter list
        self.p0 =  {k:v.variable['p0']  for k, v in self.lines.items()}
        self.blo = {k:v.variable['blo'] for k, v in self.lines.items()}
        self.bhi = {k:v.variable['bhi'] for k, v in self.lines.items()}
        
        # check for zero width
        for k in self.p0.keys():
            if 'fwhm' in k or 'sigma' in k:
                if float(self.p0[k].get()) == 0:
                     self.p0[k].set('1e-9')                
        self.run()
        
    # ====================================================================== #
    def split_components(self, mixed):
        """
            Split a dictionary of parameter components into lists of the base 
            names to be used in invididual functions
        """
        
        split = []
        if self.n_components > 1:
            for i in range(self.n_components):
                element = {}
                for k in mixed.keys():
                    if 'base' in k:
                        element[self.parmap[k]] = mixed[k] 
                    elif str(i) in k:
                        element[self.parmap['_'.join(k.split('_')[:-1])]] = mixed[k] 
                split.append(element)
        else:
            split.append({self.parmap[k]:mixed[k] for k in mixed.keys()})
        
        return split
        
    # ====================================================================== #
    def run(self):
        """
            Run the function placer
            
            comp = component number to run
        """
        
        try:
            del self.fplace
        except AttributeError:
            pass
        else:
            self.fig.axes[0].cla()
            self.fig.axes[0].errorbar(*self.xy, fmt='.')
        
        # ensure matplotlib signals work. Not sure why this is needed.
        self.fig.tight_layout()
        
        # get paramters, translating the names
        p0 =  self.split_components(self.p0)
        blo = self.split_components(self.blo)
        bhi = self.split_components(self.bhi)
        
        # get fitting function 
        if self.fname == 'Lorentzian':
            fn = fns.lorentzian     # freq, peak, fwhm, amp
        elif self.fname == 'BiLorentzian':
            fn = lambda freq, peak, fwhm, amp : fns.bilorentzian(freq, peak, fwhm, amp/3, fwhm/3, amp*2/3)
        elif self.fname == 'Gaussian':
            fn = lambda freq, peak, fwhm, amp : fns.gaussian(freq, peak, fwhm, amp)
        elif self.fname == 'QuadLorentz':
            fn = lambda freq, nu_0, nu_q, eta, theta, phi, \
                        amp0, amp1, amp2, amp3, fwhm: \
                        fns.quadlorentzian(freq, nu_0, nu_q, eta, theta, phi, \
                        amp0, amp1, amp2, amp3, \
                        fwhm, fwhm, fwhm, fwhm, 
                        I = self.fitter.spin[self.fitter.probe_species])
                
        elif self.fname in ('Exp', 'Str Exp'):
            
            # get function
            pulse = self.data.pulse_s
            lifetime = bd.life[self.bfit.probe_species.get()]
        
            if self.fname == 'Exp':
                f1 = fns.pulsed_exp(lifetime=lifetime, pulse_len=pulse)
                
                if self.bfit.probe_species.get() == 'Mg31':
                    fn = lambda x, lam, amp : fa_31Mg(x, pulse)*f1(x, lam, amp)
                else:
                    fn = lambda x, lam, amp : f1(x, lam, amp)
            
            elif self.fname == 'Str Exp':
                f1 = fns.pulsed_strexp(lifetime=lifetime, pulse_len=pulse)
                
                if self.bfit.probe_species.get() == 'Mg31':
                    fn = lambda x, lam, amp, beta : fa_31Mg(x, pulse)*f1(x, lam, beta, amp)
                else:
                    fn = lambda x, lam, amp, beta : f1(x, lam, beta, amp)
        else:
            self.cancel()
            errormsg = 'Function "%s" not implemented in P0 Finder' % self.fname
            self.logger.warning(errormsg)
            messagebox.showerror("Error", errormsg)
            raise RuntimeError(errormsg)
        
        self.fig.canvas.mpl_connect('close_event', self.cancel)
        
        self.fplace = FunctionPlacer(fig=self.fig, 
                                     data=self.data, 
                                     fn_single=fn, 
                                     ncomp=self.n_components, 
                                     p0=p0, 
                                     fnname=self.fname, 
                                     asym_mode=self.bfit.get_asym_mode(self.bfit.fit_files), 
                                     endfn=self.endfn, 
                                     spin=self.fitter.spin[self.fitter.probe_species])
        
    # ====================================================================== #        
    def endfn(self, p0, base):
        """Set output fields"""
        
        for k in self.p0.keys():
            
            # skip baseline
            if 'base' in k:
                continue
            
            # single component
            if len(p0) == 1:
                i = 0
                key = k
        
            # multi component
            else:
                s = k.split('_')
                key = '_'.join(s[:-1])
                i = int(s[-1])                
                        
            # set p0     
            val = p0[i][self.parmap[key]]
            self.lines[k].set(p0=val)
                    
            # check bounds are ok
            blo = float(self.blo[k].get())
            bhi = float(self.bhi[k].get())
            
            if val < blo:   self.blo[k].set('-inf')
            elif val < bhi: self.bhi[k].set('inf')
        
        # baseline
        if 'baseline' in self.p0.keys():
            self.p0['baseline'].set(base)
            
            # check bounds are ok
            blo = float(self.blo['baseline'].get())
            bhi = float(self.bhi['baseline'].get())
            
            if base < blo:   self.blo['baseline'].set('-inf')
            elif base < bhi: self.bhi['baseline'].set('inf')
        
    # ====================================================================== #
    def cancel(self, *args):
        if hasattr(self, 'fplace'):  del self.fplace
        if hasattr(self, 'fig'):     
            plt.close(self.fig.number)
            del self.fig
        
        self.win.destroy()



