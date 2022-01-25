# /*##########################################################################
# Copyright (C) 2016-2017 European Synchrotron Radiation Facility
#
# This file is part of the PyMca X-ray Fluorescence Toolkit developed at
# the ESRF by the Software group.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#############################################################################*/
"""convert from NXTomo to hdf5 compliant for pyhst"""

__author__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "01/04/2020"


import h5py
from collections import namedtuple
import os
import silx.io.utils
from tomwer.core.scan.hdf5scan import HDF5TomoScan
from tomwer.core.process.reconstruction.darkref.darkrefs import DarkRefs
from tomoscan.io import HDF5File


_pyhst_hdf5_info = namedtuple("_pyhst_hdf5_info", ["dark", "flats", "projections"])


_pyhst_hdf5_dark = namedtuple("_pyhst_hdf5_dark", ["file", "dataset_path"])

_pyhst_hdf5_flats = namedtuple(
    "_pyhst_hdf5_flats", ["files", "dataset_path", "intervals"]
)

_pyhst_hdf5_projections = namedtuple(
    "_pyhst_hdf5_projections", ["file", "dataset_path"]
)


def _create_file_with_virtual_dataset(
    vsource, pro_indxs, datasource_shape, mydtype, filename
):
    layout = h5py.VirtualLayout(
        shape=tuple([len(pro_indxs)] + list(datasource_shape)[1:]), dtype=mydtype
    )
    for n in range(len(pro_indxs)):
        layout[n] = vsource[pro_indxs[n]]
    with HDF5File(filename, "w") as f:
        f.create_virtual_dataset("data", layout=layout, fillvalue=-5)


def _copy_dataset(data, output_file):
    with HDF5File(output_file, "w") as f:
        f.create_dataset(name="data", data=data)


def convert_nx_to_pyhst_hdf5(scan: HDF5TomoScan) -> tuple:
    """
    Convert an HDF5TomoScan (NXTomo compliant) to 3 HDF5 compliant with pyhst:
    one for dark, one for flats and one for projections

    :param HDF5TomoScan scan: scan to convert
    :return: _pyhst_hdf5_info
            note: we create one file per flat.
    :rtype: tuple
    """
    assert isinstance(scan, HDF5TomoScan)
    output_dir = scan.path
    input_master_file = scan.master_file
    entry_name = scan.entry

    entry = HDF5File(input_master_file, "r", swmr=True)[entry_name]

    pro_indxs = []
    ff_indxs = []
    ff_poss = []
    bck_indxs = []

    keys = entry["instrument/detector"]["image_key"]

    old_ff_pos = -1
    ffblock = None
    ipro = 0
    for i, k in enumerate(list(keys)):
        if k == 2:
            bck_indxs.append(i)
        if k == 0:
            pro_indxs.append(i)
            ipro += 1
        if k == 1:
            if ipro == old_ff_pos:
                ffblock.append(i)
            else:
                ffblock = []
                ff_indxs.append(ffblock)
                ff_poss.append(ipro)
                old_ff_pos = ipro

    datasource_shape = entry["instrument/detector/data"].shape
    mydtype = entry["instrument/detector/data"].dtype

    vsource = h5py.VirtualSource(
        input_master_file,
        entry_name + "/instrument/detector/data",
        shape=datasource_shape,
    )

    # manage projections
    file_basename = ".".join(os.path.splitext(os.path.basename(scan.master_file))[:-1])
    proj_filename = "pyhst2_projs_{entry}_{basename}.h5".format(
        entry=str(scan.entry), basename=file_basename
    )
    proj_filename = os.path.join(output_dir, proj_filename)
    _create_file_with_virtual_dataset(
        vsource, pro_indxs, datasource_shape, mydtype, proj_filename
    )
    proj_ds_name = '"data"'

    projections_info = _pyhst_hdf5_projections(proj_filename, proj_ds_name)

    # manage dark
    def get_dark():
        if not os.path.exists(scan.process_file):
            return {}

        return DarkRefs.get_darks_frm_process_file(
            process_file=scan.process_file, entry=scan.entry, as_url=True
        )

    dark_url = get_dark()
    if len(dark_url) > 0:
        url = dark_url[list(dark_url.keys())[0]]
        dark_filename = "pyhst2_dark_{entry}_{basename}.h5".format(
            entry=str(scan.entry), basename=file_basename
        )
        dark_filename = os.path.join(output_dir, dark_filename)
        _copy_dataset(data=silx.io.utils.get_data(url), output_file=dark_filename)

        dark_ds_name = '"data"'
        dark_info = _pyhst_hdf5_dark(dark_filename, dark_ds_name)
    else:
        dark_info = None

    def get_flats():
        if not os.path.exists(scan.process_file):
            return {}

        return DarkRefs.get_flats_frm_process_file(
            process_file=scan.process_file, entry=scan.entry, as_url=True
        )

    # manage flats
    def adapt_flat_index_to_pyhst(urls):
        """as this is an hdf5 acquisition we now have the index of the
        acquisition but in a different referential."""
        assert len(urls) > 0
        res = {}
        if 0 in urls:
            res[0] = urls[0]
        elif 1 in urls:
            res[0] = urls[1]
        if len(urls) > 1:
            keys = list(urls.keys())
            # now consider the first projection to be 0
            last_index = keys[1] - list(scan.projections.keys())[0]
            res[last_index] = urls[keys[-1]]
        return res

    flats_url = get_flats()
    if len(flats_url):
        flats_url = adapt_flat_index_to_pyhst(flats_url)

        flats_files = []
        flats_intervals = []
        for flat_index, url in flats_url.items():
            flats_intervals.append(flat_index)
            fname = "pyhst2_flat_{:04d}_{entry}_{basename}.h5".format(
                flat_index, entry=str(scan.entry), basename=file_basename
            )
            fname = os.path.join(output_dir, fname)
            flats_files.append(fname)
            flat_data = silx.io.utils.get_data(url)
            if flat_data.ndim == 2:
                flat_data = flat_data.reshape(1, flat_data.shape[0], flat_data.shape[1])
            _copy_dataset(data=flat_data, output_file=fname)
        flats_ds_name = '"data"'
        flats_info = _pyhst_hdf5_flats(flats_files, flats_ds_name, flats_intervals)
    else:
        flats_info = None
    return _pyhst_hdf5_info(
        dark=dark_info, flats=flats_info, projections=projections_info
    )
