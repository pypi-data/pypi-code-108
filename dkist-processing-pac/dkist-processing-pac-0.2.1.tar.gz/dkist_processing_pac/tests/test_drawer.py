import os
from collections import defaultdict
from glob import glob

import numpy as np
from astropy.io import fits as pyfits
import pytest
from dkist_header_validator import spec122_validator

from dkist_processing_pac import Data, FittingFramework, generic, GenerateDemodMatrices
from dkist_processing_pac.DKISTDC.data import DCDrawer
from dkist_processing_pac.utils import gen_fake_data
from dkist_processing_pac.tests.conftest import CalibrationSequenceDataset, InstAccess


@pytest.fixture(scope="session")
def cs_with_low_flux():
    pol_status = [
            "clear",
            "Sapphire Polarizer",
            "clear",
        ]
    pol_theta = [0.0, 60., 0.0]
    ret_status = ["clear", "clear", "clear"]
    ret_theta = [0.0, 0.0, 0.0]
    dark_status = [
            "FieldStop (5arcmin)",
            "FieldStop (5arcmin)",
            "FieldStop (5arcmin)",
        ]
    ds = CalibrationSequenceDataset(array_shape=(1, 2, 2), time_delta=2.0, pol_status=pol_status, pol_theta=pol_theta,
                                    ret_status=ret_status, ret_theta=ret_theta, dark_status=dark_status)
    header_list = [
        spec122_validator.validate_and_translate_to_214_l0(d.header(), return_type=pyfits.HDUList)[0].header
        for d in ds
    ]
    out_dict = dict()
    for n in range(ds.num_steps):
        hdu_list = []
        for m in range(ds.num_mod):
            hdu_list.append(pyfits.PrimaryHDU(data=np.ones((3, 4, 1)), header=pyfits.Header(header_list.pop(0))))

        out_dict[n] = [InstAccess(h) for h in hdu_list]

    return out_dict, pol_status, pol_theta, ret_status, ret_theta, dark_status

@pytest.fixture(scope="session")
def cs_with_wrong_shape():
    pol_status = [
            "clear",
            "Sapphire Polarizer",
            "clear",
        ]
    pol_theta = [0.0, 60., 0.0]
    ret_status = ["clear", "clear", "clear"]
    ret_theta = [0.0, 0.0, 0.0]
    dark_status = [
            "FieldStop (5arcmin)",
            "FieldStop (5arcmin)",
            "FieldStop (5arcmin)",
        ]
    ds = CalibrationSequenceDataset(array_shape=(1, 2, 2), time_delta=2.0, pol_status=pol_status, pol_theta=pol_theta,
                                    ret_status=ret_status, ret_theta=ret_theta, dark_status=dark_status)
    header_list = [
        spec122_validator.validate_and_translate_to_214_l0(d.header(), return_type=pyfits.HDUList)[0].header
        for d in ds
    ]
    out_dict = dict()
    for n in range(ds.num_steps):
        hdu_list = []
        for m in range(ds.num_mod):
            hdu_list.append(pyfits.PrimaryHDU(data=np.ones((3, 4)), header=pyfits.Header(header_list.pop(0))))

        out_dict[n] = [InstAccess(h) for h in hdu_list]

    return out_dict, pol_status, pol_theta, ret_status, ret_theta, dark_status


@pytest.fixture(scope="session")
def SoCC_dir(tmpdir_factory):
    SoCC_dir = tmpdir_factory.mktemp("SoCC")
    num_pos = 5
    gen_fake_data.SoCC_multi_day(SoCC_dir, numdays=1, shape=(1, 1, num_pos), DHS=False, CS_name='may_CS')

    return str(SoCC_dir / 'day0')

@pytest.fixture(scope="function")
def DC_SoCC(SoCC_dir):
    file_list = sorted(glob(os.path.join(SoCC_dir, '*.FITS')))
    obj_dict = defaultdict(list)
    for i, f in enumerate(file_list):
        hdl = pyfits.open(f)
        for h in hdl[1:]:
            t_head = spec122_validator.validate_and_translate_to_214_l0(h.header, return_type=pyfits.HDUList)[0].header
            obj_dict[i].append(InstAccess(pyfits.ImageHDU(data=h.data, header=t_head)))

    return obj_dict


