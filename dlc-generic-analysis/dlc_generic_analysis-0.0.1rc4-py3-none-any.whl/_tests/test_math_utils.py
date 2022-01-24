import pandas
import numpy as np
from dlc_generic_analysis import math_utils, utils


def test_distance():
    data = [[0, 1, 2], [7, 5, 3]]
    data1 = [[6, 3, 9], [8, 4, 3]]
    bp1 = pandas.DataFrame(data, columns=["x", "y", "confidence"], dtype=np.float_)
    bp2 = pandas.DataFrame(data1, columns=["x", "y", "confidence"])
    dist = utils.distance(bp1, bp2, 1)
    print(f"dist = {dist}")
    assert dist == np.sqrt(2)


def test_interpolate_gaps():
    values = [1, 3, 5, 7, 9]
    filled = math_utils.interpolate_gaps(values, 5)
    print(filled)
    assert np.array_equal(np.array([1, 3, 5, 7, 9]), filled)
