# Set up default fitting routines. 
# Derek Fujimoto
# Aug 2018

import bfit.fitting.functions as fns
from bfit.fitting.decay_31mg import fa_31Mg
from bfit.fitting.gen_init_par import gen_init_par
from functools import partial
from collections.abc import Iterable
import numpy as np
import bdata as bd
import pandas as pd
import copy

class fitter(object):
    """
        Fitter base class for default minimizers
    """

    # needed to tell users what routine this is
    __name__ = 'base'
    
    # Define possible fit functions for given run modes
    function_names = {  '20':('Exp', 'Bi Exp', 'Str Exp'), 
                        '2h':('Exp', 'Bi Exp', 'Str Exp'), 
                        '1f':('Lorentzian', 'Gaussian', 'BiLorentzian', 'QuadLorentz'), 
                        '1x':('Lorentzian', 'Gaussian', 'BiLorentzian', 'QuadLorentz'), 
                        '1w':('Lorentzian', 'Gaussian', 'BiLorentzian', ), 
                        '2e':('Lorentzian', 'Gaussian', 'BiLorentzian', 'QuadLorentz')}
     
    # Define names of fit parameters:
    param_names = {     'Exp'       :('1_T1', 'amp'), 
                        'Bi Exp'    :('1_T1', '1_T1b', 'fraction_b', 'amp'), 
                        'Str Exp'   :('1_T1', 'beta', 'amp'), 
                        'Lorentzian':('peak', 'fwhm', 'height', 'baseline'), 
                        'BiLorentzian':('peak', 'fwhmA', 'heightA', 
                                               'fwhmB', 'heightB', 'baseline'), 
                        'QuadLorentz':('nu_0', 'nu_q', 'efgAsym', 'efgTheta', 'efgPhi', 
	                               'amp0', 'amp1', 'amp2', 'amp3', 'fwhm', 
                                       'baseline'), 
                        'Gaussian'  :('mean', 'sigma', 'height', 'baseline'), }

    # nice parameter names for labels - must be one to one unique for later inversion
    pretty_param = {'1_T1':             r'$1 / T_1$ (s$^{-1}$)', 
                    'T1':               r'$T_1$ (s)', 
                    'amp':              'Amplitude', 
                    'fraction_b':       r'Fraction of $T_1^{(b)}$', 
                    '1_T1b':            r'$1/T_1^{(b)}$ (s$^{-1}$)', 
                    'T1b':              r'$T_1^{(b)}$ (s)', 
                    'beta':             r'$\beta$', 
                    'fwhm':             'FWHM (%s)', 
                    'height':           'Height', 
                    'baseline':         'Baseline', 
                    'peak':             'Peak (%s)', 
                    'fwhmA':            'FWHM$_A$ (%s)', 
                    'fwhmB':            'FWHM$_B$ (%s)', 
                    'heightA':          'Height$_A$', 
                    'heightB':          'Height$_B$', 
                    'nu_0':             r'$\nu_0$ (%s)', 
                    'nu_q':             r'$\nu_q$ (%s)', 
                    'efgAsym':          r'$\eta$', 
                    'efgTheta':         r'Principle Axes $\theta$ (rad)', 
                    'efgPhi':           r'Principle Axes $\phi$ (rad)', 
                    'amp0':             'Amplitude$_0$', 
                    'amp1':             'Amplitude$_1$', 
                    'amp2':             'Amplitude$_2$', 
                    'amp3':             'Amplitude$_3$', 
                    'mean':             r'$\langle\nu\rangle$ (%s)', 
                    'sigma':            r'$\sigma$ (%s)', 
                    'Beta-Avg 1/<T1>':  r'$1/\langle T_1\rangle_\beta$ (s$^{-1}$)', 
                    'B0 Field (T)':     r'$B_0$ Field (T)', 
                    }

    # define list of ok run modes 
    valid_asym_modes = ('c', 'p', 'n', 'sl_c', 'dif_c', )
    
    # probe species spin numbers
    spin = {'Li8':2,    # radioactive daughters: none
            'Li9':1.5,  # radioactive daughters: Be8
            'Li11':0.5, # radioactive daughters: Be11, He6, Be10 
            'Be11':0.5, # radioactive daughters: none 
            'F20':2,    # radioactive daughters: none
            'Mg31':0.5, # radioactive daughters: Al31, Si31 
            'Mg29':1.5, # radioactive daughters: Al29
            'Ac230':1,  # radioactive daughters: none
            'Ac232':1,  # radioactive daughters: unknown
            'Ac234':1,  # radioactive daughters: unkonwn
            }

    # ======================================================================= #
    def __init__(self, keyfn, probe_species='Li8'):
        """
            keyfn:          function takes as input bdata or bjoined or bmerged 
                            object, returns string corresponding to unique id of 
                            that object
            probe_species: one of the keys in the bdata.life dictionary.
        """
        self.keyfn = keyfn
        self.probe_species = probe_species
        
    # ======================================================================= #
    def __call__(self, fn_name, ncomp, data_list, hist_select, asym_mode, xlims):
        """
            Fitting controller. 
            
            fn_name: name of function to fit
            ncomp : number of components to incude (2 = biexp, for example)
            data_list: list of [[fitdata object, pdict, doptions], ]
            
                where pdict = {par:(init val,   # initial guess
                                    bound_lo,   # lower fitting bound
                                    bound_hi,   # upper fitting bound
                                    is_fixed,   # boolean, fix value?
                                    is_shared,  # boolean, share value globally?
                                   )
                              }
                where doptions = {  'omit':str,     # bins to omit in 1F calcs
                                    'rebin':int,    # rebinning factor
                                    'group':int,    # fitting group
                                 }
                                 
            hist_select: string for selection of histograms
            asym_mode:  input for asymmetry calculation type 
                                               c: combined helicity
                            h: split helicity
                            p: positive helicity
                            n: negative helicity
                            
                        For 2e mode, prefix with:
                            sl_: combined timebins using slopes
                            dif_: combined timebins using differences
                            raw_: raw time-resolved
                            
                            ex: sl_c or raw_h or dif_c
            xlims: fit subrange of x axis
            returns dictionary of {runid: [[par_names], [par_values], [par_errors], 
                                          [chisquared], [fitfunction pointers]]}
                                   and global chisquared
        """

        # check ncomponents
        if ncomp < 1:
            raise RuntimeError('ncomp needs to be >= 1')
            
        asym_mode = asym_mode.replace('2e_', '')
            
        # parameter names
        keylist = list(self.gen_param_names(fn_name, ncomp, data_list[0][0].constrained))
        npar = len(keylist)
        
        # gather list of data to fit 
        fn = []
        bdata_list = []
        p0 = []
        bounds = []
        omit = []
        rebin = []
        sharelist = np.zeros(npar, dtype=bool)
        fixedlist = []
        
        for data in data_list:
            
            # split data list into parts
            dat = data[0]
            pdict = data[1]
            doptions = data[2]
            
            # probe lifetime
            life = bd.life[self.probe_species]
            
            # get fitting function for 20 and 2h
            if dat.mode in ['20', '2h']: 
                pulse = dat.pulse_s
                fn.append(self.get_fn(fn_name=fn_name, 
                                      ncomp=ncomp, 
                                      pulse_len=pulse, 
                                      lifetime=life, 
                                      constr=dat.constrained))                
                
            # 1f functions
            else:                       
                fn.append(self.get_fn(fn_name=fn_name, 
                                      ncomp=ncomp, 
                                      pulse_len=-1, 
                                      lifetime=life, 
                                      constr=dat.constrained))
            
            # get bdata objects
            bdata_list.append(dat)
            
            # get initial parameters
            p0.append(tuple(pdict[k][0] for k in keylist))
            
            # get fitting bounds
            bound = [[], []]
            shlist = []
            fixed = []
            for k in keylist:
                
                # bounds
                bound[0].append(pdict[k][1])
                bound[1].append(pdict[k][2])
                
                # fixed
                fixed.append(pdict[k][3])    
                    
                # sharelist
                shlist.append(pdict[k][4])
                
            bounds.append(bound)
            fixedlist.append(fixed)
            
            # look for any sharelist
            sharelist += np.array(shlist)
            
            # rebin and omit
            try:
                rebin.append(doptions['rebin'])
            except KeyError:
                rebin.append(1)
                
            try:
                omit.append(doptions['omit'])
            except KeyError:
                omit.append('')                
            
        # fit data
        kwargs = {'p0':p0, 'bounds':bounds}
        pars, stds_l, stds_h, covs, chis, gchi = self._do_fit(
                                        bdata_list, 
                                        fn, 
                                        omit, 
                                        rebin, 
                                        sharelist, 
                                        hist_select=hist_select, 
                                        asym_mode=asym_mode, 
                                        fixed=fixedlist, 
                                        xlims=xlims, 
                                        parnames=keylist, 
                                        **kwargs)
        
        # set up output dataframe
        if not isinstance(chis, Iterable):   # single run
            pars = [pars]
            stds_l = [stds_l]
            stds_h = [stds_h]
            chis = [chis]
            
        output = {}
        for i, d in enumerate(bdata_list):
            key = self.keyfn(d)
            output[key] = pd.DataFrame({'parname':keylist,
                                        'res': pars[i],
                                        'dres+': stds_h[i],
                                        'dres-': stds_l[i],
                                        'chi': chis[i],
                                        })
            output[key].set_index('parname', inplace=True)
        return (output, gchi)
        
    # ======================================================================= #
    def get_fit_fn(self, fn_name, ncomp, data_list):
        """
            Get dictionary of function handles keyed by run id. 
        """
        output = {}
        
        for data in data_list:
            
            # split data list into parts
            dat = data[0]
            pdict = data[1]
            doptions = data[2]
            
            # probe lifetime
            life = bd.life[self.probe_species]
            
            # get fitting function for 20 and 2h
            if dat.mode in ('20', '2h'): 
                pulse = dat.pulse_s                
                fn = self.get_fn(fn_name, ncomp, pulse, life, dat.constrained)
                
            # 1f functions
            else:                       
                fn = self.get_fn(fn_name, ncomp, -1, life, dat.constrained)

            # make output
            output[self.keyfn(dat)] = fn
        
        return output

    # ======================================================================= #
    def gen_param_names(self, fn_name, ncomp, constr=None):
        """
            Make a list of the parameter names based on the number of components.
            
            fn_name: name of function (should match those in param_names)
            ncomp: number of components
            constr: dict {defined (string) : [fn (unused), par names (list of str)]
            
            return (names)
        """
        
        if fn_name == '':
            return tuple()
        
        # get names
        names_orig = self.param_names[fn_name]
        
        # special case of one component
        if ncomp == 1: 
            names = names_orig
            
        # multicomponent: make copies of everything other than the baselines
        else:
            names = []
            for c in range(ncomp): 
                for n in names_orig:
                    if 'base' in n: continue
                    names.append(n+'_%d' % c)
                    
            if 'base' in names_orig[-1]:
                names.append(names_orig[-1])
        
        # constrained parameter names {defined: [fn, par]}        
        if constr and constr is not None:
            names = list(names)
            new_names = []
            for c in constr.keys():
                if c in names:
                    del names[names.index(c)]
                    new_names.extend(constr[c][1])    
            new_names = np.unique(new_names)
            names.extend(new_names)
            
        return tuple(names)
        
    # ======================================================================= #
    def gen_init_par(self, fn_name, ncomp, bdataobj, asym_mode='combined'):
        return gen_init_par(fn_name, ncomp, bdataobj, asym_mode)
        
    # ======================================================================= #
    def get_fn(self, fn_name, ncomp=1, pulse_len=-1, lifetime=-1, constr=None):
        """
            Get the fitting function used.
            
                fn_name: string of the function name users will select. 
                ncomp: number of components, ex if 2, then return exp+exp
                pulse_len: duration of beam on in s
                lifetime: lifetime of probe in s
            
            Returns python function(x, *pars)
        """
        
        # set fitting function
        if fn_name == 'Lorentzian':
            fn =  fns.lorentzian
            self.mode=1
        elif fn_name == 'BiLorentzian':
            fn =  fns.bilorentzian
            self.mode=1
        elif fn_name == 'QuadLorentz':
            fn =  lambda freq, nu_0, nu_q, eta, theta, phi, \
            		amp0, amp1, amp2, amp3, fwhm: \
                   	fns.quadlorentzian(freq, nu_0, nu_q, eta, theta, phi, \
		            		amp0, amp1, amp2, amp3, \
                		   	fwhm, fwhm, fwhm, fwhm, \
                		   	I=self.spin[self.probe_species])
            self.mode=1
        elif fn_name == 'Gaussian':
            fn =  fns.gaussian
            self.mode=1
        elif fn_name == 'Exp':
            fn =  fns.pulsed_exp(lifetime, pulse_len)
            self.mode=2
        elif fn_name == 'Bi Exp':
            fn =  fns.pulsed_biexp(lifetime, pulse_len)
            self.mode=2
        elif fn_name == 'Str Exp':
            fn =  fns.pulsed_strexp(lifetime, pulse_len)
            self.mode=2
        else:
            raise RuntimeError('Fitting function not found.')
        
        # add corrections for probe daughters
        if self.mode == 2 and self.probe_species == 'Mg31':
            fn = fns.decay_corrected_fn(fa_31Mg, fn, beam_pulse=pulse_len)
        
        # Make superimposed function based on number of components
        fnlist = [fn]*ncomp
        
        if self.mode == 1:
            fnlist.append(lambda x, b: b)
            
        fn = fns.get_fn_superpos(fnlist)

        # set parameter constraints
        if constr and constr is not None:
            par_names_orig = self.gen_param_names(fn_name, ncomp)
            par_names_constr = self.gen_param_names(fn_name, ncomp, constr)
            fn = fns.get_constrained_fn(fn, par_names_orig, par_names_constr, constr)
            
        return fn
        

