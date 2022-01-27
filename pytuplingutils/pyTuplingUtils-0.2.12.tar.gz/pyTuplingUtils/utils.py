#!/usr/bin/env python3
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Thu Jul 29, 2021 at 02:36 AM +0200

import numpy as np

from .io import read_branches


# Find total number of events (unique events) out of total number of candidates.
def extract_uid(ntp, tree, run_branch='runNumber', event_branch='eventNumber',
                conditional=None, run_array=None, event_array=None):
    if run_array is None or event_array is None:
        run, event = read_branches(ntp, tree, (run_branch, event_branch))
    else:
        run, event = run_array, event_array

    if conditional is not None:
        run = run[conditional]
        event = event[conditional]

    run = np.char.mod('%d', run)
    event = np.char.mod('%d', event)

    run = np.char.add(run, '-')
    ids = np.char.add(run, event)

    uid, idx, count = np.unique(ids, return_index=True, return_counts=True)

    num_of_evt = ids.size
    num_of_ids = uid.size
    num_of_dupl_ids = uid[count > 1].size
    # num_of_evt_w_dupl_id = np.sum(count[count > 1]) - num_of_dupl_ids
    num_of_evt_w_dupl_id = num_of_evt - num_of_ids

    return uid, idx, num_of_evt, num_of_ids, \
        num_of_dupl_ids, num_of_evt_w_dupl_id


def find_common_uid(ntp1, ntp2, tree1, tree2, **kwargs):
    uid1, idx1 = extract_uid(ntp1, tree1, **kwargs)[0:2]
    uid2, idx2 = extract_uid(ntp2, tree2, **kwargs)[0:2]
    uid_comm, uid_comm_idx1, uid_comm_idx2 = np.intersect1d(
        uid1, uid2, assume_unique=True, return_indices=True)

    return uid_comm, idx1[uid_comm_idx1], idx2[uid_comm_idx2]


def gen_histo(array, bins=200, scale=1.05, data_range=None, **kwargs):
    if data_range is None:
        data_min = array.min()
        data_max = array.max()

        data_min = data_min*scale if data_min < 0 else data_min/scale
        data_max = data_max/scale if data_max < 0 else data_max*scale

        return np.histogram(array, bins, (data_min, data_max), **kwargs)

    return np.histogram(array, bins, data_range, **kwargs)
