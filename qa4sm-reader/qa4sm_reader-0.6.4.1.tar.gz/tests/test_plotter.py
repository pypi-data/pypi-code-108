# -*- coding: utf-8 -*-
import os
import sys

import numpy as np
import pandas as pd
import pytest
import tempfile
import shutil

from qa4sm_reader.plotter import QA4SMPlotter
from qa4sm_reader.img import QA4SMImg
from qa4sm_reader.plotting_methods import geotraj_to_geo2d, _dict2df, bin_continuous, bin_classes, \
    bin_discrete, combine_soils, combine_depths, output_dpi
from qa4sm_reader.handlers import Metadata
from qa4sm_reader.globals import dpi_min, dpi_max


@pytest.fixture
def plotdir():
    plotdir = tempfile.mkdtemp()

    return plotdir


@pytest.fixture
def basic_plotter(plotdir):
    testfile = '0-ISMN.soil moisture_with_1-C3S.sm.nc'
    testfile_path = os.path.join(
        os.path.dirname(__file__), '..', 'tests', 'test_data', 'basic', testfile
    )
    img = QA4SMImg(testfile_path)
    plotter = QA4SMPlotter(img, plotdir)

    return plotter


@pytest.fixture
def basic_plotter_double(plotdir):
    testfile = '0-GLDAS.SoilMoi0_10cm_inst_with_1-C3S.sm_with_2-SMOS.Soil_Moisture.nc'
    testfile_path = os.path.join(
        os.path.dirname(__file__), '..', 'tests', 'test_data', 'basic', testfile
    )
    img = QA4SMImg(testfile_path)
    plotter = QA4SMPlotter(img, plotdir)

    return plotter


@pytest.fixture
def irrgrid_plotter(plotdir):
    testfile = '0-SMAP.soil_moisture_with_1-C3S.sm.nc'
    testfile_path = os.path.join(
        os.path.dirname(__file__), '..', 'tests', 'test_data', 'basic', testfile
    )
    img = QA4SMImg(testfile_path)
    plotter = QA4SMPlotter(img, plotdir)

    return plotter


@pytest.fixture
def ref_dataset_grid_stepsize(irrgrid_plotter):
    ref_dataset_grid_stepsize = irrgrid_plotter.img.ref_dataset_grid_stepsize

    return ref_dataset_grid_stepsize


@pytest.fixture
def tc_ci_plotter(plotdir):
    testfile = "0-ERA5.swvl1_with_1-ESA_CCI_SM_combined.sm_with_2-ESA_CCI_SM_combined." \
               "sm_with_3-ESA_CCI_SM_combined.sm_with_4-ESA_CCI_SM_combined.sm.CI.nc"
    testfile_path = os.path.join(os.path.dirname(__file__), '..', 'tests',
                                 'test_data', 'tc', testfile)
    img = QA4SMImg(testfile_path)
    plotter = QA4SMPlotter(img, plotdir)

    return plotter


@pytest.fixture
def tc_plotter(plotdir):
    testfile = '3-GLDAS.SoilMoi0_10cm_inst_with_1-C3S.sm_with_2-SMOS.Soil_Moisture.nc'
    testfile_path = os.path.join(
        os.path.dirname(__file__), '..', 'tests', 'test_data', 'tc', testfile
    )
    img = QA4SMImg(testfile_path)
    plotter = QA4SMPlotter(img, plotdir)

    return plotter


@pytest.fixture
def meta_plotter(plotdir):
    testfile = '0-ISMN.soil_moisture_with_1-C3S.sm.nc'
    testfile_path = os.path.join(
        os.path.dirname(__file__), '..', 'tests', 'test_data', 'metadata', testfile
    )
    img = QA4SMImg(testfile_path)
    plotter = QA4SMPlotter(img, plotdir)

    return plotter


def test_mapplot(basic_plotter, plotdir):
    n_obs_files = basic_plotter.mapplot_metric('n_obs', out_types='png', save_files=True)  # should be 1
    assert len(list(n_obs_files)) == 1
    assert len(os.listdir(plotdir)) == 1

    r_files = basic_plotter.mapplot_metric('R', out_types='svg', save_files=True)  # should be 1
    assert len(os.listdir(plotdir)) == 1 + 1
    assert len(list(r_files)) == 1

    bias_files = basic_plotter.mapplot_metric('BIAS', out_types='png', save_files=True)  # should be 1
    assert len(os.listdir(plotdir)) == 1 + 1 + 1
    assert len(list(bias_files)) == 1

    shutil.rmtree(plotdir)  # cleanup


