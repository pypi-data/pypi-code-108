# Python object for math operations on bdata objects. 
# Derek Fujimoto
# Aug 2019
from mudpy.containers import mdict, mhist, mlist
from bdata import bdata
import numpy as np
import pandas as pd

class bjoined(bdata):
    """
        Object to store lists or the combination of bdata objects. 
        
        data:                   list of bdata objects    
        hist_joined:            combined histograms
    """
    
    common = ('apparatus', 'area', 'das', 'description', 'exp', 'lab', 'method', 
              'mode', 'year')
    
    # ======================================================================= #
    def __init__(self, bdata_list):
        """
            bdata_list:               list of bdata objects
        """
        
        # sort by run number
        runs = [b.run for b in bdata_list]
        idx = np.argsort(runs)
        self.data = np.array(bdata_list)[idx]
        
        # set some calculation-required parameters
        for c in self.common:
            self._set_common(c)
        
        # combine the histograms
        self._combine_hist()
    
    # ======================================================================= #
    def __getattr__(self, name):
        """
            Get attribute of underlying data as a list.
        """
        try:
            # fetch from top level
            return getattr(object, name)
        except AttributeError:
            return mlist([getattr(d, name) for d in self.data])

    # ======================================================================= #
    def __repr__(self):
        """
            Nice printing of parameters.
        """
        
        d = [dat.__dict__ for dat in self.data]
        dkeys = list(d[0].keys())
        if dkeys:
            items = []
            dkeys.sort()
            for key in dkeys:
                if key[0] == '_': continue
                
                # exceptions
                if key in ('ivar', 'sclr'):
                    items.append([key, [di[key].__class__ for di in d]])
              
                # common items
                elif key in self.common:
                    items.append([key, getattr(self, key)])
                
                # mdict objects
                elif d[0][key].__class__ == mdict:
                    items.append([key, d[0][key]])
                
                # strings and non iterables
                elif not hasattr(d[0][key], '__iter__') or d[0][key].__class__ == str:
                    items.append([key, [di[key] for di in d]])                
                
                # misc objects
                else:
                    items.append([key, [di[key].__class__ for di in d]])
                
            m = max(map(len, dkeys)) + 1
            s = '\n'.join([k.rjust(m)+': '+repr(v) for k, v in sorted(items)])
            return s
        else:
            return self.__class__.__name__ + "()"

    # ======================================================================= #
    def _combine_hist(self):
        """
            Apply np.sum to base histograms and set result to top level
            
            Scans are concatenated. 
            SLR histograms are summed.
        """
        
        # these will get combined
        hist_names = ('F+', 'F-', 'B+', 'B-', 
                      'L+', 'L-', 'R+', 'R-', 
                      'NBMF+', 'NBMF-', 'NBMB+', 'NBMB-')
        
        # these modes require appending scans rather than averaging
        hist_xnames = ('Frequency', 'x parameter', )
        
        # make container
        hist_joined = mdict()
        
        # check if x values in histogram
        do_append = any([h in self.hist[0] for h in hist_xnames])
        
        # get x histogram name
        if do_append:
            for xname in hist_xnames: 
                if xname in self.hist[0]: 
                    break
            
        for name in self.hist[0].keys():
            
            # no rule for combining histogram
            if (name not in hist_names) and (name not in hist_xnames): continue
            
            # make the object                            
            hist_obj = mhist()
            
            # combine scan-less runs (just add the histogrms)
            if not do_append:
                hist_data = np.sum(list(self.hist[name].data), axis=0)
            
            # combine runs with scans (append the data)
            elif name in hist_xnames:                
                hist_obj.data = np.concatenate(self.hist[xname].data)
            else:
                hist_obj.data = np.concatenate(self.hist[name].data)    
            
            # set common histogram attributes
            hist_obj.title = name
            
            for key in ('background1', 'background2', 'n_events', 'n_bytes'):
                setattr(hist_obj, key, int(np.sum(getattr(self.hist[name], key))))
                
            for key in ('id_number', 'n_bins', 'good_bin1', 'good_bin2', 't0_bin', 
                        't0_ps', 's_per_bin', 'fs_per_bin', 'htype'):
                
                item = getattr(self.hist[name], key)
                if all(item[0] == item):
                    setattr(hist_obj, key, item[0])
                else:
                    setattr(hist_obj, key, np.nan)
                
            # save in dictionary
            hist_joined[name] = hist_obj
        
        self.hist_joined = hist_joined
    
    # ======================================================================= #
    def _get_area_data(self, nbm=False):
        """Get histogram list based on area type. 
        List pattern: [type1_hel+, type1_hel-, type2_hel+, type2_hel-]
        where type1/2 = F/B or R/L in that order.
        """
        
        # get histogram
        hist = self.hist_joined
        
        # return data set
        if self.mode == '1n' or nbm:
            data = [hist['NBMF+'].data, \
                    hist['NBMF-'].data, \
                    hist['NBMB+'].data, \
                    hist['NBMB-'].data]
            
        elif self.area == 'BNMR':
            data = [hist['F+'].data, \
                    hist['F-'].data, \
                    hist['B+'].data, \
                    hist['B-'].data]
        
        elif self.area == 'BNQR':
            data = [hist['R+'].data, \
                    hist['R-'].data, \
                    hist['L+'].data, \
                    hist['L-'].data]
        else:
            data = []
        
        if self.mode == '2h':
            data.extend([hist['AL1+'].data, hist['AL1-'].data, 
                         hist['AL0+'].data, hist['AL0-'].data, 
                         hist['AL3+'].data, hist['AL3-'].data, 
                         hist['AL2+'].data, hist['AL2-'].data])
        
        # copy
        return [np.copy(d) for d in data]
    
    # ======================================================================= #
    def _get_ppg(self, name):
        """Get ppg parameter mean value"""
        
        values = self.ppg[name].mean
        if not all([values[0] == v for v in values]):
            raise RuntimeError('PPG Parameter %s not equal in all cases' % name)

        return values[0]
    
    # ======================================================================= #
    def _get_xhist(self):
        """Get histogram data for x axis."""
        if self.mode == '1f':
            xlabel = 'Frequency'
        elif self.mode == '1w':
            xlabel = 'x parameter'
        elif self.mode == '1n':
            for xlabel in self.hist.keys():
                if 'cell' in xlabel.lower():    
                    break
        
        return self.hist_joined[xlabel].data
    
    # ======================================================================= #
    def _set_common(self, name):
        """
            Set attribute which is shared among all joine data sets.
        """
        
        item_list = getattr(self, name)
        if all([item_list[0] == i for i in item_list]):
            setattr(self, name, item_list[0])
        else:
            setattr(self, name, item_list)
            
    # ======================================================================= #
    def asym_mean(self, *asym_args, **asym_kwargs):
        """
            Get individual asymmetries first, then combine with weighted mean
            
            asym_args: dict, passed to bdata.asym. 
        """
    
        # calcuate asymmetries
        asym_list = [b.asym(*asym_args, **asym_kwargs) for b in self.data]
        
        # make into dataframes, get errors as weights
        for i in range(len(asym_list)):
            asym = asym_list[i]
            
            # tuple return: (x, a, da)
            if type(asym) is np.ndarray:
                asym_list[i] = pd.DataFrame({'x':asym[0], 'a':asym[1], 'da':asym[2]})
            
            # dict return: (x, p:(a, da), ...)
            elif type(asym) is mdict:
                
                # if entry is tuple, split into error and value
                klist = list(asym.keys())
                for k in klist:
                    if type(asym[k]) is tuple:
                        asym['d'+k] = asym[k][1]
                        asym[k] = asym[k][0]
                    else:
                        asym['x'] = asym[k]
                        del asym[k]
                        xk = k
                
                # make into data frame
                asym_list[i] = pd.DataFrame(asym)
        
        # combine the data frames and set index
        df = pd.concat(asym_list).set_index('x')
        
        # slice into errors and values
        values = pd.DataFrame(df[[c for c in df.columns if 'd' not in c]])
        errors = pd.DataFrame(df[[c for c in df.columns if 'd' in c]])
        
        # rename error columns
        errors.rename(columns={c:c.replace('d', '') for c in errors.columns}, 
                      inplace=True)
        
        # make errors weights
        errors = 1/errors.apply(np.square)
        
        # weight the values
        values = values * errors
        
        # group and sum 
        values = values.groupby(level=0).sum()
        errors = errors.groupby(level=0).sum()

        # weighted mean
        values = values / errors
        errors = 1/errors.apply(np.sqrt)
        
        # make output type the same as the original 
        if type(asym) is np.ndarray:
            return np.array([values.index.values, 
                             values.values.T[0], 
                             errors.values.T[0]])
        
        elif type(asym) is mdict:
            out = mdict()
            out[xk] = values.index
            for c in values.columns:
                out[c] = (values[c].values, errors[c].values)
        
            return out
        
    # ======================================================================= #
    def beam_kev(self, get_error=False):
        return np.asarray([d.beam_kev(get_error=get_error) for d in self.data])
    
    # ======================================================================= #
    def get_pulse_s(self):
        return np.asarray([d.get_pulse_s() for d in self.data])
        
