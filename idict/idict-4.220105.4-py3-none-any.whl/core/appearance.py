#  Copyright (c) 2021. Davi Pereira dos Santos
#  This file is part of the idict project.
#  Please respect the license - more about this in the section (*) below.
#
#  idict is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  idict is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with idict.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is illegal and unethical regarding the effort and
#  time spent here.

import json

from garoupa import Hosh
from garoupa.misc.colors import id2ansi

from ldict.customjson import CustomJSONEncoder
from ldict.lazyval import LazyVal


def idict2txt(d, all, history):
    r"""
    Textual representation of a ldict object

    >>> from idict.core.frozenidentifieddict import FrozenIdentifiedDict as idict
    >>> from ldict.core.appearance import decolorize
    >>> d = idict(x=1,y=2)
    >>> decolorize(idict2txt(d, False, False))
    '{\n    "x": 1,\n    "y": 2,\n    "_id": "5G_358b45f49c547174eb4bd687079b30cbbe724",\n    "_ids": "fH_5142f0a4338a1da2ca3159e2d1011981ac890 S-_074b5a806933d64f111a93af359a278402f83"\n}'
    >>> decolorize(idict2txt(d, True, False))
    '{\n    "x": 1,\n    "y": 2,\n    "_id": "5G_358b45f49c547174eb4bd687079b30cbbe724",\n    "_ids": {\n        "x": "fH_5142f0a4338a1da2ca3159e2d1011981ac890 (content: l8_09c7059156c4ed2aea46243e9d4b36c01f272)",\n        "y": "S-_074b5a806933d64f111a93af359a278402f83 (content: -B_305c3d0e44c94a5418d982f7dfe8a537a5c4b)"\n    }\n}'

    Parameters
    ----------
    d
    all

    Returns
    -------

    """
    dic = idict2dict(d, all, history)
    txt = json.dumps(dic, indent=4, ensure_ascii=False, cls=CustomJSONEncoder)
    if "_id" in dic:
        txt = txt.replace(dic["_id"], d.hosh.idc)
    if "_history" in dic:
        if isinstance(dic["_history"], LazyVal):
            dic["_history"] = dic["_history"]()
        if isinstance(dic["_history"], str):
            for id in dic["_history"].split(" "):
                txt = txt.replace(id, id2ansi(id))
    if all:
        for k, v in d.hoshes.items():
            nokey = ""
            if k in d.hashes:
                hash = v // k.encode()
                nokey = f" (content: {hash.idc})"
            txt = txt.replace(v.id, v.idc + nokey)  # REMINDER: workaround to avoid json messing with colors
    return txt


def idict2dict(d, all, history):
    # from ldict.core.base import AbstractLazyDict
    dic = d.data.copy()
    if not history and "_history" in dic and isinstance(dic["_history"], dict):
        dic["_history"] = " ".join(Hosh.fromid(k).id for k in dic["_history"])
    if not all:
        if len(d.ids) < 3:
            dic["_ids"] = " ".join(d.ids.values())
        else:
            ids = list(d.ids.values())
            dic["_ids"] = f"{ids[0]}... +{len(d) - 4} ...{ids[-1]}"
    elif "_ids" in dic:
        dic["_ids"] = d.ids.copy()
    return dic
