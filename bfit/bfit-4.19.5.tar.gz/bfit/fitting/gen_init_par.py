# Generate initial parameters for some common functions
# Derek Fujimoto
# Oct 2021

import numpy as np
import pandas as pd

# ======================================================================= #
def gen_init_par(fn_name, ncomp, bdataobj, asym_mode='combined'):
    """Generate initial parameters for a given function.
    
        fname: name of function. Should be the same as the param_names keys
        ncomp: number of components
        bdataobj: a bdata object representative of the fitting group. 
        asym_mode: what kind of asymmetry to fit
        
        Set and return pd.DataFrame of initial parameters. 
            col: p0, blo, bhi, fixed
            index: parameter name
    """
    
    fn_name = fn_name.lower()
    
    # asym_mode un-used types 
    if asym_mode in (   'h',           # Split Helicity          
                        'hm',          # Matched Helicity
                        'hs',          # Shifted Split          
                        'cs',          # Shifted Combined      
                        'hp',          # Matched Peak Finding
                        'r',           # Raw Scans            
                        'rhist',       # Raw Histograms          
                        '2e_raw_c',    # Combined Hel Raw       
                        '2e_raw_h',    # Split Hel Raw          
                        '2e_sl_h',     # Split Hel Slopes
                        '2e_dif_h',    # Split Hel Diff           
                        'ad',          # Alpha Diffusion  
                        "at_c",        # Combined Hel (Alpha Tag)
                        "at_h",        # Split Hel (Alpha Tag) 
                        "nat_c",       # Combined Hel (!Alpha Tag)
                        "nat_h",       # Split Hel (!Alpha Tag)
                    ):
        errmsg = "Asymmetry calculation type not implemented for fitting"
        raise RuntimeError(errmsg)
    
    # get asymmetry
    x, a, da = bdataobj.asym(asym_mode)
    
    # set pulsed exp fit initial parameters
    if fn_name in ('exp', 'bi exp', 'str exp', 'biexp', 'strexp'):
        # ampltitude average of first 5 bins
        amp = abs(np.mean(a[0:5])/ncomp)
        
        # T1: time after beam off to reach 1/e
        idx = int(bdataobj.ppg.beam_on.mean)
        beam_duration = x[idx]
        amp_beamoff = a[idx]
        target = amp_beamoff/np.exp(1)
        
        x_target = x[np.sum(a>target)]
        T1 = abs(x_target-beam_duration)
        
        # bounds and amp
        if asym_mode == 'n':
            amp_bounds = (-np.inf, np.inf)
            amp = -amp
        else:
            amp_bounds = (0, np.inf)
        
        # set values
        if fn_name == 'exp':
            par_values = {  '1_T1':(1./T1, 0, np.inf, False), 
                            'amp':(amp, *amp_bounds, False), 
                         }
                        
        elif fn_name in ('bi exp', 'biexp'):
            par_values = {  '1_T1':(1./T1, 0, np.inf, False), 
                            '1_T1b':(10./T1, 0, np.inf, False), 
                            'fraction_b':(0.5, 0, 1, False), 
                            'amp':(amp, *amp_bounds, False), 
                         }
        
        elif fn_name in ('str exp', 'strexp'):
            par_values = {  '1_T1':(1./T1, 0, np.inf, False), 
                            'beta':(0.5, 0, 1, False),
                            'amp':(amp, *amp_bounds, False), 
                         }
                        
    # set time integrated fit initial parameters
    elif fn_name in ('lorentzian', 'gaussian', 'bilorentzian', 'quadlorentz'):
        
        # get baseline
        base = np.mean(a[:5])
        
        # check for upside down helicities (peak going up)
        avg = np.mean(a)
        if base < avg: 
            amin = max(a[a!=0])
        else:
            amin = min(a[a!=0])
        
        # get peak asym value
        peak = x[np.where(a==amin)[0][0]]
        height = base-amin
        width = 2*abs(peak-x[np.where(a<amin+height/2)[0][0]])
        
        # bounds
        if asym_mode == 'n':
            height_bounds = [-np.inf, 0]
        else:
            height_bounds = [0, np.inf]
        
        # check bounds validity
        if height < height_bounds[0]:
            height_bounds[0] = -np.inf
        
        if height > height_bounds[1]:
            height_bounds[1] = np.inf
        
        # set values (value, low bnd, high bnd, fixed)
        if fn_name == 'lorentzian':	
            par_values = {'peak':(peak, min(x), max(x), False), 
                          'fwhm':(width, 0, np.inf, False), 
                          'height':(height, *height_bounds, False), 
                          'baseline':(base, -np.inf, np.inf, False)
                         }
        elif fn_name == 'gaussian':
            par_values = {'mean':(peak, min(x), max(x), False), 
                          'sigma':(width, 0, np.inf, False), 
                          'height':(height, *height_bounds, False), 
                          'baseline':(base, -np.inf, np.inf, False)
                          }
        elif fn_name == 'bilorentzian':
            par_values = {'peak':(peak, min(x), max(x), False), 
                          'fwhmA':(width*10, 0, np.inf, False), 
                          'heightA':(height/10, *height_bounds, False), 
                          'fwhmB':(width, 0, np.inf, False), 
                          'heightB':(height*9/10, *height_bounds, False), 
                          'baseline':(base, -np.inf, np.inf, False)
                         }
        elif fn_name == 'quadlorentz':
            
            dx = max(x)-min(x)
            par_values = {'nu_0':((max(x)+min(x))/2, min(x), max(x), False), 
                          'nu_q':(dx/12, 0, dx, False), 
                          'efgAsym':(0, 0, 1, True), 
                          'efgTheta':(0, 0, 2*np.pi, True), 
                          'efgPhi':(0, 0, 2*np.pi, True), 
                          'amp0':(height, height*0.1, np.inf, False), 
                          'amp1':(height, height*0.1, np.inf, False), 
                          'amp2':(height, height*0.1, np.inf, False), 
                          'amp3':(height, height*0.1, np.inf, False), 
                          'fwhm':(dx/10, 0, dx, False), 
                          'baseline':(base, -np.inf, np.inf, False)
                         }
     
    else:
        raise RuntimeError('Bad function name: "{}".'.format(fn_name))
    
    # do multicomponent
    par_values2 = {}
    if ncomp > 1: 
        for c in range(ncomp): 
            for n in par_values.keys():
                if 'baseline' not in n:
                    par_values2[n+'_%d' % c] = par_values[n]
                else:
                    par_values2[n] = par_values[n]
    else:
        par_values2 = par_values
    
    return pd.DataFrame(par_values2, index=['p0', 'blo', 'bhi', 'fixed']).transpose()

