import pandas as pd
import numpy as np


def frame_element_results(results_dataframe, element, quantity, location):
    _df = results_dataframe.loc[results_dataframe['Frame'] == element]
    return _df[quantity].iloc[location]
