from importlib import resources
import json

import pytest

from .. import p_astro_computation as pastrocomp
from . import data


@pytest.fixture
def thresholds_bytes():
    return resources.read_binary(
        data, 'H1L1V1-pipeline-far_snr-thresholds.json')


@pytest.fixture
def mean_counts_bytes():
    return resources.read_binary(
        data, 'H1L1V1-mean_counts-1126051217-61603201.json')


@pytest.mark.parametrize(
    'far,pipeline,instruments,snr_thresh,val',
    ([1e-25, 'mbtaonline', {'H1', 'L1', 'V1'}, 12, 1],
     [1e-8, 'mbtaonline', {'L1', 'V1'}, 33, 0.08],
     [6e-10, 'mbtaonline', {'H1', 'V1'}, 10, 0.99],
     [7.6e-59, 'spiir', {'H1', 'L1', 'V1'}, 33, 1],
     [1e-10, 'pycbc', {'H1', 'L1'}, 10, 1],
     [1e-10, 'pycbc', {'H1', 'L1', 'V1'}, 10, 1]))
def test_compute_p_astro_bns(far, pipeline, instruments,
                             snr_thresh, val,
                             thresholds_bytes,
                             mean_counts_bytes):
    """Test p_astro values using CBC catalog paper
    values for GW170817, for various mock-FARs, to test
    handling of this very loud event for MBTA, PyCBC
    and spiir.
    """
    # values based on G322759
    snr = 33.
    mass1 = 1.77
    mass2 = 1.07

    far_star = 1. / (30. * 86400.)
    snr_star = 8.5
    livetime = 166.6 * 86400.

    thresholds_dict = json.loads(thresholds_bytes)
    mean_values_dict = json.loads(mean_counts_bytes)
    mean_values_dict["counts_Terrestrial"] = far_star * livetime

    snr_choice = pastrocomp.choose_snr(far,
                                       snr,
                                       pipeline,
                                       instruments,
                                       thresholds_dict)

    astro_bayesfac = pastrocomp.get_f_over_b(far,
                                             snr_choice,
                                             far_star,
                                             snr_star)

    p_astros = \
        pastrocomp.evaluate_p_astro_from_bayesfac(astro_bayesfac,
                                                  mean_values_dict,
                                                  mass1, mass2)

    assert pytest.approx(snr_thresh, abs=1e-2) == snr_choice
    assert pytest.approx(p_astros['BNS'], abs=1e-2) == val


@pytest.mark.parametrize(
    'pipeline,instruments,far,snr,snr_c',
    (['mbtaonline', {'H1', 'L1'}, 4e-10, 50, 50],
     ['mbtaonline', {'H1', 'L1'}, 2e-10, 50, 10],
     ['mbtaonline', {'L1', 'V1'}, 8e-10, 50, 50],
     ['mbtaonline', {'L1', 'V1'}, 6e-10, 50, 10],
     ['mbtaonline', {'H1', 'V1'}, 8e-10, 50, 50],
     ['mbtaonline', {'H1', 'V1'}, 6e-10, 50, 10],
     ['mbtaonline', {'H1', 'L1', 'V1'}, 1e-13, 50, 50],
     ['mbtaonline', {'H1', 'L1', 'V1'}, 1e-15, 50, 12],
     ['pycbc', {'H1', 'L1'}, 4e-10, 50, 50],
     ['pycbc', {'H1', 'L1'}, 2e-10, 50, 10],
     ['spiir', {'H1', 'L1'}, 4e-20, 50, 50],
     ['gstlal', None, 4e-20, 50, 50]))
def test_compute_choose_snr(pipeline, instruments, far,
                            snr, snr_c,thresholds_bytes):
    """For various mock-FARs, test the snr returned for
       very loud MBTA, PyCBC and spiir events.
    """

    thresholds_dict = json.loads(thresholds_bytes)
    snr_choice = pastrocomp.choose_snr(far, snr, pipeline, instruments, thresholds_dict)

    assert pytest.approx(snr_choice, abs=1e-2) == snr_c
