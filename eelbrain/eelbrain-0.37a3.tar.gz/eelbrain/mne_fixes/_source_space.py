from functools import reduce

from mne import SourceSpaces
import numpy as np

from .._data_obj import VolumeSourceSpace, _point_graph
from .._types import PathArg


def merge_volume_source_space(sss, name='Volume'):
    """Merge multiple volume source spaces into one

    Notes
    -----
    Only intended to work properly if ``sss`` is the output of a single
    :func:`mne.setup_volume_source_space` call.
    """
    if len(sss) <= 1:
        return sss
    assert all(ss['type'] == 'vol' for ss in sss)
    ss = sss[0].copy()
    ss['vertno'] = np.unique(np.concatenate([ss['vertno'] for ss in sss]))
    ss['inuse'] = reduce(np.logical_or, (ss['inuse'] for ss in sss))
    ss['nuse'] = ss['inuse'].sum()
    ss['seg_name'] = str(name)
    del ss['neighbor_vert']
    return SourceSpaces([ss], sss.info)


def prune_volume_source_space(
        sss: SourceSpaces,
        grade: int,
        min_neighbors: int = 1,  # remove voxels with fewer neighbors
        mirror: bool = True,  # make source space symmetric
        remove_midline: bool = False,  # remove voxels along the midline
        fill_holes: int = 0,  # fill holes bordered by n voxels
):
    """Remove sources that have ``n`` or fewer neighboring sources"""
    assert len(sss) == 1
    # make copy
    ss = sss[0].copy()
    ss['inuse'] = ss['inuse'].copy()
    assert ss['type'] == 'vol'
    if 'neighbor_vert' in ss:
        del ss['neighbor_vert']
    # coordinates in mm
    rr_mm = np.round(ss['rr'] * 1000).astype(int)
    rr_vertno = {coord: v for v, coord in enumerate(map(tuple, rr_mm))}
    # remove midline
    if remove_midline:
        rm = ss['rr'][ss['vertno']][:, 0] == 0
        ss['inuse'][ss['vertno'][rm]] = 0
        ss['vertno'] = ss['vertno'][~rm]
    # make symmetric
    if mirror:
        vertex_list = list(ss['vertno'])
        for v in ss['vertno']:
            r, a, s = rr_mm[v]
            v_mirror = rr_vertno[-r, a, s]
            if v_mirror not in vertex_list:
                vertex_list.append(v_mirror)
        vertex_list.sort()
        ss['vertno'] = np.array(vertex_list, dtype=ss['vertno'].dtype)
        ss['inuse'][ss['vertno']] = True
    # fill in holes
    if fill_holes:
        assert 6 >= fill_holes >= 3
        max_coord = rr_mm.max(0)
        min_coord = rr_mm.min(0)
        while True:
            add = np.zeros(ss['np'], bool)
            for i in range(ss['np']):
                if ss['inuse'][i]:
                    continue
                ras = rr_mm[i]
                n_neighbors = 0
                for j in range(3):
                    index = list(ras)
                    # up
                    if ras[j] < max_coord[j]:
                        index[j] = ras[j] + grade
                        n_neighbors += rr_vertno[tuple(index)] in ss['vertno']
                    # down
                    if ras[j] > min_coord[j]:
                        index[j] = ras[j] - grade
                        n_neighbors += rr_vertno[tuple(index)] in ss['vertno']
                    # move on if done
                    if n_neighbors >= fill_holes:
                        add[i] = True
                        break
            if not np.any(add):
                break
            ss['inuse'][add] = True
            ss['vertno'] = np.flatnonzero(ss['inuse'])
        ss['nuse'] = len(ss['vertno'])
    # remove points with few neighbors
    if min_neighbors > 1:
        while True:
            neighbors = _point_graph(rr_mm[ss['vertno']], grade * 1.1)
            unique, counts = np.unique(neighbors, return_counts=True)
            keep = unique[counts >= min_neighbors]
            if len(keep) == ss['nuse']:
                break
            ss['vertno'] = ss['vertno'][keep]
            ss['nuse'] = len(ss['vertno'])
            break
        ss['inuse'] = np.in1d(np.arange(ss['np']), ss['vertno'])
    # check result
    assert ss['inuse'].sum() == ss['nuse']
    assert np.all(np.flatnonzero(ss['inuse']) == ss['vertno'])
    return SourceSpaces([ss], sss.info)


def restrict_volume_source_space(
        sss: SourceSpaces,
        grade: int,
        subjects_dir: PathArg,
        subject: str,
        parc: str = 'aseg',  # parcellation with labels
        label: str = '*Cortex',  # pattern for selecting labels
        grow: int = 0,  # grow index after selection
):
    assert len(sss) == 1
    # make copy
    ss = sss[0].copy()
    assert ss['type'] == 'vol'
    if 'neighbor_vert' in ss:
        del ss['neighbor_vert']
    # parcellation
    parc = VolumeSourceSpace._read_volume_parc(subjects_dir, subject, parc, ss['rr'][ss['vertno']])
    index = parc.matches(label)
    neighbors = _point_graph(ss['rr'][ss['vertno']], grade * 0.0011)
    neighbors = np.vstack((neighbors, neighbors[:, [1, 0]]))
    for _ in range(grow):
        for i in np.flatnonzero(index):
            index[neighbors[neighbors[:, 0] == i, 1]] = True
    # update ss
    ss['vertno'] = ss['vertno'][index]
    ss['inuse'] = np.in1d(np.arange(ss['np']), ss['vertno'])
    ss['nuse'] = len(ss['vertno'])
    return SourceSpaces([ss], sss.info)
