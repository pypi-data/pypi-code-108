#!/usr/bin/python
import os
import pickle
import pkg_resources
import time
import warnings
import asdf
import yaml
from importlib import resources
import numpy as np
from astropy.io import fits as pyfits
import astropy.coordinates as apc
from astropy.time import Time
from dkist_processing_pac import TelescopeModel, CUModel, generic
from dkist_processing_pac.tag import tag
from dkist_processing_pac.M12 import ContinuumPolarization
from dkist_processing_pac.data import S122
from astropy.utils.exceptions import ErfaWarning
from dkist_fits_specifications import spec122

warnings.filterwarnings('ignore', category=ErfaWarning)
np.random.seed(42)

AZ = np.random.random() * 360.
EL = np.random.random() * 360.
TAB = np.random.random() * 360.

VTF_HEAD = {}

def gen_dummy_ViSP_data(outdir, nummod=8, numsteps=20, shape=(2048, 2048)):

    for m in range(numsteps):

        hdulist = [pyfits.PrimaryHDU()]
        hdulist[0].header['TAZIMUTH'] = AZ
        hdulist[0].header['TELEVATN'] = EL
        hdulist[0].header['TTBLANGL'] = TAB
        hdulist[0].header[S122['ViSP_NumberOfModulatorStates']] = nummod
        hdulist[0].header[S122['PolarizerAngle']] = 360. * (m + 1) / numsteps
        hdulist[0].header[S122['RetarderAngle']] = 360. * (numsteps - m) / numsteps

        for n in range(nummod):
            print(m, n)
            data = np.arange(shape[0] * shape[1], dtype=np.float64).reshape(*shape) * n + m
            ih = pyfits.ImageHDU(data)
            ih.header[S122['ViSP_NumberOfModulatorStates']] = nummod
            ih.header[S122['ViSP_CurrentState']] = n
            hdulist.append(ih)

        outname = '{:}/VISP.C{:03}.FITS'.format(outdir, m)
        pyfits.HDUList(hdulist).writeto(outname, overwrite=True)


