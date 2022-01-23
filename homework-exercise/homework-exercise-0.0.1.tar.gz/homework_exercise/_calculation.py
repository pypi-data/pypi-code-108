import numpy as np

from ._data import DATA_DICT, delay_data

def some_calculation_function():
    return np.zeros((DATA_DICT["important_value1"], DATA_DICT["important_value2"]))


def some_calculation_function2():
    data = delay_data()
    return data["Section 1"]["data_point"] + data["Section 2"]["data_point"]