from tkinter import Variable
import numpy as np
import p2k
from . import utils
from sklearn import preprocessing as prep
import matplotlib.pyplot as plt
from copy import deepcopy

class Weights:
    def __init__(self, wgts):
        self.wgts = wgts
        assert len(wgts) % 12 == 0, 'len(wgts) % 12 == 0 must be satisfied!'

    def plot(self, figsize=(10, 4), title=None, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        months = np.arange(1, len(self.wgts)+1)
        ax.bar(months, self.wgts)
        ax.set_ylabel('Weight')
        ax.set_xlabel('Month')
        ax.set_xticks(months)
        ax.set_xticklabels([m if m!=0 else 12 for m in months%12])

        if title is not None:
            ax.set_title(title, fontweight='bold')

        if 'fig' in locals():
            return fig, ax
        else:
            return ax

class Series:
    ''' A timeseries object

    '''
    def __init__(self, time, value):
        self.time = time
        self.value = value
        self.dt = np.median(np.diff(time))

    def copy(self):
        return deepcopy(self)

    def annualize(self, wgts):
        '''
        Note that we assume that the time axis starts with January and
        ends with December if it is monthly.
        '''
        assert np.abs(self.dt - 1/12) < 0.1, 'The timeseries has to be monthly!'
        if isinstance(wgts, Weights): wgts = wgts.wgts

        new = self.copy()
        nw = len(wgts)
        nlags = nw // 12 - 1
        new.time = np.arange(int(self.time[0])+nlags, int(self.time[-1])+1) 
        nyr = len(new.time)
        new.value = []
        for i in range(nyr):
            new.value.append(np.dot(self.value[i*12:i*12+nw], wgts/np.sum(wgts)))

        new.value = np.array(new.value)
        return new

    def plot(self, figsize=(10, 4), title=None, ax=None, **kwargs):
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        ax.plot(self.time, self.value, **kwargs)
        ax.set_ylabel('Value')
        ax.set_xlabel('Time')

        if title is not None:
            ax.set_title(title, fontweight='bold')

        if 'fig' in locals():
            return fig, ax
        else:
            return ax


class PseudoTRW:
    def __init__(self, pobj):
        '''

        Parameters
        ----------

        pobj : p2k.ProxyRecord
            the ProxyRecord object from p2k

        '''
        self.pobj = pobj

    def linear(self, wgts_tas=None, bds_tas=None, verbose=False):
        ''' Make pseudo-TRW from GCM simulated tas

        Parameters
        ----------

        bds_tas : tuple
            assume tas in [degC]
        '''
        if isinstance(wgts_tas, Weights): wgts_tas = wgts_tas.wgts

        pTRW = self.pobj.copy()

        tas_time = self.pobj.clim['model_tas'].time
        tas_value = self.pobj.clim['model_tas'].da.values
        if np.min(tas_value) > 200:
            # if in [K], convert to [degC]
            tas_value -= 273.15

        if bds_tas is not None:
            lb, ub = bds_tas
            tas_value[tas_value<lb] = lb
            tas_value[tas_value>ub] = ub

        tas = Series(time=tas_time, value=tas_value)
        tas_ann = tas.annualize(wgts=wgts_tas)
        pTRW.time = tas_ann.time
        pTRW.value = prep.minmax_scale(tas_ann.value[:, np.newaxis])[:, 0]

        if verbose:
            utils.p_success(f'''pseudo-TRW created using [linear] method with kwargs:
            wgts_tas: {wgts_tas}
            bds_tas: {bds_tas}
            ''')

        return pTRW


    def bilinear(self, wgts_tas=None, wgts_pr=None, bds_tas=None, bds_pr=None,
        ratio_tas=0.5, ratio_pr=0.5, verbose=False):
        ''' Make pseudo-TRW from GCM simulated tas & pr

        Parameters
        ----------

        bds_tas : tuple
            assume tas in [degC]

        bds_pr : tuple
            assume pr in [mm/month]
        '''
        if isinstance(wgts_tas, Weights): wgts_tas = wgts_tas.wgts
        if isinstance(wgts_pr, Weights): wgts_pr = wgts_pr.wgts

        pTRW = self.pobj.copy()

        tas_time = self.pobj.clim['model_tas'].time
        tas_value = self.pobj.clim['model_tas'].da.values
        if np.min(tas_value) > 200:
            # if in [K], convert to [degC]
            tas_value -= 273.15

        if bds_tas is not None:
            lb, ub = bds_tas
            tas_value[tas_value<lb] = lb
            tas_value[tas_value>ub] = ub

        pr_time = self.pobj.clim['model_pr'].time
        pr_value = self.pobj.clim['model_pr'].da.values
        if np.max(pr_value) < 1:
            # if in [kg m-2 s-1], convert to [mm/month]
            pr_value *=  3600*24*30

        if np.max(pr_value) < 1:
            # if in [K], convert to [degC]
            tas_value -= 273.15
        if bds_pr is not None:
            lb, ub = bds_pr
            pr_value[pr_value<lb] = lb
            pr_value[pr_value>ub] = ub

        tas = Series(time=tas_time, value=tas_value)
        pr = Series(time=pr_time, value=pr_value)
        tas_ann = tas.annualize(wgts=wgts_tas)
        pr_ann = pr.annualize(wgts=wgts_pr)
        pTRW.time = tas_ann.time
        tas_ann_N = tas_ann.value[:, np.newaxis]
        pr_ann_N = pr_ann.value[:, np.newaxis]
        pTRW.value = ratio_tas*prep.minmax_scale(tas_ann_N)[:, 0] + ratio_pr*prep.minmax_scale(pr_ann_N)[:, 0]

        if verbose:
            utils.p_success(f'''pseudo-TRW created using [bilinear] method with kwargs:
             wgts_tas: {wgts_tas}
              wgts_pr: {wgts_pr}
            ratio_tas: {ratio_tas}
             ratio_pr: {ratio_pr}
              bds_tas: {bds_tas}
              bds_pr: {bds_pr}
            ''')

        return pTRW


class deepGreen:
    pass