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

import operator
from functools import reduce
from typing import Dict, Union

from garoupa import Hosh, removal_elem

from idict.core.frozenidentifieddict import FrozenIdentifiedDict
from idict.core.identification import fhosh, blobs_hashes_hoshes
from idict.parameter.ilet import iLet
from ldict.core.base import AbstractLazyDict


def application(self: FrozenIdentifiedDict, other, f, config_hosh, output=None):
    """
    >>> from idict import let
    >>> from garoupa import ø
    >>> d = FrozenIdentifiedDict(x=3)
    >>> f = lambda x: {"y": x**2}
    >>> f.metadata = {"id": "ffffffffffffffffffffffffffffffffffffffff"}
    >>> d2 = application(d, f, f, ø)
    >>> d2.show(colored=False)
    {
        "y": "→(x)",
        "x": 3,
        "_id": "JAsdh.I6zV6p5eiqJkTGxM4g5Dnfffffffffffff",
        "_ids": {
            "y": "23KQ2fUFGjKDTiIseYxUGS9tXqtfffffffffffff",
            "x": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9 (content: S5_331b7e710abd1443cd82d6b5cdafb9f04d5ab)"
        }
    }
    >>> d2.hosh / f.metadata["id"] == d.id
    True
    """
    f_hosh = f.metadata["id"] if hasattr(f, "metadata") and "id" in f.metadata else fhosh(f, self.identity.version)
    f_hosh_full = self.identity * config_hosh * f_hosh  # d' = d * ħ(config) * f
    if output:
        frozen = self.frozen >> {output: other}
        outputs = [output]
    else:
        frozen = self.frozen >> other
        outputs = frozen.returned
    if "_history" in outputs and ... in frozen.data["_history"]:
        frozen.data["_history"][f.hosh.id] = frozen.data["_history"].pop(...)
    uf = self.hosh * f_hosh_full
    ufu_1 = lambda: solve(self.hoshes, outputs, uf)

    # Reorder items.
    newdata, newhoshes, newblobs, newhashes, = (
        {},
        {},
        self.blobs.copy(),
        self.hashes.copy(),
    )
    noutputs = len(outputs)
    if noutputs == 1:
        k = outputs[0]
        newdata[k] = frozen.data[k]
        newhoshes[k] = ufu_1() if k in self.ids else uf * ~self.hosh
    else:
        ufu_1 = ufu_1()
        acc = self.identity
        c = 0
        last_nonmeta = None
        for k in outputs:
            if not k.startswith("_"):
                last_nonmeta = k
        for i, k in enumerate(outputs):
            newdata[k] = frozen.data[k]
            field_hosh = Hosh(f"{ufu_1.id}-{c}".encode())
            c += 1
            if k == last_nonmeta:
                field_hosh = ~acc * ufu_1
            elif not k.startswith("_"):
                acc *= field_hosh
            newhoshes[k] = field_hosh
            if k in newblobs:
                del newblobs[k]
            if k in newhashes:
                del newhashes[k]
    for k in self.ids:
        if k not in newdata:
            newhoshes[k] = self.hoshes[k]
            newdata[k] = frozen.data[k]

    cloned_internals = dict(blobs=newblobs, hashes=newhashes, hoshes=newhoshes, hosh=uf)
    return self.clone(newdata, _cloned=cloned_internals)