def gen_full_SoCC_run(outdir, ret0_h, dret_h, ret0_45, dret_45, ret0_r, dret_r,
                      theta_pol_steps, theta_ret_steps, pol_in, ret_in, dark_in,
                      wave=633., start_time=57530., nummod=8, shape=(1, 10, 10), tab_offset=0,
                      nondata_mask=None, I_sys=55555, df=-500, Q_in=0, U_in=0, V_in=0, use_M12=True,
                      rand_TM=False, spec_122=False, DHS=True, rand_trans=False, SNR=0, muellernoise=0,
                      RN=0, telescope_db=None, seed=42, modmat=None, sin_kwargs=None, allsame=False,
                      dark_signal=0, instrument='visp', suffix='FITS'):

    numsteps = theta_pol_steps.size

    # Assume each step takes 15s
    dt = 15 / (3600 * 24.)
    step_times = np.arange(numsteps) * dt + start_time
    # Within each step each modulator takes 1 second
    dt_m = 1. / (3600 * 24.)

    # This ensures that the true I_sys (the average of the clear measurements) is what the user requested
    I0 = I_sys - 0.5 * (numsteps * df)

    # Load correct instrument-specific stuff
    if instrument.lower() == 'visp':
        from ViSP_Pipeline.utils.gen_fake_data import ViSPDataSet
        from dkist_processing_pac.data import load_visp_keywords
        name_prefix = 'VISP'
        header_func = fill_visp_header
        header_func_args = []
        load_visp_keywords()
        VDS = ViSPDataSet('PolCal', start_time, wave, nummod)
        inst_head = VDS.header()

    elif instrument.lower() == 'dlnirsp':
        from DLNIRSP_Pipeline.utils.gen_fake_data import DLDataSet
        from dkist_processing_pac.data import load_dlnirsp_keywords
        name_prefix = 'DLNIRSP'
        header_func = fill_dlnirsp_header
        header_func_args = []
        load_dlnirsp_keywords()
        DDS = DLDataSet('PolCal', start_time, wave, nummod, 'DLCAM2')
        inst_head = DDS.header()

    elif instrument.lower() in ['cryo-sp', 'cryo-ci']:
        from CryoNIRSP_Pipeline.utils.gen_fake_data import CryoDataSet
        from dkist_processing_pac.data import load_cryo_keywords
        load_cryo_keywords()
        name_prefix = 'CRYONIRSP'
        header_func_args = []
        if instrument.lower() == 'cryo-sp':
            header_func = fill_cryonirsp_sp_header
            CDS = CryoDataSet(1, 'PolCal', 'PolCal4', start_time, wave, nummod)
        else:
            header_func = fill_cryonirsp_ci_header
            CDS = CryoDataSet(2, 'PolCal', 'PolCal4', start_time, wave, nummod)

        inst_head = CDS.header()

    elif instrument.lower() == 'vtf':
        name_prefix = 'VTF'
        header_func = fill_VTF_header
        header_func_args = []
        inst_head = VTF_HEAD


    bool_pol = np.array([i not in ['undefined', 'clear', False] for i in pol_in], dtype=bool)
    bool_ret = np.array([i not in ['undefined', 'clear', False] for i in ret_in], dtype=bool)
    bool_dark = np.array([i in ['Dark', 'DarkShutter'] for i in dark_in], dtype=bool)
    CS = CUModel.CalibrationSequence(theta_pol_steps, theta_ret_steps, bool_pol, bool_ret, bool_dark, step_times,
                                     ret_0_h=ret0_h, dret_h=dret_h,
                                     ret_0_45=ret0_45, dret_45=dret_45,
                                     ret_0_r=ret0_r, dret_r=dret_r,
                                     I_sys=I0, Q_in=Q_in, U_in=U_in, V_in=V_in)
    if rand_trans:
        print('setting random transmission coefficiencts')
        np.random.seed(seed)
        CS.t_ret_0 = np.random.random((1,)) * 0.3 + 0.7
        CS.t_pol_0 = np.random.random((1,)) * 0.3 + 0.7

    CS.set_py_from_database(wave)

    ele = np.zeros(numsteps)
    az = np.zeros(numsteps)
    tab = np.zeros(numsteps)
    for n in range(numsteps):
        obstime = Time(step_times[n], format='mjd')
        tele, taz, ttab = compute_telgeom(obstime)
        ele[n] = tele
        az[n] = taz
        tab[n] = ttab + tab_offset

    TM = TelescopeModel.TelescopeModel(az, ele, tab)

    if telescope_db is None:
        telescope_db = generic.get_default_telescope_db()
    TM.load_from_database(telescope_db, np.mean(step_times), wave)

    if rand_TM:
        np.random.seed(seed)
        TM.x34 += np.random.random() * 0.3 - 0.15
        TM.t34 = (np.random.random() * 60 + 150.) * np.pi / 180
        TM.x56 += np.random.random() * 0.3 - 0.15
        TM.t56 = (np.random.random() * 60 + 150.) * np.pi / 180

    if modmat is None:
        if nummod == 4:
            # Ideal 4-state matrix from DH
            sqrt3 = 1 / np.sqrt(3)
            O = np.array([[ 1.,  sqrt3,  sqrt3, -sqrt3],
                          [ 1.,  sqrt3, -sqrt3,  sqrt3],
                          [ 1., -sqrt3,  sqrt3,  sqrt3],
                          [ 1., -sqrt3, -sqrt3, -sqrt3]], dtype=np.float64)
        elif nummod == 8:
            # Real modulation matrix taken from CBeck's create_synth_cal.pro
            O = np.array([[ 0.693405 ,  0.0833252,  0.598811 , -0.269802 ],
                          [ 0.911968 ,  0.731004 ,  0.327143 , -0.376851 ],
                          [ 0.979729 ,  0.914248 ,  0.084737 ,  0.296836 ],
                          [ 0.711025 ,  0.116364 , -0.224191 ,  0.557482 ],
                          [ 0.603848 , -0.19099  , -0.518671 , -0.0773989],
                          [ 0.862482 ,  0.585429 , -0.38387  , -0.428604 ],
                          [ 1.       ,  0.981222 ,  0.191533 ,  0.0325373],
                          [ 0.789829 ,  0.35732  ,  0.639435 ,  0.233042 ]], dtype=np.float64)
        elif nummod == 10:
            # Modulation matrix for AdW's synthetic ViSP data from mod_matrix_630.out
            O = np.array([[ 1.        ,  0.19155013,  0.80446989, -0.47479524],
                          [ 1.        , -0.65839661,  0.68433984,  0.00466389],
                          [ 1.        , -0.80679413, -0.16112977,  0.48234158],
                          [ 1.        , -0.04856211, -0.56352868,  0.77578117],
                          [ 1.        ,  0.56844858,  0.03324473,  0.77289873],
                          [ 1.        ,  0.19155013,  0.80446989,  0.47479524],
                          [ 1.        , -0.65839661,  0.68433984, -0.00466389],
                          [ 1.        , -0.80679413, -0.16112977, -0.48234158],
                          [ 1.        , -0.04856211, -0.56352868, -0.77578117],
                          [ 1.        ,  0.56844858,  0.03324473, -0.77289873]], dtype=np.float64)
        else:
            raise ValueError('Nummod must be either 8 or 10')
    else:
        if modmat.shape[1] != 4:
            raise ValueError('Provided modulation matrix must have shape (M, 4)')
        O = modmat
        nummod = O.shape[0]

    if muellernoise:
        print('Perturbing Mueller matrices by {} %'.format(muellernoise * 100))
        T = TM.TM + (np.random.random(TM.TM.shape).astype(np.float64) * 2 * muellernoise * np.mean(TM.TM) - muellernoise * np.mean(TM.TM))
        M12 = TM.M12 + (np.random.random(TM.M12.shape).astype(np.float64) * 2 * muellernoise * np.mean(TM.M12) - muellernoise * np.mean(TM.M12))
        CM = CS.CM + (np.random.random(CS.CM.shape).astype(np.float64) * 2 * muellernoise * np.mean(CS.CM) - muellernoise * np.mean(CS.CM))
    else:
        T = TM.TM
        M12 = TM.M12
        CM = CS.CM

    # exp_times contains the obs time for every single modulator state
    mod_delta_t = np.arange(nummod) * dt_m
    exp_times = step_times[:, None] + mod_delta_t[None, :]  # Damn this line is cool
    # exp_times = (N, M)

    S_in = CS.S_in * (1 + df * numsteps / (numsteps - 1) / I0 * np.arange(numsteps))[:, None]
    # (N, 4)

    # This is S_in for every pixel requested (i.e., shape)
    if np.prod(shape) * np.prod(shape) * nummod < 1e5:
        S_in_big = np.dstack([S_in] * nummod * np.prod(shape)).reshape(S_in.shape + (nummod,) + shape)
        mem_err = False
    else:
        print('WARNING! NOT ENOUGH MEMORY TO VARY S_IN FOR EACH PIXEL. FALLING BACK TO SINGLE INPUT FLUX')
        mem_err = True
        OG_shape = shape
        shape = (1,1,1)
        S_in_big = np.dstack([S_in] * nummod).reshape(S_in.shape + (nummod,) + shape)

    S_in_big = np.moveaxis(S_in_big, 2, 1)
    # (N, M, 4, shape)

    if sin_kwargs:
        np.random.seed()
        print('Adding sin perturbation with {}'.format(sin_kwargs))
        sin_pert = sin_perturbation(exp_times, shape, **sin_kwargs)
        # sin_pert = (N, M, shape)
        S_in_big *= 1 + sin_pert[:, :, None, ...]
        # (N, M, 4, shape)

    expander_dims = list(range(-1, -1 * (len(shape) + 1), -1))
    if use_M12:
        print('including M12')
        # T = (N, 4, 4), CM = (N, 4, 4), M12 = (4, 4)
        TCM_exp = np.expand_dims(T @ CM @ M12, [1] + expander_dims)
        # TCM_exp = (N, 1, 4, 4, shape)
    else:
        print('omitting M12')
        TCM_exp = np.expand_dims(T @ CM, [1] + expander_dims)

    # Multiplication basically does TCM @ S_in for all pixels and all CS steps
    S = np.sum(TCM_exp * S_in_big[:, :, None, ...], axis=3)
    # S = (N, M, 4, shape)

    # More array trickery - O_exp is (M, 4, 1, shape)
    O_exp = np.expand_dims(O, [-1 * len(shape) - 1] + expander_dims)
    S_mult = np.moveaxis(S, 0, 2)
    # S_mult = (M 4, N, shape)
    I = np.sum(O_exp * S_mult, axis=1)
    # I = (M, N, shape)

    for n in range(numsteps):

        hdulist = [pyfits.PrimaryHDU()]
        hdulist[0].header.update(inst_head)
        hdulist[0].header['DATE-OBS'] = Time(step_times[n], format='mjd').fits
        hdulist[0].header['DATE-BGN'] = Time(start_time, format='mjd').fits
        hdulist[0].header['DATE-END'] = Time(step_times[-1], format='mjd').fits
        hdulist[0].header[S122['Instrument']] = instrument
        hdulist[0].header[S122['Wavelength']] = wave
        hdulist[0].header['TAZIMUTH'] = az[n]
        hdulist[0].header['TELEVATN'] = ele[n]
        hdulist[0].header['TTBLANGL'] = tab[n]
        hdulist[0].header[S122['InstrumentProgramTask']] = 'polcal'
        hdulist[0].header[S122['GOSPolarizer']] = pol_in[n]
        hdulist[0].header[S122['PolarizerAngle']] = str(theta_pol_steps[n])
        hdulist[0].header[S122['GOSRetarder']] = ret_in[n]
        hdulist[0].header[S122['RetarderAngle']] = str(theta_ret_steps[n])
        hdulist[0].header[S122['GOSLevel0']] = dark_in[n]
        if not DHS:
            hdulist[0].header[S122['ReadNoise']] = RN
        header_func(*([hdulist[0].header, -1, nummod] + header_func_args))

        for m in range(nummod):
            if mem_err:
                data = np.ones(OG_shape, dtype=np.float64) * I[m, n, 0, 0, 0]
            else:
                data = I[m, n]

            if nondata_mask is not None:
                data[nondata_mask] = 0.

            if SNR:
                np.random.seed()
                print('Adding photon noise so SNR = {} at {} counts. <Current counts> = {}'.format(SNR, I_sys,
                                                                                                   np.mean(I[m,n])))
                shotnoise = I_sys / SNR * np.sqrt(np.mean(data) / I_sys)
                print('\tshot noise sigma = {:10.3f}'.format(shotnoise))
                data += np.random.randn(*data.shape) * shotnoise
            if RN:
                np.random.seed()
                print('RN = {:3.1f}'.format(RN))
                data += np.random.randn(*data.shape) * RN

            if dark_signal:
                if type(dark_signal) is tuple and len(dark_signal) == 2:
                    print('Adding dark with mu = {:.2f} and sigma = {:.2f}'.format(*dark_signal))
                    dark = np.random.randn(*data.shape) * dark_signal[1] + dark_signal[0]
                elif type(dark_signal) in [int, float]:
                    print('Adding dark = {:.1f}'.format(dark_signal))
                    dark = dark_signal
                else:
                    raise ValueError('dark_signal must be either a number or a len 2 tuple, you passed {}'.format(dark_signal))

                data += dark

            if allsame:
                ridx = np.unravel_index(np.random.randint(0, data.size), data.shape)
                data = np.ones(shape, dtype=np.float64) * data[ridx]

            if DHS:
                ph = pyfits.PrimaryHDU(np.abs(data).astype(np.uint16), header=hdulist[0].header)
                date = Time(exp_times[n, m], format='mjd')
                ph.header['DATE-OBS'] = date.fits
                header_func(*([ph.header, m, nummod] + header_func_args))
                outname = '{}/{}_{}_{}.{}'.format(outdir, name_prefix, date.datetime.strftime("%Y%m%dT%H%M%S.%f"), m, suffix)
                print(outname)
                ph.writeto(outname, overwrite=True)
            else:
                ih = pyfits.ImageHDU(data, header=hdulist[0].header)
                ih.header['DATE-OBS'] = Time(exp_times[n, m], format='mjd').fits
                header_func(*([ih.header, m, nummod] + header_func_args))
                hdulist.append(ih)

        if not DHS:
            outname = '{:}/{}.C{:03}.{}'.format(outdir, name_prefix, n, suffix)
            pyfits.HDUList(hdulist).writeto(outname, overwrite=True)

    return O, TM, CS, I, az, ele, tab, S_in_big, exp_times


