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
from functools import reduce, cached_property
from operator import rshift as aop
from operator import xor as cop
from random import Random
from typing import TypeVar, Union, Callable

from garoupa import ø40, Hosh

from idict.config import GLOBAL
from idict.core.appearance import idict2txt
from idict.core.identification import blobs_hashes_hoshes
from idict.data.load import file2df
from idict.function.dataset import openml, df2Xy
from idict.parameter.ifunctionspace import iFunctionSpace, reduce3
from idict.parameter.ilet import iLet
from idict.persistence.cached import cached, get_following_pointers, build
from ldict.core.appearance import decolorize
from ldict.core.base import AbstractLazyDict, AbstractMutableLazyDict
from ldict.customjson import CustomJSONEncoder
from ldict.frozenlazydict import FrozenLazyDict

VT = TypeVar("VT")


# TODO (minor): pq frozen.keys retorna KeysView, que contem valores tb?
class FrozenIdentifiedDict(AbstractLazyDict):
    """Immutable lazy universally identified dict for serializable (picklable) pairs str->value

    Usage:

    >>> idict = FrozenIdentifiedDict
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
    >>> idict(y=88, x=123123).show(colored=False)
    {
        "y": 88,
        "x": 123123,
        "_id": "BZ_2ef6b00691651b6f815ba62b93416aa9b3e80",
        "_ids": {
            "y": "-j_34f477bff0a6dac76fe447d0e95003e273c62 (content: 6X_ceb4a9cfad6b3b5a56b49c3484be71dff692a)",
            "x": "CF_13e3494690e330a722667f4ab9e067c64022e (content: I6_bcc6fa41b424962f427be985853b8416b2cff)"
        }
    }
    >>> d = idict(x=123123, y=88)
    >>> d2 = d >> (lambda x: {"z": x**2})
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
    >>> from idict import Ø, setup
    >>> d = idict() >> {"x": "more content"}
    >>> d.show(colored=False)
    {
        "x": "more content",
        "_id": "zd_6a3f5ec407f6c5c24b89b35ff7cc1793969fd",
        "_ids": {
            "x": "zd_6a3f5ec407f6c5c24b89b35ff7cc1793969fd"
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
    >>> c = {}
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
    """

    hosh: Hosh

    # noinspection PyMissingConstructor
    def __init__(self, /, _dictionary=None, _id=None, _ids=None, rnd=None, identity=ø40, _cloned=None, **kwargs):
        self.rnd = rnd
        self.identity = identity
        data = _dictionary or {}
        data.update(kwargs)

        # Freeze mutable *dicts.
        for k, v in data.items():
            if isinstance(v, AbstractMutableLazyDict):
                data[k] = v.frozen

        if _cloned:
            self.blobs = _cloned["blobs"]
            self.hashes = _cloned["hashes"]
            self.hoshes = _cloned["hoshes"]
            self.hosh = _cloned["hosh"]
        else:
            if "_id" in data:
                if _id:  # pragma: no cover
                    raise Exception(f"Conflicting 'id' values: {_id} and {data['_id']}")
                _id = data.pop("_id")
            if "_ids" in data:
                if _ids:  # pragma: no cover
                    raise Exception(f"Conflicting 'ids' values: {_ids} and {data['_ids']}")
                _ids = data.pop("_ids")

            if _id:
                if _ids is None:  # pragma: no cover
                    raise Exception(f"'id' {_id} given, but 'ids' is missing.")
                self.blobs = {}
                self.hashes = {}
                self.hoshes = {k: identity * v for k, v in _ids.items()}
                hosh = identity * _id
            else:
                self.blobs, self.hashes, self.hoshes = blobs_hashes_hoshes(
                    data, identity, _ids or {}, self.identity.version
                ).values()
                hosh = None
            self.hosh = reduce(operator.mul, [identity] + [v for k, v in self.hoshes.items() if not k.startswith("_")])
            if hosh and hosh != self.hosh:  # pragma: no cover
                raise Exception(f"Inconsistent provided id {_id} and calculated id {self.hosh.id}")

        if _id is None:
            _id = self.hosh.id
            try:
                _ids = {k: v.id for k, v in self.hoshes.items()}
            except:  # pragma: no cover
                print(self.hoshes)
                raise Exception()

        # Store as an immutable lazy dict.
        self.frozen = FrozenLazyDict(data, _id=_id, _ids=_ids, rnd=rnd)
        self.data = self.frozen.data
        self.id = _id
        self.ids = _ids
        self.fields = list(k for k in _ids.keys() if not k.startswith("_"))

    def __getitem__(self, item):
        return self.frozen[item]

    def __setitem__(self, key: str, value):
        self.frozen[key] = value

    def __delitem__(self, key):
        del self.frozen[key]

    def __getattr__(self, item):
        """
        >>> d = FrozenIdentifiedDict(x=5)
        >>> f = lambda x: {"y": x**x, "_history": ...}
        >>> f.metadata = {"name": "function f"}
        >>> (d >> f).history
        {0: {'name': 'function f'}}
        """
        if item in self.frozen:
            return self.frozen[item]
        _item = "_" + item
        if _item in self.frozen:
            return self.frozen[_item]
        return self.__getattribute__(item)

    def evaluate(self):
        """
        >>> from idict.core.frozenidentifieddict import FrozenIdentifiedDict as idict
        >>> f = lambda x: {"y": x+2}
        >>> d = idict(x=3)
        >>> a = d >> f
        >>> a.show(colored=False)  # doctest:+ELLIPSIS
        {
            "y": "→(x)",
            "x": 3,
            "_id": "...",
            "_ids": {
                "y": "...",
                "x": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9 (content: S5_331b7e710abd1443cd82d6b5cdafb9f04d5ab)"
            }
        }
        >>> a.evaluate()
        >>> a.show(colored=False)  # doctest:+ELLIPSIS
        {
            "y": 5,
            "x": 3,
            "_id": "...",
            "_ids": {
                "y": "...",
                "x": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9 (content: S5_331b7e710abd1443cd82d6b5cdafb9f04d5ab)"
            }
        }
        """
        self.frozen.evaluate()

    @cached_property
    def asdict(self):
        """
        >>> from idict.core.frozenidentifieddict import FrozenIdentifiedDict as idict
        >>> d = idict(x=3, y=5)
        >>> d.id
        'Gm_969c1762a9edc78bf5dc236c663f77f39933b'
        >>> e = idict(x=7, y=8, d=d)
        >>> e.asdict
        {'x': 7, 'y': 8, 'd': {'x': 3, 'y': 5, '_id': 'Gm_969c1762a9edc78bf5dc236c663f77f39933b', '_ids': {'x': 'ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9', 'y': 'EI_20378979f4669f2e318ae9742e214fd4880d7'}}, '_id': 'dc_ecfbc17842ca0e082a02528315f3aee08ff89', '_ids': {'x': 'Ak_4864e8a41a20ba9d64284c45f82a491dd8065', 'y': '7Z_fb43f53bd25b4452c84de6ba3b3c5ffb29e31', 'd': 'Tk_c466af3b9f5f550ef5dc0d51663f77a9a933b'}}
        >>> d.hosh ** b"d" == e.hoshes["d"]
        True
        """
        return self.frozen.asdict

    def clone(self, data=None, rnd=None, _cloned=None):
        data = data or self.data
        _cloned = _cloned or dict(blobs=self.blobs, hashes=self.hashes, hoshes=self.hoshes, hosh=self.hosh)
        return FrozenIdentifiedDict(data, rnd=rnd or self.rnd, identity=self.identity, _cloned=_cloned)

    def __hash__(self):
        return hash(self.hosh)

    def show(self, colored=True, width=None, history=False):
        r"""
        >>> idict = FrozenIdentifiedDict
        >>> idict(x=134124, y= 56).show(colored=False)
        {
            "x": 134124,
            "y": 56,
            "_id": "bU_21d55fde35178c3c9f3a25462fa2dec2e2d59",
            "_ids": {
                "x": "ZN_236191b4a4b0a7813431289c16a415d4721dc (content: 3f_cbb9283e13010e09544692d7e1fe3224e4bae)",
                "y": "d6_28852d2a90a66aba6b09cc99090eb90e60c8c (content: mJ_7beba502c36bca4d52d8120da36c38faf3944)"
            }
        }
        """
        CustomJSONEncoder.width = width
        return print(self.__repr__(True, history) if colored else decolorize(self.__repr__(True, history)))

    def __repr__(self, all=False, history=False):
        return idict2txt(self, all, history)

    def __str__(self, all=False):
        return decolorize(idict2txt(self, all, False))

    @cached_property
    def all(self):
        r"""
        Usage:

        >>> from idict.core.frozenidentifieddict import FrozenIdentifiedDict as idict
        >>> from ldict.core.appearance import decolorize
        >>> out = idict(x=134124, y= 56).all
        >>> decolorize(out)
        '{\n    "x": 134124,\n    "y": 56,\n    "_id": "tV_c3c37026dc9a795bb61f18be755b7a8a094f2",\n    "_ids": {\n        "x": "Ad_045ef613e3a78b8b54468cccd1fe32d9f4bae (content: 3f_cbb9283e13010e09544692d7e1fe3224e4bae)",\n        "y": "UH_5e477903f808edcf52d8abe1a36c38b014944 (content: mJ_7beba502c36bca4d52d8120da36c38faf3944)"\n    }\n}'
        >>> from idict.core.frozenidentifieddict import FrozenIdentifiedDict
        >>> d = FrozenIdentifiedDict(x=5, y=7)
        >>> print(d)
        {
            "x": 5,
            "y": 7,
            "_id": "BB_fad4374ca911f344859dab8e4b016ba2fe65b",
            "_ids": "GS_cb0fda15eac732cb08351e71fc359058b93bd WK_6ba95267cec724067d58b3186ecbcaa4253ad"
        }
        """
        return self.__repr__(all=True)

    def __eq__(self, other):
        if isinstance(other, dict):
            if "_id" in other:
                return self.id == other["_id"]
            if list(self.keys())[:-2] != list(other.keys()):
                return False
        from idict.core.idict_ import Idict

        if isinstance(other, (FrozenIdentifiedDict, Idict)):
            return self.hosh == other.hosh
        if isinstance(other, AbstractLazyDict):
            if self.keys() != other.keys():
                return False
            other.evaluate()
            return self.data == other.data
        if isinstance(other, dict):
            data = self.data.copy()
            del data["_id"]
            del data["_ids"]
            return data == other
        raise TypeError(f"Cannot compare {type(self)} and {type(other)}")  # pragma: no cover

    def __rrshift__(self, left: Union[Random, dict, Callable, iFunctionSpace]):
        if isinstance(left, list) or callable(left):
            return iFunctionSpace(left, aop, self)
        if isinstance(left, dict) and not isinstance(left, AbstractLazyDict):
            return FrozenIdentifiedDict(left, identity=self.identity) >> self
        if isinstance(left, Random):
            return self.clone(rnd=left)
        return NotImplemented

    def __rshift__(
        self, other: Union[list, dict, AbstractLazyDict, "FrozenIdentifiedDict", Callable, iLet, iFunctionSpace, Random]
    ):
        from idict.core.rshift import application, ihandle_dict
        from idict.core.idict_ import Idict

        if isinstance(other, list):
            d = self
            for cache in other:
                if isinstance(cache, list):
                    if len(cache) == 0:  # pragma: no cover
                        raise Exception("Missing content inside list for caching.")
                    elif len(cache) > 1:  # pragma: no cover
                        raise Exception(f"Cannot have more than one cache within a nested list: {cache} in {other}.")
                    cache = cache[0]
                    d.evaluate()
                d = cached(d, cache)
            return d
        if isinstance(other, (Idict, FrozenIdentifiedDict)):
            clone = self.clone(rnd=other.rnd) if other.rnd else self.clone()
            for k, v in other.data.items():
                if k not in ["_id", "_ids"]:
                    clone.data[k] = v
                    if k in other.blobs:
                        clone.blobs[k] = other.blobs[k]
                    if k in other.hashes:
                        clone.hashes[k] = other.hashes[k]
                    clone.hoshes[k] = other.hoshes[k]
            hosh = reduce(operator.mul, [self.identity] + [v for k, v in clone.hoshes.items() if not k.startswith("_")])
            internals = dict(blobs=clone.blobs, hashes=clone.hashes, hoshes=clone.hoshes, hosh=hosh)
            del clone.data["_id"]
            del clone.data["_ids"]
            return FrozenIdentifiedDict(clone.data, rnd=clone.rnd, identity=self.identity, _cloned=internals, **{k: v})
        if isinstance(other, dict):
            return ihandle_dict(self, other)
        if isinstance(other, Random):
            return self.clone(rnd=other)
        if isinstance(other, iLet):
            return application(self, other, other.f, other.bytes)
        if callable(other):
            return application(self, other, other, self.identity)
        if isinstance(other, iFunctionSpace):
            return reduce3(lambda a, op, b: op(a, b), (self, aop) + other.functions_and_ops)
        return NotImplemented

    def __rxor__(self, left: Union[Random, dict, Callable, iFunctionSpace]):
        if (isinstance(left, (dict, list, Random)) or callable(left)) and not isinstance(left, AbstractLazyDict):
            return iFunctionSpace(left, cop, self)
        return NotImplemented

    def __xor__(self, other: Union[dict, AbstractLazyDict, Callable, iLet, iFunctionSpace, Random]):
        if callable(other) or isinstance(other, (dict, Random, list, iLet)):
            return cached(self, GLOBAL["cache"]) >> other
        if isinstance(other, iFunctionSpace):
            return reduce3(lambda a, op, b: op(a, b), (self, cop) + other.functions_and_ops)
        return NotImplemented

    @cached_property
    def metafields(self):
        return {k: v for k, v in self.items() if k.startswith("_") and k not in ["_id", "_ids"]}

    @cached_property
    def trimmed(self):
        ids = self.ids.copy()
        data = self.data.copy()
        blobs = self.blobs.copy()
        hashes = self.hashes.copy()
        hoshes = self.hoshes.copy()
        for k in self.ids:
            if k.startswith("_"):
                del ids[k]
                del data[k]
                if k in blobs:
                    del blobs[k]
                if k in hashes:
                    del hashes[k]
                del hoshes[k]
        data["_ids"] = ids
        cloned_internals = dict(blobs=blobs, hashes=hashes, hoshes=hoshes, hosh=self.hosh)
        return self.clone(data, _cloned=cloned_internals)

    # def wrapped(self, version, version_id):
    #     """Wrap a trimmed version of an idict object by a metafield container"""
    #     hosh = self.hosh * version_id
    #     ids = dict(fields=self.id, version=version_id)
    #     if not self.metafields:
    #         raise Exception(f"There are no metafields for {self.id}")
    #     for mfkey in self.metafields.keys():
    #         ids[mfkey] = self.ids[mfkey]
    #     return FrozenIdentifiedDict(fields=self.trimmed, version=version, _id=hosh.id, _ids=ids, **self.metafields)

    @staticmethod
    def fromid(id, cache, identity=ø40) -> Union["FrozenIdentifiedDict", None]:
        """
        >>> from idict import idict
        >>> cache = {}
        >>> d = idict(x=5) >> (lambda x: {"y": x**2}) >> [cache]
        >>> d.show(colored=False)  # doctest:+ELLIPSIS
        {
            "y": "→(↑ x)",
            "x": 5,
            "_id": "...",
            "_ids": {
                "y": "...",
                "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)"
            }
        }
        >>> d.y
        25
        >>> cache  # doctest:+ELLIPSIS
        {'...': 25, 'GS_cb0fda15eac732cb08351e71fc359058b93bd': 5, '...': {'_id': '...', '_ids': {'y': '...', 'x': 'GS_cb0fda15eac732cb08351e71fc359058b93bd'}}}
        >>> d2 = idict.fromid(d.id, cache)
        >>> d2.show(colored=False)  # doctest:+ELLIPSIS
        {
            "y": "→(↑)",
            "x": "→(↑)",
            "_id": "...",
            "_ids": {
                "y": "...",
                "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)"
            }
        }
        >>> d2.evaluated.show(colored=False)  # doctest:+ELLIPSIS
        {
            "y": 25,
            "x": 5,
            "_id": "...",
            "_ids": {
                "y": "...",
                "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd (content: Mj_3bcd9aefb5020343384ae8ccb88fbd872cd8f)"
            }
        }
        >>> d == d2
        True
        """
        if hasattr(cache, "user_hosh") and not id.startswith("_"):
            id2 = (id * cache.user_hosh).id
        else:
            id2 = "_" + id[1:]
        val = get_following_pointers(id2, cache)
        isdescriptor = isinstance(val, dict) and "_id" in val and "_ids" in val
        if val is None or not isdescriptor:  # pragma: no cover
            raise Exception(f"Could not find {id} / {id2}")
        return build(val["_id"], val["_ids"], cache, identity)

    @staticmethod
    def fromfile(name, output=None, output_format="df", include_name=False, identity=ø40):
        """Input format is defined by file extension: .arff, .csv
        >>> d = FrozenIdentifiedDict.fromminiarff()
        >>> d.show(colored=False)
        {
            "df": "«{'attr1@REAL': {0: 5.1, 1: 3.1}, 'attr2@REAL': {0: 3.5, 1: 4.5}, 'class@{0,1}': {0: '0', 1: '1'}}»",
            "_id": "q3_b71eb05c4be05eba7b6ae5a9245d5dd70b81b",
            "_ids": {
                "df": "q3_b71eb05c4be05eba7b6ae5a9245d5dd70b81b"
            }
        }
        >>> d.df.head()
           attr1@REAL  attr2@REAL class@{0,1}
        0         5.1         3.5           0
        1         3.1         4.5           1
        >>> d = FrozenIdentifiedDict.fromminicsv()
        >>> d.show(colored=False)
        {
            "df": "«{'attr1': {0: 5.1, 1: 3.1}, 'attr2': {0: 3.5, 1: 4.5}, 'class': {0: 0, 1: 1}}»",
            "_id": "xi_834a466f79b489b25239a6ac4004bbb9d2f8d",
            "_ids": {
                "df": "xi_834a466f79b489b25239a6ac4004bbb9d2f8d"
            }
        }
        >>> d.df.head()
           attr1  attr2  class
        0    5.1    3.5      0
        1    3.1    4.5      1
        >>> d = FrozenIdentifiedDict.fromminicsv(output=["X","y"], output_format="Xy")
        >>> d.show(colored=False)
        {
            "X": "«{'attr1': {0: 5.1, 1: 3.1}, 'attr2': {0: 3.5, 1: 4.5}}»",
            "y": "«[0 1]»",
            "_id": "4t_4c4af5afee07d07b07845855f8f249110a165",
            "_ids": {
                "X": "gZ_6d7dc2c290f446d5ac0990aee84f0dd98f8f7 (content: ZP_912089147b5e2b7781b12dc1523c3ad10f3a6)",
                "y": "Pv_a5a0391d5ea00d136a7bddb110b33c816a86d (content: Y6_6addb35449620638514b7cf9aa02ba440e525)"
            }
        }
        """
        if output is None:
            output = ["df"]
        df, name = file2df(name)
        metafields = {"_name": name} if include_name else {}
        if output_format == "df":
            if output == ["X", "y"]:
                output = ["df"]
            if len(output) != 1:  # pragma: no cover
                raise Exception(f"Wrong number of fields {len(output)}. Expected: 1.", output)
            return FrozenIdentifiedDict({output[0]: df}, identity=identity, **metafields)
        elif output_format == "Xy":
            if output == ["df"]:
                output = ["X", "y"]
            if len(output) != 2:  # pragma: no cover
                raise Exception(f"Wrong number of fields {len(output)}. Expected: 2.", output)
            dic = df2Xy(df=df)
            del dic["_history"]
            return FrozenIdentifiedDict({output[0]: dic["X"], output[1]: dic["y"]}, identity=identity, **metafields)
        else:  # pragma: no cover
            raise Exception(f"Unknown {output_format=}.")

    @staticmethod
    def fromtoy(output=["X", "y"], output_format="Xy", identity=ø40):
        from testfixtures import TempDirectory

        with TempDirectory() as tmp:
            tmp.write(
                "toy.csv",
                b"attr1,attr2,class\n5.1,6.4,0\n1.1,2.5,1\n6.1,3.6,0\n1.1,3.5,1\n3.1,2.5,0\n4.7,4.9,1\n9.1,3.5,0\n8.3,2.9,1\n9.1,7.2,0\n2.5,4.5,1\n7.1,6.6,0\n0.1,4.3,1\n2.1,0.1,0\n0.1,4.0,1\n5.1,4.5,0\n31.1,4.7,1\n1.1,3.2,0\n2.2,8.5,1\n3.1,2.5,0\n1.1,8.5,1",
            )
            return FrozenIdentifiedDict.fromfile(tmp.path + "/toy.csv", output, output_format, identity=identity)

    @staticmethod
    def fromminiarff(output=["df"], output_format="df", identity=ø40):
        from testfixtures import TempDirectory

        arff = "@RELATION mini\n@ATTRIBUTE attr1	REAL\n@ATTRIBUTE attr2 	REAL\n@ATTRIBUTE class 	{0,1}\n@DATA\n5.1,3.5,0\n3.1,4.5,1"
        if output_format == "arff":
            if output == ["df"]:
                output = ["arff"]
            if len(output) != 1:  # pragma: no cover
                raise Exception(f"Wrong number of fields {len(output)}. Expected: 1.", output)
            return FrozenIdentifiedDict({output[0]: arff}, identity=identity)
        with TempDirectory() as tmp:
            tmp.write(
                "mini.arff",
                arff.encode(),
            )
            return FrozenIdentifiedDict.fromfile(tmp.path + "/mini.arff", output, output_format, identity=identity)

    @staticmethod
    def fromminicsv(output=["df"], output_format="df", identity=ø40):
        from testfixtures import TempDirectory

        csv = "attr1,attr2,class\n5.1,3.5,0\n3.1,4.5,1"
        if output_format == "csv":
            if output == ["df"]:
                output = ["csv"]
            if len(output) != 1:  # pragma: no cover
                raise Exception(f"Wrong number of fields {len(output)}. Expected: 1.", output)
            return FrozenIdentifiedDict({output[0]: csv}, identity=identity)
        with TempDirectory() as tmp:
            tmp.write("mini.csv", csv.encode())
            return FrozenIdentifiedDict.fromfile(tmp.path + "/mini.csv", output, output_format, identity=identity)

    @staticmethod
    def fromopenml(name, version=1, Xout="X", yout="y", identity=ø40):
        """
        >>> FrozenIdentifiedDict.fromopenml("iris").show(colored=False)
        {
            "X": "«{'sepallength': {0: 5.1, 1: 4.9, 2: 4.7, 3: 4.6, 4: 5.0, 5: 5.4, 6: 4.6, 7: 5.0, 8: 4.4, 9: 4.9, 10: 5.4, 11: 4.8, 12: 4.8, 13: 4.3, 14: 5.8, 15: 5.7, 16: 5.4, 17: 5.1, 18: 5.7, 19: 5.1, 20: 5.4, 21: 5.1, 22: 4.6, 23: 5.1, 24: 4.8, 25: 5.0, 26: 5.0, 27: 5.2, 28: 5.2, 29: 4.7, 30: 4.8, 31: 5.4, 32: 5.2, 33: 5.5, 34: 4.9, 35: 5.0, 36: 5.5, 37: 4.9, 38: 4.4, 39: 5.1, 40: 5.0, 41: 4.5, 42: 4.4, 43: 5.0, 44: 5.1, 45: 4.8, 46: 5.1, 47: 4.6, 48: 5.3, 49: 5.0, 50: 7.0, 51: 6.4, 52: 6.9, 53: 5.5, 54: 6.5, 55: 5.7, 56: 6.3, 57: 4.9, 58: 6.6, 59: 5.2, 60: 5.0, 61: 5.9, 62: 6.0, 63: 6.1, 64: 5.6, 65: 6.7, 66: 5.6, 67: 5.8, 68: 6.2, 69: 5.6, 70: 5.9, 71: 6.1, 72: 6.3, 73: 6.1, 74: 6.4, 75: 6.6, 76: 6.8, 77: 6.7, 78: 6.0, 79: 5.7, 80: 5.5, 81: 5.5, 82: 5.8, 83: 6.0, 84: 5.4, 85: 6.0, 86: 6.7, 87: 6.3, 88: 5.6, 89: 5.5, 90: 5.5, 91: 6.1, 92: 5.8, 93: 5.0, 94: 5.6, 95: 5.7, 96: 5.7, 97: 6.2, 98: 5.1, 99: 5.7, 100: 6.3, 101: 5.8, 102: 7.1, 103: 6.3, 104: 6.5, 105: 7.6, 106: 4.9, 107: 7.3, 108: 6.7, 109: 7.2, 110: 6.5, 111: 6.4, 112: 6.8, 113: 5.7, 114: 5.8, 115: 6.4, 116: 6.5, 117: 7.7, 118: 7.7, 119: 6.0, 120: 6.9, 121: 5.6, 122: 7.7, 123: 6.3, 124: 6.7, 125: 7.2, 126: 6.2, 127: 6.1, 128: 6.4, 129: 7.2, 130: 7.4, 131: 7.9, 132: 6.4, 133: 6.3, 134: 6.1, 135: 7.7, 136: 6.3, 137: 6.4, 138: 6.0, 139: 6.9, 140: 6.7, 141: 6.9, 142: 5.8, 143: 6.8, 144: 6.7, 145: 6.7, 146: 6.3, 147: 6.5, 148: 6.2, 149: 5.9}, 'sepalwidth': {0: 3.5, 1: 3.0, 2: 3.2, 3: 3.1, 4: 3.6, 5: 3.9, 6: 3.4, 7: 3.4, 8: 2.9, 9: 3.1, 10: 3.7, 11: 3.4, 12: 3.0, 13: 3.0, 14: 4.0, 15: 4.4, 16: 3.9, 17: 3.5, 18: 3.8, 19: 3.8, 20: 3.4, 21: 3.7, 22: 3.6, 23: 3.3, 24: 3.4, 25: 3.0, 26: 3.4, 27: 3.5, 28: 3.4, 29: 3.2, 30: 3.1, 31: 3.4, 32: 4.1, 33: 4.2, 34: 3.1, 35: 3.2, 36: 3.5, 37: 3.1, 38: 3.0, 39: 3.4, 40: 3.5, 41: 2.3, 42: 3.2, 43: 3.5, 44: 3.8, 45: 3.0, 46: 3.8, 47: 3.2, 48: 3.7, 49: 3.3, 50: 3.2, 51: 3.2, 52: 3.1, 53: 2.3, 54: 2.8, 55: 2.8, 56: 3.3, 57: 2.4, 58: 2.9, 59: 2.7, 60: 2.0, 61: 3.0, 62: 2.2, 63: 2.9, 64: 2.9, 65: 3.1, 66: 3.0, 67: 2.7, 68: 2.2, 69: 2.5, 70: 3.2, 71: 2.8, 72: 2.5, 73: 2.8, 74: 2.9, 75: 3.0, 76: 2.8, 77: 3.0, 78: 2.9, 79: 2.6, 80: 2.4, 81: 2.4, 82: 2.7, 83: 2.7, 84: 3.0, 85: 3.4, 86: 3.1, 87: 2.3, 88: 3.0, 89: 2.5, 90: 2.6, 91: 3.0, 92: 2.6, 93: 2.3, 94: 2.7, 95: 3.0, 96: 2.9, 97: 2.9, 98: 2.5, 99: 2.8, 100: 3.3, 101: 2.7, 102: 3.0, 103: 2.9, 104: 3.0, 105: 3.0, 106: 2.5, 107: 2.9, 108: 2.5, 109: 3.6, 110: 3.2, 111: 2.7, 112: 3.0, 113: 2.5, 114: 2.8, 115: 3.2, 116: 3.0, 117: 3.8, 118: 2.6, 119: 2.2, 120: 3.2, 121: 2.8, 122: 2.8, 123: 2.7, 124: 3.3, 125: 3.2, 126: 2.8, 127: 3.0, 128: 2.8, 129: 3.0, 130: 2.8, 131: 3.8, 132: 2.8, 133: 2.8, 134: 2.6, 135: 3.0, 136: 3.4, 137: 3.1, 138: 3.0, 139: 3.1, 140: 3.1, 141: 3.1, 142: 2.7, 143: 3.2, 144: 3.3, 145: 3.0, 146: 2.5, 147: 3.0, 148: 3.4, 149: 3.0}, 'petallength': {0: 1.4, 1: 1.4, 2: 1.3, 3: 1.5, 4: 1.4, 5: 1.7, 6: 1.4, 7: 1.5, 8: 1.4, 9: 1.5, 10: 1.5, 11: 1.6, 12: 1.4, 13: 1.1, 14: 1.2, 15: 1.5, 16: 1.3, 17: 1.4, 18: 1.7, 19: 1.5, 20: 1.7, 21: 1.5, 22: 1.0, 23: 1.7, 24: 1.9, 25: 1.6, 26: 1.6, 27: 1.5, 28: 1.4, 29: 1.6, 30: 1.6, 31: 1.5, 32: 1.5, 33: 1.4, 34: 1.5, 35: 1.2, 36: 1.3, 37: 1.5, 38: 1.3, 39: 1.5, 40: 1.3, 41: 1.3, 42: 1.3, 43: 1.6, 44: 1.9, 45: 1.4, 46: 1.6, 47: 1.4, 48: 1.5, 49: 1.4, 50: 4.7, 51: 4.5, 52: 4.9, 53: 4.0, 54: 4.6, 55: 4.5, 56: 4.7, 57: 3.3, 58: 4.6, 59: 3.9, 60: 3.5, 61: 4.2, 62: 4.0, 63: 4.7, 64: 3.6, 65: 4.4, 66: 4.5, 67: 4.1, 68: 4.5, 69: 3.9, 70: 4.8, 71: 4.0, 72: 4.9, 73: 4.7, 74: 4.3, 75: 4.4, 76: 4.8, 77: 5.0, 78: 4.5, 79: 3.5, 80: 3.8, 81: 3.7, 82: 3.9, 83: 5.1, 84: 4.5, 85: 4.5, 86: 4.7, 87: 4.4, 88: 4.1, 89: 4.0, 90: 4.4, 91: 4.6, 92: 4.0, 93: 3.3, 94: 4.2, 95: 4.2, 96: 4.2, 97: 4.3, 98: 3.0, 99: 4.1, 100: 6.0, 101: 5.1, 102: 5.9, 103: 5.6, 104: 5.8, 105: 6.6, 106: 4.5, 107: 6.3, 108: 5.8, 109: 6.1, 110: 5.1, 111: 5.3, 112: 5.5, 113: 5.0, 114: 5.1, 115: 5.3, 116: 5.5, 117: 6.7, 118: 6.9, 119: 5.0, 120: 5.7, 121: 4.9, 122: 6.7, 123: 4.9, 124: 5.7, 125: 6.0, 126: 4.8, 127: 4.9, 128: 5.6, 129: 5.8, 130: 6.1, 131: 6.4, 132: 5.6, 133: 5.1, 134: 5.6, 135: 6.1, 136: 5.6, 137: 5.5, 138: 4.8, 139: 5.4, 140: 5.6, 141: 5.1, 142: 5.1, 143: 5.9, 144: 5.7, 145: 5.2, 146: 5.0, 147: 5.2, 148: 5.4, 149: 5.1}, 'petalwidth': {0: 0.2, 1: 0.2, 2: 0.2, 3: 0.2, 4: 0.2, 5: 0.4, 6: 0.3, 7: 0.2, 8: 0.2, 9: 0.1, 10: 0.2, 11: 0.2, 12: 0.1, 13: 0.1, 14: 0.2, 15: 0.4, 16: 0.4, 17: 0.3, 18: 0.3, 19: 0.3, 20: 0.2, 21: 0.4, 22: 0.2, 23: 0.5, 24: 0.2, 25: 0.2, 26: 0.4, 27: 0.2, 28: 0.2, 29: 0.2, 30: 0.2, 31: 0.4, 32: 0.1, 33: 0.2, 34: 0.1, 35: 0.2, 36: 0.2, 37: 0.1, 38: 0.2, 39: 0.2, 40: 0.3, 41: 0.3, 42: 0.2, 43: 0.6, 44: 0.4, 45: 0.3, 46: 0.2, 47: 0.2, 48: 0.2, 49: 0.2, 50: 1.4, 51: 1.5, 52: 1.5, 53: 1.3, 54: 1.5, 55: 1.3, 56: 1.6, 57: 1.0, 58: 1.3, 59: 1.4, 60: 1.0, 61: 1.5, 62: 1.0, 63: 1.4, 64: 1.3, 65: 1.4, 66: 1.5, 67: 1.0, 68: 1.5, 69: 1.1, 70: 1.8, 71: 1.3, 72: 1.5, 73: 1.2, 74: 1.3, 75: 1.4, 76: 1.4, 77: 1.7, 78: 1.5, 79: 1.0, 80: 1.1, 81: 1.0, 82: 1.2, 83: 1.6, 84: 1.5, 85: 1.6, 86: 1.5, 87: 1.3, 88: 1.3, 89: 1.3, 90: 1.2, 91: 1.4, 92: 1.2, 93: 1.0, 94: 1.3, 95: 1.2, 96: 1.3, 97: 1.3, 98: 1.1, 99: 1.3, 100: 2.5, 101: 1.9, 102: 2.1, 103: 1.8, 104: 2.2, 105: 2.1, 106: 1.7, 107: 1.8, 108: 1.8, 109: 2.5, 110: 2.0, 111: 1.9, 112: 2.1, 113: 2.0, 114: 2.4, 115: 2.3, 116: 1.8, 117: 2.2, 118: 2.3, 119: 1.5, 120: 2.3, 121: 2.0, 122: 2.0, 123: 1.8, 124: 2.1, 125: 1.8, 126: 1.8, 127: 1.8, 128: 2.1, 129: 1.6, 130: 1.9, 131: 2.0, 132: 2.2, 133: 1.5, 134: 1.4, 135: 2.3, 136: 2.4, 137: 1.8, 138: 1.8, 139: 2.1, 140: 2.4, 141: 2.3, 142: 1.9, 143: 2.3, 144: 2.5, 145: 2.3, 146: 1.9, 147: 2.0, 148: 2.3, 149: 1.8}}»",
            "y": "«{0: 'Iris-setosa', 1: 'Iris-setosa', 2: 'Iris-setosa', 3: 'Iris-setosa', 4: 'Iris-setosa', 5: 'Iris-setosa', 6: 'Iris-setosa', 7: 'Iris-setosa', 8: 'Iris-setosa', 9: 'Iris-setosa', 10: 'Iris-setosa', 11: 'Iris-setosa', 12: 'Iris-setosa', 13: 'Iris-setosa', 14: 'Iris-setosa', 15: 'Iris-setosa', 16: 'Iris-setosa', 17: 'Iris-setosa', 18: 'Iris-setosa', 19: 'Iris-setosa', 20: 'Iris-setosa', 21: 'Iris-setosa', 22: 'Iris-setosa', 23: 'Iris-setosa', 24: 'Iris-setosa', 25: 'Iris-setosa', 26: 'Iris-setosa', 27: 'Iris-setosa', 28: 'Iris-setosa', 29: 'Iris-setosa', 30: 'Iris-setosa', 31: 'Iris-setosa', 32: 'Iris-setosa', 33: 'Iris-setosa', 34: 'Iris-setosa', 35: 'Iris-setosa', 36: 'Iris-setosa', 37: 'Iris-setosa', 38: 'Iris-setosa', 39: 'Iris-setosa', 40: 'Iris-setosa', 41: 'Iris-setosa', 42: 'Iris-setosa', 43: 'Iris-setosa', 44: 'Iris-setosa', 45: 'Iris-setosa', 46: 'Iris-setosa', 47: 'Iris-setosa', 48: 'Iris-setosa', 49: 'Iris-setosa', 50: 'Iris-versicolor', 51: 'Iris-versicolor', 52: 'Iris-versicolor', 53: 'Iris-versicolor', 54: 'Iris-versicolor', 55: 'Iris-versicolor', 56: 'Iris-versicolor', 57: 'Iris-versicolor', 58: 'Iris-versicolor', 59: 'Iris-versicolor', 60: 'Iris-versicolor', 61: 'Iris-versicolor', 62: 'Iris-versicolor', 63: 'Iris-versicolor', 64: 'Iris-versicolor', 65: 'Iris-versicolor', 66: 'Iris-versicolor', 67: 'Iris-versicolor', 68: 'Iris-versicolor', 69: 'Iris-versicolor', 70: 'Iris-versicolor', 71: 'Iris-versicolor', 72: 'Iris-versicolor', 73: 'Iris-versicolor', 74: 'Iris-versicolor', 75: 'Iris-versicolor', 76: 'Iris-versicolor', 77: 'Iris-versicolor', 78: 'Iris-versicolor', 79: 'Iris-versicolor', 80: 'Iris-versicolor', 81: 'Iris-versicolor', 82: 'Iris-versicolor', 83: 'Iris-versicolor', 84: 'Iris-versicolor', 85: 'Iris-versicolor', 86: 'Iris-versicolor', 87: 'Iris-versicolor', 88: 'Iris-versicolor', 89: 'Iris-versicolor', 90: 'Iris-versicolor', 91: 'Iris-versicolor', 92: 'Iris-versicolor', 93: 'Iris-versicolor', 94: 'Iris-versicolor', 95: 'Iris-versicolor', 96: 'Iris-versicolor', 97: 'Iris-versicolor', 98: 'Iris-versicolor', 99: 'Iris-versicolor', 100: 'Iris-virginica', 101: 'Iris-virginica', 102: 'Iris-virginica', 103: 'Iris-virginica', 104: 'Iris-virginica', 105: 'Iris-virginica', 106: 'Iris-virginica', 107: 'Iris-virginica', 108: 'Iris-virginica', 109: 'Iris-virginica', 110: 'Iris-virginica', 111: 'Iris-virginica', 112: 'Iris-virginica', 113: 'Iris-virginica', 114: 'Iris-virginica', 115: 'Iris-virginica', 116: 'Iris-virginica', 117: 'Iris-virginica', 118: 'Iris-virginica', 119: 'Iris-virginica', 120: 'Iris-virginica', 121: 'Iris-virginica', 122: 'Iris-virginica', 123: 'Iris-virginica', 124: 'Iris-virginica', 125: 'Iris-virginica', 126: 'Iris-virginica', 127: 'Iris-virginica', 128: 'Iris-virginica', 129: 'Iris-virginica', 130: 'Iris-virginica', 131: 'Iris-virginica', 132: 'Iris-virginica', 133: 'Iris-virginica', 134: 'Iris-virginica', 135: 'Iris-virginica', 136: 'Iris-virginica', 137: 'Iris-virginica', 138: 'Iris-virginica', 139: 'Iris-virginica', 140: 'Iris-virginica', 141: 'Iris-virginica', 142: 'Iris-virginica', 143: 'Iris-virginica', 144: 'Iris-virginica', 145: 'Iris-virginica', 146: 'Iris-virginica', 147: 'Iris-virginica', 148: 'Iris-virginica', 149: 'Iris-virginica'}»",
            "_id": "AO_67ebfa77bd43293a189802abb8113845e87b9",
            "_ids": {
                "X": "d1_683d4d10ceb4fdb95b7898281e92fd0cb5751 (content: WT_acc04682d46ccfd830218b66878f1b4e15200)",
                "y": "nN_b3cf0d57fedea080cc103963aa7e3a4923068 (content: wo_4ff9923fa3652495b3ef18bb35dcb8fbc6d10)"
            }
        }
        """
        dic = openml(Xout, yout, name, version)
        del dic["_history"]
        return FrozenIdentifiedDict(dic, identity=identity)

    @property
    def asmutable(self):
        from idict.core.idict_ import Idict

        return Idict(self, identity=self.identity)

    def __reduce__(self):
        return self.__class__, ({k: v for k, v in self.data.items()},)