def test_mapplot_dpi_configurations(basic_plotter, plotdir):
    # test keyword compute_dpi is passed
    n_obs_files = basic_plotter.mapplot_metric(
        'n_obs',
        out_types='png',
        save_files=True,
        **{"compute_dpi": False}
    )  # should be 1
    assert len(list(n_obs_files)) == 1
    assert len(os.listdir(plotdir)) == 1

    # test compute_dpi works
    n_obs_files_dpi_computed = basic_plotter.mapplot_metric(
        'n_obs',
        out_types='png',
        save_files=True,
        **{"compute_dpi": True}
    )  # should be 1
    assert len(list(n_obs_files)) == 1
    assert len(os.listdir(plotdir)) == 1

    shutil.rmtree(plotdir)


def test_boxplot(basic_plotter, plotdir):
    n_obs_files = basic_plotter.boxplot_basic('n_obs', out_types='png', save_files=True)  # should be 1
    assert len(list(n_obs_files)) == 1
    assert len(os.listdir(plotdir)) == 1

    r_files = basic_plotter.boxplot_basic('R', out_types='svg', save_files=True)  # should be 1
    assert len(os.listdir(plotdir)) == 1 + 1
    assert len(list(r_files)) == 1

    bias_files = basic_plotter.boxplot_basic('BIAS', out_types='png', save_files=True)  # should be 1
    assert len(os.listdir(plotdir)) == 1 + 1 + 1
    assert len(list(bias_files)) == 1

    shutil.rmtree(plotdir)


def test_csv(basic_plotter, plotdir):
    csv_file = basic_plotter.save_stats()
    # file is in the right format
    assert csv_file.suffix == '.csv'

    csv_dframe = pd.read_csv(csv_file, index_col="Metric", dtype=str)
    dframe = basic_plotter.img.stats_df()

    # .csv file is the same as the statistics DataFrame
    assert csv_dframe.equals(dframe)

    shutil.rmtree(plotdir)


def test_mapplot_double(basic_plotter_double, plotdir):
    n_obs_files = basic_plotter_double.mapplot_metric('n_obs', out_types='png', save_files=True)  # should be 1
    assert len(list(n_obs_files)) == 1
    assert len(os.listdir(plotdir)) == 1

    r_files = basic_plotter_double.mapplot_metric('R', out_types='svg', save_files=True)  # should be 2 files
    assert len(os.listdir(plotdir)) == 1 + 2
    assert len(list(r_files)) == 2

    bias_files = basic_plotter_double.mapplot_metric('BIAS', out_types='png', save_files=True)  # should be 2 files
    assert len(os.listdir(plotdir)) == 1 + 2 + 2
    assert len(list(bias_files)) == 2

    shutil.rmtree(plotdir)


def test_boxplot_double(basic_plotter_double, plotdir):
    n_obs_files = basic_plotter_double.boxplot_basic('n_obs', out_types='png', save_files=True)  # should be 1
    assert len(list(n_obs_files)) == 1
    assert len(os.listdir(plotdir)) == 1

    r_files = basic_plotter_double.boxplot_basic('R', out_types='svg', save_files=True)  # should be 1
    assert len(os.listdir(plotdir)) == 1 + 1
    assert len(list(r_files)) == 1

    bias_files = basic_plotter_double.boxplot_basic('BIAS', out_types='png', save_files=True)  # should be 1
    assert len(os.listdir(plotdir)) == 1 + 1 + 1
    assert len(list(bias_files)) == 1

    shutil.rmtree(plotdir)


def test_mapplot_tc(tc_plotter, plotdir):
    n_obs_files = tc_plotter.mapplot_metric('n_obs', out_types='png', save_files=True)  # should be 1
    assert len(list(n_obs_files)) == 1
    assert len(os.listdir(plotdir)) == 1

    r_files = tc_plotter.mapplot_metric('R', out_types='svg', save_files=True)  # should be 2
    assert len(os.listdir(plotdir)) == 1 + 2
    assert len(list(r_files)) == 2

    bias_files = tc_plotter.mapplot_metric('BIAS', out_types='png', save_files=True)  # should be 2
    assert len(os.listdir(plotdir)) == 1 + 2 + 2
    assert len(list(bias_files)) == 2

    snr_files = tc_plotter.mapplot_metric('snr', out_types='svg', save_files=True)  # should be 2
    assert len(os.listdir(plotdir)) == 1 + 2 + 2 + 2
    assert len(list(snr_files)) == 2

    err_files = tc_plotter.mapplot_metric('err_std', out_types='svg', save_files=True)  # should be 2
    assert len(os.listdir(plotdir)) == 1 + 2 + 2 + 2 + 2
    assert len(list(err_files)) == 2

    shutil.rmtree(plotdir)


