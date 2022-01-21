from dlc_generic_analysis import utils
import numpy as np
import pandas


def test_point_array():
    data = [[0, 1, 2], [3, 4, 5]]
    index = pandas.MultiIndex.from_product(
        [["Glab"], ["x", "y", "likelihood"]], names=["scorer", "coords"]
    )
    df = pandas.DataFrame(data, columns=index)
    print(df)
    arr = utils.point_array(df, ["Glab"])
    np.array_equal(arr, np.array([[0, 3]]))


def test_angle_between_lines():
    assert np.round(utils.angle_between_lines(np.sqrt(3), 0), 6) == -60


#  testing video manipulation functions is too expensive