def sin_perturbation(exp_times, shape, amp=0.1, noise=0.1, phase=0, rand_phase=False):

    numsteps, nummod = exp_times.shape

    x = (exp_times.reshape(nummod * numsteps) - exp_times.min()) / (exp_times.max() - exp_times.min()) * 2 * np.pi

    if rand_phase:
        phase_vec = np.random.random(shape) * 2 * np.pi
    else:
        phase_vec = np.ones(shape) * phase
    sin_pert = np.sin(np.expand_dims(x, list(range(-1, -1 * (len(shape) + 1), -1))) + phase_vec[None, ...]) * amp
    if noise > 0:
        sin_pert += np.random.randn(*((numsteps * nummod,) + shape)) * noise * amp

    sin_pert = sin_pert.reshape((numsteps, nummod) + shape)

    return sin_pert

def fill_visp_header(header, m, nummod):
    header[S122['Instrument']] = 'VISP'
    header[S122['ViSP_NumberOfModulatorStates']] = nummod
    header[S122['ViSP_CurrentState']] = m + 1
    header[S122['ViSP_PolarimeterMode']] = 'Full Stokes'
    # header[S122['ViSP_BeamBorder']] = 1080

def fill_dlnirsp_header(header, m, nummod):
    header[S122['DLN_NumberOfModulatorStates']] = nummod
    header[S122['DLN_CurrentState']] = m

def fill_cryonirsp_sp_header(header, m, nummod):
    header[S122['Instrument']] = 'cryo'
    header[S122['CRSP_NumberOfModulatorStates']] = nummod
    header[S122['CRSP_CurrentState']] = m
    header[S122['CRSP_CryoInstrument']] = 1
    header[S122['CRSP_SubtaskName']] = 'Polcal4'
    header[S122['CRSP_PolarimeterMode']] = 'Full Stokes'

def fill_cryonirsp_ci_header(header, m, nummod):
    header[S122['Instrument']] = 'cryo'
    header[S122['CRSP_NumberOfModulatorStates']] = nummod
    header[S122['CRSP_CurrentState']] = m
    header[S122['CRSP_CryoInstrument']] = 2
    header[S122['CRSP_SubtaskName']] = 'Polcal4'
    header[S122['CRSP_PolarimeterMode']] = 'Full Stokes'

def fill_VTF_header(header, m, nummod):
    header[S122['VTF_NumberOfModulatorStates']] = nummod
    header[S122['VTF_CurrentState']] = m

def SoCC_fixed_pol(outputdir, nummod=10, shape=(1, 1, 1), seed=42, itc=True, clear=True, dret=False, rand_S_in=False,
                   rand_Q=False, rand_ret=False, dark=True, wave=633., **full_kwargs):

    polcal_init_file = pkg_resources.resource_filename('dkist_processing_pac', 'data/init_values/polcal_default.asdf')
    with asdf.open(polcal_init_file, 'rb', lazy_load=False, copy_arrays=True) as f:
        polcal_init = f.tree
    wave_idx = np.argmin(np.abs(polcal_init['wave'] - wave))
    params = polcal_init['params']

    if rand_ret:
        np.random.seed(seed)
        ret0_h = np.random.random() * 0.1 + 0.9
        ret0_45 = np.random.random() * 0.1 + 1.4
        ret0_r = np.random.random() * 0.015 + 0.02
    else:
        rng = np.random.default_rng(seed)
        ret0_h = rng.uniform(params['ret0h'][wave_idx, :][0], params['ret0h'][wave_idx, :][2])
        ret0_45 = rng.uniform(params['ret045'][wave_idx, :][0], params['ret045'][wave_idx, :][2])
        ret0_r = rng.uniform(params['ret0r'][wave_idx, :][0], params['ret0r'][wave_idx, :][2])

    if dret:
        # dret from assumption of 0.1 deg per deg C and a ~5 deg C heating over 15 min
        dret_h = 0.5 / 15 * 60 * 24 * np.pi / 180.
        dret_h += np.random.random() * dret_h * 0.2 - (dret_h * 0.1)
        dret_45 = 0.5 / 15 * 60 * 24 * np.pi / 180.
        dret_45 += np.random.random() * dret_45 * 0.2 - (dret_45 * 0.1)
        dret_r = 0.5 / 15 * 60 * 24 * np.pi / 180.
        dret_r += np.random.random() * dret_r * 0.2 - (dret_r * 0.1)
    else:
        dret_h = 0
        dret_45 = 0
        dret_r = 0

    if itc:
        numsteps = 53
        ret_reset = np.array([40., 20.])
    else:
        numsteps = 49
        ret_reset = np.array([40.])

    Q_in = np.random.uniform(params['Q_in'][wave_idx, :][0], params['Q_in'][wave_idx, :][2])
    U_in = 0
    V_in = 0
    if rand_Q:
        Q_in += np.random.random()
    if rand_S_in:
        U_in += np.random.random()
        V_in += np.random.random()

    theta_pol_steps = np.ones(numsteps - 8) * 180.
    theta_ret_steps = np.r_[np.linspace(0, 90, 10), ret_reset]
    for i in range(3):
        theta_ret_steps = np.r_[theta_ret_steps, np.linspace(100, 180, 9) + 90 * i, ret_reset]
    theta_pol_steps = np.r_[np.array([0, 45, 90, 135.]), theta_pol_steps, np.array([180, 225, 270, 315.])]
    theta_ret_steps = np.r_[np.zeros(4), theta_ret_steps, np.zeros(4)]

    pol_in = np.ones(numsteps, dtype=bool)
    ret_in = np.ones(numsteps, dtype=bool)
    ret_in[-4:] = False
    ret_in[:4] = False
    dark_in = np.zeros(numsteps, dtype=bool)

    # Add clears
    if clear:
        pol_in = np.r_[False, pol_in, False]
        ret_in = np.r_[False, ret_in, False]
        dark_in = np.r_[False, dark_in, False]
        theta_pol_steps = np.r_[0., theta_pol_steps, 0.]
        theta_ret_steps = np.r_[0., theta_ret_steps, 0.]

    # Add darks
    if dark:
        pol_in = np.r_[False, pol_in, False]
        ret_in = np.r_[False, ret_in, False]
        dark_in = np.r_[True, dark_in, True]
        theta_pol_steps = np.r_[0., theta_pol_steps, 0.]
        theta_ret_steps = np.r_[0., theta_ret_steps, 0.]

    O, TM, CS, I, _, _, _, _, _ = gen_full_SoCC_run(outputdir, ret0_h, dret_h, ret0_45, dret_45, ret0_r, dret_r,
                                                    theta_pol_steps, theta_ret_steps, pol_in, ret_in, dark_in,
                                                    nummod=nummod, shape=shape, Q_in=Q_in, U_in=U_in, V_in=V_in,
                                                    wave=wave, **full_kwargs)

    return ret0_h, dret_h, ret0_45, dret_45, ret0_r, dret_r, O, TM, CS, I


