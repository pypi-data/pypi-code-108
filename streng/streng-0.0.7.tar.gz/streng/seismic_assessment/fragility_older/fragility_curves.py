from dataclasses import dataclass, field
from typing import List
import numpy as np
import pandas as pd
import h5py
from scipy.stats import lognorm

import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")


def p_ds(x, medians, stddevs, dist_type='lognormal'):
    if dist_type == 'lognormal':
        return lognorm(s=stddevs, scale=medians).cdf(x)
    else:
        return None


@dataclass
class FragilityCurves:
    θs: List[float] = field(default_factory=list)
    βs: List[float] = field(default_factory=list)
    μXs: List[float] = field(default_factory=list)
    σXs: List[float] = field(default_factory=list)
    ds_descriptions: List[str] = field(default_factory=list)
    thresholds: List[float] = field(default_factory=list)
    centrals: List[float] = field(default_factory=list)
    __centrals: List[float] = field(default_factory=list, init=False, repr=False)

    __n_ds: int = 0
    typology: str = ''
    description: str = ''
    shape: str = 'lognormal'
    imt: str = 'PGA'
    units: str = 'g'
    df_all: pd.DataFrame = None
    # means: list = field(default_factory=list)

    def __post_init__(self):
        pass

    # -------------------------------------
    # ---- Properties ---------------------
    # -------------------------------------
    @property
    def centrals(self) -> List[float]:
        return self.__centrals

    @centrals.setter
    def centrals(self, value: List[float]):
        self.__centrals = value

    @property
    def n_ds(self) -> int:
        return self.__n_ds

    # -------------------------------------
    # ---- Classmethods -------------------
    # -------------------------------------

    @classmethod
    def from_hdf5_θβ_continuous(cls, filename, group_name, dataset_name):
        with h5py.File(filename, mode='r') as f:
            group = f.get(group_name)
            dataset = group[dataset_name]

            fc = cls()
            fc.θs = list(dataset['θ'])
            fc.βs = list(dataset['β'])
            fc.thresholds = list(dataset['thresholds'])
            fc.ds_descriptions = dataset.attrs['damage state description']
            fc.typology = dataset.attrs['typology']
            fc.shape = dataset.attrs['shape']
            fc.imt = dataset.attrs['imt']
            fc.units = dataset.attrs['units']

            # fc.__calc_centrals()

            return fc




    def get_centrals_from_thresholds(self):
        _centrals = []
        _thresholds = self.thresholds.copy()
        _thresholds.append(1.0)
        for i in range(0, len(_thresholds) - 1):
            _centrals.append(0.5 * (_thresholds[i] + _thresholds[i + 1]))

        # Για το DS0 θεωρώ ότι ο κεντρικός δείκτης βλάβης είναι 0
        self.__centrals = [0.0] + _centrals


    # @property
    # def centrals(self):
    #     return self.__centrals
    #
    # @centrals.setter
    # def centrals(self, centrals):
    #     self.__centrals = centrals
    #     # if len(centrals) > 0:
    #     #     self.__centrals = centrals
    #     # else:
    #     #     self.__calc_centrals()

    @property
    def make_the_dataframe_from_θβs(self):
        minIML = 0.0
        maxIML = 4.0
        xs = np.linspace(minIML, maxIML, 500)

        for iDS in range(len(self.θs)):
            _θ = self.θs[iDS]
            _β = self.βs[iDS]
            p_ds(xs, _θ, _β, self.dist_type)


    def get_μs_from_medians(self):
        if self.dist_type == 'lognormal':
            self.μXs = np.log(np.array(self.θs)).tolist()
            
    # def get_means_from_μs(self):
    #     if self.dist_type == 'lognormal':
    #         self.means = np.exp(np.array(self.μs) + 0.5*np.array(self.stddevs)**2).tolist()



    def calc(self, x):
        p = p_ds(x, self.medians, self.stddevs, self.dist_type)

        _δP = []
        for i in range(0, len(p) - 1):
            _δP.append(p[i] - p[i + 1])
        # Για το τελευταίο DS η πιθανότητα είναι απευθείας από την καμπύλη τρωτότητας
        _δP.append(p[-1])
        # Για το DS0 η πιθανότητα είναι η 1.0 μείον την πιθανότητα του DS1
        δP = [1.0 - p[0]] + _δP

        if len(self.thresholds) > 0:
            mdf = sum(np.array(δP) * np.array(self.centrals))
        else:
            mdf = None

        _results = {'P': p,
                    'δP': δP,
                    'MDF': mdf}

        return _results

    def plot_fragility_model(self, minIML, maxIML, dist_type='lognormal', colors=None):
        xs = np.linspace(minIML, maxIML, 500)

        f, ax = plt.subplots(figsize=(12, 8))

        for iDS in range(len(self.θs)):
            _θ = self.θs[iDS]
            _β = self.βs[iDS]

            if colors is None:
                color = 'grey'
            else:
                if colors=='default5':
                    colors = ['#abdb57', '#086c34', '#e28b05', '#fb4c4c', '#b91f1f']
                color = colors[iDS]

            if len(self.ds_descriptions) > 0:
                _label = f'{self.ds_descriptions[iDS]}'
            else:
                _label = f'DS{iDS + 1}'

            ax.plot(xs, p_ds(xs, _θ, _β, dist_type), linewidth=2, color=color, label=_label)

        ax.set_xlim(minIML, maxIML)

        ax.set_xlabel(f'{self.imt} [{self.units}]', fontsize=12)

        ax.set_ylim(0., 1.01)
        ax.set_ylabel('Probabilty of exceedance', fontsize=12)
        ax.legend()

        return f, ax







