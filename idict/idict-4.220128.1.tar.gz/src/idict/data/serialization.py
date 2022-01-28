#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the i-dict project.
#  Please respect the license - more about this in the section (*) below.
#
#  i-dict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  i-dict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with i-dict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and it is unethical regarding the effort and
#  time spent here.
#
import json
from importlib import import_module

from orjson import dumps, OPT_SORT_KEYS


def import_dependence(dep):
    try:
        return import_module(dep)
    except ImportError as e:
        raise Exception(f"Missing {dep} library. Need a complete install\n" "pip install -U idict[full]")


def custom_orjson_encoder(obj):
    # E.g., pandas dataframes.
    typ = str(type(obj))
    if typ == "<class 'pandas.core.frame.DataFrame'>":
        return obj.to_numpy()
    if typ == "<class 'pandas.core.series.Series'>":
        return obj.to_numpy()
    # if hasattr(obj, 'to_json'):
    #     # REMINDER: default_handler=str is to avoid infinite recursion, e.g., on iris.arff
    #     txt = obj.to_json(force_ascii=False, default_handler=str)
    #     return {"_type_orjson": str(type(obj)), "_obj.to_json()": txt}

    # Numpy objects generic type and ndarray, keeping dtype.
    if typ == "<class 'numpy.ndarray'>":
        print(typ)
        try:
            return serialize_numpy(obj)
        except Exception as e:
            print(e)
            exit()

    # try:
    #     import numpy
    #     if isinstance(obj, numpy.generic):
    #         return {"_type_orjson": str(obj.dtype), "_numpy.asscalar(obj)": numpy.asscalar(obj)}
    #     if isinstance(obj, numpy.ndarray):
    #         return {"_type_orjson": str(obj.dtype), "_numpy.ndarray.tolist()": obj.tolist()}
    # except ImportError as e:
    #     pass

    if isinstance(obj, bytes):
        return obj.decode()  # nem qq byte vira string!
    raise TypeError


def json_object_hook_decoder(dic):
    if "_type_orjson" in dic:
        if "_obj.to_json()" in dic:
            if dic["_type_orjson"] == "<class 'pandas.core.frame.DataFrame'>":
                m = import_dependence("pandas")
                return m.read_json(dic["_obj.to_json()"])  # , default_handler=str)
            if dic["_type_orjson"] == "<class 'pandas.core.series.Series'>":
                m = import_dependence("pandas")
                # default_handler=callable
                return m.read_json(dic["_obj.to_json()"], typ=dic["_type_orjson"])
            else:  # pragma: no cover
                raise Exception(f"Cannot desserialize object of type '{dic['_type_orjson']}'")
        if (c := "_numpy.asscalar(obj)") in dic or (c := "_numpy.ndarray.tolist()") in dic:
            m = import_dependence("numpy")
            dtype = "str" if len(dic["_type_orjson"]) > 10 else dic["_type_orjson"]
            return m.array(dic[c], dtype=dtype)
    return dic


def serialize_json(obj):
    # r"""
    # >>> import numpy as np
    # >>> import math
    # >>> a = np.array([[1/3, 5/4], [1.3**6, "text"]])
    # >>> a
    # array([['0.3333333333333333', '1.25'],
    #        ['4.826809000000001', 'text']], dtype='<U32')
    # >>> b = np.array([[1/3,5/4], [1.3**6, 4]], dtype = np.int64)
    # >>> b
    # array([[0, 1],
    #        [4, 4]])
    # >>> c = np.array([[1/3,5/4], [1.3**6, 4]], dtype = np.int8)
    # >>> c
    # array([[0, 1],
    #        [4, 4]], dtype=int8)
    # >>> serialize_json([math.inf, a, b, c])
    # b'[null,{"_numpy.ndarray.tolist()":[["0.3333333333333333","1.25"],["4.826809000000001","text"]],"_type_orjson":"<U32"},{"_numpy.ndarray.tolist()":[[0,1],[4,4]],"_type_orjson":"int64"},{"_numpy.ndarray.tolist()":[[0,1],[4,4]],"_type_orjson":"int8"}]'
    # >>> import pandas as pd
    # >>> df = pd.DataFrame(
    # ...     [[1/3, 5/4], [1.3**54, "text"]],
    # ...     index=["row 1", "row 2"],
    # ...     columns=["col 1", "col 2"],
    # ... )
    # >>> df
    #               col 1 col 2
    # row 1  3.333333e-01  1.25
    # row 2  1.422136e+06  text
    # >>> serialize_json(df)
    # b'{"_obj.to_json()":"{\\"col 1\\":{\\"row 1\\":0.3333333333,\\"row 2\\":1422135.6537506874},\\"col 2\\":{\\"row 1\\":1.25,\\"row 2\\":\\"text\\"}}","_type_orjson":"<class \'pandas.core.frame.DataFrame\'>"}'
    # >>> s = pd.Series(
    # ...     [1/3, 5/4, (1.3)**54, "text"],
    # ...     index=["row 1", "row 2", "row 3", "row 4"],
    # ... )
    # >>> s
    # row 1          0.333333
    # row 2              1.25
    # row 3    1422135.653751
    # row 4              text
    # dtype: object
    # >>> serialize_json(s)
    # b'{"_obj.to_json()":"{\\"row 1\\":0.3333333333,\\"row 2\\":1.25,\\"row 3\\":1422135.6537506874,\\"row 4\\":\\"text\\"}","_type_orjson":"<class \'pandas.core.series.Series\'>"}'
    # """
    return dumps(obj, default=custom_orjson_encoder, option=OPT_SORT_KEYS)


