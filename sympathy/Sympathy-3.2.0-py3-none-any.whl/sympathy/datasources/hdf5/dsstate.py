# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import warnings
import collections
# Ignore a warning from numpy>=1.14 when importing h5py<=2.7.1:
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    import h5py


__hdf5_state = None


def hdf5_state():
    if __hdf5_state is None:
        set_hdf5_state(Hdf5State())
    return __hdf5_state


def get_hdf5_state():
    return __hdf5_state


def set_hdf5_state(state):
    global __hdf5_state
    __hdf5_state = state


class Hdf5State:
    # Maximum file handles:
    #     Windows 7-10: 2048 (non-configurable)

    link_lru_cache_len_max = 1600

    def __init__(self):
        # self.filestate contains the port files, opened directly and without
        # links.  These are kept opened and should be fairly limited in number.
        self.filestate = {}
        # self._link_lru_cache contains files opened through links, if a link
        # file is somehow added to filestate instead it will be removed from
        # lru.
        self._link_lru_cache = collections.OrderedDict()

    def create(self):
        self.clear()
        self.filestate = {}
        self._link_lru_cache = collections.OrderedDict()

    def clear(self):
        for filename in list(self.filestate):
            self.close(filename)

        self.clear_lru()

    def clear_lru(self):
        for filename in list(self._link_lru_cache):
            self._close_lru(filename)

    def add(self, filename, group):
        if filename not in self.filestate:
            self.filestate[filename] = group

        self._link_lru_cache.pop(filename, None)

    def open(self, filename, mode):
        if filename in self.filestate:
            hdf5_file = self.filestate[filename]
        else:
            hdf5_file = self._link_lru_cache.get(filename, None)
            if hdf5_file is None:
                hdf5_file = h5py.File(filename, mode)
                if mode == 'r':
                    if (len(self._link_lru_cache) >=
                            self.link_lru_cache_len_max):
                        prev = self._link_lru_cache.popitem(False)[1]
                        self._close_file(prev)
                    self._link_lru_cache[filename] = hdf5_file
                else:
                    assert False, (
                        'Only files for node ports should be opened in write '
                        'mode and the should not be closed.')

        return hdf5_file

    def _close_file(self, hdf5_file, filename=None):
        try:
            file_ = None
            if filename is None and hdf5_file:
                file_ = hdf5_file.file
                if file_:
                    filename = file_.filename
            if filename:
                self.filestate.pop(filename, None)
                self._link_lru_cache.pop(filename, None)
            try:
                if file_:
                    file_.flush()
                    file_.close()
            except ValueError:
                # Do not allow exceptions here due to already closed file.
                pass

        except RuntimeError:
            pass

    def close(self, filename):
        hdf5_file = self.filestate.pop(filename)
        self._close_file(hdf5_file, filename)

    def _close_lru(self, filename):
        hdf5_file = self._link_lru_cache.pop(filename)
        self._close_file(hdf5_file)

    def getlink(self, hdf5_file, entry):
        link = hdf5_file.get(entry, getlink=True)
        if isinstance(link, h5py.ExternalLink):
            link_hdf5_file = self.open(link.filename, 'r')
            return self.get(link_hdf5_file, link.path)
        else:
            dataset = hdf5_file[entry]
            return h5py.ExternalLink(dataset.file.filename,
                                     dataset.name)

    def is_closed(self, filename):
        hdf5_file = None
        if filename in self.filestate:
            hdf5_file = self.filestate[filename]
        else:
            hdf5_file = self._link_lru_cache.get(filename, None)
        if hdf5_file is None:
            res = True
        else:
            res = bool(hdf5_file)
        return res

    def file(self, filename):
        hdf5_file = None
        if filename in self.filestate:
            hdf5_file = self.filestate[filename]
        else:
            hdf5_file = self._link_lru_cache.get(filename, None)
        if hdf5_file is None:
            res = None
        else:
            res = hdf5_file.file
        return res
