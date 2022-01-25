# coding: utf-8
# /*##########################################################################
# Copyright (C) 2016 European Synchrotron Radiation Facility
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


__authors__ = ["H.Payno"]
__license__ = "MIT"
__date__ = "09/08/2018"


import os
import h5py

try:
    # new settings names
    from nxtomomill.settings import Tomo

    H5_INIT_TITLES = Tomo.H5.INIT_TITLES
    from nxtomomill.settings import Tomo

    H5_ZSERIE_INIT_TITLES = Tomo.H5.ZSERIE_INIT_TITLES
except ImportError:
    # old settings names
    from nxtomomill.settings import H5_INIT_TITLES
    from nxtomomill.settings import H5_ZSERIE_INIT_TITLES
from silx.io.utils import h5py_read_dataset
import logging
from tomoscan.io import HDF5File


_logger = logging.getLogger(__name__)


class BlissScan:
    """Simple class to define a Bliss sequence aka as Bliss scan inside tomwer.

    :warning: BlissScan is not compatible with tomwer treatment. This is
    why it does not inherit from TomwerScanBase. This is a utility class.
    """

    _TYPE = "bliss_hdf5"

    def __init__(
        self, master_file, entry, proposal_file, scan_numbers=None, saving_file=None
    ):
        self._master_file = master_file
        if isinstance(entry, str) and not entry.startswith("/"):
            self._entry = "/" + entry
        else:
            self._entry = entry
        self._proposal_file = proposal_file
        self._scan_numbers = scan_numbers or []
        self._saving_file = saving_file
        self._tomo_n = None
        self._n_acquired = None
        self._dir_path = os.path.dirname(self.master_file)

    @property
    def tomo_n(self):
        """total number of projections"""
        return self._tomo_n

    @property
    def proposal_file(self):
        return self._proposal_file

    @property
    def saving_file(self):
        return self._saving_file

    @tomo_n.setter
    def tomo_n(self, n):
        self._tomo_n = n

    @property
    def n_acquired(self):
        """
        number of frame acquired until now. Does not take into account
        dark, flats or alignment"""
        return self._n_acquired

    @n_acquired.setter
    def n_acquired(self, n):
        self._n_acquired = n

    @property
    def master_file(self):
        return self._master_file

    @property
    def entry(self):
        return self._entry

    @property
    def path(self):
        return self._dir_path

    @property
    def scan_numbers(self):
        return self._scan_numbers

    def add_scan_number(self, scan_number):
        self._scan_numbers.append(scan_number)

    def __str__(self):
        return self.get_id_name(master_file=self.master_file, entry=self.entry)

    @staticmethod
    def get_id_name(master_file, entry):
        return "@".join((str(entry), master_file))

    def _deduce_transfert_scan(self, output_dir):
        new_master_file = os.path.join(output_dir, os.path.basename(self.master_file))
        return BlissScan(master_file=new_master_file, entry=self.entry)

    @staticmethod
    def is_bliss_file(file_path):
        return len(BlissScan.get_valid_entries(file_path)) > 0

    @staticmethod
    def is_bliss_valid_entry(file_path: str, entry: str):
        def is_standard_tomo(current_title: str):
            for title in H5_INIT_TITLES:
                if current_title.startswith(title):
                    return True
            return False

        def is_zseries_tomo(current_title: str):
            for title in H5_ZSERIE_INIT_TITLES:
                if current_title.startswith(title):
                    return True
            return False

        with HDF5File(file_path, mode="r", swmr=True) as h5s:
            if not isinstance(h5s, h5py.Group) or not isinstance(
                h5s[entry], h5py.Group
            ):
                return False
            if "title" in h5s[entry]:
                title = h5py_read_dataset(h5s[entry]["title"])
                try:
                    return is_standard_tomo(title) or is_zseries_tomo(title)
                except Exception:
                    pass
            return False

    @staticmethod
    def get_valid_entries(file_path) -> tuple:
        if not h5py.is_hdf5(file_path):
            _logger.warning("Provided file %s is not a hdf5 file" % file_path)
            return tuple()
        else:
            res = []
            with HDF5File(file_path, mode="r", swmr=True) as h5s:
                for entry in h5s:
                    if BlissScan.is_bliss_valid_entry(file_path=file_path, entry=entry):
                        res.append(entry)
            return tuple(res)

    def to_dict(self):
        return {
            "DICT_TYPE_KEY": self._TYPE,
            "master_file": self.master_file,
            "entry": self.entry,
            "proposal_file": self.proposal_file,
            "scan_numbers": self.scan_numbers,
        }

    @staticmethod
    def from_dict(ddict):
        master_file = ddict["master_file"]
        entry = ddict["entry"]
        return BlissScan(
            master_file=master_file, entry=entry, proposal_file=None
        ).load_frm_dict(ddict=ddict)

    def load_frm_dict(self, ddict):
        if "master_file" in ddict:
            self._master_file = ddict["master_file"]
        if "entry" in ddict:
            self._entry = ddict["entry"]
        if "proposal_file" in ddict:
            self._proposal_file = ddict["proposal_file"]
        if "scan_numbers" in ddict:
            self._scan_numbers = ddict["scan_numbers"]
        return self
