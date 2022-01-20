# -*- coding: utf-8 -*-
import pandas as pd
import xarray as xr

import pytest
import os

from qa4sm_reader.handlers import QA4SMDatasets, QA4SMVariable, QA4SMMetric, \
    MetricVariable, Metadata, ConfidenceInterval


@pytest.fixture
def basic_attributes():
    testfile = os.path.join(os.path.dirname(__file__), 'test_data', 'basic',
                            '6-ISMN.soil moisture_with_1-C3S.sm_with_2-C3S.sm_with_3-SMOS.Soil_Moisture_with_4-SMAP.soil_moisture_with_5-ASCAT.sm.nc')
    ds = xr.open_dataset(testfile)
    return ds.attrs


@pytest.fixture
def tc_attributes():
    testfile = os.path.join(os.path.dirname(__file__), 'test_data', 'tc',
                            '3-ERA5_LAND.swvl1_with_1-C3S.sm_with_2-ASCAT.sm.nc')
    ds = xr.open_dataset(testfile)
    return ds.attrs


@pytest.fixture
def ci_attributes():
    testfile = os.path.join(os.path.dirname(__file__), 'test_data', 'tc',
                            "0-ERA5.swvl1_with_1-ESA_CCI_SM_combined.sm_with_2-ESA_CCI_SM_combined.sm_with_3-ESA_CCI_SM_combined.sm_with_4-ESA_CCI_SM_combined.sm.CI.nc")
    ds = xr.open_dataset(testfile)
    return ds.attrs


#@pytest.fixture
#def metadata_attributes():
#    testfile = os.path.join(os.path.dirname(__file__), 'test_data', 'metadata',
#                            "0-ISMN.soil_moisture_with_1-C3S.sm.nc")
#    ds = xr.open_dataset(testfile)
#    return ds.attrs


@pytest.fixture
def datasets(basic_attributes):
    return QA4SMDatasets(global_attrs=basic_attributes)


@pytest.fixture
def datasets_names(datasets):
    names = {
        "ismn": datasets._dc_names(dc=5),
        "c3s17": datasets._dc_names(dc=0),
        "c3s18": datasets._dc_names(dc=1),
        "smos": datasets._dc_names(dc=2),
        "smap": datasets._dc_names(dc=3),
        "ascat": datasets._dc_names(dc=4),
    }

    return names


@pytest.fixture
def tc_metrics(tc_attributes):
    df_nobs = pd.DataFrame(index=range(10), data={'n_obs': range(10)})
    metrics = {
        "n_obs": QA4SMVariable('n_obs', tc_attributes, values=df_nobs).initialize(),
        "r": QA4SMVariable('R_between_3-ERA5_LAND_and_1-C3S', tc_attributes).initialize(),
        "beta": QA4SMVariable('beta_1-C3S_between_3-ERA5_LAND_and_1-C3S_and_2-ASCAT', tc_attributes).initialize(),
    }

    return metrics


@pytest.fixture
def basic_metrics(basic_attributes):
    df_nobs = pd.DataFrame(index=range(10), data={'n_obs': range(10)})

    metrics = {
        "n_obs": QA4SMVariable('n_obs', basic_attributes, values=df_nobs).initialize(),
        "r": QA4SMVariable('R_between_6-ISMN_and_4-SMAP', basic_attributes).initialize(),
        "p": QA4SMVariable('p_rho_between_6-ISMN_and_5-ASCAT', basic_attributes).initialize(),
    }

    return metrics


def test_grid_stepsize():
    testfile = os.path.join(os.path.dirname(__file__), 'test_data', 'basic',
                            '0-SMAP.soil_moisture_with_1-C3S.sm.nc')
    attrs = xr.open_dataset(testfile).attrs

    assert attrs['val_dc_dataset0_grid_stepsize'] == 0.35


def test_get_ref_name(datasets):
    ref_names = datasets.ref
    assert ref_names['short_name'] == 'ISMN'
    assert ref_names['pretty_name'] == 'ISMN'
    assert ref_names['short_version'] == 'ISMN_V20180712_MINI'
    assert ref_names['pretty_version'] == '20180712 mini testset'
    return ref_names