def test_boxplot_tc(tc_plotter, plotdir):
    n_obs_files = tc_plotter.boxplot_basic('n_obs', out_types='png', save_files=True)  # should be 1
    assert len(list(n_obs_files)) == 1
    assert len(os.listdir(plotdir)) == 1

    r_files = tc_plotter.boxplot_basic('R', out_types='svg', save_files=True)  # should be 1
    assert len(os.listdir(plotdir)) == 1 + 1
    assert len(list(r_files)) == 1

    bias_files = tc_plotter.boxplot_basic('BIAS', out_types='png', save_files=True)  # should be 1
    assert len(os.listdir(plotdir)) == 1 + 1 + 1
    assert len(list(bias_files)) == 1

    snr_files = tc_plotter.boxplot_tc('snr', out_types='svg', save_files=True)  # should be 2
    assert len(os.listdir(plotdir)) == 1 + 1 + 1 + 2
    assert len(list(snr_files)) == 2

    err_files = tc_plotter.boxplot_tc('err_std', out_types='svg', save_files=True)  # should be 2
    assert len(os.listdir(plotdir)) == 1 + 1 + 1 + 2 + 2
    assert len(list(err_files)) == 2

    shutil.rmtree(plotdir)


def test_mapplot_irrgrid(irrgrid_plotter, plotdir):
    n_obs_files = irrgrid_plotter.mapplot_metric('n_obs', out_types='png', save_files=True)  # should be 1
    assert len(list(n_obs_files)) == 1
    assert len(os.listdir(plotdir)) == 1

    r_files = irrgrid_plotter.mapplot_metric('R', out_types='svg', save_files=True)  # should be 2
    assert len(os.listdir(plotdir)) == 1 + 1
    assert len(list(r_files)) == 1

    bias_files = irrgrid_plotter.mapplot_metric('BIAS', out_types='png', save_files=True)  # should be 2
    assert len(os.listdir(plotdir)) == 1 + 1 + 1
    assert len(list(bias_files)) == 1

    shutil.rmtree(plotdir)


def test_boxplot_irrgrid(irrgrid_plotter, plotdir):
    n_obs_files = irrgrid_plotter.boxplot_basic('n_obs', out_types='png', save_files=True)  # should be 1
    assert len(list(n_obs_files)) == 1
    assert len(os.listdir(plotdir)) == 1

    r_files = irrgrid_plotter.boxplot_basic('R', out_types='svg', save_files=True)  # should be 1
    assert len(os.listdir(plotdir)) == 1 + 1
    assert len(list(r_files)) == 1

    bias_files = irrgrid_plotter.boxplot_basic('BIAS', out_types='png', save_files=True)  # should be 1
    assert len(os.listdir(plotdir)) == 1 + 1 + 1
    assert len(list(bias_files)) == 1

    shutil.rmtree(plotdir)


def test_grid_creation(irrgrid_plotter, ref_dataset_grid_stepsize):
    metric = 'n_obs'
    for Var in irrgrid_plotter.img._iter_vars(filter_parms={'metric': metric}):
        varname = Var.varname
        df = irrgrid_plotter.img._ds2df([varname])[varname]
        zz, grid, origin = geotraj_to_geo2d(df, grid_stepsize=ref_dataset_grid_stepsize)
        print('varname: ', varname, 'zz: ', zz, 'grid: ', grid)
        assert zz.count() != 0
        assert origin == 'upper'


def test_boxplot_basic_ci(tc_ci_plotter, plotdir):
    bias_files = tc_ci_plotter.boxplot_basic('BIAS', out_types='png', save_files=True)  # should be 1
    assert len(os.listdir(plotdir)) == 1
    assert len(list(bias_files)) == 1

    shutil.rmtree(plotdir)


def test_boxplot_tc_ci(tc_ci_plotter, plotdir):
    snr_files = tc_ci_plotter.boxplot_tc('snr', out_types='svg', save_files=True)  # should be 4
    assert len(os.listdir(plotdir)) == 4
    assert len(list(snr_files)) == 4

    shutil.rmtree(plotdir)


def test_bin_continuous():
    """Test continuous binning with 'elevation' metadata"""
    meta_val = pd.DataFrame(data=np.linspace(1, 100, 100), columns=["elevation"])
    val = pd.DataFrame(data=np.zeros(100), columns=["dataset"])
    binned = bin_continuous(val, meta_val, meta_key="elevation")

    exp = {
        '1.00-25.00 [m]': pd.Series(data=np.zeros(25), index=np.linspace(0, 24, 25, dtype=int), name="dataset"),
        '26.00-50.00 [m]': pd.Series(data=np.zeros(25), index=np.linspace(25, 49, 25, dtype=int), name="dataset"),
        '51.00-75.00 [m]': pd.Series(data=np.zeros(25), index=np.linspace(50, 74, 25, dtype=int), name="dataset"),
        '76.00-100.00 [m]': pd.Series(data=np.zeros(25), index=np.linspace(75, 99, 25, dtype=int), name="dataset"),
    }

    assert binned.keys() == exp.keys()
    for act, expected in zip(binned.values(), exp.values()):
        pd.testing.assert_series_equal(act[act.columns[0]], expected)


