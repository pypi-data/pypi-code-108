# Python object for combining bdata objects, resulting in an object that 
# behaves exactly like a bdata object. 
# Derek Fujimoto 
# Mar 2020

from bdata import bdata
from mudpy.containers import mdict, mhist, mlist, mvar
import numpy as np
import pandas as pd
import re

class bmerged(bdata):
    """
        Object to store lists or the combination of bdata objects, emulates
        bdata object on completion
    """

    # float machine epsilon - use later to avoid division by zero
    epsilon = np.finfo(float).eps
    
    # modes which are compatible, recorded mode is first entry
    equivalent_modes = [['1x', '1f']]

    # ======================================================================= #
    def __init__(self, bdata_list):
        """
            bdata_list:               list of bdata objects
        """
        
        # sort by run number
        runs = [b.run for b in bdata_list]
        idx = np.argsort(runs)
        bdata_list = np.array(bdata_list)[idx]
        runs = np.array(runs)[idx]
        years = np.array([b.year for b in bdata_list])
        
        # set some common parameters
        for key in ('apparatus', 'area', 'das', 'description', 'duration', 'end_date', 
                    'end_time', 'exp', 'experimenter', 'lab', 'method', 'mode', 
                    'orientation', 'sample', 'start_date', 'start_time', 'title'):
                        
            x = np.array([getattr(b, key) for b in bdata_list])
            setattr(self, key, self._combine_values(key, x))
            
        # set the run number and year
        self.run = int(''.join(map(str, runs)))
        self.year = int(''.join(map(str, years)))
        
        # set ppg, camp, and epics
        for top in ('ppg', 'epics', 'camp'):
            
            d = mdict()
            
            keys = list(getattr(bdata_list[0], top).keys())
            x = mlist([getattr(b, top) for b in bdata_list])
            for key in keys:
                d[key] = self._combine_var(x[key])
                
            setattr(self, top, d)
            
        # combine the histograms
        self._combine_hist(bdata_list)
        
        # checks
        if '2' in self.mode:
            dwelltime = np.array([b.ppg.dwelltime.mean for b in bdata_list])
            beam_off = np.array([b.ppg.beam_off.mean for b in bdata_list])
            beam_on = np.array([b.ppg.beam_on.mean for b in bdata_list])
            
            if any(dwelltime[0] != dwelltime) or any(beam_off[0] != beam_off) \
                or any(beam_on[0] != beam_on):
                raise RuntimeError('%s run has varying ppg ' % self.mode+\
                    'parameters and dwelltimes. Cannot combine histograms.')
            
    # ======================================================================= #
    def _combine_hist(self, bdata_list):
        """
            Apply np.sum to base histograms and set result to top level
            
            Scans are concatenated. 
            SLR histograms are summed.
        """
        
        hist = mlist([b.hist for b in bdata_list])
        
        # these will get combined
        hist_names = ('F+', 'F-', 'B+', 'B-', 
                      'L+', 'L-', 'R+', 'R-', 
                      'NBMF+', 'NBMF-', 'NBMB+', 'NBMB-')
        
        # these modes require appending scans rather than averaging
        hist_xnames = ('Frequency', 'x parameter', )
        
        # make container
        hist_joined = mdict()
        
        # check if x values in histogram
        do_append = any([h in hist[0] for h in hist_xnames])
        
        # get x histogram name
        if do_append:
            for xname in hist_xnames: 
                if xname in hist[0]: 
                    break
            
        for name in hist[0].keys():
            
            # no rule for combining histogram
            if (name not in hist_names) and (name not in hist_xnames): continue
            
            # make the object                            
            hist_obj = mhist()
                        
            # combine scan-less runs (just add the histogrms)
            if not do_append:
                hist_obj.data = np.sum(list(hist[name].data), axis=0)
            
            # combine runs with scans (append the data)
            else:
                hist_obj.data = np.concatenate(hist[name].data)    
            
            # set common histogram attributes
            hist_obj.title = name
            
            for key in ('background1', 'background2', 'n_events', 'n_bytes'):
                setattr(hist_obj, key, int(np.sum(getattr(hist[name], key))))
                
            for key in ('id_number', 'n_bins', 'good_bin1', 'good_bin2', 't0_bin', 
                        't0_ps', 's_per_bin', 'fs_per_bin', 'htype'):
                
                item = getattr(hist[name], key)
                if all(item[0] == item):
                    setattr(hist_obj, key, item[0])
                else:
                    setattr(hist_obj, key, np.nan)
                
            # save in dictionary
            hist_joined[name] = hist_obj
        
        self.hist = hist_joined
    
    # ======================================================================= #
    def _combine_values(self, name, x):
        """
            Combine data array
            
            name:   key associated with attribute
            x:      array of values to combine
        """
        
        if type(x) in (np.ndarray, mlist):
            
            x = np.asarray(x)
            
            if name == 'duration':    return int(np.sum(x))
                          
            elif name in ('end_date', 
                          'end_time'):  return x[-1]
                          
            elif name in ('start_date', 
                          'start_time'):return x[0]
            
            elif name == 'experimenter':
                
                # remove duplicates
                all_names = []
                for i in x:
                    all_names.extend(re.split('[:, ]', i))
                all_names = np.unique(all_names)
                all_names = all_names[all_names!='']
                return ', '.join(all_names)
                
            elif name == 'mode':
                
                if all(x == x[0]):      
                    return x[0]
                else:
                    
                    # check if equivalent mode
                    check, new_mode = self._is_equivalent_mode(x)
                    
                    if check:
                        return new_mode
                    else:               
                        return 'non-matching ("' + str(x[0]) + '" + others)'
                
                
                
            elif name in ('apparatus', 
                          'area', 
                          'das', 
                          'lab', 
                          'method', 
                          'orientation', 
                          'description', 
                          'sample', 
                          'title', 
                          'exp'):
                if all(x == x[0]):      return x[0]
                else:                   return 'non-matching ("' + str(x[0]) + \
                                               '" + others)'
            else:
                raise RuntimeError('Attribute %s not accounted for' % name)
        else:
            return x
    
    # ======================================================================= #
    def _combine_var(self, varlist):
        """
            Combine variable
            
            x: list of mvar objects
        """
        
        # make new variable
        var = mvar()    
        
        # get lists of mean and std
        avg = np.array([v.mean for v in varlist])
        std = np.array([v.std for v in varlist])
        
        # add the float machine epsilon to std to prevent division by zero in
        # the calculation of the weighted mean
        std += self.epsilon
        
        # weighted mean 
        var.mean = np.average(avg, weights=1/std**2)
        
        # stdev of weighted mean
        if all(std == self.epsilon): 
            var.std = 0.0
        else:
            var.std = 1/np.sum(1/std**2)**0.5
        
        # don't know what to do with the skew
        var.skew = np.nan
        
        # min and max
        var.high = np.max([v.high for v in varlist])
        var.low = np.min([v.low for v in varlist])
        
        # things which should be the same across all elements
        for name in ('units', 'description', 'title', 'id_number'):
                
            x = np.array([getattr(v, name) for v in varlist])
                            
            if all(x == x[0]):      
                setattr(var, name, x[0])
            else:                   
                setattr(var, name, 'non-matching ("%s" + others)' % str(x[0]))

        return var

    # ======================================================================= #
    def _is_equivalent_mode(self, mode_list):
        """
            Check if the modes in the mode_list are equivalent, if so, return 
            the first equivalent mode and True, else return false and none
        """
        
        check = False
        for equiv in self.equivalent_modes:
            
            check = all([mode in equiv for mode in mode_list])
            
            if check:   
                return (True, mode_list[0])
                
        return (False, mode_list[0])
                
