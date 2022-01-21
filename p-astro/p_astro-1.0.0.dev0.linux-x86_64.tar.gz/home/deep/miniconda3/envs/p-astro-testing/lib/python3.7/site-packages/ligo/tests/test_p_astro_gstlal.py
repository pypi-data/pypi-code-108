from importlib import resources
import json
import numpy as np
import pytest

from .. import p_astro_gstlal_utils as gstlal
from .. import p_astro_computation as pastrocomp
from . import data


@pytest.fixture
def coinc_bytes_1():
    return resources.read_binary(data, 'coinc_G322589.xml')


@pytest.fixture
def coinc_bytes_2():
    return resources.read_binary(data, 'coinc_G5351.xml')


@pytest.fixture
def coinc_bytes_3():
    return resources.read_binary(data, 'coinc.xml')


@pytest.fixture
def ranking_data_bytes():
    return resources.read_binary(data, 'ranking_data_G322589.xml.gz')


@pytest.fixture
def activation_counts_bytes():
    return resources.read_binary(
        data, 'H1L1V1-weights-bins_686-1126051217-61603201.json')

@pytest.fixture
def mean_values_bytes():
    return resources.read_binary(
        data, 'H1L1V1-mean_counts-1126051217-61603201.json')

def test_get_ln_f_over_b(ranking_data_bytes):
    """Test to check `_get_ln_f_over_b` returns values
    which are not inf or nan for high ln_likelihood_ratio.
    Test to check the computation of terrestrial count
    `lam_0` returns the expected value."""
    ln_f_over_b, lam_0 = gstlal._get_ln_f_over_b(
        ranking_data_bytes,
        [100., 200., 300.],
        livetime=14394240,
        extinct_zerowise_elems=40)
    assert np.all(np.isfinite(ln_f_over_b))
    assert lam_0 == pytest.approx(32575, abs=1.0)


def test_get_event_ln_likelihood_ratio_svd_endtime_mass(coinc_bytes_1):
    likelihood, mass1, mass2, spin1z, spin2z, snr, far = \
        gstlal._get_event_ln_likelihood_ratio_svd_endtime_mass(
            coinc_bytes_1)
    assert mass1 == pytest.approx(2.8, abs=0.1)
    assert mass2 == pytest.approx(1.0, abs=0.1)
    assert spin1z == pytest.approx(-0.99, abs=0.01)
    assert spin2z == pytest.approx(0.049, abs=0.01)
    assert likelihood == pytest.approx(21.65, abs=0.1)


def test_compute_p_astro_1(coinc_bytes_1,
                           ranking_data_bytes,
                           mean_values_bytes,
                           activation_counts_bytes):
    """Test to call `compute_p_astro` on gracedb event G322589.
    m1 = 2.7, m2 = 1.0 solar mass for this event"""
    files = coinc_bytes_1, ranking_data_bytes

    activation_counts_dict = json.loads(activation_counts_bytes)
    mean_values_dict = json.loads(mean_values_bytes)

    likelihood, mass1, mass2, spin1z, spin2z, snr, far = \
        gstlal._get_event_ln_likelihood_ratio_svd_endtime_mass(
            coinc_bytes_1)

    ln_f_over_b, lam_0 = gstlal._get_ln_f_over_b(ranking_data_bytes,
                                                 [likelihood],
                                                 livetime=14394240,
                                                 extinct_zerowise_elems=40)

    mean_values_dict["counts_Terrestrial"] = lam_0
    num_bins = 686

    p_astros = \
        pastrocomp.evaluate_p_astro_from_bayesfac(np.exp(ln_f_over_b),
                                                  mean_values_dict,
                                                  mass1, mass2,
                                                  spin1z, spin2z,
                                                  num_bins,
                                                  activation_counts_dict)

    assert p_astros['BNS'] == pytest.approx(1, abs=1e-2)
    assert p_astros['NSBH'] == pytest.approx(0, abs=1e-2)
    assert p_astros['BBH'] == pytest.approx(0, abs=1e-2)
    assert p_astros['MassGap'] == pytest.approx(0, abs=1e-2)
    assert p_astros['Terrestrial'] == pytest.approx(0, abs=1e-2)


def test_compute_p_astro_2(coinc_bytes_2,
                           ranking_data_bytes,
                           mean_values_bytes,
                           activation_counts_bytes):
    """Test to call `compute_p_astro` on gracedb event G5351. Use ranking
    data from an O3 event G330299. m1 = 1.1, m2 = 1.0 solar mass
    for this event. FAR = 1.9e-6, P_terr has a moderate value."""
    files = coinc_bytes_2, ranking_data_bytes

    activation_counts_dict = json.loads(activation_counts_bytes)
    mean_values_dict = json.loads(mean_values_bytes)

    likelihood, mass1, mass2, spin1z, spin2z, snr, far = \
        gstlal._get_event_ln_likelihood_ratio_svd_endtime_mass(
            coinc_bytes_2)

    ln_f_over_b, lam_0 = gstlal._get_ln_f_over_b(ranking_data_bytes,
                                                 [likelihood],
                                                 livetime=14394240,
                                                 extinct_zerowise_elems=40)

    mean_values_dict["counts_Terrestrial"] = lam_0
    num_bins = 686

    p_astros = \
        pastrocomp.evaluate_p_astro_from_bayesfac(np.exp(ln_f_over_b),
                                                  mean_values_dict,
                                                  mass1, mass2,
                                                  spin1z, spin2z,
                                                  num_bins,
                                                  activation_counts_dict)

    assert p_astros['Terrestrial'] > 0.25