def test_get_other_names(datasets):
    other_names = datasets.others
    # index is dc, as in the meta values not as in the variable name
    assert other_names[0]['short_name'] == 'C3S'
    assert other_names[0]['pretty_name'] == 'C3S'
    assert other_names[0]['short_version'] == 'C3S_V201706'
    assert other_names[0]['pretty_version'] == 'v201706'

    assert other_names[1]['short_name'] == 'C3S'
    assert other_names[1]['pretty_name'] == 'C3S'
    assert other_names[1]['short_version'] == 'C3S_V201812'
    assert other_names[1]['pretty_version'] == 'v201812'

    assert other_names[2]['short_name'] == 'SMOS'
    assert other_names[2]['pretty_name'] == 'SMOS IC'
    assert other_names[2]['short_version'] == 'SMOS_105_ASC'
    assert other_names[2]['pretty_version'] == 'V.105 Ascending'

    assert other_names[3]['short_name'] == 'SMAP'
    assert other_names[3]['pretty_name'] == 'SMAP level 3'
    assert other_names[3]['short_version'] == 'SMAP_V5_PM'
    assert other_names[3]['pretty_version'] == 'v5 PM/ascending'

    assert other_names[4]['short_name'] == 'ASCAT'
    assert other_names[4]['pretty_name'] == 'H-SAF ASCAT SSM CDR'
    assert other_names[4]['short_version'] == 'ASCAT_H113'
    assert other_names[4]['pretty_version'] == 'H113'

    return other_names


# ---- Tests based on netCDF file where reference id == 6 (i.e. different from 0, old format) -----
def test_id_dc(datasets):
    assert datasets._ref_dc() != datasets._ref_id()
    assert datasets._ref_id() == 6
    assert datasets.offset == -1
    assert datasets._id2dc(6) == 5


def test_dcs(datasets):
    for i in range(5):
        assert i in datasets._dcs().keys()
    assert len(datasets._dcs().keys()) == 5


def test_fetch_attributes(datasets):
        del datasets.meta['val_dc_variable_pretty_name0']
        vers0 = datasets._fetch_attribute('_val_dc_variable_pretty_name', 0)
        # check that fallback method works
        assert vers0 == "soil moisture"


def test_dc_names(datasets_names):
    assert datasets_names["ismn"]['pretty_name'] == 'ISMN'
    assert datasets_names["ismn"]['pretty_version'] == '20180712 mini testset'

    assert datasets_names["c3s17"]['pretty_name'] == 'C3S'
    assert datasets_names["c3s17"]['pretty_version'] == 'v201706'

    assert datasets_names["c3s18"]['pretty_name'] == 'C3S'
    assert datasets_names["c3s18"]['pretty_version'] == 'v201812'

    assert datasets_names["smos"]['pretty_name'] == 'SMOS IC'
    assert datasets_names["smos"]['pretty_version'] == 'V.105 Ascending'

    assert datasets_names["smap"]['pretty_name'] == 'SMAP level 3'
    assert datasets_names["smap"]['pretty_version'] == 'v5 PM/ascending'

    assert datasets_names["ascat"]['pretty_name'] == 'H-SAF ASCAT SSM CDR'
    assert datasets_names["ascat"]['pretty_version'] == 'H113'


def test_others(datasets):
    assert len(datasets.others) == 5


def test_dataset_metadata(datasets):
    meta_ref = datasets.dataset_metadata(6)[1]  # shape (id, {names})
    also_meta_ref = datasets._dc_names(5)
    assert meta_ref == also_meta_ref


# ---- Tests with TC metrics -----
def test_properties(tc_metrics):
    assert tc_metrics["beta"].isempty
    assert tc_metrics["beta"].ismetric


def test_pretty_name(tc_metrics):
    assert tc_metrics["beta"].pretty_name == \
           "TC scaling coefficient of C3S (v201812) \n against ERA5-Land (ERA5-Land test), H-SAF ASCAT SSM CDR (H113)"


def test_parse_varname(tc_metrics):
    for var in [tc_metrics["beta"], tc_metrics["r"], tc_metrics["n_obs"]]:
        info = var._parse_varname()
        assert type(info[0]) == str
        assert type(info[1]) == int
        assert type(info[2]) == dict


def test_get_tc_varmeta(tc_metrics):
    # n_obs has only the reference dataset
    assert tc_metrics["n_obs"].ismetric
    assert not tc_metrics["n_obs"].isempty
    ref_ds, metric_ds, other_ds = tc_metrics["n_obs"].get_varmeta()
    assert ref_ds[1]['short_name'] == 'ERA5_LAND'
    assert metric_ds == other_ds is None

    # R has only the reference and metric dataset
    ref_ds, metric_ds, other_ds = tc_metrics["r"].get_varmeta()
    assert ref_ds[0] == 3
    assert ref_ds[1]['short_name'] == 'ERA5_LAND'
    assert ref_ds[1]['pretty_name'] == 'ERA5-Land'
    assert ref_ds[1]['short_version'] == 'ERA5_LAND_TEST'
    assert ref_ds[1]['pretty_version'] == 'ERA5-Land test'

    assert metric_ds[0] == 1
    mds_meta = metric_ds[1]
    assert mds_meta['short_name'] == 'C3S'
    assert mds_meta['pretty_name'] == 'C3S'
    assert mds_meta['short_version'] == 'C3S_V201812'
    assert mds_meta['pretty_version'] == 'v201812'
    assert other_ds is None

    # p has all three datasets, it being a TC metric
    ref_ds, metric_ds, other_ds = tc_metrics["beta"].get_varmeta()
    assert ref_ds[0] == 3
    assert ref_ds[1]['short_name'] == 'ERA5_LAND'
    assert ref_ds[1]['pretty_name'] == 'ERA5-Land'
    assert ref_ds[1]['short_version'] == 'ERA5_LAND_TEST'
    assert ref_ds[1]['pretty_version'] == 'ERA5-Land test'

    assert metric_ds[0] == 1
    assert other_ds[0] == 2
    mds_meta = metric_ds[1]
    other_meta = other_ds[1]
    assert mds_meta['short_name'] == 'C3S'
    assert mds_meta['pretty_name'] == 'C3S'
    assert mds_meta['short_version'] == 'C3S_V201812'
    assert mds_meta['pretty_version'] == 'v201812'

    assert other_meta['short_name'] == 'ASCAT'
    assert other_meta['pretty_name'] == 'H-SAF ASCAT SSM CDR'
    assert other_meta['short_version'] == 'ASCAT_H113'
    assert other_meta['pretty_version'] == 'H113'


