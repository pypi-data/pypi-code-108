# Fit set of data globally 
# Derek Fujimoto
# Nov 2018

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os
import time
from bfit.fitting.minuit import minuit
from collections.abc import Iterable
from bfit.fitting.leastsquares import LeastSquares
import warnings

__doc__=\
"""
    Global fitter. 
    
    Uses scipy.optimize.curve_fit to fit a function or list of functions to a 
    set of data with shared parameters.
    
    Usage: 
        
        Construct fitter:
            
            g = global_fitter(x, y, dy, fn, sharelist, npar=-1)
            
            %s
    
        Fit
            g.fit(**fitargs)
        
            %s
            
        Get chi squared
            g.get_chi()
            
            %s
        
        Get fit parameters
            g.get_par()
            
            %s
            
        Draw the result
        
            g.draw(mode='stack', xlabel='', ylabel='', do_legend=False, labels=None, 
                   savefig='', **errorbar_args)
           
            %s
"""

# =========================================================================== #
class global_fitter(object):
    """
        Set up fitting a set of data with arbitrary function. Arbitrary 
        globally shared parameters. 
        
        Instance Variables: 
            
            chi_glbl                global chisqured, also accessible through gchi2
            chi                     list of chisquared values for each data set, also accessible through chi2
            
            fn                      list of fitting function handles
            fixed                   list of fixed variables (corresponds to input)
            fprime_dx               x spacing in calculating centered differences derivative
            
            metadata                array of additional inputs, fixed for each data set
                                    (if len(shared) < len(actual inputs))
            
            minuit                  Minuit object for minimizing with migrad algorithm
            minimizer               string: one of "curve_fit" or "migrad"
            
            npar                    number of parameters in input function
            nsets                   number of data sets
            
            par                     fit results with unnecessary variables stripped 
            par_runwise             fit results run-by-run with all needed inputs, also accessible via values
            std_l, std_u            lower/upper errors with unnecessary variables stripped 
            std_l_runwise           lower errors run-by-run with all needed inputs, also accessible via lower
            std_u_runwise           upper errors run-by-run with all needed inputs, also accessible via upper
            cov                     fit covarince matrix with unnecessary variables stripped, , also accessible via covariance
            cov_runwise             fit covarince matrix run-by-run with all needed inputs
            
            shared                  array of bool of len = nparameters, share parameter if true. 
            sharing_links           2D array of ints, linking global inputs to function-wise inputs
            
            xcat                    concatenated xdata for global fitting
            ycat                    concatenated ydata for global fitting
            dycat                   concatenated dydata for global fitting
            dxcat                   concatenated dydata for global fitting
            dycat_low               concatenated dydata for global fitting
            dxcat_low               concatenated dydata for global fitting
            
            x                       input array of x data sets [array1, array2, ...]
            y                       input array of y data sets [array1, array2, ...]
            dy                      input array of y error sets [array1, array2, ...]
            dx                      input array of x error sets [array1, array2, ...]
            dy_low                  input array of y error sets [array1, array2, ...]
            dx_low                  input array of x error sets [array1, array2, ...]
    """
    
    # class variables
    draw_modes = ('stack', 's', 'new', 'n', 'append', 'a')   # for checking modes
    ndraw_pts = 500             # number of points to draw fits with
    
    # ======================================================================= #
    def __init__(self, fn, x, y, dy=None, dx=None, dy_low=None, dx_low=None, 
                shared=None, fixed=None, metadata=None, fprime_dx=1e-6):
        """
            fn:         function handle OR list of function handles. 
                        MUST specify inputs explicitly if list must have that 
                        len(fn) = len(x) and all function must have the same 
                        inputs in the same order
        
            x, y:       2-list of data sets of equal length. 
                        fmt: [[a1, a2, ...], [b1, b2, ...], ...]
            
            dx, dy:     list of errors in x or y with same format as x and y
            dx_low, dy_low: list of low bound errors in x or y with same format 
                        as x and y. 
                            
                        If not None, then assume dy and dx are the upper errors
                        If None, assume symmetric errors
            
            shared:     tuple of booleans indicating which values to share. 
                        len = number of parameters 
                        
            fixed:      list of booleans indicating if the paramter is to be 
                        fixed to p0 value (same length as p0). Returns best 
                        parameters in order presented, with the fixed 
                        parameters omitted.
                        
            metadata:   array of values to pass to fn which are fixed for each 
                        data set (ex: the temperature of each data set). 
                        format: len(metadata) = number of data sets. 
                        
                        number of parameters is set by len(shared), all 
                        remaining inputs are expected to be metadata inputs
                        function call: fn[i](x[i], *par[i], *metadata[i])
            
            fprime_dx:  x spacing in calculating centered differences derivative
            
        """
        # ---------------------------------------------------------------------
        # Check and assign inputs
        self.fprime_dx = fprime_dx
    
        if (dy is None and dy_low is not None) or (dx is None and dx_low is not None): 
            raise RuntimeError("If specifying lower errors, must also specify dy or dx")
            
        # data types: check and assign
        msg = 'Lengths of input data arrays do not match.\nnsets: %s, %s =  %d, %d\n'
        x = list(x)
        y = list(y)
        
        if not len(x) == len(y):
            raise RuntimeError(msg % ('x', 'y', len(x), len(y)))
        
        self.nsets = len(x)
        
        if dy is not None:          
            dy = list(dy)
            if not self.nsets == len(dy):
                raise RuntimeError(msg % ('n', 'dy', self.nsets, len(dy)))
        
        if dx is not None:          
            dx = list(dx)
            if not self.nsets == len(dx):
                raise RuntimeError(msg % ('n', 'dx', self.nsets, len(dx)))
            
        if dy_low is not None:      
            dy_low = list(dy_low)
            if not self.nsets == len(dy_low):
                raise RuntimeError(msg % ('n', 'dy_low', self.nsets, len(dy_low)))
        
        if dx_low is not None:      
            dx_low = list(dx_low)
            if not self.nsets == len(dx_low):
                raise RuntimeError(msg % ('n', 'dx_low', self.nsets, len(dx_low)))
        
        # shared parameters
        self.shared = np.asarray(shared)
        
        # get number of input parameters
        if shared is None:
            raise RuntimeError("Must specified shared parameter as boolean iterable")
        self.npar = len(shared)

        # if errors, remove points with zero error from data
        if dy is not None or dx is not None:
            for i in range(self.nsets):
                
                # get indexing
                idx = np.full(len(x[i]), False)
                if dy is not None:      idx = idx | (dy[i] != 0)
                if dx is not None:      idx = idx | (dx[i] != 0)
                if dy_low is not None:  idx = idx | (dy_low[i] != 0)
                if dx_low is not None:  idx = idx | (dx_low[i] != 0)
                
                # crop
                x[i] = x[i][idx]
                y[i] = y[i][idx]
                
                if dy is not None:      dy[i] = dy[i][idx]
                if dx is not None:      dx[i] = dx[i][idx]
                if dy_low is not None:  dy_low[i] = dy_low[i][idx]
                if dx_low is not None:  dx_low[i] = dx_low[i][idx]

        # check if list of functions given 
        if not isinstance(fn, Iterable):
            fn = [fn]*self.nsets
        
        # check metadata
        if metadata is not None:
            
            # check for not enough data
            if len(metadata) != self.nsets:
                raise RuntimeError('metadata has the wrong shape: len(metadata) = len(x)')  
                
            # check for 1D input
            metadata = np.asarray(metadata)
            if len(metadata.shape) == 1:
                metadata = np.asarray([metadata]).T
        else:
            metadata = [[]]*self.nsets
        self.metadata = metadata
        
        # expand fixed
        if fixed is not None: 
            if len(np.asarray(fixed).shape) == 1:
                fixed = np.full((self.nsets, self.npar), fixed)
            else:
                fixed = np.asarray(fixed)
        else:
            fixed = np.zeros((self.nsets, self.npar)).astype(bool)
        
        fixed_flat = np.concatenate(fixed)
        
        # check that no shared parameters are fixed
        shared_as_int = self.shared.astype(int)
        for fix in fixed: 
            if any(fix+shared_as_int>1):
                raise RuntimeError('Cannot fix a shared parameter') 
        
        # ---------------------------------------------------------------------
        # Build fitting functions
        
        # get linking indexes    
        sharing_links = [] # [input index] organized by output index position
        p_index = 0
        par_numbers_shared = np.arange(self.npar)
        
        for i in range(self.nsets):
            
            # parameter intdexes
            par_numbers = par_numbers_shared+p_index
            
            # link shared variables
            par_numbers[self.shared] = par_numbers_shared[self.shared]  
            
            # link fixed variables
            par_numbers[fixed[i]] = -par_numbers[fixed[i]]-1
            sharing_links.append(par_numbers)
            
            # iterate
            p_index += self.npar
        
        # reduce too-high indexes
        sharing_links = np.array(sharing_links)        
        unq = np.unique(sharing_links)
        unq = unq[unq>=0]
        for i, u in enumerate(unq):
            sharing_links[sharing_links==u] = i
        
        # save results
        self.fn = fn
        self.x = x
        self.y = y
        self.dy = dy
        self.dx = dx
        self.dy_low = dy_low
        self.dx_low = dx_low
        self.fixed = fixed
        self.sharing_links = sharing_links
        
        # get concatenated data
        self.xcat = np.concatenate(x)
        self.ycat = np.concatenate(y)
        
        if dy is not None:          self.dycat = np.concatenate(dy)
        else:                       self.dycat = None
        
        if dx is not None:          self.dxcat = np.concatenate(dx)
        else:                       self.dxcat = None
        
        if dy_low is not None:      self.dycat_low = np.concatenate(dy_low)
        else:                       self.dycat_low = None
        
        if dx_low is not None:      self.dxcat_low = np.concatenate(dx_low)
        else:                       self.dxcat_low = None
        
    # ======================================================================= #
    def _do_curve_fit(self, master_fn, p0_first, **fitargs):
        """
            Run curve_fit minimmizer
        """
        
        dycat = self.dycat
        absolute_sigma = self.dycat is not None
            
        if self.dxcat is not None:
            warnings.warn("curve_fit minimizer does not account for x errors")
            
        par, cov = curve_fit(master_fn, 
                            self.xcat, 
                            self.ycat, 
                            sigma=dycat, 
                            absolute_sigma=absolute_sigma, 
                            p0 = p0_first, 
                            **fitargs)
                            
        std = np.diag(cov)**0.5
        return (par, std, std, cov)
    
    # ======================================================================= #
    def _do_migrad(self, master_fn, master_fnprime, do_minos, p0_first, **fitargs):
                
        # set args
        limit = fitargs.get('bounds', None)
        if limit is not None:
            limit = np.array(limit).T
        
        kwargs_minuit = {'start':p0_first, 
                         'limit':limit, 
                         'print_level':fitargs.get('print_level', 1), 
                        }
        
        # get minuit obj
        m = minuit(master_fn, self.xcat, self.ycat, 
                            dy = self.dycat, 
                            dx = self.dxcat, 
                            dy_low = self.dycat_low, 
                            dx_low = self.dxcat_low, 
                            fn_prime = master_fnprime,
                            **kwargs_minuit)

        self.ls = m.ls
        self.minuit = m
        
        # minimize
        try:
            m.migrad()    
        except UnicodeEncodeError:  # can't print on older machines
            pass
        
        # check minimum
        if not m.fmin.is_valid:
            raise RuntimeError('Minuit failed to converge to a valid minimum')
        
        # get errors
        if do_minos:
            try:
                m.minos()    
            except UnicodeEncodeError:  # can't print on older machines
                pass
                
            lower = np.abs(m.mlower)
            upper = m.mupper
        else:
            try:
                m.hesse()
            except UnicodeEncodeError:  # can't print on older machines
                pass
        
            lower = m.errors
            upper = lower
        
        # get output
        par = m.values
        cov = m.covariance
        
        return (par, lower, upper, cov)
        
    # ======================================================================= #
    def draw(self, mode='stack', xlabel='', ylabel='', do_legend=False, labels=None, 
             savefig='', **errorbar_args):
        """
            Draw data and fit results. 
            
            mode:           drawing mode. 
                            one of 'stack', 'new', 'append' (or first character 
                                for shorhand)
            
            xlabel/ylabel:  string for axis labels
            
            do_legend:      if true set legend
            
            labels:         list of string to label data
            
            savefig:        if not '', save figure with this name
            
            errorbar_args:  arguments to pass on to plt.errorbar
            
            Returns list of matplotlib figure objects
        """
        
        fig_list = []
        last = 0
        
        # check input
        if mode not in self.draw_modes:
            raise RuntimeError('Drawing mode %s not recognized' % mode)
        
        # get label
        if labels is None:
            labels = ['_no_label_' for i in range(self.nsets)]
        
        # draw all
        for i in range(self.nsets):
            
            # get data
            x, y, = self.x[i], self.y[i]
            
            if self.dy is not None:         dy = self.dy[i]
            else:                           dy = None
            
            if self.dx is not None:         dx = self.dx[i]
            else:                           dx = None
            
            if self.dy_low is not None:     dy_low = self.dy_low[i]
            else:                           dy_low = dy
            
            if self.dx_low is not None:     dx_low = self.dx_low[i]
            else:                           dx_low = dx
            
            f = self.fn[i]
            md = self.metadata[i]
                        
            # make new figure
            if mode in ['new', 'n']:            
                fig_list.append(plt.figure())
            elif len(fig_list) == 0:
                fig_list.append(plt.figure())
            
            # shift x values
            if mode in ['append', 'a']:
                x_draw = x+last
                last = x_draw[-1]
            else:
                x_draw = x
                
            # draw data
            if dy is None:      dy_draw = None
            else:               dy_draw = (dy_low, dy)    
            
            if dx is None:      dx_draw = None
            else:               dx_draw = (dx_low, dx)    
            
            datplt = plt.errorbar(x_draw, y, yerr=dy_draw, xerr=dx_draw, 
                                  label=labels[i], **errorbar_args)
            
            # get color for fit curve
            if mode in ['stack', 's']:
                color = datplt[0].get_color()
            else:
                color = 'k'
            
            # draw fit
            xfit = np.linspace(min(x), max(x), self.ndraw_pts)
            xdraw = np.linspace(min(x_draw), max(x_draw), self.ndraw_pts)
            plt.plot(xdraw, f(xfit, *self.par_runwise[i], *md), color=color, zorder=10)
        
            # plot elements
            plt.ylabel(ylabel)
            plt.xlabel(xlabel)
            
            if do_legend:       plt.legend(fontsize='x-small')
            if savefig!='':     plt.savefig(savefig)
            
            plt.tight_layout()

        return fig_list
        
    # ======================================================================= #
    def fit(self, minimizer='migrad', **fitargs):
        """
            fitargs: parameters to pass to fitter (scipy.optimize.curve_fit) 
            
            p0:         [(p1, p2, ...), ...] innermost tuple is initial parameters 
                            for each data set, list of tuples for all data sets
                            if not enough sets of inputs, last input is copied 
                            for remaining data sets.
                            
                            p0.shape = (nsets, npars)
                    OR
                        (p1, p2, ...) single tuple to set same initial parameters 
                            for all data sets
            
                            p0.shape = (npars, )
            
            bounds:     [((l1, l2, ...), (h1, h2, ...)), ...] similar to p0, but use 
                            2-tuples instead of the 1-tuples of p0
                        
                            bounds.shape = (nsets, 2, npars)
                        
                    OR
                        ((l1, l2, ...), (h1, h2, ...)) single 2-tuple to set same 
                            bounds for all data sets
                            
                            bounds.shape = (2, npars)
                            
            minimizer:      string. One of "trf", "dogbox", or "migrad" indicating 
                            which code to use to minimize the function
            
            do_minos:       if true, and if minimizer==migrad, then run minos errors
            
            returns (parameters, lower errors, upper errors, covariance matrix)
        """
        
        # get values from self
        fixed = self.fixed
        shared = self.shared
        sharing_links = self.sharing_links
        fn = self.fn
        self.minimizer = minimizer
        
        # set default p0
        if 'p0' in fitargs:
            p0 = np.array(list(fitargs['p0']))
            del fitargs['p0']
            
            # expand p0
            if len(p0.shape) == 1:
                p0 = np.full((self.nsets, self.npar), p0)
        else:
            p0 = np.ones((self.nsets, self.npar))
        
        # for fixed parameters
        p0_flat_inv = np.concatenate(p0)[::-1]
        
        # get flattened p0 values which are not fixed
        p0_first = self._flatten(p0)
        
        # set default bounds
        if 'bounds' in fitargs.keys():
            
            # get bounds
            bounds = fitargs['bounds']
            
            # check bounds depth
            depth0 = get_depth(bounds[0])
            depth1 = get_depth(bounds[1])
            
            # error output
            err = RuntimeError("Bad bounds format")
            
            # case: low bound == const, set for all
            if depth0 == 0:
                
                hi = bounds[1]
                
                # case: upper bound == const, set for all
                if depth1 == 0:
                    lo = bounds[0]
                        
                # case: upper bound == list, set for all
                elif depth1 == 1:
                    lo = [bounds[0]]*len(hi)
                    
                else:
                    raise err
                    
            # case: low bound == list 
            elif depth0 == 1:
                
                # case: upper bound == const, set for all
                if depth1 == 0:
                    lo = bounds[0]
                    hi = [bounds[1]]*len(lo)
                    
                # case: upper bound == list, set for all
                elif depth1 == 1:
                    lo = bounds[0]
                    hi = bounds[1]
            
                # case: upper bound == list, set for each
                elif depth1 == 2:
                    hi = [b[1] for b in bounds]
                    lo = [[b[0]]*len(b[1]) for b in bounds]

                else:
                    raise err    

            # case: low bound == list, set for each
            elif depth0 == 2:
                
                lo = [b[0] for b in bounds]
                
                # case: upper bound == const, set for each
                if depth1 == 1:
                    hi = [[b[1]]*len(b[0]) for b in bounds]
            
                # case: upper bound == list, set for each
                elif depth1 == 2:
                    hi = [b[1] for b in bounds]
                    
                else:
                    raise err
            
            else:
                raise err
                
            # expand bounds
            lo = self._expand_bound_lim(lo)
            hi = self._expand_bound_lim(hi)
            
            # flatten bounds 
            lo = self._flatten(lo)
            hi = self._flatten(hi)
            
            # construct bounds
            bounds = (lo, hi)
            fitargs['bounds'] = bounds
    
        # make the master function 
        x = self.x
        rng = range(self.nsets)
        metadata = self.metadata
        fprime_dx = self.fprime_dx
          
        def master_fn(x_unused, *par):
            inputs = np.take(np.hstack((par, p0_flat_inv)), sharing_links)
            return np.concatenate([fn[i](x[i], *inputs[i], *metadata[i]) for i in rng])
        
        self.master_fn = master_fn
            
        # make derivative of master function
        def master_fnprime(x_unused, *par):
            inputs = np.take(np.hstack((par, p0_flat_inv)), sharing_links)
            xhi = np.concatenate([fn[i](x[i]+fprime_dx/2, *inputs[i], *metadata[i]) for i in rng])
            xlo = np.concatenate([fn[i](x[i]-fprime_dx/2, *inputs[i], *metadata[i]) for i in rng])
            return (xhi-xlo)/fprime_dx
            
        self.master_fnprime = master_fnprime
      
        # do curve_fit
        if minimizer in ('trf', 'dogbox'):
            fitargs['method'] = minimizer
            par, std_l, std_u, cov = self._do_curve_fit(master_fn, p0_first, **fitargs)
        
        # do migrad
        elif minimizer in ('migrad', 'minos'):
            fprime_dx = self.fprime_dx
            self.master_fn = master_fn
                    
            par, std_l, std_u, cov = self._do_migrad(master_fn, 
                                                     master_fnprime, 
                                                     minimizer == 'minos', 
                                                     p0_first, 
                                                     **fitargs)
        else:
            raise RuntimeError("Unrecognized minimizer input '%s'" % minimizer)
        
        # to array
        par = np.asarray(par)
        std_l = np.asarray(std_l)
        std_u = np.asarray(std_u)
        cov = np.asarray(cov)
        
        # inflate parameters
        par_out = np.hstack((par, p0_flat_inv))[sharing_links]
        
        zero = np.zeros(len(p0_flat_inv))
        std_l_out = np.hstack((std_l, zero))[sharing_links]
        std_u_out = np.hstack((std_u, zero))[sharing_links]
        
        # inflate covariance matrix
        cov_out = []
        for lnk in sharing_links:
            
            # init
            cov_run = np.zeros((self.npar, self.npar))
            
            # assign
            for i in range(self.npar):
                for j in range(self.npar):
                    
                    # fixed values
                    if lnk[j] < 0 or lnk[i] < 0: 
                        cov_run[i, j] = np.nan
                    
                    # cov
                    else:
                        cov_run[i, j] = cov[lnk[i], lnk[j]]
            cov_out.append(cov_run)
                    
        # return
        self.par = par
        self.std_l = std_l
        self.std_u = std_u
        self.cov = cov
        self.par_runwise = par_out
        self.std_l_runwise = std_l_out
        self.std_u_runwise = std_u_out
        self.cov_runwise = cov_out
        
        return (par_out, std_l_out, std_u_out, cov_out)
    
    # ======================================================================= #
    def get_chi(self):
        """
            Calculate chisq/DOF, both globally and for each function.
            
            sets self.chi and self.chi_glbl
            
            return (global chi, list of chi for each fn)
        """
        return (self.gchi2, self.chi2)

    @property
    def gchi2(self):
        """
            Get global chisquared / DOF
        """
        dof = len(self.xcat)-len(self.par)
        if dof <= 0:
            raise DivisionByZero("Zero degrees of freedom")
        
        if self.minimizer == 'migrad':
            self.chi_glbl = self.minuit.fval/dof
        else:
            
            ls = LeastSquares(self.master_fn, self.xcat, self.ycat, 
                            dy = self.dycat, 
                            dx = self.dxcat, 
                            dy_low = self.dycat_low, 
                            dx_low = self.dxcat_low, 
                            fn_prime = self.master_fnprime)
            
            self.chi_glbl = ls(*self.par) / dof
        return self.chi_glbl
        
    @property
    def chi2(self):
        """
            Get chisquared / DOF for each fit function
        """
        self.chi = []
        for i in range(self.nsets):
            
            # get data
            x = self.x[i]
            y = self.y[i]
            p = self.par_runwise[i]
            f = self.fn[i]
            fx = self.fixed[i]
            m = self.metadata[i]
            
            dy = None if self.dy is None else self.dy[i]
            dx = None if self.dx is None else self.dx[i]
            dy_low = None if self.dy_low is None else self.dy_low[i]
            dx_low = None if self.dx_low is None else self.dx_low[i]
        
            # calc ls sum
            ls = LeastSquares(  f, x, y, 
                                dy = dy, 
                                dx = dx, 
                                dx_low = dx_low, 
                                dy_low = dy_low, 
                            )
            # get dof
            dof = len(x)-self.npar+sum(fx)
            if dof == 0:
                warnings.warn("Zero degrees of freedom for data set %d, using len(x) as dof" % i)
                dof = len(x)
            
            self.chi.append(ls(*np.concatenate((p, m))) / dof)
        
        self.chi = np.array(self.chi)
            
        return self.chi
        
    # ======================================================================= #
    def get_par(self):
        """
            Fetch fit parameters
            
            return 4-tuple of (par, std_l, std_u, cov) with format
            
            ([data1:[par1, par2, ...], data2:[], ...], 
             [data1:[std_l1, std_l2, ...], data2:[], ...], 
             [data1:[std_u1, std_u2, ...], data2:[], ...], 
             [data1:[cov1, cov2, ...], data2:[], ...])
        """
        return (self.values, 
                self.lower, 
                self.upper, 
                self.covariance)
    
    @property
    def values(self):       return self.par_runwise
    
    @property
    def lower(self):        return np.abs(self.std_l_runwise)
    
    @property
    def upper(self):        return self.std_u_runwise
    
    @property
    def covariance(self):   return self.cov_runwise
    
    # ======================================================================= #
    def _expand_bound_lim(self, lim):
        """
            For various bound input formats expand such that all bounds are 
            defined explicitly. 
        """

        lim = np.asarray(lim)
        
        # single float case
        if not lim.shape:
            return np.full((self.nsets, self.npar), np.full(self.npar, lim))
            
        # list case: probably each variable defined
        if len(lim.shape) == 1 and len(lim) == self.npar:
            return np.full((self.nsets, self.npar), lim)
        
        # list case: probably each data set defined in full
        if lim.shape == (self.nsets, self.npar):
            return lim
        
        # we don't know what's happening
        raise RuntimeError('Unexpected bound size input')
        
    # ======================================================================= #
    def _flatten(self, arr):
        """
            Flatten input array based on sharing and fixing. 
            Use for p0, bounds
        """
    
        fixed = self.fixed
        shared = self.shared
    
        arr2 = list(arr[0][~fixed[0]])
        for i in range(1, len(arr)):
            arr2.extend(arr[i][(~fixed[i])*(~shared)])
        return np.array(arr2)

# =========================================================================== #
def get_depth(lst, _n=0):
    """
        get depth of list of lists using first element
        
        lst: list
        _n:   internal depth input (n=0 means not a list)
    """
    
    try:
        lst[0]
    except (TypeError, IndexError):
        return _n
    else:
        return get_depth(lst[0], _n+1)
    
# Add to module docstring
__doc__ = __doc__ % (global_fitter.__init__.__doc__, 
                     global_fitter.fit.__doc__, 
                     global_fitter.get_chi.__doc__, 
                     global_fitter.get_par.__doc__, 
                     global_fitter.draw.__doc__, 
                     )