def deserialize_json(blob):
    r"""
    >>> deserialize_json(b'null')
    >>> deserialize_json(b'{"_numpy.ndarray.tolist()":[["0.3333333333333333","1.25"],["4.826809000000001","text"]],"_type_orjson":"<U32"}')
    array([['0.3333333333333333', '1.25'],
           ['4.826809000000001', 'text']], dtype='<U32')
    >>> deserialize_json(b'{"_numpy.ndarray.tolist()":[[0,1],[4,4]],"_type_orjson":"int64"}')
    array([[0, 1],
           [4, 4]])
    >>> deserialize_json(b'{"_numpy.ndarray.tolist()":[[0,1],[4,4]],"_type_orjson":"int8"}')
    array([[0, 1],
           [4, 4]], dtype=int8)
    >>> deserialize_json(b'{"_obj.to_json()":"{\\"col 1\\":{\\"row 1\\":0.3333333333,\\"row 2\\":1422135.6537506874},\\"col 2\\":{\\"row 1\\":1.25,\\"row 2\\":\\"text\\"}}","_type_orjson":"<class \'pandas.core.frame.DataFrame\'>"}')
                  col 1 col 2
    row 1  3.333333e-01  1.25
    row 2  1.422136e+06  text
    >>> deserialize_json(b'{"_obj.to_json()":"{\\"row 1\\":0.3333333333,\\"row 2\\":1.25,\\"row 3\\":1422135.6537506874,\\"row 4\\":\\"text\\"}","_type_orjson":"<class \'pandas.core.series.Series\'>"}')
    row 1          0.333333
    row 2              1.25
    row 3    1422135.653751
    row 4              text
    dtype: object
    """
    return json.loads(blob, object_hook=json_object_hook_decoder)


def serialize_numpy(obj):
    # r"""
    # >>> import numpy as np
    # >>> m = np.array([1,2,3,4])
    # >>> m
    # array([1, 2, 3, 4])
    # >>> deserialize_numpy(serialize_numpy(m))
    # array([1, 2, 3, 4])
    # >>> m = np.array([[1,2],[3,4]])
    # >>> m
    # array([[1, 2],
    #        [3, 4]])
    # >>> deserialize_numpy(serialize_numpy(m))
    # array([[1, 2],
    #        [3, 4]])
    # >>> m = np.array([1,2.7,3,4])
    # >>> deserialize_numpy(serialize_numpy(m))
    # array([1. , 2.7, 3. , 4. ])
    # >>> m = np.array([[1,2],[3,4/3]])
    # >>> deserialize_numpy(serialize_numpy(m))
    # array([[1.        , 2.        ],
    #        [3.        , 1.33333333]])
    # >>> m = np.array([1,2,3,"txt"])
    # >>> deserialize_numpy(serialize_numpy(m))
    # array(['1', '2', '3', 'txt'], dtype='<U21')
    # >>> m = np.array([[1,"txt"],[3,4]])
    # >>> deserialize_numpy(serialize_numpy(m))
    # array([['1', 'txt'],
    #        ['3', '4']], dtype='<U21')
    # """
    import numpy

    if isinstance(obj, numpy.ndarray):
        dims = len(obj.shape)
        dtype = str(obj.dtype)
        headerlen = 1 + len(dtype)
        header = f"{headerlen}§{dims}§{dtype}§".encode() + integers2bytes(obj.shape)
        return header, obj.data
    raise Exception(f"Cannot handle this type {type(obj)}, check its shape or dtype")


# passar memoryview direto pro compressor, talvez cada serializador tenha que comprimir por si
# faz msm mais sentido o header fora da parte comprimida
# tentar fazer com que json resolva tudo, só q delegando numpy e pandas pra mim. testar depois veocidade
#   vantagem: numpys nested inside dict/lists/sets
#   desvantagem?: converter de bytes p/ str


def deserialize_numpy(blob):
    import numpy

    view = memoryview(blob)
    prefix, dtype, hw = view[:30].split(b"_")
    dims = int(chr(prefix[2]))
    dtype = dtype.decode().rstrip()
    h, w = bytes2integers(hw)
    dump = blob[30:]
    m = numpy.frombuffer(dump, dtype=dtype)
    if dims == 2:
        m = numpy.reshape(m, newshape=(h, w))
    return m


def integers2bytes(lst, n=4) -> bytes:
    """Each int becomes N bytes. max=4294967294 for 4 bytes"""
    return b"".join(d.to_bytes(n, byteorder="little") for d in lst)


def bytes2integers(bytes_content: bytes, n=4):
    """Each 4 bytes become an int."""
    return [int.from_bytes(bytes_content[i : i + n], "little") for i in range(0, len(bytes_content), n)]
