# Data object for holding bdata and related file settings for drawing and 
# fitting. 
# Derek Fujimoto
# Nov 2018

from tkinter import *
from bdata import bdata, bmerged
from bdata.calc import nqr_B0_hh6, nqr_B0_hh3
from bfit import logger_name
from scipy.special import gamma, polygamma

from bfit.backend.raise_window import raise_window
from bfit.backend.get_derror import get_derror

import numpy as np
import pandas as pd

import bfit
import logging
import textwrap

# =========================================================================== #
# =========================================================================== #
class fitdata(object):
    """
        Hold bdata and related file settings for drawing and fitting in fetch 
        files tab and fit files tab. 
        
        Data Fields:
            
            base_bins:  n bins to use in baseline flatten (IntVar)
            bd:         bdata object for data and asymmetry (bdata)
            bfit:       pointer to top level parent object (bfit)
            bias:       platform bias in kV (float)
            bias_std:   platform bias in kV (float)
            
            check_draw_data: BooleanVar, draw data?
            check_draw_fit: BooleanVar, draw fit?
            check_draw_res: BooleanVar, draw residuals?
            check_state: BooleanVar, include in fit?
            
            chi:        chisquared from fit (float)
            constrained:dict of (fn handles, inputs (str)), keyed by names of 
                        constrained parameters
            dataline:   pointer to dataline object in fetch_files tab
            fitline:    pointer to fitline object in fit_files tab
            flip_asym:  BooleanVar, if true, invert asymmetry about 0
            drawarg:    drawing arguments for errorbars (dict)
            field:      magnetic field in T (float)
            field_std:  magnetic field standard deviation in T (float)
            fitfn:      function (function pointer)
            fitfnname:  function (str)
            fitpar:     initial parameters {column:{parname:float}} and results
                        Columns are fit_files.fitinputtab.collist
            id:         key for unique idenfication (str)    
            label:      label for drawing (StringVar)
            manually_updated_var: dict of epics, camp, ppg, containing dict of 
                        mvar which will not be updated on read
            mode:       run mode (str, ex: 1f)
            omit:       omit bins, 1f only (StringVar)
            omit_scan:  if true omit incomplete scan (BoolVar)
            parnames:   parameter names in the order needed by the fit function
            rebin:      rebin factor (IntVar)
            run:        run number (int)
            year:       run year (int)
              
    """
     
    # ======================================================================= #
    def __init__(self, bfit, bd):
        
        # get logger
        self.logger = logging.getLogger(logger_name)
        self.logger.debug('Initializing run %d (%d).', bd.run, bd.year)
        
        # top level pointers
        self.bfit = bfit
        self.dataline = None
        self.fitline = None
        
        # bdata access
        self.bd = bd
        
        # fetch files variables
        self.check_state = BooleanVar()
        self.rebin = IntVar()
        self.base_bins = IntVar()
        self.omit = StringVar()
        self.label = StringVar()
        self.check_draw_data = BooleanVar()
        self.check_draw_fit = BooleanVar()
        self.check_draw_res = BooleanVar()
        self.omit_scan = BooleanVar()
        self.flip_asym = BooleanVar()
        
        # fetch files defaults
        self.check_state.set(True)
        self.rebin.set(1)
        self.base_bins.set(0)
        self.omit.set('')
        self.label.set('')
        self.check_draw_data.set(True)
        self.check_draw_fit.set(False)
        self.check_draw_res.set(False)
        self.omit_scan.set(False)
        self.flip_asym.set(False)
        
        self.scan_repair_options = ''
        self.parnames = []
        
        # key for IDing file 
        self.id = self.bfit.get_run_key(data=bd)
        
        # initialize fitpar
        self.reset_fitpar()
        self.constrained = {}
        
        # reset manually set varaibles
        self.manually_updated_var = {'epics':{}, 'camp':{}, 'ppg':{}}
        
        # set area as upper
        self.area = self.area.upper()
        
        self.read()

    # ======================================================================= #
    def __getattr__(self, name):
        """Access bdata attributes in the case that fitdata doesn't have it."""
        try:
            return self.__dict__[name]
        except KeyError:
            return getattr(self.bd, name)
        
    # ======================================================================= #
    def asym(self, *args, **kwargs):
        """
            Get asymmetry
        """
        deadtime = 0
        
        # check if deadtime corrections are needed
        if self.bfit.deadtime_switch.get():
            
            # check if corrections should be calculated for each run
            if self.bfit.deadtime_global.get():
                deadtime = self.bfit.deadtime
            else:
                deadtime = self.bd.get_deadtime(c=self.bfit.deadtime, fixed='c')
        
        # set repair options 
        if 'scan_repair_options' not in kwargs.keys():
            s1 = 'omit' if self.omit_scan.get() else ''
            s2 = '%d' % self.base_bins.get()
            kwargs['scan_repair_options'] = '%s:%s' % (s1, s2)
        
        # rebin
        if 'rebin' not in kwargs.keys():
            kwargs['rebin'] = self.rebin.get()
        
        # omit
        if 'omit' not in kwargs.keys():
            omit = self.omit.get()
            if omit == self.bfit.fetch_files.bin_remove_starter_line:
                omit = ''
        
            kwargs['omit'] = omit
            
        # nbm
        if 'nbm' not in kwargs.keys():
            kwargs['nbm'] = self.bfit.use_nbm.get()
                          
        # hist select
        if 'hist_select' not in kwargs.keys():
            kwargs['hist_select'] = self.bfit.hist_select
                          
        # check for errors
        try:
            asym = self.bd.asym(*args, deadtime=deadtime, 
                                **kwargs)
        except Exception as err:
            messagebox.showerror(title=type(err).__name__, message=str(err))
            self.logger.exception(str(err))
            raise err from None
            
        # check if inversion is needed
        if self.flip_asym.get():
            if type(asym) in (tuple, np.ndarray):
                asym[1] = -1 * asym[1]
                
            else: # assume mdict
                
                for k, val in asym.items():
                    if k in 'pnfbc':
                        val = list(val)
                        val[0] = -1*val[0]
                        asym[k] = tuple(val)
                        
        return asym

    # ======================================================================= #
    @property
    def beam_kev(self): 
        try:
            return self.bd.beam_keV
        except AttributeError:
            return np.nan
    
    @property
    def beam_kev_err(self): 
        try:
            return self.bd.beam_keV_err
        except AttributeError:
            return np.nan
    
    # ======================================================================= #
    def draw(self, asym_type, figstyle='', asym_args=None, **drawargs):
        """
            Draw the selected file
            
            bfit:       bfit object
            asym_type:  input for asymmetry calculation
            figstyle:   figure style. One of "inspect", "data", "fit", or "param"
            drawargs:   passed to errorbar
        """
        
        self.logger.info('Drawing run %d (%d). mode: %s, rebin: %d, '+\
                     'asym_type: %s, style: %s, %s', 
                     self.run, 
                     self.year, 
                     self.mode, 
                     self.rebin.get(), 
                     asym_type, 
                     self.bfit.draw_style.get(), 
                     drawargs)
                
        # format
        if asym_args is None:
            asym_args = {}
                
        # useful pointers
        bfit = self.bfit
        plt = self.bfit.plt
        
        # convert asym type
        asym_type = self.bfit.asym_dict.get(asym_type, asym_type)
        
        # default label value
        if 'label' not in drawargs.keys():
            label = str(self.run)
        else:
            label = drawargs.pop('label', None)
            
        # set drawing style arguments
        for k in bfit.style:
            if k not in drawargs.keys():
                drawargs[k] = bfit.style[k]
        
        # get drawing style (ex: stack)
        draw_style = bfit.draw_style.get()
        
        # make new window
        if draw_style == 'new' or not plt.active[figstyle]:
            plt.figure(figstyle)
        elif draw_style == 'redraw':
            plt.clf(figstyle)
            
        ax = plt.gca(figstyle)
        
        # set axis offset
        try:
            ax.get_xaxis().get_major_formatter().set_useOffset(False)
        except AttributeError:
            pass
        
        # get asymmetry: raw scans
        if asym_type == 'r' and '1' in self.mode:
            a = self.asym('raw', **asym_args)
            x = np.arange(len(a.p[0]))
            idx_p = a.p[0]!=0
            idx_n = a.n[0]!=0
            
            # mouseover shows bin
            drawargs['annot_label'] = x[idx_p]
            
            xlabel = 'Bin'
            plt.errorbar(figstyle, self.id, x[idx_p], a.p[0][idx_p], a.p[1][idx_p], 
                    label=label+"($+$)", **drawargs)
            
            drawargs['unique'] = False
            drawargs['annot_label'] = x[idx_n]
            plt.errorbar(figstyle, self.id, x[idx_n], a.n[0][idx_n], a.n[1][idx_n], 
                    label=label+"($-$)", **drawargs)
            
        # do 2e mode
        elif self.mode == '2e':
            
            # get asym
            a = self.asym(**asym_args)
        
            # draw
            if asym_type in ["raw_c", "raw_h", "raw_hs"]:
                
                # make 3D axes
                if type(plt.gcf(figstyle)) == type(None):   
                    plt.figure(figstyle)
                ax = plt.gcf(figstyle).add_subplot(111, projection='3d', 
                                  label=str(len(plt.gcf(figstyle).axes)))
                
                # get rid of bad draw options
                try:                del drawargs['capsize']
                except KeyError:    pass
                try:                del drawargs['elinewidth']
                except KeyError:    pass
                
                # for every frequency there is a multiple of times
                x = np.asarray([[t]*len(a.freq) for t in a.time])
                x = np.hstack(x)
                
                # for every time there is a set of frequencies
                y = np.asarray([a.freq for i in range(len(a.raw_c[0][0]))])*1e-6
                y = np.hstack(y)
                    
                # draw combined asym
                if asym_type == "raw_c":
                
                    z = a.raw_c[0].transpose()
                    z = np.hstack(z)
                    fig = ax.plot(x, y, z, label=label, **drawargs)
                    
                elif asym_type == "raw_h":
                
                    z = a.raw_p[0].transpose()
                    z = np.hstack(z)
                    fig = ax.plot(x, y, z, label=label+' ($+$)', **drawargs)
                    
                    
                    z = a.raw_n[0].transpose()
                    z = np.hstack(z)
                    fig = ax.plot(x, y, z, label=label+' ($-$)', **drawargs)
                    
                elif asym_type == "raw_hs":
                
                    z = (a.raw_p[0]-a.raw_p[0][0]).transpose()
                    z = np.hstack(z)
                    fig = ax.plot(x, y, z, label=label+' ($+$)', **drawargs)
                    
                    z = (a.raw_n[0]-a.raw_n[0][0]).transpose()
                    z = np.hstack(z)
                    fig = ax.plot(x, y, z, label=label+' ($-$)', **drawargs)
                    
                # plot elements
                ax.set_xlabel('Time (ms)')
                ax.set_ylabel('Frequency (%s)' % bfit.units['2e'][1])
                
                if asym_type != "raw_hs":
                    ax.set_zlabel('Asymmetry')
                else:
                    ax.set_zlabel(r"Asym-Asym($\nu_{min}$)")
                ax.get_yaxis().get_major_formatter().set_useOffset(False)
                ax.get_xaxis().set_ticks(a.time)
            
            else:
                f = a.freq*bfit.units['2e'][0]
                if asym_type == 'sl_c':
                    plt.errorbar(figstyle, self.id, f, a.sl_c[0], a.sl_c[1], label=label, 
                                 **drawargs)
                    
                elif asym_type == 'dif_c':
                    plt.errorbar(figstyle, self.id, f, a.dif_c[0], a.dif_c[1], label=label, 
                                 **drawargs)
                    
                elif asym_type == 'sl_h':
                    plt.errorbar(figstyle, self.id, f, a.sl_p[0], a.sl_p[1], 
                                 label=label+' ($+$)', **drawargs)
                    
                                 
                    plt.errorbar(figstyle, self.id, f, a.sl_n[0], a.sl_n[1], 
                                 label=label+' ($-$)', **drawargs)
                    
                elif asym_type == 'dif_h':
                    plt.errorbar(figstyle, self.id, f, a.dif_p[0], a.dif_p[1], 
                                 label=label+' ($+$)', **drawargs)
                    
                    plt.errorbar(figstyle, self.id, f, a.dif_n[0], a.dif_n[1], 
                                 label=label+' ($-$)', **drawargs)
                    
                elif asym_type == 'sl_hs':
                    plt.errorbar(figstyle, self.id, f, a.sl_p[0]-a.sl_p[0][0], a.sl_p[1], 
                                 label=label+' ($+$)', **drawargs)
                    
                                 
                    plt.errorbar(figstyle, self.id, f, a.sl_n[0]-a.sl_n[0][0], a.sl_n[1], 
                                 label=label+' ($-$)', **drawargs)
                    
                    
                elif asym_type == 'dif_hs':
                    plt.errorbar(figstyle, self.id, f, a.dif_p[0]-a.dif_p[0][0], a.dif_p[1], 
                                 label=label+' ($+$)', **drawargs)
                    
                    
                    plt.errorbar(figstyle, self.id, f, a.dif_n[0]-a.dif_n[0][0], a.dif_n[1], 
                                 label=label+' ($-$)', **drawargs)
                    
                    
                plt.xlabel(figstyle, bfit.xlabel_dict[self.mode] % bfit.units['2e'][1])
                
                if '_hs' in asym_type:
                    plt.ylabel(figstyle, r"Asym-Asym($\nu_{min}$)")
                else:
                    plt.ylabel(figstyle, "Asymmetry")
            
        # get asymmetry: not raw scans, not 2e
        else:
            a = self.asym(**asym_args)
            
            # get x self
            if 'custom' in a.keys():
                x = a.custom
                unit = self.ppg.scan_var_histo_factor.units
                bfit.units[self.mode][1] = 'disable'
            else:
                x = a[bfit.x_tag[self.mode]]
                xlabel = bfit.xlabel_dict[self.mode]
            
            # get bfit-defined units
            if self.mode in bfit.units.keys() and bfit.units[self.mode][1].lower() \
                                                  not in ('default', 'disable'):                                                     
                unit = bfit.units[self.mode]
                xlabel = xlabel % unit[1]
            
            # get units for custom scans
            elif 'scan_var_histo_factor' in self.ppg.keys():
                unit = [self.ppg.scan_var_histo_factor.mean,
                        self.ppg.scan_var_histo_factor.units]     
                   
                # check custom name
                if 'customv_enable' in self.ppg.keys() and bool(self.ppg.customv_enable.mean):
                    xlabel = '%s (%s)' % (self.ppg.customv_name_write.units, unit[1])
                    
                # 1c runs custom name
                elif 'scan_device' in self.ppg.keys():
                    xlabel = '%s (%s)' % (self.ppg.scan_device.units, unit[1])
                
                # no name, use default
                else:
                    xlabel = xlabel % unit[1]
                        
            else:
                unit = [1, 'default']
                xlabel = xlabel % unit[1]
                        
            # unit conversions
            if self.mode in ('1n', '1w', '1c', '1d'): 
                x *= unit[0]
                
            elif self.mode in ('1f', '1x'): 
                
                # draw relative to peak 0
                if bfit.draw_rel_peak0.get():
                    
                    # get reference
                    par = self.fitpar
                    
                    if 'peak_0' in par.index:   index = 'peak_0'
                    elif 'mean_0' in par.index: index = 'mean_0'
                    elif 'peak' in par.index:   index = 'peak'
                    elif 'mean' in par.index:   index = 'mean'
                    else:
                        msg = "No 'peak' or 'mean' fit parameter found. Fit with" +\
                             " an appropriate function."
                        self.logger.exception(msg)
                        messagebox.showerror(msg)
                        raise RuntimeError(msg)
                    
                    ref = par.loc[index, 'res']
                    
                    # do the shift
                    x -= ref                    
                    x *= unit[0]
                    xlabel = 'Frequency Shift (%s)' % unit[1]
                    self.logger.info('Drawing as freq shift from peak_0')
                
                # ppm shift
                elif bfit.draw_ppm.get():
                    
                    # check div zero
                    try:
                        x = 1e6*(x-bfit.ppm_reference)/bfit.ppm_reference
                    except ZeroDivisionError as err:
                        self.logger.exception(str(msg))
                        messagebox.showerror(str(msg))
                        raise err
                    
                    self.logger.info('Drawing as PPM shift with reference %s Hz', 
                                     bfit.ppm_reference)
                    xlabel = 'Frequency Shift (PPM)'
                    
                else: 
                    x *= unit[0]
            
            # plot split helicities
            if asym_type == 'h':
                
                # remove zero asym
                ap = a.p[0]
                an = a.n[0]
                tag_p = ap!=0
                tag_n = an!=0
                tag_cmb = tag_p*tag_n
                
                # get average
                avg = np.mean(ap[tag_cmb]+an[tag_cmb])/2
                
                # draw
                plt.errorbar(figstyle, self.id, x[tag_p], ap[tag_p], 
                                a.p[1][tag_p], label=label+" ($+$)", **drawargs)
                plt.errorbar(figstyle, self.id, x[tag_n], an[tag_n], 
                            a.n[1][tag_n], label=label+" ($-$)", unique=False, 
                            **drawargs)
                plt.axhline(figstyle, 'line', avg, color='k', linestyle='--')
                
            # plot positive helicity
            elif asym_type == 'p':
                
                # remove zero asym
                ap = a.p[0]
                tag = ap!=0
                
                # draw
                plt.errorbar(figstyle, self.id, x[tag], ap[tag], a.p[1][tag], 
                                        label=label+" ($+$)", **drawargs)
                
            # plot negative helicity
            elif asym_type == 'n':
                
                # remove zero asym
                an = a.n[0]
                tag = an!=0
                
                # draw
                plt.errorbar(figstyle, self.id, x[tag], an[tag], a.n[1][tag], 
                                        label=label+" ($-$)", **drawargs)
                
            # plot forward counter
            elif asym_type == 'fc':
                
                # remove zero asym
                af = a.f[0]
                tag = af!=0
                
                # draw
                plt.errorbar(figstyle, self.id, x[tag], af[tag], a.f[1][tag], 
                                        label=label+" (Fwd)", **drawargs)
                
            # plot back counter
            elif asym_type == 'bc':
                                
                # remove zero asym
                ab = a.b[0]
                tag = ab!=0
                
                # draw
                plt.errorbar(figstyle, self.id, x[tag], ab[tag], a.b[1][tag], 
                                        label=label+" (Bck)", **drawargs)
            
            # plot right counter
            elif asym_type == 'rc':
                
                # remove zero asym
                ar = a.r[0]
                tag = ar!=0
                
                # draw
                plt.errorbar(figstyle, self.id, x[tag], ar[tag], a.r[1][tag], 
                                        label=label+" (Rgt)", **drawargs)
                
            # plot left counter
            elif asym_type == 'lc':
                                
                # remove zero asym
                al = a.l[0]
                tag = al!=0
                
                # draw
                plt.errorbar(figstyle, self.id, x[tag], al[tag], a.l[1][tag], 
                                        label=label+" (Lft)", **drawargs)
                
            # plot split helicities, shifted by baseline
            elif asym_type == 'hs':
                
                # remove zero asym
                ap = a.p[0]
                an = a.n[0]
                dap = a.p[1]
                dan = a.n[1]
                tag_p = ap!=0
                tag_n = an!=0
                ap = ap[tag_p]
                an = an[tag_n]
                dap = dap[tag_p]
                dan = dan[tag_n]
                
                # subtract last 5 values
                end = np.average(ap[-5:], weights=1/dap[-5:]**2)
                dend = 1/np.sum(1/dap[-5:]**2)**0.5
                
                ap -= end
                dap = ((dend)**2+(dap)**2)**0.5
                
                end = np.average(an[-5:], weights=1/dan[-5:]**2)
                dend = 1/np.sum(1/dan[-5:]**2)**0.5
                
                an -= end
                dan = ((dend)**2+(dan)**2)**0.5
                
                plt.errorbar(figstyle, self.id, x[tag_p], ap, dap, 
                        label=label+" ($+$)", **drawargs)
                plt.errorbar(figstyle, self.id, x[tag_n], an, dan, 
                        label=label+" ($-$)", unique=False, **drawargs)
                
            # plot split helicities, flipped about the average
            elif asym_type == 'hm':
                
                # remove zero asym
                ap = a.p[0]
                an = a.n[0]
                tag_p = ap!=0
                tag_n = an!=0
                tag_cmb = tag_p*tag_n
            
                avg = np.mean(ap[tag_cmb]+an[tag_cmb])/2
                
                plt.errorbar(figstyle, self.id, x[tag_p], a.p[0][tag_p], a.p[1][tag_p], 
                        label=label+" ($+$)", **drawargs)
                plt.errorbar(figstyle, self.id, x[tag_n], 2*avg-a.n[0][tag_n], a.n[1][tag_n], 
                        label=label+" ($-$)", unique=False, **drawargs)
                plt.axhline(figstyle, 'line', avg, color='k', linestyle='--')
            
            # plot split helicities, flipped about the average, find the largest 
            elif asym_type == 'hp':
                
                # remove zero asym
                ap = a.p[0]
                an = a.n[0]
                tag_p = ap!=0
                tag_n = an!=0
                tag_cmb = tag_p*tag_n
                avg = np.mean(ap[tag_cmb]+an[tag_cmb])/2
                ap = ap[tag_p]
                an = an[tag_n]
                
                # get flipped asymmetries
                if np.mean(an) < avg:
                    an = 2*avg-an
                if np.mean(ap) < avg:
                    ap = 2*avg-ap
                
                # get largest asymmetry
                largest_p = max(ap)
                largest_n = max(an)
                
                if largest_p > largest_n:
                    largest = largest_p
                    vmax = x[np.where(ap==largest)[0][0]]
                else:
                    largest = largest_n
                    vmax = x[np.where(an==largest)[0][0]]
                
                # print
                print('Max asymmetry is %f at V = %f V' % (largest, vmax))
                
                # draw    
                plt.errorbar(figstyle, self.id, x[tag_p], ap, a.p[1][tag_p], 
                                  label=label+" ($+$)", **drawargs)
                plt.errorbar(figstyle, self.id, x[tag_n], an, a.n[1][tag_n], 
                                  label=label+" ($-$)", unique=False, **drawargs)
                plt.axhline(figstyle, 'line', largest, color='k', linestyle='--')
                plt.axvline(figstyle, 'line', vmax, color='k', linestyle='--', 
                                 unique=False)
                plt.text(figstyle, vmax+0.5, largest+0.0001, '%g V' % vmax, 
                              id='line', unique=False)
                
            # plot comined helicities
            elif asym_type == 'c':
                tag = a.c[0]!=0 # remove zero asym
                plt.errorbar(figstyle, self.id, x[tag], a.c[0][tag], a.c[1][tag], 
                                  label=label, **drawargs)
                         
            # plot combined helicities, shifted by baseline
            elif asym_type == 'cs':
                
                # remove zero asym
                ac = a.c[0]
                dac = a.c[1]
                tag = ac!=0
                ac = ac[tag]
                dac = dac[tag]
                
                # subtract last 5 values
                x = x[tag]
                
                if 'baseline' in self.fitpar['res'].keys() and bfit.norm_with_param.get():
                    shift = self.fitpar['res']['baseline']
                    dshift = np.sqrt(self.fitpar['dres+']['baseline']**2 + \
                                     self.fitpar['dres-']['baseline']**2)
                    asym_type += 'f'
                else:                
                    shift = np.average(ac[-5:], weights=1/dac[-5:]**2)
                    dshift = 1/np.sum(1/dac[-5:]**2)**0.5
                        
                ac -= shift
                dac = ((dshift)**2+(dac)**2)**0.5
                
                plt.errorbar(figstyle, self.id, x, ac, dac, label=label, **drawargs)
                
            # plot normalizd combined helicities
            elif asym_type == 'cn':

                # remove zero asym
                ac = a.c[0]
                dac = a.c[1]
                tag = ac!=0
                ac = ac[tag]
                dac = dac[tag]
                x = x[tag]
                
                # normalize
                asym_type, norm, dnorm = self.get_norm(asym_type, ac, dac)
                dac = ac/norm * ((dnorm/norm)**2 + (dac/ac)**2)**0.5
                ac /= norm
                
                # draw
                plt.errorbar(figstyle, self.id, x, ac, dac, label=label, **drawargs)
                
            # attempting to draw raw scans unlawfully
            elif asym_type == 'r':
                return
                
            # draw alpha diffusion
            elif asym_type == 'ad':
                a = self.asym('adif', **asym_args)
                plt.errorbar(figstyle, self.id, *a, label=label, **drawargs)
                plt.ylabel(figstyle, r'$N_\alpha/N_\beta$')
                
            # draw normalized alpha diffusion
            elif asym_type == 'adn':
                
                a = self.asym('adif', rebin=1, **asym_args)
                          
                # take mean of first few points
                idx = (a[0]<bfit.norm_alph_diff_time)*(~np.isnan(a[1]))
                a0 = np.average(a[1][idx], weights=1/a[2][idx]**2)
                
                # normalize
                a = self.asym('adif', **asym_args)
                a[1] /= a0
                a[2] /= a0
                
                plt.errorbar(figstyle, self.id, *a, label=label, **drawargs)
                plt.ylabel(figstyle, r'$N_\alpha/N_\beta$ (Normalized by t=0)')
                
            # draw alpha tagged runs
            elif asym_type in ['at_c', 'at_h', 'nat_c', 'nat_h']:
                
                a = self.asym('atag', **asym_args)
                t = a.time_s
                
                if asym_type == 'at_c':
                    plt.errorbar(figstyle, self.id, t, a.c_wiA[0], a.c_wiA[1], 
                                 label=label+r" $\alpha$", **drawargs)
                    
                elif asym_type == 'nat_c':
                    plt.errorbar(figstyle, self.id, t, a.c_noA[0], a.c_noA[1], 
                                 label=label+r" !$\alpha$", **drawargs)
                    
                elif asym_type == 'at_h':
                    plt.errorbar(figstyle, self.id, t, a.p_wiA[0], a.p_wiA[1], 
                                 label=label+r" $\alpha$ ($+$)", **drawargs)
                    
                    plt.errorbar(figstyle, self.id, t, a.n_wiA[0], a.n_wiA[1], 
                                 label=label+r" $\alpha$ ($-$)", **drawargs)
                    
                elif asym_type == 'nat_h':
                    plt.errorbar(figstyle, self.id, t, a.p_noA[0], a.p_noA[1], 
                                 label=label+r" !$\alpha$ ($+$)", **drawargs)
                    
                    plt.errorbar(figstyle, self.id, t, a.n_noA[0], a.n_noA[1], 
                                 label=label+r" !$\alpha$ ($-$)", **drawargs)
                    
            # draw raw histograms
            elif asym_type == 'rhist':
                
                # get the histograms 
                hist = self.hist
                
                # draw
                keylist = ('F+', 'F-', 'B+', 'B-', 'L+', 'R+', 'L-', 'R-', 
                             'NBMF+', 'NBMF-', 'NBMB+', 'NBMB-', 'AL0+', 'AL0-')
                for i, h in enumerate(keylist):
                    
                    # get bins
                    try:
                        x = np.arange(len(hist[h].data))
                    except KeyError:
                        continue
                    
                    # check for non-empty histograms, then draw
                    if np.mean(hist[h].data) > 0:                        
                        plt.plot(figstyle, self.id, x, hist[h].data, label=h, 
                                        unique=not bool(i))
                        
                plt.ylabel(figstyle, bfit.ylabel_dict[asym_type])
                plt.xlabel(figstyle, 'Bin')
                            
            # unknown run type
            else:
                raise RuntimeError("Unknown draw style")
                    
        # plot elements
        if self.mode != '2e' and asym_type != 'rhist':
            plt.xlabel(figstyle, xlabel)
            
            label = bfit.ylabel_dict.get(asym_type, "Asymmetry")
            if bfit.use_nbm.get():              label = 'NBM ' + label    
            plt.ylabel(figstyle, label)    
            
        plt.tight_layout(figstyle)
        plt.legend(figstyle)
        
        # bring window to front
        if figstyle != 'periodic':
            raise_window()   
            
        self.logger.debug('Drawing success.')

    # ======================================================================= #
    def draw_fit(self, figstyle, unique=True, asym_mode=None, **drawargs):
        """
            Draw fit for a single run
            
            figstyle: one of "data", "fit", or "param" to choose which figure
                    to draw in
            asym_mode: from bfit.get_asym_mode, string of mode to draw
         """

        self.logger.info('Drawing fit for run %s. %s', id, drawargs)

        # get data and fit results
        fit_par = self.fitpar.loc[self.parnames, 'res'].values

        # get draw style
        style = self.bfit.draw_style.get()
        
        # get PltTracker
        plt = self.bfit.plt

        # label reset
        if 'label' not in drawargs.keys():
            drawargs['label'] = self.label.get()
        drawargs['label'] += ' (fit)'
        label = drawargs['label']

        # set drawing style
        draw_id = self.id

        # make new window
        if style == 'new' or not plt.active[figstyle]:
            plt.figure(figstyle)
        elif style == 'redraw':
            plt.figure(figstyle)
            plt.clf(figstyle)

        # set drawing style arguments
        for k in self.bfit.style:
            if k not in drawargs.keys() \
                    and 'marker' not in k \
                    and k not in ['elinewidth', 'capsize']:
                drawargs[k] = self.bfit.style[k]

        # linestyle reset
        if drawargs['linestyle'] == 'None':
            drawargs['linestyle'] = '-'

        # draw
        t, a, da = self.asym('c')

        fitx = np.linspace(min(t), max(t), self.bfit.fit_files.n_fitx_pts)

        if self.mode in self.bfit.units:
            unit = self.bfit.units[self.mode]
            xlabel = self.bfit.xlabel_dict[self.mode] % unit[1]
        else:
            xlabel = self.bfit.xlabel_dict[self.mode]

        # get fity
        fity = self.fitfn(fitx, *fit_par)

        # draw relative to peak 0
        if self.bfit.draw_rel_peak0.get():
            
            # get reference
            par = self.fitpar
            
            if 'peak_0' in par.index:   index = 'peak_0'
            elif 'mean_0' in par.index: index = 'mean_0'
            elif 'peak' in par.index:   index = 'peak'
            elif 'mean' in par.index:   index = 'mean'
            else:
                msg = "No 'peak' or 'mean' fit parameter found. Fit with" +\
                     " an appropriate function."
                self.logger.exception(msg)
                messagebox.error(msg)
                raise RuntimeError(msg)
            
            ref = par.loc[index, 'res']
            
            # do the shift
            fitx -= ref                    
            fitx *= unit[0]
            xlabel = 'Frequency Shift (%s)' % unit[1]
            self.logger.info('Drawing as freq shift from peak_0')
        
        # ppm shift
        elif self.bfit.draw_ppm.get():
            
            # check div zero
            try:
                fitx = 1e6*(fitx-self.bfit.ppm_reference)/self.bfit.ppm_reference
            except ZeroDivisionError as err:
                self.logger.exception(str(msg))
                messagebox.error(str(msg))
                raise err
            
            self.logger.info('Drawing as PPM shift with reference %s Hz', 
                             self.bfit.ppm_reference)
            xlabel = 'Frequency Shift (PPM)'
            
        else: 
            fitx *= unit[0]

        # account for normalized draw modes
        if asym_mode == 'cn':
            asym_mode, norm, dnorm = self.get_norm(asym_mode, a, da)
            fity /= norm    
                
        elif asym_mode == 'cs':
            asym_mode += 'f'
            fity -= self.fitpar.loc['baseline', 'res']

        plt.plot(figstyle, draw_id, fitx, fity, zorder=10,
                      unique=unique, **drawargs)

        # plot elements
        plt.ylabel(figstyle, self.bfit.ylabel_dict.get(asym_mode, 'Asymmetry'))
        plt.xlabel(figstyle, xlabel)

        # show
        plt.tight_layout(figstyle)
        plt.legend(figstyle)

        # bring window to front
        raise_window()
    
    # ======================================================================= #
    def draw_residual(self, figstyle, rebin=1, asym_args=None, **drawargs):
        """Draw fitting residuals for a single run"""

        self.logger.info('Drawing residual for run %s, rebin %d, '+\
                         'standardized: %s, %s', self.id, rebin,
                         self.bfit.draw_standardized_res.get(), drawargs)

        plt = self.bfit.plt

        # get draw setting
        figstyle = 'data'
        draw_style = self.bfit.draw_style
        
        # format
        if asym_args is None:
            asym_args = {}

        # get data and fit results
        fit_par = self.fitpar.loc[self.parnames, 'res'].values
        
        # default label value
        if 'label' not in drawargs.keys():
            label = str(self.run)
        else:
            label = drawargs.pop('label', None)

        # set drawing style arguments
        for k in self.bfit.style:
            if k not in drawargs.keys():
                drawargs[k] = self.bfit.style[k]

        # make new window
        style = self.bfit.draw_style.get()
        if style == 'new' or not plt.active[figstyle]:
            plt.figure(figstyle)
        elif style == 'redraw':
            plt.clf(figstyle)

        ax = plt.gca(figstyle)
        ax.get_xaxis().get_major_formatter().set_useOffset(False)

        # get draw style
        style = self.bfit.draw_style.get()

        # get residuals
        x, a, da = self.asym(self.bfit.get_asym_mode(self.bfit.fetch_files), 
                             **asym_args)
        res = a - self.fitfn(x, *fit_par)

        # set x axis
        if self.mode in self.bfit.units:
            unit = self.bfit.units[self.mode]
            x *= unit[0]
            xlabel = self.bfit.xlabel_dict[self.mode] % unit[1]
        else:
            xlabel = self.bfit.xlabel_dict[self.mode]

        # draw
        if self.bfit.draw_standardized_res.get():
            plt.errorbar(figstyle, id, x, res/da, np.zeros(len(x)),
                              label=label, **drawargs)

            # draw fill
            ax = plt.gca(figstyle)
            lim = ax.get_xlim()
            for i in range(1, 4):
                ax.fill_between(lim, -1*i, i, color='k', alpha=0.1)
            plt.xlim(figstyle, lim)
            plt.ylabel(figstyle, r'Standardized Residual ($\sigma$)')
        else:
            plt.errorbar(figstyle, id, x, res, da, label=label, **drawargs)
            plt.ylabel(figstyle, 'Residual')

        # draw pulse marker
        if '2' in self.mode:
            plt.axvline(figstyle, 'line', self.pulse_s, ls='--', color='k')
            unq = False
        else:
            unq = True

        # plot elements
        plt.xlabel(figstyle, xlabel)
        plt.axhline(figstyle, 'line', 0, color='k', linestyle='-', zorder=20,
                        unique=unq)

        # show
        plt.tight_layout(figstyle)
        plt.legend(figstyle)

        raise_window()
    
    # ======================================================================= #
    def drop_param(self, parnames):
        """
            Check self.fitpar for parameters not in list of parnames. Drop them.
        """
        present = [p for p in parnames if p in self.fitpar.index]
        self.fitpar.drop(present, axis='index', inplace=True)
    
    # ======================================================================= #
    def drop_unused_param(self, parnames):
        """
            Check self.fitpar for parameters not in list of parnames. Drop them.
        """
        unused = [p for p in self.fitpar.index if p not in parnames]
        self.fitpar.drop(unused, axis='index', inplace=True)
    
    # ======================================================================= #
    def gen_set_from_var(self, pname, col, obj):
        """Make function to set fitting initial parameters from StringVar or 
            BooleanVarobject
            
            pname: string, name of parameter
            col: string, one of 'p0', 'blo', 'bhi'
            obj: the StringVar or BooleanVar to fetch from
        """
    
        if pname in self.fitpar.index and col in self.fitpar.columns:
            if type(obj) is StringVar:
                
                def set_from_var(*args):
                    try:
                        value = float(obj.get())
                    except ValueError:
                        pass
                    else:
                        self.fitpar.loc[pname, col] = value
                        if pname not in self.constrained.keys():
                            self.set_constrained(col)
                        
            elif type(obj) is BooleanVar:
                
                def set_from_var(*args):
                    try:
                        value = bool(obj.get())
                    except ValueError:
                        pass
                    else:
                        self.fitpar.loc[pname, col] = value
                        
            else:
                
                raise RuntimeError('Bad obj input')
    
            return set_from_var
            
    # ======================================================================= #
    def get_norm(self, asym_type, asym, dasym):
        """
            Get normalization constant for drawing normalized
            
            asym_type: type of asymmetry to calculate (ex: c)
            asym: array of asymmetry values 
            dasym: array of asymmetry errors 
            
            modifies asym_type for id'ing the drawing label
        """

        # type 1 runs: divide by last value or by baseline
        if '1' in self.mode:
            asym_type += '1'
            
            if 'baseline' in self.fitpar['res'].keys() and self.bfit.norm_with_param.get():
                norm = self.fitpar.loc['baseline', 'res']
                dnorm = np.sqrt(self.fitpar.loc['baseline', 'dres+']**2 + \
                                self.fitpar.loc['baseline', 'dres-']**2)
                asym_type += 'f'
            else:                
                norm = np.average(asym[-5:], weights=1/dasym[-5:]**2)
                dnorm = 1/np.sum(1/dasym[-5:]**2)**0.5

        # type 2 runs: divide by first value
        elif '2' in self.mode:
            asym_type += '2'
            
            if 'amp' in self.fitpar['res'].keys() and self.bfit.norm_with_param.get():
                norm = self.fitpar.loc['amp', 'res']
                dnorm = np.sqrt(self.fitpar.loc['amp', 'dres+']**2 + \
                                self.fitpar.loc['amp', 'dres-']**2)
                asym_type += 'f'
            else:
                norm = asym[0]
                dnorm = dasym[0]
        
        # unknown mode
        else:
            msg = 'Unknown run mode %s (cannot detect if type 1 or 2)' % self.mode
            self.logger.exception(msg)
            raise RuntimeError(msg)
            
        return(asym_type, norm, dnorm)
    
    # ======================================================================= #
    def get_temperature(self, channel='A'):
        """
            Get the temperature of the run.
            Return (T, std T)
        """
        
        try:
            if channel == 'A':
                T = self.bd.camp['smpl_read_A'].mean
                dT = self.bd.camp['smpl_read_A'].std
            elif channel == 'B':
                T = self.bd.camp['smpl_read_B'].mean
                dT = self.bd.camp['smpl_read_B'].std
            elif channel == '(A+B)/2':
                Ta = self.bd.camp['smpl_read_A'].mean
                Tb = self.bd.camp['smpl_read_B'].mean
                dTa = self.bd.camp['smpl_read_A'].std
                dTb = self.bd.camp['smpl_read_B'].std
                
                T = (Ta+Tb)/2
                dT = ((dTa**2+dTb**2)**0.5)/2
            else:
                raise AttributeError("Missing required temperature channel.")
        
        except KeyError:
            T = np.nan
            dT = np.nan
        
        return (T, dT)
        
    # ======================================================================= #
    def get_values(self, select):
        """ Get plottable values"""

        # fit parameters
        parnames = self.parnames
        
        # popup for adding new parameters
        try:
            pop_addpar = self.bfit.fit_files.pop_addpar
        except AttributeError:
            pop_addpar = {}
        
        # helper function
        def fetch(obj, attr):
            """
                Try fetching, if fails, return np.nan
            """
            try:
                if len(attr) == 1:
                    return getattr(obj, attr[0])
                else:
                    obj = getattr(obj, attr[0])
                    return fetch(obj, attr[1:])

            except (KeyError, AttributeError):
                return np.nan

        # Data file options
        if select == 'Temperature (K)':
            val = fetch(self, ['temperature','mean'])
            err = fetch(self, ['temperature', 'std'])

        elif select == 'B0 Field (T)':
            val = fetch(self, ['field'])
            err = fetch(self, ['field_std'])

        elif select == 'RF Level DAC':
            try:
                val = fetch(self, ['rf_dac','mean'])
                err = fetch(self, ['rf_dac','std'])
            except AttributeError:
                pass

        elif select == 'Platform Bias (kV)':
            try:
                val = fetch(self, ['bias'])
                err = fetch(self, ['bias_std'])
            except AttributeError:
                pass

        elif select == 'Impl. Energy (keV)':
            val = fetch(self, ['beam_kev'])
            err = fetch(self, ['beam_kev_err'])

        elif select == 'Run Duration (s)':
            val = fetch(self, ['duration'])
            err = np.nan

        elif select == 'Run Number':
            val = fetch(self, ['run'])
            err = np.nan

        elif select == 'Sample':
            val = fetch(self, ['sample'])
            err = np.nan

        elif select == 'Start Time':
            val = fetch(self, ['start_time'])
            err = np.nan

        elif select == 'Title':
            val = fetch(self, ['title'])
            err = np.nan

        elif select == '1000/T (1/K)':
            val = 1000/fetch(self, ['temperature', 'mean'])
            err = 1000*fetch(self, ['temperature', 'std'])/\
                        (fetch(self, ['temperature', 'mean'])**2)

        elif select == 'Chi-Squared':
            val = fetch(self, ['chi'])
            err = np.nan

        elif select == 'Year':
            val = fetch(self, ['year'])
            err = np.nan

        elif select == 'Unique Id':
            val = fetch(self, ['id'])
            err = np.nan

        elif 'Beta-Avg 1/<T1' in select:

            # get component
            idx = select.find('_')
            if idx < 0:     comp_num = ''
            else:           comp_num = select[idx:]
            comp_num = comp_num.replace('>', '')

            # get T1 and beta from that component average
            T1i = self.fitpar.loc['1_T1'+comp_num, 'res']
            T1 = 1/T1i
            dT1_l = self.fitpar.loc['1_T1'+comp_num, 'dres-']/(T1i**2)
            dT1_u = self.fitpar.loc['1_T1'+comp_num, 'dres+']/(T1i**2)

            dT1 = (dT1_l + dT1_u)/2

            beta = self.fitpar.loc['beta'+comp_num, 'res']
            dbeta_l = self.fitpar.loc['beta'+comp_num, 'dres-']
            dbeta_u = self.fitpar.loc['beta'+comp_num, 'dres+']

            dbeta = (dbeta_l + dbeta_u)/2

            # take average
            betai = 1./beta
            pd_T1 = gamma(betai)/beta
            pd_beta = -T1*gamma(betai)*(1+betai*polygamma(0, betai))*(betai**2)
            T1avg = T1*pd_T1
            dT1avg = ( (pd_T1*dT1)**2 + (pd_beta*dbeta)**2 )**0.5

            val = 1/T1avg
            err = dT1avg/(T1avg**2)

        elif 'Beta-Avg <T1' in select:

            # get component
            idx = select.find('_')
            if idx < 0:     comp_num = ''
            else:           comp_num = select[idx:]
            comp_num = comp_num.replace('>', '')

            # get T1 and beta from that component average
            T1i = self.fitpar.loc['1_T1'+comp_num, 'res']
            T1 = 1/T1i
            dT1_l = self.fitpar.loc['1_T1'+comp_num, 'dres-']/(T1i**2)
            dT1_u = self.fitpar.loc['1_T1'+comp_num, 'dres+']/(T1i**2)

            dT1 = (dT1_l + dT1_u)/2

            beta = self.fitpar.loc['beta'+comp_num, 'res']
            dbeta_l = self.fitpar.loc['beta'+comp_num, 'dres-']
            dbeta_u = self.fitpar.loc['beta'+comp_num, 'dres+']

            dbeta = (dbeta_l + dbeta_u)/2

            # take average
            betai = 1./beta
            pd_T1 = gamma(betai)/beta
            pd_beta = -T1*gamma(betai)*(1+betai*polygamma(0, betai))*(betai**2)
            T1avg = T1*pd_T1
            dT1avg = ( (pd_T1*dT1)**2 + (pd_beta*dbeta)**2 )**0.5

            val = T1avg
            err = dT1avg

        elif 'Cryo Lift Set (mm)' in select:
            val = fetch(self, ['clift_set', 'mean'])
            err = fetch(self, ['clift_set', 'std'])

        elif 'Cryo Lift Read (mm)' in select:
            val = fetch(self, ['clift_read', 'mean'])
            err = fetch(self, ['clift_read', 'std']) 

        elif 'He Mass Flow' in select:
            var = 'mass_read' if self.area == 'BNMR' else 'he_read'
            val = fetch(self, [var, 'mean'])
            err = fetch(self, [var, 'std']) 

        elif 'CryoEx Mass Flow' in select:
            val = fetch(self, ['cryo_read', 'mean'])
            err = fetch(self, ['cryo_read', 'std']) 

        elif 'Needle Set (turns)' in select:
            val = fetch(self, ['needle_set', 'mean'])
            err = fetch(self, ['needle_set', 'std']) 

        elif 'Needle Read (turns)' in select:
            val = fetch(self, ['needle_pos', 'mean'])
            err = fetch(self, ['needle_pos', 'std']) 

        elif 'Laser Power (V)' in select:
            val = fetch(self, ['las_pwr', 'mean'])
            err = fetch(self, ['las_pwr', 'std']) 

        elif 'Laser Wavelength (nm)' in select:
            val = fetch(self, ['las_lambda', 'mean'])
            err = fetch(self, ['las_lambda', 'std']) 

        elif 'Laser Wavenumber (1/cm)' in select:
            val = fetch(self, ['las_wavenum', 'mean'])
            err = fetch(self, ['las_wavenum', 'std']) 

        elif 'Target Bias (kV)' in select:
            val = fetch(self, ['target_bias', 'mean'])
            err = fetch(self, ['target_bias', 'std']) 

        elif 'NBM Rate (count/s)' in select:
            rate = lambda b : np.sum([b.hist['NBM'+h].data \
                                    for h in ('F+', 'F-', 'B-', 'B+')])/b.duration
            val = rate(self.bd)
            err = np.nan

        elif 'Sample Rate (count/s)' in select:
            hist = ('F+', 'F-', 'B-', 'B+') if self.area.upper() == 'BNMR' \
                                         else ('L+', 'L-', 'R-', 'R+')

            rate = lambda b : np.sum([b.hist[h].data for h in hist])/b.duration
            val = rate(self.bd)
            err = np.nan

        elif 'NBM Counts' in select:
            counts = lambda b : np.sum([b.hist['NBM'+h].data \
                                    for h in ('F+', 'F-', 'B-', 'B+')])
            val = counts(self.bd)
            err = np.nan
        
        elif 'Sample Counts' in select:
            hist = ('F+', 'F-', 'B-', 'B+') if self.area.upper() == 'BNMR' \
                                         else ('L+', 'L-', 'R-', 'R+')

            counts = lambda b : np.sum([b.hist[h].data for h in hist])
            val = counts(self.bd)
            err = np.nan
        
        elif 'T1' in select and '1_T1' not in select:
            
            
            # get component
            idx = select.find('_')
            if idx < 0:     comp_num = ''
            else:           comp_num = select[idx:]

            # get T1 and beta from that component average
            T1i = self.fitpar.loc['1_T1'+comp_num, 'res']
            T1 = 1/T1i
            dT1_l = self.fitpar.loc['1_T1'+comp_num, 'dres-']/(T1i**2)
            dT1_u = self.fitpar.loc['1_T1'+comp_num, 'dres+']/(T1i**2)

            dT1 = (dT1_l + dT1_u)/2

            val = T1
            err = dT1
            
        # fitted parameter options
        elif select in parnames:
            try:
                val = self.fitpar.loc[select, 'res']
                err_l = self.fitpar.loc[select, 'dres-']
                err_u = self.fitpar.loc[select, 'dres+']
            except KeyError:
                val = np.nan
                err_l = np.nan
                err_u = np.nan
            err = (err_l, err_u)

        # check user-defined parameters
        elif select in pop_addpar.set_par.keys():
            val, err = pop_addpar.set_par[select](self.id)

        try:
            return (val, err)
        except UnboundLocalError:
            self.logger.warning('Parameter selection "%s" not found' % select)
            raise AttributeError('Selection "%s" not found' % select) from None
    
    # ======================================================================= #
    def read(self):
        """Read data file"""
        
        # bdata access
        if type(self.bd) is bdata:
            
            # load real run
            try:
                self.bd = bdata(self.run, self.year)
                
            # load test run
            except ValueError:
                self.bd = bdata(filename = self.bfit.fileviewer.filename)
                
        elif type(self.bd) is bmerged:
            years = list(map(int, textwrap.wrap(str(self.year), 4)))
            runs = list(map(int, textwrap.wrap(str(self.run), 5)))
            self.bd = bmerged([bdata(r, y) for r, y in zip(runs, years)])
         
        # set manually updated variables
        for key, dic in self.manually_updated_var.items():
            for key2, prop in dic.items():
                getattr(self.bd, key)[key2] = prop
         
        # set new variables
        self.set_new_var()
        
    # ======================================================================= #
    def reset_fitpar(self):
        self.fitpar = pd.DataFrame([], columns=['p0', 'blo', 'bhi', 'res', 
                                    'dres+', 'dres-', 'chi', 'fixed', 'shared'])
        
    # ======================================================================= #
    def set_fitpar(self, values):
        """Set fitting initial parameters
        values: output of routine gen_init_par: DataFrame:            
                columns: [p0, blo, bhi, fixed]
                index: parameter names
        """
    
        self.parnames = values.index.values
    
        for v in self.parnames:
            for c in values.columns:
                self.fitpar.loc[v, c] = values.loc[v, c]
                
        self.logger.debug('Fit initial parameters set to %s', self.fitpar)

    # ======================================================================= #
    def set_constrained(self, col):
        """
            Change parameter values based on constraint equation and typed inputs
        """
        for par in self.fitpar.index:
            if par in self.constrained.keys():
                
                # set errors
                if 'dres' in col:
                    try:
                        inputs_par = self.fitpar.loc[self.constrained[par][1], 'res']
                        inputs_err = self.fitpar.loc[self.constrained[par][1], col]
                    except KeyError:
                        pass
                    else:
                        fn = self.constrained[par][0]
                        val = get_derror(fn, inputs_par, inputs_err)
                        self.fitline.set(par, **{col:val})
                        
                # set non-error
                else:                
                    try:
                        inputs = self.fitpar.loc[self.constrained[par][1], col]
                    except KeyError:
                        pass
                    else:
                        val = self.constrained[par][0](*inputs)
                        self.fitline.set(par, **{col:val})
                
    # ======================================================================= #
    def set_fitresult(self, values):
        """
            Set fit results. Values is output of fitting routine. 
            
            values: {fn: function handle, 
                     'results': DataFrame of fit results,
                     'gchi': global chi2}
                     
            values['results']: 
                columns: [res, dres+, dres-, chi, fixed, shared]
                index: parameter names
        """
        
        # set function
        self.fitfn = values['fn']
        
        # get data frame
        df = values['results']
        
        # set parameter names
        self.parnames = df.index.values
        
        # set chi
        self.chi = df['chi'].values[0]
        
        # set parameters
        for v in self.parnames:
            for c in df.columns:
                self.fitpar.loc[v, c] = df.loc[v, c]
        self.logger.debug('Setting fit results to %s', self.fitpar)
    
    # ======================================================================= #
    def set_new_var(self):
        """
            Set new variables for easy access
        """
        
        # set temperature 
        try:
            self.temperature = temperature_class(*self.get_temperature(self.bfit.thermo_channel.get()))
        except AttributeError as err:
            self.logger.exception(err)
            try:
                self.temperature = self.bd.camp.oven_readC
            except AttributeError:
                self.logger.exception('Thermometer oven_readC not found')
                self.temperature = -1111
        
        # field
        try:
            if self.area == 'BNMR':
                self.field = self.bd.camp.b_field.mean
                self.field_std = self.bd.camp.b_field.std
            else:
                
                if hasattr(self.bd.epics, 'hh6_current'):
                    self.field,     err = nqr_B0_hh6(amps=self.bd.epics.hh6_current.mean)
                    self.field_std, err = nqr_B0_hh6(amps=self.bd.epics.hh6_current.std)                    
                else:
                    self.field,     err = nqr_B0_hh3(amps=self.bd.epics.hh_current.mean)
                    self.field_std, err = nqr_B0_hh3(amps=self.bd.epics.hh_current.std)
                
                self.field_std = (err**2 + self.field_std**2)**0.5
                self.field *= 1e-4
                self.field_std *= 1e-4
                    
        except AttributeError:
            self.logger.exception('Field not found')
            self.field = np.nan
            self.field_std = np.nan
            
        # bias
        try:
            if self.area == 'BNMR': 
                self.bias = self.bd.epics.nmr_bias.mean
                self.bias_std = self.bd.epics.nmr_bias.std
            else:
                self.bias = self.bd.epics.nqr_bias.mean/1000.
                self.bias_std = self.bd.epics.nqr_bias.std/1000.
        except AttributeError:
            self.logger.exception('Bias not found')
            self.bias = np.nan
            
        # set area as upper
        self.area = self.area.upper()
        
# ========================================================================== #
class temperature_class(object):
    """
        Emulate storage container for camp variable smpl_read_%
    """
    
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std
    
    def __str__(self):
        return '%f K' % self.mean