def ihandle_dict(self, dictlike: Union[AbstractLazyDict, dict]):
    """
    >>> from idict.core.frozenidentifieddict import FrozenIdentifiedDict as idict
    >>> d = idict(x=5, y=7, z=8)
    >>> d.show(colored=False)
    {
        "x": 5,
        "y": 7,
        "z": 8,
        "_id": "LB_8c3817cc329ce53b9a02233dbe666a9c05819",
        "_ids": {
            "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)",
            "z": "90_a163ef70987bf1f6157477ae63650fe9161cd (content: fA_de7615cbcc0d4d67bf0d85f2d59addbeccbf8)"
        }
    }
    >>> di = ihandle_dict(d, {"y":None})
    >>> di.show(colored=False)
    {
        "x": 5,
        "y": null,
        "z": 8,
        "_id": "2teR7BgSlcNN0XkG9NShsLJqLZLUp-A7p2gW8E3i",
        "_ids": {
            "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "1hDHzktW1h8pWCu7CsjgxBcPk0FUp-A7p2gW8E3i",
            "z": "90_a163ef70987bf1f6157477ae63650fe9161cd (content: fA_de7615cbcc0d4d67bf0d85f2d59addbeccbf8)"
        }
    }
    >>> di2 = ihandle_dict(di, {"w":lambda x,z: x**z})
    >>> di2.show(colored=False)  # doctest:+ELLIPSIS
    {
        "w": "→(x z)",
        "x": 5,
        "y": null,
        "z": 8,
        "_id": "Q0jOriyrlj63FL3CHO27WUS2rd350InR5ysi4Vfi",
        "_ids": {
            "w": "ZothRZe0R17sOdagBGqPouJ7ZwlcCJOJIvcoXgc0",
            "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)",
            "y": "1hDHzktW1h8pWCu7CsjgxBcPk0FUp-A7p2gW8E3i",
            "z": "90_a163ef70987bf1f6157477ae63650fe9161cd (content: fA_de7615cbcc0d4d67bf0d85f2d59addbeccbf8)"
        }
    }
    >>> ihandle_dict(di2, {"x": 55555}).show(colored=False)  # doctest:+ELLIPSIS
    {
        "w": "→(x z)",
        "x": 55555,
        "y": null,
        "z": 8,
        "_id": "fqC1B4bcNgfT9zTqPDTIBKkOfb350InR5ysi4Vfi",
        "_ids": {
            "w": "ZothRZe0R17sOdagBGqPouJ7ZwlcCJOJIvcoXgc0",
            "x": "Xs_cef5ebf024434be670eb110ae10b9067b7f69 (content: 1W_b62d995bf2d19eeb90f0f150cd45cde01a94b)",
            "y": "1hDHzktW1h8pWCu7CsjgxBcPk0FUp-A7p2gW8E3i",
            "z": "90_a163ef70987bf1f6157477ae63650fe9161cd (content: fA_de7615cbcc0d4d67bf0d85f2d59addbeccbf8)"
        }
    }
    >>> (d := ihandle_dict(idict(), {"x": 1555})).show(colored=False)
    {
        "x": 1555,
        "_id": "et_a95995634419ec27251e2f71acf2ef31109d8",
        "_ids": {
            "x": "et_a95995634419ec27251e2f71acf2ef31109d8"
        }
    }
    >>> d >>= lambda x: {"x": x**2}
    >>> d.show(colored=False)  # doctest:+ELLIPSIS
    {
        "x": "→(x)",
        "_id": "...",
        "_ids": {
            "x": "..."
        }
    }
    >>> e = idict(y=7) >> d
    >>> e.show(colored=False)  # doctest:+ELLIPSIS
    {
        "y": 7,
        "x": "→(x)",
        "_id": "kSXVu8FBqNHPSdEaa1dXgyOXI5yWX7zUjhvy-1n0",
        "_ids": {
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)",
            "x": "SSBT4S9CxTb9pCd1US4DCDlXIEwWX7zUjhvy-1n0 (content: cgNWCdJP7XKZASgpBlTRcNAJMPoMv3y0LQcFOoIK)"
        }
    }
    """
    from idict.core.frozenidentifieddict import FrozenIdentifiedDict

    clone = self.clone(rnd=dictlike.rnd) if isinstance(dictlike, AbstractLazyDict) and dictlike.rnd else self.clone()
    for k, v in dictlike.items():
        if v is None:
            clone = delete(clone, k)
        elif k not in ["_id", "_ids"]:
            if isinstance(v, iLet):
                clone = application(clone, v, v.f, v.bytes, k)
            elif callable(v):
                clone = application(clone, v, v, self.identity, k)
            else:
                internals = blobs_hashes_hoshes({k: v}, self.identity, {}, self.identity.version)
                if k in internals["blobs"]:
                    clone.blobs[k] = internals["blobs"][k]
                if k in internals["hashes"]:
                    clone.hashes[k] = internals["hashes"][k]
                clone.hoshes[k] = internals["hoshes"][k]
                hosh = reduce(
                    operator.mul, [self.identity] + [v for k, v in clone.hoshes.items() if not k.startswith("_")]
                )
                internals = dict(blobs=clone.blobs, hashes=clone.hashes, hoshes=clone.hoshes, hosh=hosh)
                del clone.data["_id"]
                del clone.data["_ids"]
                clone = FrozenIdentifiedDict(
                    clone.data, rnd=clone.rnd, identity=self.identity, _cloned=internals, **{k: v}
                )
    return clone


