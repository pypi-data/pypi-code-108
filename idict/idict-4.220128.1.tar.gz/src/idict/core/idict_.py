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
#
import operator
from functools import reduce
from operator import rshift as aop
from operator import xor as cop
from random import Random
from typing import TypeVar, Union, Callable

from garoupa import ø40

import idict.core.frozenidentifieddict as fro
from idict.parameter.ifunctionspace import iFunctionSpace
from idict.parameter.ilet import iLet
from idict.persistence.cache import Cache
from ldict.core.appearance import decolorize
from ldict.core.base import AbstractMutableLazyDict, AbstractLazyDict
from ldict.exception import WrongKeyType

VT = TypeVar("VT")


# TODO: k-fold CV
# TODO (minor):  implement extend, to avoid excessive calculation when batch inserting values
# TODO (minor): let(f, ..., omit=["_name", ...])
# TODO: serialize pandas (and define safe/unsafe unpack), or some of the options bellow
# TODO: Store DF as LazyDF that depends on column metafeatures?
#   or column metafeatures?
#   or depends on a cache? Or both?    LazyDF(cols, indices, cache)
# TODO: document multilevel cache:  .. >> [oka, disk, RAM] >> ..
class Idict(AbstractMutableLazyDict):
    r"""Mutable lazy identified dict for serializable (picklable) pairs str->value

    Usage:

    >>> from idict import idict
    >>> idict().show(colored=False)
    {
        "_id": "0000000000000000000000000000000000000000",
        "_ids": {}
    }
    >>> d = idict(x=5, y=3)
    >>> d.show(colored=False)
    {
        "x": 5,
        "y": 3,
        "_id": "pl_8763f6625970707cdef7dfd31096db4c63c91",
        "_ids": {
            "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "Ku_f738128d6e27a03ec6c2e76d23514b4e998e3 (content: S5_331b7e710abd1443cd82d6b5cdafb9f04d5ab)"
        }
    }
    >>> d["y"]
    3
    >>> d = idict(x=123123, y=88)
    >>> d2 = d >> (lambda x: {"z": x**2})
    >>> d2.ids  # doctest:+ELLIPSIS
    {'z': '...', 'x': 'CF_13e3494690e330a722667f4ab9e067c64022e', 'y': '-j_34f477bff0a6dac76fe447d0e95003e273c62'}
    >>> d2.hosh == d2.identity * d2.ids["z"] * d2.ids["x"] * d2.ids["y"]
    True
    >>> e = d2 >> (lambda x,y: {"w": x/y})
    >>> e.show(colored=False)  # doctest:+ELLIPSIS
    {
        "w": "→(x y)",
        "z": "→(x)",
        "x": 123123,
        "y": 88,
        "_id": "...",
        "_ids": {
            "w": "...",
            "z": "...",
            "x": "CF_13e3494690e330a722667f4ab9e067c64022e (content: I6_bcc6fa41b424962f427be985853b8416b2cff)",
            "y": "-j_34f477bff0a6dac76fe447d0e95003e273c62 (content: 6X_ceb4a9cfad6b3b5a56b49c3484be71dff692a)"
        }
    }
    >>> a = d >> (lambda x: {"z": x**2}) >> (lambda x, y: {"w": x/y})
    >>> b = d >> (lambda x, y: {"w": x/y}) >> (lambda x: {"z": x**2})
    >>> dic = d.asdict  # Converting to dict
    >>> dic
    {'x': 123123, 'y': 88, '_id': 'BZ_2ef6b00691651b6f815ba62b93416aa9b3e80', '_ids': {'x': 'CF_13e3494690e330a722667f4ab9e067c64022e', 'y': '-j_34f477bff0a6dac76fe447d0e95003e273c62'}}
    >>> d2 = idict(dic)  # Reconstructing from a dict
    >>> d2.show(colored=False)
    {
        "x": 123123,
        "y": 88,
        "_id": "BZ_2ef6b00691651b6f815ba62b93416aa9b3e80",
        "_ids": {
            "x": "CF_13e3494690e330a722667f4ab9e067c64022e",
            "y": "-j_34f477bff0a6dac76fe447d0e95003e273c62"
        }
    }
    >>> d == d2
    True
    >>> from idict import Ø
    >>> d = Ø >> {"x": "more content"}
    >>> d.show(colored=False)
    {
        "x": "more content",
        "_id": "zd_6a3f5ec407f6c5c24b89b35ff7cc1793969fd",
        "_ids": {
            "x": "zd_6a3f5ec407f6c5c24b89b35ff7cc1793969fd"
        }
    }
    >>> d = idict() >> {"x": "more content"}
    >>> d.show(colored=False)
    {
        "x": "more content",
        "_id": "zd_6a3f5ec407f6c5c24b89b35ff7cc1793969fd",
        "_ids": {
            "x": "zd_6a3f5ec407f6c5c24b89b35ff7cc1793969fd"
        }
    }
    >>> e.ids.keys()
    dict_keys(['w', 'z', 'x', 'y'])
    >>> del e["z"]
    >>> e.show(colored=False)  # doctest:+ELLIPSIS
    {
        "w": "→(x y)",
        "x": 123123,
        "y": 88,
        "_id": "...",
        "_ids": {
            "w": "...",
            "x": "CF_13e3494690e330a722667f4ab9e067c64022e (content: I6_bcc6fa41b424962f427be985853b8416b2cff)",
            "y": "-j_34f477bff0a6dac76fe447d0e95003e273c62 (content: 6X_ceb4a9cfad6b3b5a56b49c3484be71dff692a)"
        }
    }
    >>> e.hosh == e.identity * e.ids["w"] * e.ids["x"] * e.ids["y"]
    True
    >>> e["x"] = 77
    >>> e.show(colored=False)  # doctest:+ELLIPSIS
    {
        "w": "→(x y)",
        "x": 77,
        "y": 88,
        "_id": "...",
        "_ids": {
            "w": "...",
            "x": "Ye_5b015377273c0cfa49e037788b4c618a9431c (content: 2I_96abdb2113ef4fff69f518ce57969e04f6ded)",
            "y": "-j_34f477bff0a6dac76fe447d0e95003e273c62 (content: 6X_ceb4a9cfad6b3b5a56b49c3484be71dff692a)"
        }
    }
    >>> f = lambda x,y: {"z":x+y}
    >>> d = idict(x=5, y=7)
    >>> d2 = d >> f
    >>> d2.show(colored=False)  # doctest:+ELLIPSIS
    {
        "z": "→(x y)",
        "x": 5,
        "y": 7,
        "_id": "...",
        "_ids": {
            "z": "...",
            "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> c = {}
    >>> d3 = d2 >> [c]
    >>> d3.show(colored=False)  # doctest:+ELLIPSIS
    {
        "z": "→(↑ x y)",
        "x": 5,
        "y": 7,
        "_id": "...",
        "_ids": {
            "z": "...",
            "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> c
    {}
    >>> d3.z
    12
    >>> c  # doctest:+ELLIPSIS
    {'XZJr5b7N0ASkdIo2alN.Crfx7plafTxoqcpJj46e': 12, 'GS_cb0fda15eac732cb08351e71fc359058b93bd': 5, 'WK_6ba95267cec724067d58b3186ecbcaa4253ad': 7, '_NHayCulARZBLYdg-niJJt-SyOeafTxoqcpJj46e': {'_id': 'SNHayCulARZBLYdg-niJJt-SyOeafTxoqcpJj46e', '_ids': {'z': 'XZJr5b7N0ASkdIo2alN.Crfx7plafTxoqcpJj46e', 'x': 'GS_cb0fda15eac732cb08351e71fc359058b93bd', 'y': 'WK_6ba95267cec724067d58b3186ecbcaa4253ad'}}}
    >>> d3.show(colored=False)  # doctest:+ELLIPSIS
    {
        "z": 12,
        "x": 5,
        "y": 7,
        "_id": "...",
        "_ids": {
            "z": "...",
            "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> c = {}
    >>> from idict import setup
    >>> setup(cache=c)
    >>> d3 = d >> f ^ Ø
    >>> d3.show(colored=False)  # doctest:+ELLIPSIS
    {
        "z": "→(↑ x y)",
        "x": 5,
        "y": 7,
        "_id": "...",
        "_ids": {
            "z": "...",
            "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> c
    {}
    >>> d3.z
    12
    >>> c  # doctest:+ELLIPSIS
    {'...': 12, 'GS_cb0fda15eac732cb08351e71fc359058b93bd': 5, 'WK_6ba95267cec724067d58b3186ecbcaa4253ad': 7, '...': {'_id': '...', '_ids': {'z': '...', 'x': 'GS_cb0fda15eac732cb08351e71fc359058b93bd', 'y': 'WK_6ba95267cec724067d58b3186ecbcaa4253ad'}}}
    >>> d3.show(colored=False)  # doctest:+ELLIPSIS
    {
        "z": 12,
        "x": 5,
        "y": 7,
        "_id": "...",
        "_ids": {
            "z": "...",
            "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> f = lambda x: {"y": x ** 2, "_history": ...}
    >>> g = lambda x: {"y":x + 1000, "_history": ...}
    >>> f.metadata = {"id": "b5d6efbc9820dafe0d8fbe87a79adbe9797abc87", "name": "squared", "description": "Some text."}
    >>> g.metadata = {"id": "05d6efbc9820dafe0d8fbe87a79adbe9797abc87", "name": "add1000", "description": "Some text."}
    >>> d = idict(x=3) >> f >> g
    >>> d.show(colored=False)
    {
        "y": "→(x)",
        "_history": "b5d6efbc9820dafe0d8fbe87a79adbe9797abc87 05d6efbc9820dafe0d8fbe87a79adbe9797abc87",
        "x": 3,
        "_id": "FHezbXIcslIpb9mWpbUat7LaEAk1smsieeekmoge",
        "_ids": {
            "y": "Wdha30jmnlZs7fMYWOyoCdQnuoq1smsieeekmoge",
            "_history": "MjnLuTHcrK0ieeQI5ks5ia15W5snEsIJDcm7aDLt",
            "x": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9 (content: S5_331b7e710abd1443cd82d6b5cdafb9f04d5ab)"
        }
    }
    >>> (idict(x=3).hosh * "b5d6efbc9820dafe0d8fbe87a79adbe9797abc87" * "05d6efbc9820dafe0d8fbe87a79adbe9797abc87").show(colored=False)
    FHezbXIcslIpb9mWpbUat7LaEAk1smsieeekmoge
    >>> a = idict(x=3)
    >>> b = idict(y=5)
    >>> b["d"] = lambda y: a
    >>> cache = {}
    >>> b >>= [cache]
    >>> b.show(colored=False)  # doctest:+ELLIPSIS
    {
        "d": "→(↑ y)",
        "y": 5,
        "_id": "...",
        "_ids": {
            "d": "...",
            "y": "EI_20378979f4669f2e318ae9742e214fd4880d7 (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)"
        }
    }
    >>> b.d.show(colored=False)
    {
        "x": 3,
        "_id": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9",
        "_ids": {
            "x": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9"
        }
    }
    >>> import json
    >>> print(json.dumps(cache, indent=2))  # doctest:+ELLIPSIS
    {
      "...": {
        "_id": "_E_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9"
      },
      "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9": 3,
      "_E_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9": {
        "_id": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9",
        "_ids": {
          "x": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9"
        }
      },
      "EI_20378979f4669f2e318ae9742e214fd4880d7": 5,
      "...": {
        "_id": "...",
        "_ids": {
          "d": "...",
          "y": "EI_20378979f4669f2e318ae9742e214fd4880d7"
        }
      }
    }
    >>> d = idict.fromid("ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9", cache)
    >>> d.show(colored=False)
    {
        "x": "→(↑)",
        "_id": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9",
        "_ids": {
            "x": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9"
        }
    }
    >>> d.evaluated.show(colored=False)
    {
        "x": 3,
        "_id": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9",
        "_ids": {
            "x": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9"
        }
    }
    >>> idict.fromid(d.id, cache).evaluated.show(colored=False)
    {
        "x": 3,
        "_id": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9",
        "_ids": {
            "x": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9"
        }
    }
    >>> e = idict(f=lambda x: 5)
    >>> e.show(colored=False)  # doctest:+ELLIPSIS
    {
        "f": "<function <lambda> at 0x...>",
        "_id": "pqmFNR-9nNXACJsyc6Ro3BA.wfz.mD0zHOgI9vYy",
        "_ids": {
            "f": "pqmFNR-9nNXACJsyc6Ro3BA.wfz.mD0zHOgI9vYy"
        }
    }
    >>> from idict.core.appearance import idict2txt
    >>> d = idict(x=1,y=2)
    >>> decolorize(idict2txt(d, False, False))
    '{\n    "x": 1,\n    "y": 2,\n    "_id": "5G_358b45f49c547174eb4bd687079b30cbbe724",\n    "_ids": "fH_5142f0a4338a1da2ca3159e2d1011981ac890 S-_074b5a806933d64f111a93af359a278402f83"\n}'
    >>> decolorize(idict2txt(d, True, False))
    '{\n    "x": 1,\n    "y": 2,\n    "_id": "5G_358b45f49c547174eb4bd687079b30cbbe724",\n    "_ids": {\n        "x": "fH_5142f0a4338a1da2ca3159e2d1011981ac890 (content: l8_09c7059156c4ed2aea46243e9d4b36c01f272)",\n        "y": "S-_074b5a806933d64f111a93af359a278402f83 (content: -B_305c3d0e44c94a5418d982f7dfe8a537a5c4b)"\n    }\n}'
    >>> cache = {}
    >>> a = idict(x=5) >> (lambda x:{"y": x**x}) >> [[cache]]  # Cache within double brackets has strict/eager behavior.
    >>> a.show(colored=False)  # doctest:+ELLIPSIS
    {
        "y": 3125,
        "x": 5,
        "_id": "...",
        "_ids": {
            "y": "...",
            "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)"
        }
    }
    >>> idict(a.id, cache).show(colored=False)  # doctest:+ELLIPSIS
    {
        "y": "→(↑)",
        "x": "→(↑)",
        "_id": "...",
        "_ids": {
            "y": "...",
            "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)"
        }
    }
    >>> a.hosh.html
    '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n<html>\n<head>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n<title></title>\n<style type="text/css">\n.ansi2html-content { display: inline; white-space: pre-wrap; word-wrap: break-word; }\n.body_foreground { color: #AAAAAA; }\n.body_background { background-color: #000000; }\n.body_foreground > .bold,.bold > .body_foreground, body.body_foreground > pre > .bold { color: #FFFFFF; font-weight: normal; }\n.inv_foreground { color: #000000; }\n.inv_background { background-color: #AAAAAA; }\n.ansi1 { font-weight: bold; }\n.ansi48-0 { background-color: #000316; }\n.ansi38-117 { color: #87d7ff; }\n.ansi38-153 { color: #afd7ff; }\n.ansi38-189 { color: #d7d7ff; }\n.ansi38-122 { color: #87ffd7; }\n.ansi38-123 { color: #87ffff; }\n.ansi38-159 { color: #afffff; }\n.ansi38-194 { color: #d7ffd7; }\n.ansi38-195 { color: #d7ffff; }\n.ansi38-251 { color: #c6c6c6; }\n</style>\n</head>\n<body class="body_foreground body_background" style="font-size: normal;" >\n<pre class="ansi2html-content">\n<span class="ansi38-123"></span><span class="ansi1 ansi38-123"></span><span class="ansi1 ansi38-123 ansi48-0">q</span><span class="ansi38-159"></span><span class="ansi1 ansi38-159"></span><span class="ansi1 ansi38-159 ansi48-0">1</span><span class="ansi38-195"></span><span class="ansi1 ansi38-195"></span><span class="ansi1 ansi38-195 ansi48-0">O</span><span class="ansi38-195"></span><span class="ansi1 ansi38-195"></span><span class="ansi1 ansi38-195 ansi48-0">Q</span><span class="ansi38-194"></span><span class="ansi1 ansi38-194"></span><span class="ansi1 ansi38-194 ansi48-0">E</span><span class="ansi38-153"></span><span class="ansi1 ansi38-153"></span><span class="ansi1 ansi38-153 ansi48-0">t</span><span class="ansi38-122"></span><span class="ansi1 ansi38-122"></span><span class="ansi1 ansi38-122 ansi48-0">J</span><span class="ansi38-189"></span><span class="ansi1 ansi38-189"></span><span class="ansi1 ansi38-189 ansi48-0">.</span><span class="ansi38-122"></span><span class="ansi1 ansi38-122"></span><span class="ansi1 ansi38-122 ansi48-0">n</span><span class="ansi38-153"></span><span class="ansi1 ansi38-153"></span><span class="ansi1 ansi38-153 ansi48-0">4</span><span class="ansi38-123"></span><span class="ansi1 ansi38-123"></span><span class="ansi1 ansi38-123 ansi48-0">q</span><span class="ansi38-195"></span><span class="ansi1 ansi38-195"></span><span class="ansi1 ansi38-195 ansi48-0">t</span><span class="ansi38-159"></span><span class="ansi1 ansi38-159"></span><span class="ansi1 ansi38-159 ansi48-0">4</span><span class="ansi38-194"></span><span class="ansi1 ansi38-194"></span><span class="ansi1 ansi38-194 ansi48-0">D</span><span class="ansi38-251"></span><span class="ansi1 ansi38-251"></span><span class="ansi1 ansi38-251 ansi48-0">.</span><span class="ansi38-117"></span><span class="ansi1 ansi38-117"></span><span class="ansi1 ansi38-117 ansi48-0">w</span><span class="ansi38-123"></span><span class="ansi1 ansi38-123"></span><span class="ansi1 ansi38-123 ansi48-0">P</span><span class="ansi38-159"></span><span class="ansi1 ansi38-159"></span><span class="ansi1 ansi38-159 ansi48-0">J</span><span class="ansi38-195"></span><span class="ansi1 ansi38-195"></span><span class="ansi1 ansi38-195 ansi48-0">K</span><span class="ansi38-195"></span><span class="ansi1 ansi38-195"></span><span class="ansi1 ansi38-195 ansi48-0">l</span><span class="ansi38-194"></span><span class="ansi1 ansi38-194"></span><span class="ansi1 ansi38-194 ansi48-0">S</span><span class="ansi38-153"></span><span class="ansi1 ansi38-153"></span><span class="ansi1 ansi38-153 ansi48-0">G</span><span class="ansi38-122"></span><span class="ansi1 ansi38-122"></span><span class="ansi1 ansi38-122 ansi48-0">F</span><span class="ansi38-189"></span><span class="ansi1 ansi38-189"></span><span class="ansi1 ansi38-189 ansi48-0">F</span><span class="ansi38-122"></span><span class="ansi1 ansi38-122"></span><span class="ansi1 ansi38-122 ansi48-0">E</span><span class="ansi38-153"></span><span class="ansi1 ansi38-153"></span><span class="ansi1 ansi38-153 ansi48-0">x</span><span class="ansi38-123"></span><span class="ansi1 ansi38-123"></span><span class="ansi1 ansi38-123 ansi48-0">Y</span><span class="ansi38-195"></span><span class="ansi1 ansi38-195"></span><span class="ansi1 ansi38-195 ansi48-0">u</span><span class="ansi38-159"></span><span class="ansi1 ansi38-159"></span><span class="ansi1 ansi38-159 ansi48-0">j</span><span class="ansi38-194"></span><span class="ansi1 ansi38-194"></span><span class="ansi1 ansi38-194 ansi48-0">1</span><span class="ansi38-251"></span><span class="ansi1 ansi38-251"></span><span class="ansi1 ansi38-251 ansi48-0">6</span><span class="ansi38-117"></span><span class="ansi1 ansi38-117"></span><span class="ansi1 ansi38-117 ansi48-0">i</span><span class="ansi38-123"></span><span class="ansi1 ansi38-123"></span><span class="ansi1 ansi38-123 ansi48-0">t</span><span class="ansi38-159"></span><span class="ansi1 ansi38-159"></span><span class="ansi1 ansi38-159 ansi48-0">l</span><span class="ansi38-195"></span><span class="ansi1 ansi38-195"></span><span class="ansi1 ansi38-195 ansi48-0">1</span><span class="ansi38-195"></span><span class="ansi1 ansi38-195"></span><span class="ansi1 ansi38-195 ansi48-0">y</span><span class="ansi38-194"></span><span class="ansi1 ansi38-194"></span><span class="ansi1 ansi38-194 ansi48-0">Q</span><span class="ansi38-153"></span><span class="ansi1 ansi38-153"></span><span class="ansi1 ansi38-153 ansi48-0">B</span><span class="ansi38-122"></span><span class="ansi1 ansi38-122"></span><span class="ansi1 ansi38-122 ansi48-0">L</span><span class="ansi38-189"></span><span class="ansi1 ansi38-189"></span><span class="ansi1 ansi38-189 ansi48-0">4</span>\n</pre>\n</body>\n\n</html>\n'
    >>> a.fields
    ['y', 'x']
    """

    frozen: fro.FrozenIdentifiedDict

    # noinspection PyMissingConstructor
    def __init__(self, /, _dictionary=None, _id=None, _ids=None, rnd=None, identity=ø40, _cloned=None, **kwargs):
        from idict.core.frozenidentifieddict import FrozenIdentifiedDict

        self.identity = identity
        if isinstance(_dictionary, str) and isinstance(_id, (dict, Cache)):
            # Build idict from id+cache.
            if _ids or rnd or _cloned or kwargs:  # pragma: no cover
                raise Exception("Cannot pass more arguments when first argument is id and second argument is cache.")
            # TODO (minor): detect identity (other than ø40) from number of digits
            self.frozen = FrozenIdentifiedDict.fromid(_dictionary, _id, identity=identity)
        elif isinstance(_dictionary, FrozenIdentifiedDict):
            self.frozen = _dictionary
        else:
            self.frozen = FrozenIdentifiedDict(_dictionary, _id, _ids, rnd, identity, _cloned, **kwargs)

    @property
    def id(self):
        return self.hosh.id

    @property
    def ids(self):
        return self.frozen.ids

    @property
    def fields(self):
        return self.frozen.fields

    @property
    def hosh(self):
        return self.frozen.hosh

    @property
    def blobs(self):
        return self.frozen.blobs

    @property
    def hashes(self):
        return self.frozen.hashes

    @property
    def hoshes(self):
        return self.frozen.hoshes

    def __getattr__(self, item):
        if item in self.frozen:
            return self.frozen[item]
        _item = "_" + item
        if _item in self.frozen:
            return self.frozen[_item]
        return self.__getattribute__(item)

    def __delitem__(self, key):
        if not isinstance(key, str):
            raise WrongKeyType(f"Key must be string, not {type(key)}.", key)
        data, blobs, hashes, hoshes = self.data.copy(), self.blobs.copy(), self.hashes.copy(), self.hoshes.copy()
        del data[key]
        for coll in [blobs, hashes, hoshes]:
            if key in coll:
                del coll[key]
        hosh = reduce(operator.mul, [self.identity] + [v for k, v in hoshes.items() if not k.startswith("_")])
        self.frozen = self.frozen.clone(data, _cloned=dict(blobs=blobs, hashes=hashes, hoshes=hoshes, hosh=hosh))

    def clone(self, data=None, rnd=None, _cloned=None):
        return self.frozen.clone(data, rnd, _cloned).asmutable

    def show(self, colored=True, width=None):
        self.frozen.show(colored, width)

    def __rrshift__(self, left: Union[Random, dict, Callable, iFunctionSpace]):
        """
        >>> ({"x": 5} >> Idict(y=2)).show(colored=False)
        {
            "x": 5,
            "y": 2,
            "_id": "xR_15583f654491968d294f9b1622dfb782db241",
            "_ids": {
                "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
                "y": "S-_074b5a806933d64f111a93af359a278402f83 (content: -B_305c3d0e44c94a5418d982f7dfe8a537a5c4b)"
            }
        }
        >>> from ldict import ldict
        >>> (lambda x: {"y": 5*x}) >> ldict(y = 2)
        «λ × {
            "y": 2
        }»
        """
        if isinstance(left, list) or callable(left):
            return iFunctionSpace(left, aop, self)
        clone = self.__class__(identity=self.identity)
        clone.frozen = left >> self.frozen
        return clone

    def __rshift__(self, other: Union[list, dict, AbstractLazyDict, Callable, iLet, iFunctionSpace, Random]):
        """
        >>> d = Idict(x=2) >> (lambda x: {"y": 2 * x})
        >>> d.ids  # doctest:+ELLIPSIS
        {'y': '...', 'x': 'U8_a7205a343c568c5fe7c4619104ae78bd43279'}
        """
        clone = self.__class__(identity=self.identity)
        clone.frozen = self.frozen >> other
        return clone

    def __rxor__(self, left: Union[Random, dict, Callable, iFunctionSpace]):
        if isinstance(left, list) or callable(left):
            return iFunctionSpace(left, cop, self)
        clone = self.__class__(identity=self.identity)
        clone.frozen = left ^ self.frozen
        return clone

    def __xor__(self, other: Union[dict, AbstractLazyDict, Callable, iLet, iFunctionSpace, Random]):
        clone = self.__class__(identity=self.identity)
        clone.frozen = self.frozen ^ other
        return clone

    @property
    def all(self):
        return self.frozen.all

    @staticmethod
    def fromid(id, cache, identity=ø40):
        from idict.core.frozenidentifieddict import FrozenIdentifiedDict

        return FrozenIdentifiedDict.fromid(id, cache, identity).asmutable

    @staticmethod
    def fromfile(name, output=["df"], output_format="df", include_name=False, identity=ø40):
        from idict.core.frozenidentifieddict import FrozenIdentifiedDict

        return FrozenIdentifiedDict.fromfile(name, output, output_format, include_name, identity).asmutable

    @staticmethod
    def fromtoy(output=["X", "y"], output_format="Xy", identity=ø40):
        from idict.core.frozenidentifieddict import FrozenIdentifiedDict

        return FrozenIdentifiedDict.fromtoy(output, output_format, identity).asmutable

    @staticmethod
    def fromminiarff(output=["df"], output_format="df", identity=ø40):
        from idict.core.frozenidentifieddict import FrozenIdentifiedDict

        return FrozenIdentifiedDict.fromminiarff(output, output_format, identity).asmutable

    @staticmethod
    def fromminicsv(output=["df"], output_format="df", identity=ø40):
        from idict.core.frozenidentifieddict import FrozenIdentifiedDict

        return FrozenIdentifiedDict.fromminicsv(output, output_format, identity).asmutable

    @staticmethod
    def fromopenml(name, version=1, Xout="X", yout="y", identity=ø40):
        from idict.core.frozenidentifieddict import FrozenIdentifiedDict

        return FrozenIdentifiedDict.fromopenml(name, version, Xout, yout, identity).asmutable

    @property
    def metafields(self):
        """
        >>> from idict import idict
        >>> idict(a=1, _b=2, _c=3).metafields
        {'_b': 2, '_c': 3}
        """
        return self.frozen.metafields

    @property
    def trimmed(self):
        """
        >>> from idict import idict
        >>> idict(a=1, _b=2, _history=[1,2,3]).trimmed.show(colored=False)
        {
            "a": 1,
            "_id": "DZ_3d0ee28486d9b4f5e2fe257bc33f1266688fb",
            "_ids": {
                "a": "DZ_3d0ee28486d9b4f5e2fe257bc33f1266688fb"
            }
        }
        """
        return self.frozen.trimmed.asmutable

    def __reduce__(self):
        return self.__class__, ({k: v for k, v in self.data.items()},)

    # def wrapped(self, version, version_id):
    #     """
    #     Wrap a trimmed version of an idict object by a metafield container
    #
    #     The container is identified by `object.id * extra_field__id`.
    #
    #     >>> from idict import idict
    #     >>> d = idict(x=3, _metafield_1=5, _history={"id-of-some-previous-step----------------": 5})
    #     >>> d.show(colored=False)
    #     {
    #         "x": 3,
    #         "_metafield_1": 5,
    #         "_history": "id-of-some-previous-step----------------",
    #         "_id": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9",
    #         "_ids": {
    #             "x": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9",
    #             "_metafield_1": "KG_c33bb4404f27e9a7878b29dcb88fbd772cd8f (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
    #             "_history": "T4_254b4402e8d23be907236a140ff90245285a8 (content: VO_b2b5c7d8ff9718670723c03f0ff9028f085a8)"
    #         }
    #     }
    #     >>> e = d.wrapped("user 1", "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu")
    #     >>> e.show(colored=False)
    #     {
    #         "fields": {
    #             "x": 3,
    #             "_id": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9",
    #             "_ids": {
    #                 "x": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9"
    #             }
    #         },
    #         "version": "user 1",
    #         "_metafield_1": 5,
    #         "_history": "id-of-some-previous-step----------------",
    #         "_id": "g.0pzcYOgFTneQ8ojVDcReKkaqDuuuuuuuuuuuuu",
    #         "_ids": {
    #             "fields": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9",
    #             "version": "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu",
    #             "_metafield_1": "KG_c33bb4404f27e9a7878b29dcb88fbd772cd8f",
    #             "_history": "T4_254b4402e8d23be907236a140ff90245285a8"
    #         }
    #     }
    #     >>> d.hosh == e.fields.hosh
    #     True
    #     """
    #     return self.frozen.wrapped(version, version_id).asmutable
