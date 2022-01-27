# This file is part of Sympathy for Data.
# Copyright (c) 2016-2017, Combine Control Systems AB
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
import os
import sys
import json
import collections


_fs_encoding = sys.getfilesystemencoding()
fs_encoding = _fs_encoding


def _fs_decode_list(list_):
    return [x.decode(_fs_encoding) for x in list_]


def _fs_encode_list(list_):
    return [x.encode(_fs_encoding) for x in list_]


def environ_wrapper(environ=os.environ):
    return environ


OS = os
SYS = sys


def py_file(file_):
    if isinstance(file_, bytes):
        file_ = file_.decode(_fs_encoding)
    return os.path.abspath(file_)


def py_file_dir(file_):
    return os.path.dirname(py_file(file_))


def encode(string, encoding):
    if isinstance(string, bytes):
        return string
    return string.encode(encoding)


def decode(string, encoding):
    if isinstance(string, str):
        return string
    return string.decode(encoding)


def fs_encode(string):
    return encode(string, _fs_encoding)


def fs_decode(string):
    return decode(string, _fs_encoding)


def str_(string, encoding='ascii', errors='strict'):
    if isinstance(string, str):
        return string
    return string.decode(encoding, errors)


_dict = {}
_odict = collections.OrderedDict()
_dict_iters = set(type(x) for x in [
    _dict.keys(), _dict.values(), _dict.items(),
    _odict.keys(), _odict.values(), _odict.items()])


def dict_encoder(obj):
    if type(obj) in _dict_iters:
        return list(obj)
    return json.JSONEncoder().default(obj)


def json_dumps(*args, **kwargs):
    return json.dumps(*args, default=dict_encoder, **kwargs)


def samefile(filename1, filename2):
    return os.path.samefile(filename1, filename2)


def deepcopy(obj):
    return json.loads(json_dumps(obj), object_hook=collections.OrderedDict)


if sys.version_info.minor < 6:
    OrderedDict = collections.OrderedDict
else:
    # Python3.6 and forward should have ordered dict.
    OrderedDict = dict
