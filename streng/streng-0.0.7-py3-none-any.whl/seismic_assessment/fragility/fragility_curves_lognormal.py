import numpy as np
import pandas as pd
from dataclasses import dataclass
from .fragility_curves import FragilityCurves
from scipy.stats import lognorm

@dataclass
class FragilityCurvesLognormal(FragilityCurves):
    medians: np.array
    stddevs: np.array

    ########################################
    ############# static methods ###########
    ########################################
    @staticmethod
    def prob_for_im_lognormal(intensity_measure: float,
                              medians: np.array,
                              stddevs: np.array) -> np.array:
        return lognorm(s=stddevs, scale=medians).cdf(intensity_measure)

    @staticmethod
    def dataframe_from_lognormal(medians: np.array,
                                 stddevs: np.array,
                                 intensity_measure:str = 'PGA',
                                 intensity_measure_min: float = 0.01,
                                 intensity_measure_max: float = 4.01,
                                 intensity_measure_steps: int = 200,
                                 damage_state_names: list = None):

        intensity_measure_values = np.linspace(intensity_measure_min,
                                               intensity_measure_max,
                                               intensity_measure_steps)

        if damage_state_names == None:
            damage_state_names = [f'DS{i + 1}' for i, m in enumerate(medians)]

        probabilities_array = np.array(
            [FragilityCurvesLognormal.prob_for_im_lognormal(im,
                                                            medians,
                                                            stddevs)
             for im in intensity_measure_values])

        df = pd.DataFrame(index=intensity_measure_values,
                            data=probabilities_array,
                            columns=damage_state_names).rename_axis(intensity_measure, axis=0)

        return df

    ######################################
    ############# constructors ###########
    ######################################
    @classmethod
    def from_medians_stddevs(cls,
                             typology:str,
                             medians: np.array,
                             stddevs: np.array,
                             intensity_measure: str = 'PGA',
                             intensity_measure_min: float = 0.01,
                             intensity_measure_max: float = 4.01,
                             intensity_measure_steps: int = 200,
                             damage_state_names: list = None,
                             format: str = 'lognormal',
                             units: str = 'g',
                             thresholds: np.array = None,
                             centrals: np.array = None):

        df = cls.dataframe_from_lognormal(medians, stddevs,
                                 intensity_measure,
                                 intensity_measure_min,
                                 intensity_measure_max,
                                 intensity_measure_steps,
                                 damage_state_names)



        fc = cls(medians=medians,
                 stddevs=stddevs,
                 format=format,
                 typology=typology,
                 intensity_measure=intensity_measure,
                 units=units,
                 dataframe=df
                 )

        fc.thresholds = thresholds

        if len(thresholds)>0:
            fc.centrals = fc.get_centrals_from_thresholds(thresholds)
        else:
            fc.centrals = centrals

        return fc