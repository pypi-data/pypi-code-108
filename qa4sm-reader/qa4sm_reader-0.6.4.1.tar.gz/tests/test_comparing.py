import threading
import os
import sys

import numpy as np
import numpy.testing
import pytest
from qa4sm_reader.comparing import QA4SMComparison, SpatialExtentError
from qa4sm_reader.img import QA4SMImg

import pandas as pd
import matplotlib.pyplot as plt


# if sys.platform.startswith("win"):
#     pytestmark = pytest.mark.skip(
#         "Failing on Windows."
#     )


@pytest.fixture
def single_img():
    testfile = '3-ERA5_LAND.swvl1_with_1-C3S.sm_with_2-ASCAT.sm.nc'
    testfile_path = os.path.join(os.path.dirname(__file__), '..', 'tests',
                                 'test_data', 'tc', testfile)
    return QA4SMComparison(testfile_path)


@pytest.fixture
def double_img_paths():
    first = '0-ISMN.soil moisture_with_1-C3S.sm.nc'
    second = '0-ISMN.soil moisture_with_1-C3S.sm-overlap.nc'
    testfile_paths = [
        os.path.join(
            os.path.dirname(__file__),
            '..', 'tests', 'test_data', 'comparing',
            i
        ) for i in [
            first,
            second]
    ]
    # initialized with intersection
    return testfile_paths


@pytest.fixture
def double_img_overlap(double_img_paths):
    """Initialized souble image comparison with intersection"""
    return QA4SMComparison(double_img_paths)


def test_init(single_img):
    assert isinstance(single_img.compared, list)


def test_check_ref(single_img):
    assert single_img._check_ref() == {
        'short_name': 'ERA5_LAND',
        'pretty_name': 'ERA5-Land',
        'short_version': 'ERA5_LAND_TEST',
        'pretty_version': 'ERA5-Land test',
        'pretty_variable': 'swvl1',
        'mu': 'm³/m³',
        'pretty_title': 'ERA5-Land (ERA5-Land test)',
    }


def test_intersection(double_img_overlap):
    assert not double_img_overlap.union


def test_geometry(double_img_overlap):
    assert double_img_overlap._combine_geometry(double_img_overlap.compared) \
           != double_img_overlap._combine_geometry(double_img_overlap.compared, get_intersection=False)


def test_get_pairwise(single_img, double_img_overlap):
    pair = single_img._get_pairwise("R")

    assert isinstance(pair, pd.DataFrame)
    assert len(pair.columns) == 3, "There should be one column for comparison term" \
                                   "plus the column with difference values"
    pair = double_img_overlap._get_pairwise("R")

    assert isinstance(pair, pd.DataFrame)
    assert len(pair.columns) == 3, "There should be one column for comparison term" \
                                   "plus the column with difference values"


def test_checks(single_img, double_img_overlap):
    """No assertion, but will throw error if any of the checks are not passed"""
    assert single_img.perform_checks()

    double_img_overlap.perform_checks(
        overlapping=True,
        union=True,
        pairwise=True
    )


def test_wrapper(single_img, double_img_overlap):
    """
    This tests the wrapper function but more in general also the
    plotting functions/table
    """
    methods = [
        'boxplot',
        'mapplot'
    ]
    for method in methods:
        out = single_img.wrapper(method, "R")
        plt.close("all")
        assert not out  # generates a plot and returns nothing

    for method in methods:
        out = double_img_overlap.wrapper(method, "R")
        plt.close("all")
        if method == "table":
            assert out is not None  # generates a pandas dataframe
        else:
            assert not out  # generates a plot and returns nothing


def test_init_union(double_img_overlap):
    """Should go at the end as it chnages the attributes"""
    double_img_overlap.init_union()
    assert double_img_overlap.union


def test_pairwise_methods(double_img_paths):
    comp = QA4SMComparison(
        double_img_paths,
        get_intersection=False
    )  # todo: solve unexpected behavior on perform_checks
    works = False
    methods = [
        'boxplot',
        'mapplot'
    ]
    for method in methods:
        try:  # they all have same behavior
            comp.wrapper(
                method,
                metric="R"
            )
        except SpatialExtentError:
            works = True

    assert works


@pytest.fixture
def double_paths_nonoverlap():
    first = '0-ISMN.soil moisture_with_1-C3S.sm.nc'
    second = '0-ISMN.soil moisture_with_1-C3S.sm-nonoverlap.nc'
    testfile_paths = [
        os.path.join(
            os.path.dirname(__file__),
            '..', 'tests', 'test_data', 'comparing',
            i
        ) for i in [
            first,
            second]
    ]
    # initialize the comparison with intersection and check that no error is raised
    QA4SMComparison(
        testfile_paths,
        get_intersection=False
    )

    return testfile_paths


