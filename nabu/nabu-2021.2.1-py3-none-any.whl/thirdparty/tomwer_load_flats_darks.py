"""
script embedding all function needed to read flats and darks.

For information calculation method is stored in the results/configuration
dictionary
"""


"""
IMPORTANT: this script is used as long as flat-fielding with "raw" flats/daks
is not implemented in nabu.
For now we load results from tomwer.
"""

import typing
import h5py
from silx.io.url import DataUrl
from tomoscan.io import HDF5File
from silx.io.utils import h5py_read_dataset
import logging

MAX_DEPTH = 2

logger = logging.getLogger(__name__)

def get_process_entries(root_node: h5py.Group, depth: int) -> tuple:
    """
    return the list of 'Nxtomo' entries at the root level

    :param str file_path:
    :return: list of valid Nxtomo node (ordered alphabetically)
    :rtype: tuple

    ..note: entries are sorted to insure consistency
    """
    def _get_entries(node, depth_):
        if isinstance(node, h5py.Dataset):
            return {}
        res_buf = {}
        if is_process_node(node) is True:
            res_buf[node.name] = int(node['sequence_index'][()])
        assert isinstance(node, h5py.Group)
        if depth_ >= 1:
            for sub_node in node.values():
                res_buf[node.name] = _get_entries(node=sub_node, depth_=depth_-1)
        return res_buf

    res = {}
    for node in root_node.values():
        res.update(_get_entries(node=node, depth_=depth-1))

    return res


def is_process_node(node):
    return (node.name.split('/')[-1].startswith('tomwer_process_') and
            'NX_class' in node.attrs and
            node.attrs['NX_class'] == "NXprocess" and
            'program' in node and
            h5py_read_dataset(node['program']) == 'tomwer_dark_refs' and
            'version' in node and
            'sequence_index' in node)


def get_darks_frm_process_file(process_file, entry) -> typing.Union[None, dict]:
    """

    :param process_file:
    :return:
    """
    if entry is None:
        with HDF5File(process_file, 'r', swmr=True) as h5f:
            entries = get_process_entries(root_node=h5f, depth=MAX_DEPTH)
            if len(entries) == 0:
                logger.info(
                    'unable to find a DarkRef process in %s' % process_file)
                return None
            elif len(entries) > 0:
                raise ValueError('several entry found, entry should be '
                                 'specify')
            else:
                entry = list(entries.keys())[0]
                logger.info('take %s as default entry' % entry)

    with HDF5File(process_file, 'r', swmr=True) as h5f:
        dark_nodes = get_process_entries(root_node=h5f[entry],
                                          depth=MAX_DEPTH-1)
        index_to_path = {}
        for key, value in dark_nodes.items():
            index_to_path[key] = key

        if len(dark_nodes) == 0:
            return {}
        # take the last processed dark ref
        last_process_index = sorted(dark_nodes.keys())[-1]
        last_process_dark = index_to_path[last_process_index]
        if(len(index_to_path)) > 1:
            logger.warning('several processing found for dark-ref,'
                           'take the last one: %s' % last_process_dark)

        res = {}
        if 'results' in h5f[last_process_dark].keys():
            results_node = h5f[last_process_dark]['results']
            if 'darks' in results_node.keys():
                darks = results_node['darks']
                for index in darks:
                    res[int(index)] = DataUrl(
                        file_path=process_file,
                        data_path=darks[index].name,
                        scheme="silx"
                    )
        return res


def get_flats_frm_process_file(process_file, entry) -> typing.Union[None, dict]:
    """

    :param process_file:
    :return:
    """
    if entry is None:
        with HDF5File(process_file, 'r', swmr=True) as h5f:
            entries = get_process_entries(root_node=h5f, depth=MAX_DEPTH)
            if len(entries) == 0:
                logger.info(
                    'unable to find a DarkRef process in %s' % process_file)
                return None
            elif len(entries) > 0:
                raise ValueError('several entry found, entry should be '
                                 'specify')
            else:
                entry = list(entries.keys())[0]
                logger.info('take %s as default entry' % entry)

    with HDF5File(process_file, 'r', swmr=True) as h5f:
        dkref_nodes = get_process_entries(root_node=h5f[entry],
                                          depth=MAX_DEPTH-1)
        if len(dkref_nodes) == 0:
            return {}
        index_to_path = {}
        for key, value in dkref_nodes.items():
            index_to_path[key] = key

        # take the last processed dark ref
        last_process_index = sorted(dkref_nodes.keys())[-1]
        last_process_dkrf = index_to_path[last_process_index]
        if(len(index_to_path)) > 1:
            logger.warning('several processing found for dark-ref,'
                           'take the last one: %s' % last_process_dkrf)

        res = {}
        if 'results' in h5f[last_process_dkrf].keys():
            results_node = h5f[last_process_dkrf]['results']
            if 'flats' in results_node.keys():
                flats = results_node['flats']
                for index in flats:
                    res[int(index)] = DataUrl(
                        file_path=process_file,
                        data_path=flats[index].name,
                        scheme="silx"
                    )
        return res