def SoCC_fixed_ret(outputdir, nummod=10, shape=(1, 1, 1), seed=42, itc=True, clear=True, dret=False, rand_S_in=False,
                   rand_Q=False, rand_ret=False, dark=True, wave=633., **full_kwargs):

    polcal_init_file = pkg_resources.resource_filename('dkist_processing_pac', 'data/init_values/polcal_default.asdf')
    with asdf.open(polcal_init_file, 'rb', lazy_load=False, copy_arrays=True) as f:
        polcal_init = f.tree
    wave_idx = np.argmin(np.abs(polcal_init['wave'] - wave))
    params = polcal_init['params']

    if rand_ret:
        np.random.seed(seed)
        ret0_h = np.random.random() * 0.1 + 0.9
        ret0_45 = np.random.random() * 0.1 + 1.4
        ret0_r = np.random.random() * 0.015 + 0.02
    else:
        rng = np.random.default_rng(seed)
        ret0_h = rng.uniform(params['ret0h'][wave_idx, :][0], params['ret0h'][wave_idx, :][2])
        ret0_45 = rng.uniform(params['ret045'][wave_idx, :][0], params['ret045'][wave_idx, :][2])
        ret0_r = rng.uniform(params['ret0r'][wave_idx, :][0], params['ret0r'][wave_idx, :][2])

    if dret:
        # dret from assumption of 0.1 deg per deg C and a ~5 deg C heating over 15 min
        dret_h = 0.5 / 15 * 60 * 24 * np.pi / 180.
        dret_h += np.random.random() * dret_h * 0.2 - (dret_h * 0.1)
        dret_45 = 0.5 / 15 * 60 * 24 * np.pi / 180.
        dret_45 += np.random.random() * dret_45 * 0.2 - (dret_45 * 0.1)
        dret_r = 0.5 / 15 * 60 * 24 * np.pi / 180.
        dret_r += np.random.random() * dret_r * 0.2 - (dret_r * 0.1)
    else:
        dret_h = 0
        dret_45 = 0
        dret_r = 0

    if itc:
        numsteps = 53
        pol_reset = np.array([0., 40])
        ret_reset = np.array([22.5, 22.5])
    else:
        numsteps = 49
        pol_reset = np.array([0.])
        ret_reset = np.array([22.5])

    Q_in = np.random.uniform(params['Q_in'][wave_idx, :][0], params['Q_in'][wave_idx, :][2])
    U_in = 0
    V_in = 0
    if rand_Q:
        Q_in += np.random.random()
    if rand_S_in:
        U_in += np.random.random()
        V_in += np.random.random()

    theta_pol_steps = np.linspace(0, 360, 37)
    theta_ret_steps = np.ones(37) * 22.5
    theta_ret_steps[1::4] += 5
    theta_ret_steps[2::4] += 5

    for i in range(3):
        idx = 10 + i * (9 + len(pol_reset))
        theta_pol_steps = np.r_[theta_pol_steps[:idx], pol_reset, theta_pol_steps[idx:]]
        theta_ret_steps = np.r_[theta_ret_steps[:idx], ret_reset, theta_ret_steps[idx:]]

    theta_pol_steps = np.r_[theta_pol_steps, pol_reset]
    theta_ret_steps = np.r_[theta_ret_steps, ret_reset]

    theta_pol_steps = np.r_[np.array([0, 45, 90, 135.]), theta_pol_steps, np.array([180, 225, 270, 315.])]
    theta_ret_steps = np.r_[np.zeros(4), theta_ret_steps, np.zeros(4)]

    pol_in = np.ones(numsteps, dtype=bool)
    ret_in = np.ones(numsteps, dtype=bool)
    dark_in = np.zeros(numsteps, dtype=bool)
    ret_in[-4:] = False
    ret_in[:4] = False

    # Add clears
    if clear:
        pol_in = np.r_[False, pol_in, False]
        ret_in = np.r_[False, ret_in, False]
        dark_in = np.r_[False, dark_in, False]
        theta_pol_steps = np.r_[0., theta_pol_steps, 0.]
        theta_ret_steps = np.r_[0., theta_ret_steps, 0.]

    # Add darks
    if dark:
        pol_in = np.r_[False, pol_in, False]
        ret_in = np.r_[False, ret_in, False]
        dark_in = np.r_[True, dark_in, True]
        theta_pol_steps = np.r_[0., theta_pol_steps, 0.]
        theta_ret_steps = np.r_[0., theta_ret_steps, 0.]

    O, TM, CS, I, _, _, _, _, _ = gen_full_SoCC_run(outputdir, ret0_h, dret_h, ret0_45, dret_45, ret0_r, dret_r,
                                                    theta_pol_steps, theta_ret_steps, pol_in, ret_in, dark_in,
                                                    nummod=nummod, shape=shape, Q_in=Q_in, U_in=U_in, V_in=V_in,
                                                    wave=wave, **full_kwargs)

    return ret0_h, dret_h, ret0_45, dret_45, ret0_r, dret_r, O, TM, CS, I

def CS_from_defaults(CS_name):

    if '_CS' not in CS_name:
        CS_name = CS_name + '_CS'
    CS_file = pkg_resources.resource_filename('dkist_processing_pac', 'data/CS_files/{}.txt'.format(CS_name))
    theta_pol_steps, theta_ret_steps, pol_in, ret_in, dark_in = np.loadtxt(CS_file, unpack=True)

    pol_in = np.array(pol_in, dtype=bool)
    ret_in = np.array(ret_in, dtype=bool)
    dark_in = np.array(dark_in, dtype=bool)

    pol_in = np.array(['Polarizer' if i else 'clear' for i in pol_in])
    ret_in = np.array(['SAR' if i else 'clear' for i in ret_in])
    dark_in = np.array(['DarkShutter' if i else "FieldStop (5arcmin)" for i in dark_in])

    return theta_pol_steps, theta_ret_steps, pol_in, ret_in, dark_in