def placeholder(key, f_hosh, identity, hoshes: Dict[str, Hosh]):
    it = iter(hoshes.items())
    while (pair := next(it))[0] != key:
        pass
    # noinspection PyTypeChecker
    oldfield_hosh: Hosh = pair[1]
    right = identity
    for k, v in it:
        right *= v
    field_hosh = oldfield_hosh * right * f_hosh * ~right
    return field_hosh


def solve(hoshes, output, uf: Hosh):
    """
    >>> from idict.core.frozenidentifieddict import FrozenIdentifiedDict as idict
    >>> a = idict(x=3)
    >>> a.show(colored=False)
    {
        "x": 3,
        "_id": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9",
        "_ids": {
            "x": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9"
        }
    }
    >>> a >>= (lambda x: {"x": x+2})
    >>> a.show(colored=False)
    {
        "x": "→(x)",
        "_id": "y.yeWyCCKqZ36hpE39Y9pta9JiV4XkvCAtYc9OWr",
        "_ids": {
            "x": "y.yeWyCCKqZ36hpE39Y9pta9JiV4XkvCAtYc9OWr"
        }
    }
    >>> a = idict(x=3, y=5) >> (lambda x: {"x": x+2})
    >>> a.hosh == a.hoshes["x"] * a.hoshes["y"]
    True
    >>> a = idict(w=2, x=3) >> (lambda x: {"x": x+2})
    >>> a.hosh == a.hoshes["x"] * a.hoshes["w"]
    True
    >>> a = idict(w=2, x=3, z=1, y=4) >> (lambda x: {"x": x+2})
    >>> a.hosh == a.hoshes["x"] * a.hoshes["w"] * a.hoshes["z"] * a.hoshes["y"]
    True
    >>> a = idict(w=2, x=3, z=1, y=4) >> (lambda w,x,y: {"x": x+2, "a": w*x*y})
    >>> a.hosh == a.hoshes["x"] * a.hoshes["a"] * a.hoshes["w"] * a.hoshes["z"] * a.hoshes["y"]
    True
    >>> a = idict(w=2, x=3, z=1, y=4) >> (lambda w,x,y: {"x": x+2, "y": w*x*y})
    >>> a.hosh == a.hoshes["x"] * a.hoshes["y"] * a.hoshes["w"] * a.hoshes["z"]
    True
    >>> a.show(colored=False)
    {
        "x": "→(w x y)",
        "y": "→(w x y)",
        "w": 2,
        "z": 1,
        "_id": "JN-puhssoMO2iTwz8coREZG5ts9KdJ-3GBbIubB7",
        "_ids": {
            "x": "ypDxvzf3UHQIWNGWB2p5swFgn9eQOGOx5aS5yOxs",
            "y": "oDP6ovudiaAlc2aJ3JoN6tu913zpm9cyAPQBYo3H",
            "w": "Tr_9c39277012db0264069f5c777cdf5ae3c57bc (content: -B_305c3d0e44c94a5418d982f7dfe8a537a5c4b)",
            "z": "fA_f76604de6c618f2740bd6cf44b16673648837 (content: l8_09c7059156c4ed2aea46243e9d4b36c01f272)"
        }
    }
    """
    previous = uf.ø
    for k, v in hoshes.items():
        if k not in output and not k.startswith("_"):
            previous *= v
    return uf * ~previous


def delete(self, k):
    f_hosh = removal_elem(k)
    uf = self.hosh * f_hosh
    newdata = self.data.copy()
    newdata[k] = None
    newhoshes, newblobs, newhashes, = (
        self.hoshes.copy(),
        self.blobs.copy(),
        self.hashes.copy(),
    )
    newhoshes[k] = placeholder(k, f_hosh, self.identity, self.hoshes)
    if k in newblobs:
        del newblobs[k]
    if k in newhashes:
        del newhashes[k]
    return self.clone(newdata, _cloned=dict(blobs=newblobs, hashes=newhashes, hoshes=newhoshes, hosh=uf))