def test_bin_classes():
    """Test continuous binning with 'elevation' metadata"""
    meta_val = pd.DataFrame(data=[10, 10, 10, 10, 10, 11, 11, 11, 11, 11], columns=["lc_2010"])
    val = pd.DataFrame(data=np.zeros(10), columns=["dataset"])
    binned = bin_classes(val, meta_val, meta_key="lc_2010")

    exp = {"Cropland": pd.Series(data=np.zeros(10), name="dataset")}
    assert binned.keys() == exp.keys()
    for act, expected in zip(binned.values(), exp.values()):
        pd.testing.assert_series_equal(act[act.columns[0]], expected)


def test_bin_discrete():
    """Test continuous binning with 'elevation' metadata"""
    data = ["i1", "i1", "i1", "i1", "i1", "i2", "i2", "i2", "i2", "i2"]
    meta_val = pd.DataFrame(data=data, columns=["instrument"])
    val = pd.DataFrame(data=np.zeros(10), columns=["dataset"])
    binned = bin_discrete(val, meta_val, meta_key="instrument")

    exp = pd.DataFrame(index=np.linspace(0, 9, 10, dtype=int))
    exp["values"] = 0.0
    exp["instrument"] = data
    exp["Dataset"] = "dataset"

    pd.testing.assert_frame_equal(binned, exp)


def test_combine_soils():
    sidata = pd.Series(data=[30, 90, 5])
    sadata = pd.Series(data=[75, 5, 90])
    cdata = pd.Series(data=[5, 5, 5])
    soil_fractions = {
        "silt_fraction": Metadata(varname="silt_fraction", global_attrs={}, values=sidata),
        "sand_fraction": Metadata(varname="sand_fraction", global_attrs={}, values=sadata),
        "clay_fraction": Metadata(varname="clay_fraction", global_attrs={}, values=cdata),
    }
    combined = combine_soils(soil_fractions)
    exp = pd.DataFrame(
        data=["Coarse\ngranulometry", "Fine\ngranulometry", "Coarse\ngranulometry"],
        columns=["soil_type"]
    )

    pd.testing.assert_frame_equal(combined, exp)


def test_combine_depths():
    datafrom = pd.Series(data=np.zeros(10))
    datato = pd.Series(data=np.full(10, 1))
    df = Metadata(varname="instrument_depthfrom", global_attrs={}, values=datafrom)
    dt = Metadata(varname="instrument_depthto", global_attrs={}, values=datato)
    depth_dict = {
        "instrument_depthfrom": df,
        "instrument_depthto": dt,
    }
    combined = combine_depths(depth_dict)
    exp = pd.DataFrame(index=np.linspace(0, 9, 10, dtype=int), data=np.full(10, 0.5), columns=["instrument_depth"])

    pd.testing.assert_frame_equal(combined, exp)


def test_dict2df():
    data = np.zeros(shape=(10, 2))
    dict_meta = {
        "meta1": pd.DataFrame(data=data, columns=["dataset1", "dataset2"]),
        "meta2": pd.DataFrame(data=data, columns=["dataset1", "dataset2"]),
    }
    key = "meta"
    df_meta = _dict2df(dict_meta, meta_key=key)
    assert all(actual == exp for actual, exp in zip(df_meta.columns, ["values", "Dataset", key]))
    assert len(df_meta.index) == 40, "should be 10 values x 2 Datasets x 2 metadata"
    assert all(actual == exp for actual, exp in zip(df_meta["Dataset"].unique(), ["dataset1", "dataset2"]))
    assert all(actual == exp for actual, exp in zip(df_meta[key].unique(), ["meta1", "meta2"]))


def test_output_dpi():
    res1, unit1 = 12.5, "km"
    res2, unit2 = 25, "km"
    extent1 = 71.6, 34, 48.3, -11.2
    extent2 = 71.6, 54, 48.3, -11.2

    dpi1 = output_dpi(res1, unit1, extent1)
    dpi2 = output_dpi(res2, unit2, extent1)
    dpi3 = output_dpi(res1, unit1, extent2)

    assert type(dpi1) == float

    assert dpi1 > dpi2, "lower resolution should produce a lower dpi"
    assert dpi1 > dpi3, "smaller extent should produce a lower dpi"

    # test dpi formula
    dpi_fraction = np.sqrt(
        ((1 - (res1 - 1)/35)**2)**2 + (((extent1[1]-extent1[0]) * (extent1[3]-extent1[2]))/(360 * 110))**2
    ) / np.sqrt(2)
    dpi1_should = dpi_min + (dpi_max-dpi_min) * dpi_fraction

    assert dpi1_should == dpi1, "Check correctness of dpi formula and/or constants, " \
                                "e.g. the maximum resolution in km"
