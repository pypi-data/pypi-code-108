import numpy as np
import pandas as pd
from lxml import etree
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from dataclasses import dataclass
from dataclasses import field
from cached_property import cached_property


@dataclass
class FragilityCurves:
    typology: str  # e.g. 'RC3.1LL'
    format: str  # e.g. 'discrete', 'lognormal'
    intensity_measure: str  # e.g. 'PGA', 'Sa03', 'AvgSa'
    units: str  # e.g. 'g'
    dataframe: pd.DataFrame = field(repr=False)

    thresholds: np.array = field(init=False, repr=False)
    centrals: np.array = field(init=False, repr=False)

    _damage_state_descriptions: list = field(init=False, repr=False)
    _intensity_measure_values: np.array = field(init=False, repr=False)

    def __post_init__(self):
        self._damage_state_descriptions = list(self.dataframe.columns)
        self._intensity_measure_values = self.dataframe.index.to_numpy()

    ####################################
    ############# properties ###########
    ####################################
    @property
    def damage_state_descriptions(self) -> list:
        return self._damage_state_descriptions

    @property
    def intensity_measure_values(self) -> np.array:
        return self._intensity_measure_values

    #####################################
    ####### cached properties ###########
    #####################################
    @cached_property
    def mean_damage_factors_array(self) -> np.array:
        return self.dataframe.apply(
            lambda row: self.mean_damage_factor(self.delta_probabilities(row.to_numpy()), self.centrals),
            axis=1).to_numpy()

    ########################################
    ############# static methods ###########
    ########################################
    @staticmethod
    def delta_probabilities(probabilities: np.array) -> np.array:
        _deltaP = list()

        for i, poe in enumerate(probabilities):  # or for i in range(0, len(poes)-1):
            if i < len(probabilities) - 1:
                _deltaP.append(probabilities[i] - probabilities[i + 1])

        _deltaP.append(probabilities[-1])
        deltaP = np.array([1.0 - sum(_deltaP)] + _deltaP)
        return deltaP

    @staticmethod
    def mean_damage_factor(dps: np.array, centrals: np.array) -> float:
        return sum(centrals * dps[1:])

    @staticmethod
    def get_centrals_from_thresholds(thresholds: np.array) -> np.array:
        _centrals = []
        _thresholds = np.append(thresholds, 1.0)
        for i in range(0, len(_thresholds) - 1):
            _centrals.append(0.5 * (_thresholds[i] + _thresholds[i + 1]))

        return np.array(_centrals)

    #################################
    ############# methods ###########
    #################################
    def plot(self, figure_size: tuple = (12, 8), include_mdf: bool = False) -> Figure:
        f, ax = plt.subplots(figsize=figure_size)

        if len(self.damage_state_descriptions) == 5:
            colors_damage = ["#40c5bf", "#53db5f", "#e0ea21", "#deaf2d", "#ef2c23"]
        elif len(self.damage_state_descriptions) == 4:
            colors_damage = ["#53db5f", "#e0ea21", "#deaf2d", "#ef2c23"]
        else:
            colors_damage = None


        for i, ds in enumerate(self.damage_state_descriptions):
            ys = self.dataframe[ds]
            ax.plot(self.intensity_measure_values,
                    ys,
                    lw=2,
                    linestyle='-',
                    label=f"DS{i + 1}",
                    color=colors_damage[i])

        if include_mdf:
            ax.plot(self.intensity_measure_values, self.mean_damage_factors_array, color='dimgrey', lw=4,
                    linestyle='--', label=f"MDF")

        ax.set_title(self.typology, fontsize=20)
        ax.set_ylabel('Probability of Exceedance', fontsize=16)
        ax.set_xlabel(f'{self.intensity_measure} ({self.units})', fontsize=16)
        ax.legend()
        ax.set_xlim(0.0, max(self.intensity_measure_values))
        ax.set_ylim(0.0, 1.0)

        print(type(f))
        return f

    def get_oq_xml_element_fragility(self, xml_root: etree.Element) -> etree.SubElement:
        ff_child = etree.SubElement(xml_root, "fragilityFunction")
        ff_child.set('id', self.typology)
        ff_child.set('format', 'discrete')

        imls_child = etree.SubElement(ff_child, "imls")
        imls_child.set('imt', self.intensity_measure)
        imls_child.set('noDamageLimit', '0.02')
        imls_child.text = ' '.join([f'{i:.6f}' for i in self.intensity_measure_values])

        for ls in self.damage_state_descriptions:
            poes_child = etree.SubElement(ff_child, "poes")
            poes_child.set('ls', ls)
            poes_child.text = ' '.join([f'{i:.6f}' for i in self.dataframe[ls].tolist()])

        return ff_child

    def get_oq_xml_element_vulnerability(self, xml_root: etree.Element) -> etree.SubElement:
        vf_child = etree.SubElement(xml_root, "vulnerabilityFunction")
        vf_child.set('id', self.typology)
        vf_child.set('dist', 'BT')

        imls_child = etree.SubElement(vf_child, "imls")
        imls_child.set('imt', self.intensity_measure)
        imls_child.text = ' '.join([f'{i:.4f}' for i in self.intensity_measure_values])

        meanLRs_child = etree.SubElement(vf_child, "meanLRs")
        meanLRs_child.text = ' '.join([f'{i:.4f}' for i in self.mean_damage_factors_array])

        zeros = np.zeros(len(self.intensity_measure_values)).tolist()
        covLRs_child = etree.SubElement(vf_child, "covLRs")
        covLRs_child.text = ' '.join([f'{i:.1f}' for i in zeros])

        return vf_child

    ######################################
    ############# constructors ###########
    ######################################
    @classmethod
    def from_martins_silva_2020_csv(cls, path: str, csv_filename: str):

        # Read the csv file contents and create the dataframe
        typology = csv_filename[0:len(csv_filename) - 4]
        df = pd.read_csv(f'{path}{csv_filename}', index_col=0, sep=r",").T

        # changing index column to float
        df.index = df.index.astype(float)

        # get intensity measure
        intensity_measure = df.columns.name
        df.columns.name = None
        df.index.name = intensity_measure

        # create the class instance
        fc = cls(format='discrete',
                 typology=typology,
                 intensity_measure=intensity_measure,
                 units='g',
                 dataframe=df)

        fc.centrals = np.array([0.05, 0.2, 0.6, 1.0])

        return fc

    @classmethod
    def from_martins_silva_2020_hdf5_collection(
            cls,
            path_filename: str,
            typology: str):

        df = pd.read_hdf(path_filename, f'/MartinsSilva2020/fragility_other_IMs/{typology}')

        intensity_measure = df.columns[0]
        df.set_index([intensity_measure], inplace=True)
        df.index.name = intensity_measure

        # create the class instance
        fc = cls(format='discrete',
                 typology=typology,
                 intensity_measure=intensity_measure,
                 units='g',
                 dataframe=df)

        fc.centrals = np.array([0.05, 0.2, 0.6, 1.0])

        return fc