def SoCC_from_defaults(outputdir, CS_name, nummod=10, shape=(1, 1, 1), seed=42, dret=False, rand_S_in=False,
                       rand_Q=False, rand_ret=False, wave=633, **full_kwargs):

    polcal_init_file = pkg_resources.resource_filename('dkist_processing_pac', 'data/init_values/polcal_default.asdf')
    with asdf.open(polcal_init_file, 'rb', lazy_load=False, copy_arrays=True) as f:
        polcal_init = f.tree
    wave_idx = np.argmin(np.abs(polcal_init['wave'] - wave))
    params = polcal_init['params']

    if rand_ret:
        np.random.seed(seed)
        ret0_h = np.random.random() * 0.1 + 0.9
        ret0_45 = np.random.random() * 0.1 + 1.4
        ret0_r = np.random.random() * 0.015 + 0.02
    else:
        rng = np.random.default_rng(seed)
        ret0_h = legacy_uniform_generator(rng, params['ret0h'][wave_idx, :])
        ret0_45 = legacy_uniform_generator(rng, params['ret045'][wave_idx, :])
        ret0_r = legacy_uniform_generator(rng, params['ret0r'][wave_idx, :])

    if dret:
        # dret from assumption of 0.1 deg per deg C and a ~5 deg C heating over 15 min
        dret_h = 0.5 / 15 * 60 * 24 * np.pi / 180.
        dret_h += np.random.random() * dret_h * 0.2 - (dret_h * 0.1)
        dret_45 = 0.5 / 15 * 60 * 24 * np.pi / 180.
        dret_45 += np.random.random() * dret_45 * 0.2 - (dret_45 * 0.1)
        dret_r = 0.5 / 15 * 60 * 24 * np.pi / 180.
        dret_r += np.random.random() * dret_r * 0.2 - (dret_r * 0.1)
    else:
        dret_h = 0
        dret_45 = 0
        dret_r = 0

    Q_in = np.random.uniform(params['Q_in'][wave_idx, :][0], params['Q_in'][wave_idx, :][2])
    U_in = 0
    V_in = 0
    if rand_Q:
        Q_in += np.random.random()
    if rand_S_in:
        U_in += np.random.random()
        V_in += np.random.random()


    theta_pol_steps, theta_ret_steps, pol_in, ret_in, dark_in = CS_from_defaults(CS_name)

    O, TM, CS, I, _, _, _, _, _ = gen_full_SoCC_run(outputdir, ret0_h, dret_h, ret0_45, dret_45, ret0_r, dret_r,
                                                    theta_pol_steps, theta_ret_steps, pol_in, ret_in, dark_in,
                                                    nummod=nummod, shape=shape, Q_in=Q_in, U_in=U_in, V_in=V_in,
                                                    wave=wave, **full_kwargs)

    return ret0_h, dret_h, ret0_45, dret_45, ret0_r, dret_r, O, TM, CS, I

def SoCC_multi_day(outputdir, numdays=10, nummod=10, shape=(1, 1, 1), rand_TM=True, DHS=True, rand_Q=False, rand_S_in=False,
                   only_pol=False, only_ret=False, spec_122=True, clear=True, df=None, I_sys=None, dret=False, use_M12=True,
                   rand_trans=True, SNR=0, muellernoise=0, seed=42, modmat=None,
                   start_time=57531., CS_name=None, **full_kwargs):

    dt = 0.021 # ~0.5 hours

    ret0_h_list = []
    dret_h_list = []
    ret0_45_list = []
    dret_45_list = []
    ret0_r_list = []
    dret_r_list = []
    t_pol_list = []
    t_ret_list = []
    I_sys_list = []
    Q_list = []
    U_list = []
    V_list = []
    for i in range(numdays):
        print(compute_telgeom(Time(start_time + (1 + dt) * i, format='mjd'))[0])
        outdir = '{}/day{}'.format(outputdir, i)
        os.makedirs(outdir, exist_ok=True)

        if I_sys is None:
            II_sys = np.random.random() * 50000 + 10000
        else:
            II_sys = I_sys
        if df is None:
            ddf = np.random.random() * 200 - 100
        else:
            ddf = df

        if CS_name is not None:
            print('{}: Making Drawer from CS {}'.format(tag(), CS_name))
            o = SoCC_from_defaults(outdir, CS_name, nummod=nummod, shape=shape, DHS=DHS, start_time=start_time + dt * i,
                                   rand_TM=rand_TM, seed=seed + i, spec_122=spec_122, df=ddf,
                                   I_sys=II_sys, dret=dret, rand_Q=rand_Q, use_M12=use_M12,
                                   rand_S_in=rand_S_in, SNR=SNR, muellernoise=muellernoise, rand_trans=rand_trans,
                                   modmat=modmat, **full_kwargs)
        else:
            np.random.seed()
            choice = np.random.random()
            if (choice > 0.5 and not only_ret) or only_pol:
                print('{}: Making Drawer with fixed_pol'.format(tag()))
                o = SoCC_fixed_pol(outdir, nummod=nummod, shape=shape, DHS=DHS, start_time=start_time + dt * i, rand_TM=rand_TM,
                                   seed=seed + i, spec_122=spec_122, ogy=ogy, clear=clear, df=ddf, I_sys=II_sys, dret=dret,
                                   rand_Q=rand_Q, use_M12=use_M12, rand_S_in=rand_S_in,
                                   SNR=SNR, muellernoise=muellernoise, rand_trans=rand_trans, modmat=modmat, **full_kwargs)
            else:
                print('{}: Making Drawer with fixed_ret'.format(tag()))
                o = SoCC_fixed_ret(outdir, nummod=nummod, shape=shape, DHS=DHS, start_time=start_time + dt * i, rand_TM=rand_TM,
                                   seed=seed + i, spec_122=spec_122, ogy=ogy, clear=clear, df=ddf, I_sys=II_sys, dret=dret,
                                   rand_Q=rand_Q, use_M12=use_M12, rand_S_in=rand_S_in,
                                   SNR=SNR, muellernoise=muellernoise, rand_trans=rand_trans, modmat=modmat, **full_kwargs)

        ret0_h, dret_h, ret0_45, dret_45, ret0_r, dret_r, _, TM, CS, _ = o

        ret0_h_list.append(ret0_h)
        dret_h_list.append(dret_h)
        ret0_45_list.append(ret0_45)
        dret_45_list.append(dret_45)
        ret0_r_list.append(ret0_r)
        dret_r_list.append(dret_r)
        t_pol_list.append(CS.t_pol_0[0])
        t_ret_list.append(CS.t_ret_0[0])
        I_sys_list.append(II_sys)
        Q_list.append(CS.Q_in)
        U_list.append(CS.U_in)
        V_list.append(CS.V_in)

    truth = {'x12': TM.x12,
             't12': TM.t12,
             'x34': TM.x34,
             't34': TM.t34,
             'x56': TM.x56,
             't56': TM.t56,
             'I_sys': I_sys_list,
             't_pol': t_pol_list,
             't_ret': t_ret_list,
             'Q_in': Q_list,
             'U_in': U_list,
             'V_in': V_list,
             'ret_0_h': ret0_h_list,
             'dret_h': dret_h_list,
             'ret_0_45': ret0_45_list,
             'dret_45': dret_45_list,
             'ret_0_r': ret0_r_list,
             'dret_r': dret_r_list}

    with open('{}/truth.pkl'.format(outputdir),'wb') as f:
        pickle.dump(truth, f)
    print_truth('{}/truth.pkl'.format(outputdir))

    return truth


def print_truth(truth_file='truth.pkl'):
    with open(truth_file, 'rb') as f:
        truth = pickle.load(f)

    for k in truth.keys():
        print('{:<10}:'.format(k), end='')
        if type(truth[k]) is list:
            try:
                print(str('{:10.3f}'*len(truth[k])).format(*truth[k]))
            except ValueError:
                print(str('{:10}'*len(truth[k])).format(*truth[k]))
            except Exception:
                print(' CANNOT PRINT')
        else:
            try:
                print('{:10.3f}'.format(truth[k]))
            except ValueError:
                print('{:10}'.format(truth[k]))

