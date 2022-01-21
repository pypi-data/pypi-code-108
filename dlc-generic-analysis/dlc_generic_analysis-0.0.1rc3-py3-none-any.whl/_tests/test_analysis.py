import os
import numpy as np
from dlc_generic_analysis.analysis import Analysis
import pandas


class ATest(Analysis):
    def __init__(self, h5, dlc_scorer):
        Analysis.__init__(self, h5, dlc_scorer)

    def draw(self):
        pass

    def write_csv(self):
        pass


def test_analyze():
    index = pandas.MultiIndex.from_product(
        [["dlc_sc"], ["Glab", "Ment"], ["x", "y", "likelihood"]],
        names=["scorer", "bodyparts", "coords"],
    )
    data = np.array([[0, 1, 0.5, 3, 4, 0.99], [6, 7, 0.8, 1, 2, 0.6], [4, 5, 0.9, 7, 8, 0.9]])
    print(data)
    df = pandas.DataFrame(data, columns=index)
    path = "test.h5"
    df.to_hdf(path, "dlc_sc")
    at = ATest(path, "dlc_sc")
    at.draw()
    at.write_csv()
    os.remove("test.h5")
