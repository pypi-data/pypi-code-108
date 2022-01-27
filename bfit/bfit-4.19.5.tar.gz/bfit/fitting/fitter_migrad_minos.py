# Fitter functions using curve_fit as the backend
# Derek Fujimoto
# Nov 2020

from bfit.fitting.fit_bdata import fit_bdata
from bfit.fitting.fitter import fitter as fit_base

class fitter(fit_base):
    
    __name__ = 'migrad (minos)'
    
    def _do_fit(self, data, fn, omit=None, rebin=None, shared=None, hist_select='', 
                xlims=None, asym_mode='c', fixed=None, parnames=None, **kwargs):
        """Inputs match fit_bdata"""
        
        return fit_bdata(data, 
                         fn, 
                         omit=omit, 
                         rebin=rebin, 
                         shared=shared, 
                         hist_select=hist_select, 
                         xlims=xlims, 
                         asym_mode=asym_mode, 
                         fixed=fixed, 
                         minimizer='minos', 
                         name=parnames, 
                         **kwargs)
            