def make_M12_map(outdir, simdir='/home/ade/PycharmProjects/ViSP_pipeline/sim_data',
                 low_lim=15, high_lim=75, cont_low=-20, cont_high=None, datanoise=0):

    TM = TelescopeModel.TelescopeModel(0,0,0)
    np.random.seed(13)
    TM.x12 = np.random.random() * 0.35 + 0.9
    TM.t12 = (np.random.random() * 60 + 150.) * np.pi / 180

    for i in range(1000):
        print(i)
        hdus = pyfits.open('{:}/stokes/image.{:04}.fits'.format(simdir,i))
        stokes = np.dstack([h.data for h in hdus[1:]])

        data = np.sum(TM.M12 * stokes[:, :, None, :], axis=3)

        if datanoise:
            data += np.random.randn(*data.shape) * datanoise * np.mean(data)

        hdulist = pyfits.HDUList([pyfits.PrimaryHDU()])
        for j, s in enumerate(['I','Q','U','V']):
            hdulist.append(pyfits.ImageHDU(data[:, low_lim:high_lim, j]))
            hdulist[-1].header['VISP_STK'] = s
            hdulist[-1].header[S122['Wavelength']] = 588
            hdulist[-1].header['DATE-OBS'] = Time(57560, format='mjd').fits

        hdulist.writeto('{}/M12.{:04n}.FITS'.format(outdir, i), overwrite=True)

        I = data[:, cont_low:cont_high, 0]
        Q = data[:, cont_low:cont_high, 1]
        U = data[:, cont_low:cont_high, 2]

        i2q = np.nanmedian(Q / I)
        i2u = np.nanmedian(U / I)

        ContinuumPolarization.update_xtalk_database(i2q, i2u, 'gen_fake_data',
                                                    Time.now().mjd, 666)
        hdus.close()
        del hdus
        del stokes

    big_list = []
    for i in range(1000):
        print(i)
        hdus = pyfits.open('{}/M12.{:04}.FITS'.format(outdir,i))
        big_list.append(np.dstack([h.data for h in hdus[1:]]))
        hdus.close()

    big_map = np.stack(big_list, 1)
    del big_list
    print(big_map.shape)
    print(TM.x12, TM.t12)

    hdulist = pyfits.HDUList([pyfits.PrimaryHDU()])
    for i in range(4):
        hdulist.append(pyfits.ImageHDU(big_map[:, :, :, i]))

    hdulist[0].header[S122['Wavelength']] = 588
    hdulist[0].header['DATE-OBS'] = Time(57560, format='mjd').fits
    hdulist.writeto(outdir + '/full_maps.FITS', overwrite=True)

    return

 #  re-work of Arthur's function by DMH
def compute_telgeom(time_hst):
  dkist_lon = (156 + 15/60.0 + 21.7/3600.0) * (-1)
  dkist_lat = ( 20 + 42/60.0 + 27.0/3600.0)
  hel  = 3040.4
  hloc = apc.EarthLocation.from_geodetic(dkist_lon, dkist_lat, hel)
  sun_body = apc.get_body('sun', time_hst, hloc)  #get the solar ephemeris
  sun_dec = sun_body.dec.value   # Extract declination in degrees
  azel_frame = apc.AltAz(obstime=time_hst, location=hloc)  # Horizon coords
  sun_altaz = sun_body.transform_to(azel_frame)  # Sun in horizon coords
  alt = sun_altaz.alt.value  # Extract altitude
  azi = sun_altaz.az.value   # Extract azimuth

  #  COMPUTE Gregorian image rotation relative to celestial
  #  \cos\theta_{G} = \frac {\sin(Lat) - \sin(El) \sin(Dec)}  {\cos(El)\cos(Dec)}
  r2d = np.double(180) / np.pi
  cos_thetaG_top = np.sin( dkist_lat/r2d ) - np.sin( alt/r2d ) * np.sin(sun_dec/r2d)
  cos_thetaG_bot = np.cos(alt/r2d) * np.cos(sun_dec/r2d)
  thetaG = np.arccos( cos_thetaG_top / cos_thetaG_bot ) * r2d  #Gregorian image rot

  tableang = alt-azi#-thetaG

  return alt, azi, tableang#, thetaG

def convert_cbeck_db(inputfile='/home/ade/PAC/DKIST_programs/telescope_parameters.txt', outputfile='telescope_db.txt'):

    wave, x12, t12, x34, t34, x56, t56 = np.loadtxt(inputfile, usecols=(2, 3, 4, 5, 6, 7, 8), unpack=True, skiprows=1,
                                                    delimiter=',')
    date, time = np.loadtxt(inputfile, usecols=(0, 1), dtype=str, unpack=True, skiprows=1, delimiter=',')

    obstime = np.zeros(wave.size)
    for i in range(obstime.size):
        obstime[i] = Time('{}T{}:00'.format(date[i], time[i]), format='fits').mjd

    stack = np.vstack((obstime, wave, x12, t12 * np.pi / 180, x34, t34 * np.pi / 180, x56, t56 * np.pi / 180)).T

    with open(outputfile, 'w') as f:
        f.write(str('#{:>14}' + '{:>8}' + '{:>7}' * 6 + '\n').format('MJD', 'wave', 'x12', 't12', 'x34', 't34', 'x56',
                                                                     't56'))
        for i in range(obstime.size):
            f.write(str('{:15.6f}' + '{:8.2f}' + '{:7.3f}' * 6 + '\n').format(*stack[i]))

    return


def convert_cbeck_contrast(inputfile='/home/ade/PAC/polarizer_contrast_py_curve.sav', outputfile=None):
    import scipy.io as spio

    data = spio.readsav(inputfile)

    if outputfile is None:
        outputfile = './dkist_processing_pac/data/py_table.txt'

    N = data['wavel'].size
    with open(outputfile, 'w') as f:
        f.write(
            '# Lookup table for polarizer py values, assuming px = 1\n# File generated on {}\n'.format(time.asctime()))
        f.write('#{:>10}{:>13}\n\n'.format('wave [nm]', 'py'))
        for i in range(N):
            f.write('{:11.1f}{:13.9f}\n'.format(data['wavel'][i], data['py_wavel'][i]))

    return


def fill_spec122_header(header, inst_head):

    DEFAULT_STRING = 'Etaoin Shrdlu'
    DEFAULT_TIME = '1988-05-25T00:00:00'
    DEFAULT_INT = 666
    DEFAULT_FLOAT = 6.283185307179586
    DEFAULT_BOOL = False

    # Sections of SPEC 122 that should be present in VTF data
    sections = ['ao', 'camera', 'dkist-dkist', 'dkist-id', 'fits', 'pac', 'visp', 'wcs', 'wfc', 'ws']

    # Keywords that are automatically generated by the astropy library
    ignore = ['SIMPLE', 'BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2', 'NAXIS3', 'EXTEND', 'END', 'BLANK']

    for section in sections:
        DC_s122 = yaml.load(resources.read_text(spec122, '{}.yml'.format(section)), Loader=yaml.Loader)
        for key in DC_s122:
            keyword_name = key
            # Check if the keyword should be ignored
            if keyword_name not in ignore:
                keyword_type = DC_s122[key]['type']
                try:
                    comment = DC_s122[key]['comment']
                except KeyError:
                    comment = 'Default comment'
                # Get data of the correct type
                if keyword_type == 'str':
                    if 'DATE' in key:
                        header[keyword_name] = (DEFAULT_TIME, comment)
                    else:
                        header[keyword_name] = (DEFAULT_STRING, comment)
                if keyword_type == 'int':
                    header[keyword_name] = (DEFAULT_INT, comment)
                if keyword_type == 'float':
                    header[keyword_name] = (DEFAULT_FLOAT, comment)
                if keyword_type == 'bool':
                    header[keyword_name] = (DEFAULT_BOOL, comment)

    header.update(inst_head)
    header.update(CAM_HEAD)

    header[S122['InstrumentProgramID']] = 'gen_fake_data'

def legacy_uniform_generator(rng, limits):
    # Needed after numpy changed how uniform() works in 1.21.0
    low = limits[0]
    high = limits[-1]
    scale = 1
    if low > high:
        low *= -1
        high *= -1
        scale *= -1

    return scale * rng.uniform(low, high)

