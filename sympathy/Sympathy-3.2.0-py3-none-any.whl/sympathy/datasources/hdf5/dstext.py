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
"""Text Data source module."""
import numpy as np
import h5py
from sympathy.utils import prim

from . import dsgroup
from . import dstable

_h5py_chunk_size = 2 ** 22
_numpy_max_strlen = 2 ** 31 - 1
_ext_col_fn = '__sy_col_fn__'
_ext_col_ds = '__sy_col_ds__'
_dataset_name = 'text'


def _encode_chunks(chunks):
    for chunk in chunks:
        yield chunk.encode('utf8')


def _chunk_text(text, chunk_size=_h5py_chunk_size):
    for x in prim.chunk(text, chunk_size):
        yield x


def _chunk_encode_bytes(text_chunks, chunk_size=_h5py_chunk_size):
    for chunk in prim.rechunk(
            _encode_chunks(text_chunks), chunk_size, b''.join):
        yield chunk


def _utf8_length(text):
    return sum(len(c) for c in _encode_chunks(_chunk_text(text)))


def _n_chunks(total_size, chunk_size):
    res = total_size // chunk_size
    if total_size % chunk_size > 0:
        res += 1
    return res


class Hdf5Text(dsgroup.Hdf5Group):
    """Abstraction of an HDF5-text."""
    def __init__(self, factory, **kwargs):
        super().__init__(
            factory, **kwargs)
        self._src_filename = self.group.attrs.get(_ext_col_fn, None)
        self._src_dataset = self.group.attrs.get(_ext_col_ds, None)

    def read(self):
        """Return stored text, or '' if nothing is stored."""
        try:
            dataset = self.group['text']
            chunks = []
            for i in range(len(dataset)):
                chunks.append(dataset[i])
            return b''.join(chunks).decode('utf8')
        except KeyError:
            return ''

    def write(self, text):
        """
        Stores text in the hdf5 file, at path,
        with data from the given text
        """
        encoded_length = _utf8_length(text)
        if encoded_length <= _numpy_max_strlen:
            self.group.create_dataset(
                'text', data=np.array([text.encode('utf8')]))
        else:
            # 3.2.0, chunk only excessive data to ensure compatibility.
            self._write_chunked_text(text, encoded_length)

    def _write_chunked_text(self, text, encoded_length):
        chunks = _chunk_encode_bytes(_chunk_text(text))
        chunk = next(chunks, b'')
        n_chunks = max(1, _n_chunks(encoded_length, _h5py_chunk_size))
        dtype = f'S{max(1, len(chunk))}'

        kwargs = {}
        if n_chunks > 1:
            kwargs['chunks'] = (1,)
            kwargs.update(dstable.int_compress)

        dataset = self.group.create_dataset(
            'text', shape=(n_chunks,), dtype=dtype,
            **kwargs)

        dataset[0] = chunk
        for i, chunk in enumerate(chunks, 1):
            dataset[i] = chunk

    def transferable(self, other):
        return (isinstance(other, Hdf5Text) and
                self.can_link and other.can_link and
                _dataset_name in other.group)

    def transfer(self, name, other, other_name):
        src_filename = other._src_filename
        if src_filename:
            src_dataset = other._src_dataset
        else:
            dataset = other.group[_dataset_name]
            src_filename = dataset.file.filename
            src_dataset = dataset.name

        self.group[_dataset_name] = h5py.ExternalLink(
            src_filename, src_dataset)

        self._src_filename = src_filename
        self._src_dataset = src_dataset
        self.group.attrs[_ext_col_fn] = self._src_filename
        self.group.attrs[_ext_col_ds] = self._src_dataset

    def write_link(self, name, other, other_name):
        return False
