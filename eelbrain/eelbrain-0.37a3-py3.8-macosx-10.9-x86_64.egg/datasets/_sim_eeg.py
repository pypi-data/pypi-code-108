# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"""Simulate EEG data"""
import numpy as np
import scipy.signal
import scipy.spatial

from .._data_obj import Dataset, Factor, Var, NDVar, Sensor, UTS
from .._ndvar import gaussian, powerlaw_noise
from .. import _info


def _topo(sensor, center, falloff=1):
    i = sensor.names.index(center)
    loc = sensor.locs[i]
    dists = scipy.spatial.distance.cdist([loc], sensor.locs)[0]
    radius = sensor._sphere_fit[1].mean()
    dists /= radius
    topo = 1.0 - dists
    # topo **= falloff
    return NDVar(topo, (sensor,))


def simulate_erp(
        n_trials: int = 80,
        seed: int = 0,
        snr: float = 0.2,
) -> Dataset:
    """Simulate event-related EEG data

    Parameters
    ----------
    n_trials
        Number of trials (default 100).
    seed
        Random seed.
    snr
        Signal-to-noise ratio.

    Examples
    --------
    Compare with kiloword::

        ys = datasets.simulate_erp()['eeg']
        ys -= ys.mean(sensor=['M1', 'M2'])
        import mne
        path = mne.datasets.kiloword.data_path()
        y = load.fiff.epochs_ndvar(path + '/kword_metadata-epo.fif')
        plot.TopoButterfly([y, ys])

    """
    assert n_trials % 2 == 0

    sensor = Sensor.from_montage('standard_alphabetic')
    sensor.set_connectivity(connect_dist=1.66)
    time = UTS(-0.100, 0.005, 140)

    # Generate random values for the independent variable (cloze probability)
    rng = np.random.RandomState(seed)
    cloze_x = np.concatenate([
        rng.uniform(0, 0.3, n_trials // 2),
        rng.uniform(0.8, 1.0, n_trials // 2),
    ])
    rng.shuffle(cloze_x)
    cloze = Var(cloze_x)
    # Word complexity (number of characters)
    n_chars = Var(np.round(rng.normal(4, 1.5, n_trials)).astype(int))

    # Generate topography
    n400_topo = -2.0 * _topo(sensor, 'Cz')
    # Generate timing
    n400_timecourse = gaussian(0.400, 0.034, time)
    # Put all the dimensions together to simulate the EEG signal
    signal = (1 - cloze) * n400_timecourse * n400_topo

    # add early responses:
    # 130 ms
    tc = gaussian(0.130, 0.025, time)
    topo = _topo(sensor, 'O1') + _topo(sensor, 'O2') - 0.5 * _topo(sensor, 'Cz')
    signal += n_chars * 0.5 * tc * topo
    # 195 ms
    amp = Var(rng.normal(0.8, 1, n_trials))
    tc = gaussian(0.195, 0.015, time)
    topo = 1.2 * _topo(sensor, 'F3') + _topo(sensor, 'F4')
    signal += amp * tc * topo
    # 270
    amp = Var(rng.normal(1., 1, n_trials))
    tc = gaussian(0.270, 0.050, time)
    topo = _topo(sensor, 'O1') + _topo(sensor, 'O2')
    signal += amp * tc * topo
    # 280
    amp = Var(rng.normal(-1, 1, n_trials))
    tc = gaussian(0.280, 0.030, time)
    topo = _topo(sensor, 'Pz')
    signal += amp * tc * topo
    # 600
    amp = Var(rng.normal(0.5, 1, n_trials))
    tc = gaussian(0.590, 0.100, time)
    topo = -_topo(sensor, 'Fz')
    signal += amp * tc * topo

    # Add noise
    noise = powerlaw_noise(signal, 1, rng)
    noise = noise.smooth('sensor', 0.02, 'gaussian')
    noise *= (signal.std() / noise.std() / snr)
    signal += noise

    # Data scale
    signal *= 1e-6
    signal.info = _info.for_eeg()

    # Store EEG data in a Dataset with trial information
    ds = Dataset()
    ds['eeg'] = signal
    ds['cloze'] = Var(cloze_x)
    ds['cloze_cat'] = Factor(cloze_x > 0.5, labels={True: 'high', False: 'low'})
    ds['n_chars'] = Var(n_chars)
    return ds