# ---- Tests with non-TC metrics -----
def test_get_varmeta(basic_metrics):
    # n_obs
    assert basic_metrics["n_obs"].ismetric
    assert not basic_metrics["n_obs"].isempty
    ref_ds, metric_ds, other_ds = basic_metrics["n_obs"].get_varmeta()
    assert ref_ds[1]['short_name'] == 'ISMN'
    assert metric_ds == other_ds is None

    # R
    ref_ds, metric_ds, other_ds = basic_metrics["r"].get_varmeta()
    assert ref_ds[0] == 6
    assert ref_ds[1]['short_name'] == 'ISMN'
    assert ref_ds[1]['pretty_name'] == 'ISMN'
    assert ref_ds[1]['short_version'] == 'ISMN_V20180712_MINI'
    assert ref_ds[1]['pretty_version'] == '20180712 mini testset'
    assert metric_ds[0] == 4
    mds_meta = metric_ds[1]
    assert mds_meta['short_name'] == 'SMAP'
    assert mds_meta['pretty_name'] == 'SMAP level 3'
    assert mds_meta['short_version'] == 'SMAP_V5_PM'
    assert mds_meta['pretty_version'] == 'v5 PM/ascending'
    assert other_ds is None

    # p
    ref_ds, metric_ds, other_ds = basic_metrics["p"].get_varmeta()
    assert ref_ds[0] == 6
    assert ref_ds[1]['short_name'] == 'ISMN'
    assert ref_ds[1]['pretty_name'] == 'ISMN'
    assert ref_ds[1]['short_version'] == 'ISMN_V20180712_MINI'
    assert ref_ds[1]['pretty_version'] == '20180712 mini testset'
    assert metric_ds[0] == 5
    mds_meta = metric_ds[1]
    assert mds_meta['short_name'] == 'ASCAT'
    assert mds_meta['pretty_name'] == 'H-SAF ASCAT SSM CDR'
    assert mds_meta['short_version'] == 'ASCAT_H113'
    assert mds_meta['pretty_version'] == 'H113'
    assert other_ds is None


def test_get_attributes(tc_attributes) -> None:

    r1 = QA4SMVariable('R_between_3-ERA5_LAND_and_2-ASCAT', tc_attributes).initialize()
    r2 = QA4SMVariable('R_between_3-ERA5_LAND_and_1-C3S', tc_attributes).initialize()
    r = QA4SMMetric('R', variables_list=[r1, r2])

    assert r.g == r1.g == r2.g


# todo: update with correct CI .nc file
def test_ci_var(ci_attributes):
    ci_var = QA4SMVariable(
        "RMSD_ci_upper_between_0-ERA5_and_2-ESA_CCI_SM_combined",
        ci_attributes
    ).initialize()

    assert ci_var.ismetric
    assert ci_var.is_CI
    assert ci_var.pretty_name == "Confidence interval (upper) of Root-mean-square deviation\nof ESA CCI " \
                                 "SM combined (v05.2)\nwith ERA5 (v20190613) as reference"
    assert ci_var.bound == "upper"


def test_class_attributes(basic_attributes, ci_attributes):
    basic_var = QA4SMVariable(
        "R_between_6-ISMN_and_4-SMAP",
        basic_attributes
    ).initialize()

    ci_var = QA4SMVariable(
        "RMSD_ci_upper_between_0-ERA5_and_2-ESA_CCI_SM_combined",
        ci_attributes
    ).initialize()

    #metadata_var = QA4SMVariable(
    #    "lc_2010",
    #    metadata_attributes
    #).initialize()

    for attr in ["ref_ds", "metric_ds", "other_ds"]:
        assert hasattr(ci_var, attr)
        assert hasattr(basic_var, attr)

    #assert hasattr(metadata_var, "key_meta")
