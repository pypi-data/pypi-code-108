from dlc_generic_analysis.filter import threshold_confidence
import pandas
import numpy as np


def test_threshold_confidence():
    index = pandas.MultiIndex.from_product(
        [["dlc_sc"], ["Glab", "Ment"], ["x", "y", "likelihood"]],
        names=["scorer", "bodyparts", "coords"],
    )
    data = np.array([[0, 1, 0.5, 3, 4, 0.99], [6, 7, 0.8, 1, 2, 0.6], [4, 5, 0.9, 7, 8, 0.9]])
    print(data)
    df = pandas.DataFrame(data, columns=index)
    path = "test.h5"
    df.to_hdf(path, "dlc_sc")
    path_thresh = threshold_confidence([path], 0.85)[0]
    df_thresh = pandas.read_hdf(path_thresh)
    data_thresh = df_thresh["dlc_sc"].to_numpy()
    np.testing.assert_equal(
        data_thresh,
        [
            [np.nan, np.nan, 0.5, 3, 4, 0.99],
            [np.nan, np.nan, 0.8, np.nan, np.nan, 0.6],
            [4, 5, 0.9, 7, 8, 0.9],
        ],
    )
