from dataclasses import dataclass, field
from typing import List
import numpy as np
import pandas as pd
import h5py
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("whitegrid")


@dataclass
class FragilityCurves:
    ds_descriptions: List[str] = field(default_factory=list)
    thresholds: List[float] = field(default_factory=list)
    centrals: List[float] = field(default_factory=list)
    typology: str = ''
    description: str = ''
    shape: str = 'lognormal'
    imt: str = 'PGA'
    units: str = 'g'

    # private members for properties
    __centrals: List[float] = field(default_factory=list, init=False, repr=False)
    __n_ds: int = 0


    @classmethod
    def from_hdf5_discrete(cls, filename, group_name, dataset_name):
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