#TODO: Move this to somewhere in the tests directory
def make_testing_data():
    from ViSP_Pipeline.utils.gen_fake_data import ViSPDataSet
    from dkist_processing_pac.data import load_visp_keywords

    outputdir = pkg_resources.resource_filename('dkist_processing_pac', 'tests/data')
    numsteps = 7
    shape = (3, 2, 1)
    for td in ['run1', 'run2', 'bad_inst', 'bad_date', 'bad_wave', 'bad_mod', 'bad_shape', 'DL', 'cryo', 'lowflux']:
        os.makedirs(outputdir + '/' + td, exist_ok=True)

    # One with fixed ret
    ####################
    ret0_h = np.pi / 2.
    dret_h = 0.5 / 15 * 60 * 24 * np.pi / 180
    ret0_45 = np.pi / 2.
    dret_45 = 0.5 / 15 * 60 * 24 * np.pi / 180
    ret0_r = np.pi / 2.
    dret_r = 0.5 / 15 * 60 * 24 * np.pi / 180

    theta_pol_steps = np.r_[np.array([0]), np.linspace(0, 360, numsteps - 2), np.array([0])]
    theta_ret_steps = np.ones(numsteps) * 25
    theta_ret_steps[::2] -= 2.5
    theta_ret_steps[1::2] += 2.5

    pol_in = np.ones(numsteps, dtype=bool)
    ret_in = np.ones(numsteps, dtype=bool)
    ret_in[-2] = False
    ret_in[2] = False
    dark_in = np.zeros(numsteps, dtype=bool)
    dark_in[-1] = True
    dark_in[0] = True

    pol_in = np.array(['Polarizer' if i else 'clear' for i in pol_in])
    ret_in = np.array(['SAR' if i else 'clear' for i in ret_in])
    dark_in = np.array(['DarkShutter' if i else "FieldStop (5arcmin)" for i in dark_in])

    gen_full_SoCC_run(outputdir + '/run1', ret0_h, dret_h, ret0_45, dret_45, ret0_r, dret_r,
                      theta_pol_steps, theta_ret_steps, pol_in, ret_in, dark_in,
                      nummod=10, shape=shape, spec_122=True, wave=620., start_time=57530., DHS=False, RN=9.)

    # DLNIRSP
    #########
    gen_full_SoCC_run(outputdir + '/DL', ret0_h, dret_h, ret0_45, dret_45, ret0_r, dret_r,
                      theta_pol_steps, theta_ret_steps, pol_in, ret_in, dark_in,
                      nummod=10, shape=shape, spec_122=True, wave=620., start_time=57530., DHS=False, RN=9.,
                      instrument='dlnirsp')

    # Cryo
    ######
    gen_full_SoCC_run(outputdir + '/cryo', ret0_h, dret_h, ret0_45, dret_45, ret0_r, dret_r,
                      theta_pol_steps, theta_ret_steps, pol_in, ret_in, dark_in,
                      nummod=10, shape=shape, spec_122=True, wave=620., start_time=57530., DHS=False, RN=9.,
                      instrument='cryo-sp')

    # No flux
    ######
    theta_pol_steps = np.r_[np.array([0]), np.linspace(0, 360, numsteps - 2), np.array([0])]
    theta_ret_steps = np.ones(numsteps) * 25
    theta_ret_steps[::2] -= 2.5
    theta_ret_steps[1::2] += 2.5

    pol_in = np.ones(numsteps, dtype=bool)
    ret_in = np.ones(numsteps, dtype=bool)
    ret_in[-2] = False
    ret_in[1] = False
    pol_in[-2] = False
    pol_in[1] = False
    dark_in = np.zeros(numsteps, dtype=bool)
    dark_in[-1] = True
    dark_in[0] = True

    pol_in = np.array(['Polarizer' if i else 'clear' for i in pol_in])
    ret_in = np.array(['SAR' if i else 'clear' for i in ret_in])
    dark_in = np.array(['DarkShutter' if i else "FieldStop (5arcmin)" for i in dark_in])

    gen_full_SoCC_run(outputdir + '/lowflux', ret0_h, dret_h, ret0_45, dret_45, ret0_r, dret_r,
                      theta_pol_steps, theta_ret_steps, pol_in, ret_in, dark_in,
                      nummod=10, shape=shape, spec_122=True, wave=620., start_time=57530., DHS=False, RN=9.,
                      I_sys=10, df=0)

    # One with fixed pol
    ####################
    ret0_h = np.pi / 2.
    dret_h = 0.5 / 15 * 60 * 24 * np.pi / 180
    ret0_45 = np.pi / 2.
    dret_45 = 0.5 / 15 * 60 * 24 * np.pi / 180
    ret0_r = np.pi / 2.
    dret_r = 0.5 / 15 * 60 * 24 * np.pi / 180

    theta_pol_steps = np.ones(numsteps) * 180
    theta_ret_steps = np.r_[np.array([0]), np.linspace(0, 360, numsteps - 2), np.array([0])]

    pol_in = np.ones(numsteps, dtype=bool)
    ret_in = np.ones(numsteps, dtype=bool)
    ret_in[-2] = False
    ret_in[2] = False
    dark_in = np.zeros(numsteps, dtype=bool)
    dark_in[-1] = True
    dark_in[0] = True

    pol_in = np.array(['Polarizer' if i else 'clear' for i in pol_in])
    ret_in = np.array(['SAR' if i else 'clear' for i in ret_in])
    dark_in = np.array(['DarkShutter' if i else "FieldStop (5arcmin)" for i in dark_in])

    gen_full_SoCC_run(outputdir + '/run2', ret0_h, dret_h, ret0_45, dret_45, ret0_r, dret_r,
                      theta_pol_steps, theta_ret_steps, pol_in, ret_in, dark_in,
                      nummod=10, shape=shape, spec_122=True, wave=620., start_time=57560., DHS=False, RN=13.)

    # One with the wrong shape
    ##########################
    gen_full_SoCC_run(outputdir + '/bad_shape', ret0_h, dret_h, ret0_45, dret_45, ret0_r, dret_r,
                      theta_pol_steps, theta_ret_steps, pol_in, ret_in, dark_in,
                      nummod=10, shape=(10,10), spec_122=True, wave=620., start_time=57560., DHS=False)

    # Data with inconsistent instrument headers
    ###########################################
    load_visp_keywords()
    VDS = ViSPDataSet('PolCal', 57530., 666, 10)
    VISP_HEAD = VDS.header()

    primary = pyfits.PrimaryHDU()
    primary.header.update(VISP_HEAD)
    primary.header[S122['Instrument']] = 'visp'
    primary.header[S122['ViSP_NumberOfModulatorStates']] = 10
    pyfits.HDUList([primary, pyfits.ImageHDU(np.ones((3, 2, 1)), header=primary.header)]).writeto(
            outputdir + '/bad_inst/VISP1.FITS', overwrite=True)

    primary = pyfits.PrimaryHDU()
    primary.header.update(VISP_HEAD)
    primary.header[S122['Instrument']] = 'not_visp'
    primary.header[S122['ViSP_NumberOfModulatorStates']] = 10
    pyfits.HDUList([primary, pyfits.ImageHDU(np.ones((3, 2, 1)), header=primary.header)]).writeto(
            outputdir + '/bad_inst/VISP2.FITS', overwrite=True)

    # Data with inconsistent date headers
    ###########################################
    primary = pyfits.PrimaryHDU()
    primary.header.update(VISP_HEAD)
    primary.header[S122['Instrument']] = 'visp'
    primary.header[S122['ViSP_NumberOfModulatorStates']] = 10
    pyfits.HDUList([primary, pyfits.ImageHDU(np.ones((3, 2, 1)), header=primary.header)]).writeto(
            outputdir + '/bad_date/VISP1.FITS', overwrite=True)

    primary = pyfits.PrimaryHDU()
    primary.header.update(VISP_HEAD)
    primary.header[S122['Instrument']] = 'visp'
    primary.header['DATE-BGN'] = 'Um, is this even a date?'
    primary.header[S122['ViSP_NumberOfModulatorStates']] = 10
    pyfits.HDUList([primary, pyfits.ImageHDU(np.ones((3, 2, 1)), header=primary.header)]).writeto(
            outputdir + '/bad_date/VISP2.FITS', overwrite=True)

    # Data with inconsistent wavelength headers
    ###########################################
    primary = pyfits.PrimaryHDU()
    primary.header.update(VISP_HEAD)
    primary.header[S122['Instrument']] = 'visp'
    primary.header[S122['ViSP_NumberOfModulatorStates']] = 10
    primary.header[S122['Wavelength']] = 620
    pyfits.HDUList([primary, pyfits.ImageHDU(np.ones((3, 2, 1)), header=primary.header)]).writeto(
            outputdir + '/bad_wave/VISP1.FITS', overwrite=True)

    primary = pyfits.PrimaryHDU()
    primary.header.update(VISP_HEAD)
    primary.header[S122['Instrument']] = 'visp'
    primary.header[S122['ViSP_NumberOfModulatorStates']] = 10
    primary.header[S122['Wavelength']] = 666
    pyfits.HDUList([primary, pyfits.ImageHDU(np.ones((3, 2, 1)), header=primary.header)]).writeto(
            outputdir + '/bad_wave/VISP2.FITS', overwrite=True)

    # Data with inconsistent modulator headers
    ###########################################
    primary = pyfits.PrimaryHDU()
    primary.header.update(VISP_HEAD)
    primary.header[S122['Instrument']] = 'visp'
    primary.header[S122['ViSP_NumberOfModulatorStates']] = 10
    pyfits.HDUList([primary, pyfits.ImageHDU(np.ones((3, 2, 1)), header=primary.header)]).writeto(
            outputdir + '/bad_mod/VISP1.FITS', overwrite=True)

    primary = pyfits.PrimaryHDU()
    primary.header.update(VISP_HEAD)
    primary.header[S122['Instrument']] = 'visp'
    primary.header[S122['ViSP_NumberOfModulatorStates']] = 8
    pyfits.HDUList([primary, pyfits.ImageHDU(np.ones((3, 2, 1)), header=primary.header)]).writeto(
            outputdir + '/bad_mod/VISP2.FITS', overwrite=True)


