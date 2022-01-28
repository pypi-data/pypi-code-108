# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"""Continuous neural data (CND) format used for mTRF-Toolbox"""
from pathlib import Path
from typing import Optional, Sequence, Union

import mne
from mne.externals.pymatreader import read_mat
import numpy

from .._data_obj import Dataset, Factor, NDVar, Scalar, Sensor, UTS, Var, combine, _matrix_graph
from .._io.fiff import mne_neighbor_files
from .._types import PathArg
from .._utils import ui


FILETYPES = [("CND files", "*.mat")]


def read_cnd(
        filename: PathArg = None,
        connectivity: Union[str, Sequence, float] = None,
) -> Optional[Dataset]:
    """Load continuous neural data (CND) file used in the mTRF-Toolbox

    Parameters
    ----------
    filename
        Path to the data file (``*.mat``). If unspecified, open a file dialog.
    connectivity
        Sensor adjacency graph for EEG sensors.
        By default, the function tries to use the ``deviceName`` entry and falls
        back on distance-based connectivity for unkown devices.
        Can be explicitly specified as a `FieldTrip neighbor file
        <https://www.fieldtriptoolbox.org/template/neighbours/>`_ (e.g., ``'biosemi64'``;
        Use a :class:`float` for distance-based connectivity (see :meth:`Sensor.set_connectivity`).
        For more options see :class:`Sensor`.

    Notes
    -----
    This format is experimental and the returned data format might change in the future;
    Please report any problems you might encounter.
    """
    if filename is None:
        path = ui.ask_file("Load CND File", "Select CND file to load as NDVar", FILETYPES)
        if not path:
            return
    else:
        path = Path(filename)
        if not path.suffix and not path.exists():
            path = path.with_suffix('.mat')
    data = read_mat(path)
    if 'eeg' in data:
        data_type = data['eeg']['dataType']
        # EEG sensor properties
        dist_connectivity = None
        sysname = data['eeg']['deviceName']
        ch_names = data['eeg']['chanlocs']['labels']
        # connectivity default
        if connectivity is None:
            available = mne_neighbor_files()
            if sysname in available:
                connectivity = sysname
            else:
                connectivity = 1.6
        # find connectivity
        if isinstance(connectivity, float):
            dist_connectivity = connectivity
            connectivity = 'none'
        elif connectivity is False:
            connectivity = 'none'
        elif isinstance(connectivity, str) and connectivity not in ('grid', 'none'):
            adj_matrix, adj_names = mne.channels.read_ch_adjacency(connectivity)
            # fix channel order
            if adj_names != ch_names:
                index = numpy.array([adj_names.index(name) for name in ch_names])
                adj_matrix = adj_matrix[index][:, index]
            connectivity = _matrix_graph(adj_matrix)
        locs = numpy.vstack([
            -numpy.array(data['eeg']['chanlocs']['Y']),
            data['eeg']['chanlocs']['X'],
            data['eeg']['chanlocs']['Z'],
        ]).T
        sensor = Sensor(locs, ch_names, sysname, connectivity=connectivity)
        if dist_connectivity:
            sensor.set_connectivity(connect_dist=dist_connectivity)
        # EEG data
        tstep = 1 / data['eeg']['fs']
        eeg = []
        for trial_data in data['eeg']['data']:
            uts = UTS(0, tstep, trial_data.shape[0])
            eeg.append(NDVar(trial_data, (uts, sensor), 'eeg'))
        # Trial position
        ds = Dataset({
            data_type.lower(): combine(eeg, to_list=True),
            'origTrialPosition': Var(data['eeg']['origTrialPosition'] - 1),
        })
        # Extra channels
        if 'extChan' in data['eeg']:
            desc = ds.info['extChan'] = data['eeg']['extChan']['description']
            extra_data = []
            for trial_data in data['eeg']['data']:
                uts = UTS(0, tstep, trial_data.shape[0])
                channel = Scalar('channel', range(trial_data.shape[1]))
                extra_data.append(NDVar(trial_data, (uts, channel), desc))
            ds['extChan'] = extra_data
        if 'reRef' in data['eeg']:
            ds.info['reRef'] = data['eeg']['reRef']
        return ds
    if 'stim' in data:
        ds = Dataset({'stimIdxs': Var(data['stim']['stimIdxs'] - 1)})
        # stim.data has size nStim x nRuns.
        tstep = 1 / data['stim']['fs']
        stim_names = data['stim']['names']
        for name, stim_data in zip(stim_names, data['stim']['data']):
            stim_ndvars = []
            for run_data in stim_data:
                uts = UTS(0, tstep, len(run_data))
                stim_ndvars.append(NDVar(run_data, uts, name))
            key = Dataset.as_key(name)
            ds[key] = combine(stim_ndvars, to_list=True)
        # Condition labels
        if 'condIdxs' in data['stim']:
            ds['condIdxs'] = Var(data['stim']['condIdxs'] - 1)
            labels = dict(enumerate(data['stim']['condNames'], 1))
            ds['condition'] = Factor(data['stim']['condIdxs'], labels=labels)
        return ds
    raise IOError("File contains neither 'eeg' or 'stim' entry")