def test_dkistdc_drawer(general_cs):
    cs_step_obj_dict = general_cs[0]
    D = DCDrawer(cs_step_obj_dict, remove_I_trend=False)
    assert D.nummod == 3
    assert D.numsteps == 7 - 2
    np.testing.assert_array_equal(D.pol_in, [False, True, True, True, False])
    np.testing.assert_array_equal(D.theta_pol_steps, [0.0, 60.0, 60.0, 120.0, 0.0])
    np.testing.assert_array_equal(D.ret_in, [False, False, True, False, False])
    np.testing.assert_array_equal(D.theta_ret_steps, [0.0, 0.0, 45.0, 0.0, 0.0])
    np.testing.assert_array_equal(D.dark_in, [False, False, False, False, False])
    assert D.shape == (3, 4, 1)
    cc = np.ones((3, 5)) * np.arange(1, 6)[None, :] + 100 * np.arange(3)[:, None]
    for i in range(np.prod(D.shape)):
        D_cc = D[np.unravel_index(i, D.shape)]
        assert type(D_cc) is np.ndarray
        assert D_cc.dtype == np.float64
        np.testing.assert_array_equal(D_cc, cc)

    # Test slicing errors
    with pytest.raises(IndexError):
        I = D[1,0]
    with pytest.raises(IndexError):
        I = D[0]
    with pytest.raises(IndexError):
        I = D[0,1.1,0]
    with pytest.raises(IndexError):
        I = D[0,:,0]

    # Test uncertainty
    assert D.RN == 0. # TODO: Update this test when RN is updated in the actual Drawer module

    I = D[0,0,0]
    u = D.get_uncertainty(I)
    np.testing.assert_array_equal(u, np.sqrt(np.abs(I) + D.RN**2))

def test_dkistdc_drawer_with_darks(general_cs):
    cs_step_obj_dict = general_cs[0]
    D = DCDrawer(cs_step_obj_dict, skip_darks=False, remove_I_trend=False)
    assert D.nummod == 3
    assert D.numsteps == 7
    np.testing.assert_array_equal(D.pol_in, [False, False, True, True, True, False, False])
    np.testing.assert_array_equal(D.theta_pol_steps, [0.0, 0.0, 60.0, 60.0, 120.0, 0.0, 0.0])
    np.testing.assert_array_equal(D.ret_in, [False, False, False, True, False, False, False])
    np.testing.assert_array_equal(D.theta_ret_steps, [0.0, 0.0, 0.0, 45.0, 0.0, 0.0, 0.0])
    np.testing.assert_array_equal(D.dark_in, [True, False, False, False, False, False, True])
    assert D.shape == (3, 4, 1)
    cc = np.ones((3, 7)) * np.arange(7)[None, :] + 100 * np.arange(3)[:, None]
    for i in range(np.prod(D.shape)):
        np.testing.assert_array_equal(D[np.unravel_index(i, D.shape)], cc)

def test_dkistdc_drawer_I_trend(general_cs):
    cs_step_obj_dict = general_cs[0]
    D = DCDrawer(cs_step_obj_dict, remove_I_trend=True)
    assert D.shape == (3, 4, 1)
    cc = np.ones((3, 5)) * np.arange(1, 6)[None, :] + 100 * np.arange(3)[:, None]
    cc /= np.arange(1, 6) * 0.00970874 + 0.97087379
    for i in range(np.prod(D.shape)):
        np.testing.assert_allclose(D[np.unravel_index(i, D.shape)], cc)

def test_dkistdc_drawer_low_flux(cs_with_low_flux):
    with pytest.raises(ValueError):
        D = DCDrawer(cs_with_low_flux[0], remove_I_trend=True)

def test_dkistdc_drawer_bad_shape(cs_with_wrong_shape):
    with pytest.raises(ValueError):
        D = DCDrawer(cs_with_wrong_shape[0])