def test_common_metrics(double_img_paths, double_img_overlap):
    """Check the common_metrics function in the comparison"""
    metrics_list = []
    for path in double_img_paths:
        im = QA4SMImg(path)
        format_dict = {short: metric_obj.pretty_name for short, metric_obj in im.metrics.items()}
        metrics_list.append(format_dict)
    metrics_should = {key: val for key, val in metrics_list[0].items() if key in metrics_list[1].keys()}
    metrics_should_hardcoded = {
        'R': "Pearson's r",
        'rho': "Spearman's ρ",
        'RMSD': 'Root-mean-square deviation',
        # 'p_tau': 'Kendall tau p-value',
        'RSS': 'Residual sum of squares',
        'p_R': "Pearson's r p-value",
        'mse_corr': 'Mean square error correlation',
        'mse': 'Mean square error',
        # 'tau': 'Kendall rank correlation',
        'mse_bias': 'Mean square error bias',
        'p_rho': "Spearman's ρ p-value",
        'BIAS': 'Bias (difference of means)',
        'urmsd': 'Unbiased root-mean-square deviation',
        'mse_var': 'Mean square error variance'
    }
    assert double_img_overlap.common_metrics == metrics_should_hardcoded
    # check if n_obs is excluded:
    del metrics_should["n_obs"]
    del metrics_should["tau"]
    del metrics_should["p_tau"]

    assert metrics_should == metrics_should_hardcoded


def test_get_reference_points(double_img_overlap):
    """Check get_reference_points function for first 10 points"""
    points_should = np.array([
        [0.3361, 43.9744],
        [0.3361, 43.9744],
        [-0.0469, 43.9936],
        [-0.0469, 43.9936],
        [-0.0469, 43.9936],
        [-0.0469, 43.9936],
        [0.8878, 43.5472],
        [0.8878, 43.5472],
        [2.7283, 43.1733],
        [2.7283, 43.1733]
    ])
    assert double_img_overlap.get_reference_points().shape == (61, 2)
    np.testing.assert_array_equal(double_img_overlap.get_reference_points()[:10], points_should)


def test_get_data(double_img_overlap):
    """Check get_data function"""
    data, ci = double_img_overlap._get_data("R").values()
    assert len(data) == 2
    data = data[0]
    name_should = "Validation 0:\n1-C3S\n(v202012)\nVariable: sm [m³/m³]\n"
    assert data.name == name_should
    data_should = [
        0.679918, 0.707091, 0.713081, 0.808353,
        0.700307, 0.852756, 0.714132, 0.621769,
        0.741732, 0.691499
    ]
    # slightly different due to array transformation from Dataframe
    numpy.testing.assert_array_almost_equal(np.array(data_should), data.iloc[:10].to_numpy(), 6)


def test_init_error(double_paths_nonoverlap):
    works = False
    try:
        QA4SMComparison(
            double_paths_nonoverlap
        )
    except SpatialExtentError:
        works = True

    assert works


# --- reload all imahs to reproduce test_simultaneous_netcdf_loading test ----

def load_extent_image(paths):
    comp = QA4SMComparison(paths)
    comp.visualize_extent(
        intersection=True,
        plot_points=True
    )


def load_table(paths):
    comp = QA4SMComparison(paths)
    metrics = comp.common_metrics
    comp = QA4SMComparison(paths)
    comp.diff_table(metrics=list(metrics.keys()))


def load_plots(paths):
    comp = QA4SMComparison(paths)
    metrics = comp.common_metrics
    first_called = list(metrics.keys())[0]
    comp = QA4SMComparison(paths)
    comp.wrapper(
        method="boxplot",
        metric=first_called
    )
    comp = QA4SMComparison(paths)
    comp.wrapper(
        method="mapplot",
        metric=first_called
    )


def test_simultaneous_netcdf_loading(double_img_paths):
    # this test should reproduce the calls that are made simultaneously from the server, causing a problem with the
    # netcdf loading function. The calls are made from the view:
    # https://github.com/pstradio/qa4sm/blob/comparison2angular_issue-477/479/api/views/comparison_view.py
    threading.Thread(target=load_extent_image(double_img_paths)).start()
    threading.Thread(target=load_table(double_img_paths)).start()
    threading.Thread(target=load_plots(double_img_paths)).start()
