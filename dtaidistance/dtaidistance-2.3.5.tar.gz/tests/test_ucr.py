import sys, os
import logging
from pathlib import Path

import pytest

from dtaidistance import dtw, util_numpy
from dtaidistance import dtw_visualisation as dtwvis


numpyonly = pytest.mark.skipif("util_numpy.test_without_numpy()")
logger = logging.getLogger("be.kuleuven.dtai.distance")


def read_twolead(ucr):
    with util_numpy.test_uses_numpy() as np:
        datafile = ucr / "TwoLeadECG" / "TwoLeadECG_TRAIN"
        data = []
        with open(datafile, "r") as ifile:
            for line in ifile:
                data.append([float(v) for v in line.split(",")])
        data = np.array(data)
        series = data[:, 1:]
        labels = data[:, 0]
        return series, labels


@numpyonly
def test_distance_twolead_startdiff(directory=None, ucr=None):
    if ucr is None:
        # skip test
        return
    series, labels = read_twolead(ucr)
    series1 = series[9]
    series2 = series[21]
    # print(labels[9])
    # print(series1)
    # print(labels[21])
    # print(series2)

    window, psi = 10, 2
    d1a = dtw.distance_fast(series1, series2, window=window, psi=psi)
    d1b = dtw.distance(series1, series2, window=window, psi=psi)
    # print(d1a, d1b)

    if directory:
        fn = directory / "warpingpaths_startdiff.png"
        d2, paths = dtw.warping_paths(series1, series2, window=window, psi=psi)
        best_path = dtw.best_path(paths)
        dtwvis.plot_warpingpaths(series1, series2, paths, best_path, filename=fn, shownumbers=False)
        print(f"Figure saved to {fn}")


@numpyonly
def test_distance_twolead_sameclass(directory=None, ucr=None):
    if ucr is None:
        # skip test
        return
    series, labels = read_twolead(ucr)
    series1 = series[9]
    series2 = series[10]
    # print(labels[9])
    # print(series1)
    # print(labels[10])
    # print(series2)

    window, psi = 10, 2
    d1a = dtw.distance_fast(series1, series2, window=window, psi=psi)
    d1b = dtw.distance(series1, series2, window=window, psi=psi)
    # print(d1a, d1b)

    if directory:
        fn = directory / "warpingpaths_sameclass.png"
        d2, paths = dtw.warping_paths(series1, series2, window=window, psi=psi)
        best_path = dtw.best_path(paths)
        dtwvis.plot_warpingpaths(series1, series2, paths, best_path, filename=fn, shownumbers=False)
        print(f"Figure saved to {fn}")


@numpyonly
def test_distance_twolead_diffclass(directory=None, ucr=None):
    if ucr is None:
        # skip test
        return
    series, labels = read_twolead(ucr)
    series1 = series[9]
    series2 = series[11]
    # print(labels[9])
    # print(series1)
    # print(labels[11])
    # print(series2)

    window, psi = 10, 2
    d1a = dtw.distance_fast(series1, series2, window=window, psi=psi)
    d1b = dtw.distance(series1, series2, window=window, psi=psi)
    # print(d1a, d1b)

    if directory:
        fn = directory / "warpingpaths_diffclass.png"
        d2, paths = dtw.warping_paths(series1, series2, window=window, psi=psi)
        best_path = dtw.best_path(paths)
        dtwvis.plot_warpingpaths(series1, series2, paths, best_path, filename=fn, shownumbers=False)
        print(f"Figure saved to {fn}")


@numpyonly
def test_distance_twolead_matrix(directory=None, ucr=None):
    if ucr is None:
        # skip test
        return
    series, labels = read_twolead(ucr)

    window, psi = 10, 2
    dists = dtw.distance_matrix_fast(series, window=window, psi=psi)

    if directory:
        fn = directory / "matrix.png"
        dtwvis.plot_matrix(dists, filename=fn, shownumbers=True)
        print(f"Figure saved to {fn}")


if __name__ == "__main__":
    # Print options
    with util_numpy.test_uses_numpy() as np:
        np.set_printoptions(precision=2)
    # Logger options
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(message)s')
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    logger.propagate = 0
    # Output path
    directory = Path(__file__).resolve().parent.parent / "tests" / "output"

    ucr = Path("/Users/wannes/Projects/Datasets/UCR_TS_Archive_2015/")

    # test_distance_twolead_startdiff(directory=directory, ucr=ucr)
    # test_distance_twolead_sameclass(directory=directory, ucr=ucr)
    # test_distance_twolead_diffclass(directory=directory, ucr=ucr)
    test_distance_twolead_matrix(directory=directory, ucr=ucr)