def test_dresser(general_cs):
    cs_step_obj_dict = general_cs[0]
    D1 = DCDrawer(cs_step_obj_dict, skip_darks=False, remove_I_trend=False)
    D2 = DCDrawer(cs_step_obj_dict, skip_darks=True, remove_I_trend=False)
    DRSR = Data.Dresser()
    DRSR.add_drawer(D1)
    DRSR.add_drawer(D2)

    assert DRSR.nummod == 3
    assert DRSR.numsteps == 7 + 7 - 2
    np.testing.assert_array_equal(DRSR.pol_in,
                                  [False, False, True, True, True, False, False] + [False, True, True, True, False])
    np.testing.assert_array_equal(DRSR.theta_pol_steps,
                                  [0.0, 0.0, 60.0, 60.0, 120.0, 0.0, 0.0] + [0.0, 60.0, 60.0, 120.0, 0.0])
    np.testing.assert_array_equal(DRSR.ret_in,
                                  [False, False, False, True, False, False, False] + [False, False, True, False, False])
    np.testing.assert_array_equal(DRSR.theta_ret_steps,
                                  [0.0, 0.0, 0.0, 45.0, 0.0, 0.0, 0.0] + [0.0, 0.0, 45.0, 0.0, 0.0])
    np.testing.assert_array_equal(DRSR.dark_in,
                                  [True, False, False, False, False, False, True] + [False, False, False, False, False])
    assert DRSR.shape == (3, 4, 1)
    cc1 = np.ones((3, 7)) * np.arange(7)[None, :] + 100 * np.arange(3)[:, None]
    cc2 = np.ones((3, 5)) * np.arange(1, 6)[None, :] + 100 * np.arange(3)[:, None]
    cc = np.hstack([cc1, cc2])
    for i in range(np.prod(DRSR.shape)):
        np.testing.assert_array_equal(DRSR[np.unravel_index(i, DRSR.shape)][0], cc)

    # Test that uncertainty is correctly computed
    I1 = D1[0, 0, 0]
    I2 = D2[0, 0, 0]
    I, u = DRSR[0, 0, 0]
    np.testing.assert_array_equal(u, np.hstack((D1.get_uncertainty(I1), D2.get_uncertainty(I2))))

@pytest.mark.skip(reason="Depends on SV-style data")
def test_same_dresser_as_non_DC(SoCC_dir, DC_SoCC):
    DRSR = Data.Dresser()
    DRSR.add_drawer(Data.Drawer(SoCC_dir))

    dc_DRSR = Data.Dresser()
    dc_DRSR.add_drawer(DCDrawer(DC_SoCC))

    for attr in ['instrument', 'nummod', 'numsteps', 'shape', 'theta_pol_steps', 'theta_ret_steps', 'pol_in',
                 'ret_in', 'date_bgn', 'date_end', 'wavelength', 'azimuth', 'elevation', 'table_angle',
                 'I_clear']:
        print(attr)
        if type(getattr(DRSR, attr)) is np.ndarray:
            np.testing.assert_equal(getattr(DRSR, attr), getattr(dc_DRSR, attr))
        else:
            assert getattr(DRSR, attr) == getattr(dc_DRSR, attr)

    for i in range(np.prod(DRSR.shape)):
        idx = np.unravel_index(i, DRSR.shape)
        np.testing.assert_array_equal(DRSR[idx][0], dc_DRSR[idx][0])
        np.testing.assert_array_equal(DRSR[idx][1], dc_DRSR[idx][1])

@pytest.mark.skip(reason="Depends on SV-style data")
@pytest.mark.slow
def test_same_fit_and_demod_as_non_DC(SoCC_dir, DC_SoCC, tmp_path):
    CMP, TMP, TM = FittingFramework.run_fits([SoCC_dir], fit_TM=False, threads=2,
                                             telescope_db=generic.get_default_telescope_db())
    cmp_file = tmp_path / 'cmp.fits'
    CMP.writeto(cmp_file)

    DRSR = Data.Dresser()
    DRSR.add_drawer(DCDrawer(DC_SoCC))
    dc_CMP, dc_TMP, dc_TM = FittingFramework.run_core(DRSR, fit_TM=False, threads=2,
                                             telescope_db=generic.get_default_telescope_db())

    np.testing.assert_equal(CMP.CU_params, dc_CMP.CU_params)
    np.testing.assert_equal(TMP.TM_params, dc_TMP.TM_params)

    dmod_file = tmp_path / 'dmod.fits'
    GenerateDemodMatrices.main(SoCC_dir, str(cmp_file), str(dmod_file),
                               telescope_db=generic.get_default_telescope_db())
    dhdl = pyfits.open(dmod_file)
    dmod = dhdl[1].data

    dc_dmod = GenerateDemodMatrices.DC_main(DRSR, dc_CMP, telescope_db=generic.get_default_telescope_db())
    np.testing.assert_equal(dmod, dc_dmod)