def command_line():
    import argparse

    parser = argparse.ArgumentParser(description='Generate a SoCC that can be used for science data reduction')
    parser.add_argument('output_dir', help='Location to save the data', nargs=1)
    parser.add_argument('-C', '--CS-name', help='Name of pre-defined default Calibration Sequence to use')
    parser.add_argument('-I', '--instrument', help='The instrument to generate PolCal for',
                        choices=['visp', 'dlnirsp', 'cryo-sp', 'cryo-ci', 'vtf'], default='visp')
    parser.add_argument('-m', '--mask', help='File defining non-data pixels. Needed if instrument is "dlnirsp"')
    parser.add_argument('-p', '--fixed-pol',
                        help='Use a CS with a fixed polarizer. The default is to use a fixed retarder',
                        action='store_true')
    parser.add_argument('-N', '--SNR', help='Signal to Noise of data frames (0 = no noise)',
                        nargs=1, default=[0], type=float)
    parser.add_argument('-R', '--read-noise', help='Read noise (0 = no noise)', default=0, type=float)
    parser.add_argument('-M', '--mueller-noise',
                        help='Fractional amount of uniform noise to perturb telescope and CU Mueller matrices (0 - 1)',
                        nargs=1, default=[0], type=float)
    parser.add_argument('-D', '--two-d', help='Make 2D DHS data', action='store_true')
    parser.add_argument('--no-dhs', help='Make CS for direct input to PA&C Modules', action='store_false')

    args = parser.parse_args()

    O540_modmat = np.array([[1, -0.85243,  0.18135, -0.49039],
                            [1, -0.04202, -0.59912, -0.79956],
                            [1,  0.73844,  0.21129, -0.64036],
                            [1, -0.07196,  0.99175, -0.10604],
                            [1, -0.85243,  0.18135,  0.49039],
                            [1, -0.04202, -0.59912,  0.79956],
                            [1,  0.73844,  0.21129,  0.64036],
                            [1, -0.07196,  0.99175,  0.10604]], dtype=np.float32)

    dark_signal = 0
    if args.instrument == 'visp':
        shape = (1, 2160, 2560)
        mask = None
        modmat = None
        nummod = 10
        wave = 588.
        suffix = 'FITS'
        start_time=57531.
        dark_signal = (94., 3.)
    elif args.instrument == 'dlnirsp':
        try:
            mask = pyfits.open(args.mask)[0].data.astype(bool)
        except:
            raise ValueError('Could not load data mask. Make sure you specified a good mask with "-m"')
        nummod = 8
        modmat = O540_modmat
        wave = 633.
        shape = mask.shape
        suffix = 'FITS'
        start_time = 57531.
        dark_signal = (628., 25)
    elif args.instrument == 'cryo-sp':
        shape = (1, 2048, 2048)
        mask = None
        modmat = O540_modmat
        nummod = 8
        wave = 1080.
        suffix = 'FITS'
        start_time=57529.
    elif args.instrument == 'cryo-ci':
        shape = (1, 2048, 2048)
        mask = None
        modmat = O540_modmat
        nummod = 8
        wave = 1080.
        suffix = 'FITS'
        start_time = 57528.
        dark_signal = (3000., 200.)
    elif args.instrument == 'vtf':
        shape = (1, 2048, 2048)
        mask = None
        sqrt3 = 1 / np.sqrt(3)
        modmat = np.array([[ 1.,  sqrt3,  sqrt3,  sqrt3],
                           [ 1.,  sqrt3, -sqrt3, -sqrt3],
                           [ 1., -sqrt3, -sqrt3,  sqrt3],
                           [ 1., -sqrt3,  sqrt3, -sqrt3]], dtype=np.float64)
        nummod = 4
        wave = 633.
        suffix = 'FITS'
        start_time=57527.

    if args.two_d:
        if len(shape) == 3 and shape[0] == 1:
            shape = shape[1:]
        else:
            raise ValueError('OG shape {} is wrong. Weird'.format(shape))
        if args.instrument == 'dlnirsp':
            mask = mask[0, :, :]

    if not args.no_dhs:
        shape = (1, 1, 1)
        mask = None

    output_dir = args.output_dir[0]
    os.makedirs(output_dir, exist_ok=True)
    SoCC_multi_day(output_dir, numdays=1, DHS=args.no_dhs, spec_122=True, rand_TM=False, only_pol=args.fixed_pol, CS_name=args.CS_name,
                   only_ret=True, shape=shape, SNR=args.SNR[0], I_sys=40000, df=-200, nondata_mask=mask, nummod=nummod,
                   muellernoise=args.mueller_noise[0], instrument=args.instrument, wave=wave, dark_signal=dark_signal,
                   modmat=modmat, RN=args.read_noise, suffix=suffix, start_time=start_time)

    os.system('mv {0}/day0/* {0}'.format(output_dir))
    os.removedirs('{}/day0'.format(output_dir))

    print(
        'All done! Add EXACTLY the following lines to the [PolarimetricCalibration] section of your {} config '
        'file:\n'.format(args.instrument))
    print("raw_pol_dir = {}".format(os.path.abspath(output_dir)))


if __name__ == '__main__':
    command_line()
