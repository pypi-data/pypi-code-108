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

    def copy(self):
        return deepcopy(self)

    def annualize(self, wgts):
        '''
        Note that we assume that the time axis starts with January and
        ends with December if it is monthly.
        '''
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

    def mk_linear(self, wgts_tas=None, verbose=False):
        ''' Make pseudo-TRW from GCM simulated tas
        '''
        if isinstance(wgts_tas, Weights): wgts_tas = wgts_tas.wgts

        pTRW = self.pobj.copy()
        tas = Series(time=self.pobj.clim['model_tas'].time, value=self.pobj.clim['model_tas'].da.values)
        tas_ann = tas.annualize(wgts=wgts_tas)
        pTRW.time = tas_ann.time
        pTRW.value = prep.minmax_scale(tas_ann.value[:, np.newaxis])[:, 0]

        if verbose:
            utils.p_success(f'''pseudo-TRW created using [linear] method with kwargs:
            wgts_tas: {wgts_tas}
            ''')

        return pTRW


    def mk_bilinear(self, wgts_tas=None, wgts_pr=None, ratio_tas=0.5, ratio_pr=0.5, verbose=False):
        ''' Make pseudo-TRW from GCM simulated tas & pr
        '''
        if isinstance(wgts_tas, Weights): wgts_tas = wgts_tas.wgts
        if isinstance(wgts_pr, Weights): wgts_pr = wgts_pr.wgts

        pTRW = self.pobj.copy()
        tas = Series(time=self.pobj.clim['model_tas'].time, value=self.pobj.clim['model_tas'].da.values)
        pr = Series(time=self.pobj.clim['model_pr'].time, value=self.pobj.clim['model_pr'].da.values)
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
            ''')

        return pTRW


class deepGreen:
    pass