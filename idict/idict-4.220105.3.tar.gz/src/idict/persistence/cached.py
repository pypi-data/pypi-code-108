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

from ldict.core.base import AbstractLazyDict
from ldict.lazyval import LazyVal


# TODO: store metafield even if idict-id is already stored
def storevalue_func(cache):
    def f(k, id, value):
        cache[id] = value

    return f


def storeblob_func(cache, blobs):
    def f(k, id, value):
        if k in blobs:
            cache.setblob(id, blobs[k])
        else:
            cache[id] = value

    return f


def cached(d, cache) -> AbstractLazyDict:
    """
    Store each value (fid: value) and an extra value containing the fids (did: {"_id": did, "_ids": fids}).
    When the dict is a singleton, we have to use "_"+id[1:] as dict id to workaround the ambiguity did=fid.

    Lock the id during the job, to avoid duplicate jobs in a distributed system, if supported by the provided cache.
    """
    # TODO: gravar hashes como aliases no cache pros hoshes. tb recuperar. [serve p/ poupar espaço. e tráfego se usar duplo cache local-remoto]
    #  mas hash não é antecipável! 'cached' teria de fazer o ponteiro: ho -> {"_id": ". . ."}.  aproveitar pack() para guardar todo valor assim.
    from idict.core.idict_ import Idict
    from idict.core.frozenidentifieddict import FrozenIdentifiedDict

    # TODO (minor): do the same for fetch(). useful in the future if needed to speedup syncing of caches avoiding *pack
    store = storeblob_func(cache, d.blobs) if hasattr(cache, "setblob") else storevalue_func(cache)
    front_id = "_" + d.id[1:]

    def closure(outputf, fid, fids, data, output_fields, id):
        def func(**kwargs):
            # Try loading.
            if fid in cache:
                return get_following_pointers(fid, cache)

            # Lock the id for this job.
            if hasattr(cache, "lock"):
                if (t := cache.lockid(fid)) is not None:
                    raise LockedEntryException(f"There is already a job producing the data {fid}, since {t}.")

            # Process and save (all fields, to avoid a parcial idict being stored).
            k = None
            changed = False
            for k, v in fids.items():
                if isinstance(data[k], LazyVal):
                    data[k] = data[k](**kwargs)
                if isinstance(data[k], (FrozenIdentifiedDict, Idict)):
                    cache[v] = {"_id": "_" + data[k].id[1:]}
                    data[k] = cached(data[k], cache)
                    changed = True
                elif v not in cache:
                    store(k, v, data[k])
                    changed = True
            if (result := data[outputf]) is None:  # pragma: no cover
                if k is None:
                    raise Exception(f"No ids")
                raise Exception(f"Key {k} not in output fields: {output_fields}. ids: {fids.items()}")

            front_id_ = front_id
            if hasattr(cache, "user_hosh"):
                # print("has hosh", d.id)
                if front_id_ in cache and changed:
                    del cache[front_id_]
                if front_id_ not in cache:
                    cache[front_id_] = {"_id": id, "_ids": {k: v for k, v in fids.items() if not k.startswith("_")}}
                front_id_ = (d.id * cache.user_hosh).id
            cache[front_id_] = {"_id": id, "_ids": fids}

            # Unlock id.
            if hasattr(cache, "unlock"):
                cache.unlockid(fid)
            return result

        return func

    data = d.data.copy()
    lazies = False
    output_fields = []
    for field, v in list(data.items()):
        if isinstance(v, LazyVal):
            # REMINDER: Check removed because metafield values recovered from cache are lazy.
            # if field.startswith("_"):  # pragma: no cover
            #     raise Exception("Cannot have a lazy value in a metafield.", field)
            output_fields.append(field)
            lazies = True
            id = d.hashes[field].id if field in d.hashes else d.hoshes[field].id
            deps = {"↑": None}
            deps.update(v.deps)
            lazy = LazyVal(field, closure(field, id, d.ids, d.data, output_fields, d.id), deps, data, None)
            data[field] = lazy

    # Eager saving when there are no lazies.
    if not lazies:
        changed = False
        for k, fid in d.ids.items():
            if fid not in cache:
                if isinstance(data[k], (FrozenIdentifiedDict, Idict)):
                    cache[fid] = {"_id": "_" + data[k].id[1:]}
                    data[k] = cached(data[k], cache)
                else:
                    store(k, fid, data[k])
                changed = True
        front_id_ = (d.id * cache.user_hosh).id if hasattr(cache, "user_hosh") else front_id
        if front_id_ in cache and changed:
            del cache[front_id_]
        if front_id_ not in cache:
            if hasattr(cache, "user_hosh"):
                cache[front_id_] = {"_id": d.id, "_ids": {k: v for k, v in d.ids.items() if not k.startswith("_")}}
            else:
                cache[front_id_] = {"_id": d.id, "_ids": d.ids}

    return d.clone(data)


def build(id, ids, cache, identity, include_blobs=False):
    """Build an idict from a given identity

    >>> from idict import idict
    >>> a = idict(x=5,z=9)
    >>> b = idict(y=7)
    >>> b["d"] = a
    >>> b >>= [cache := {}]
    >>> print(json.dumps(cache, indent=2))
    {
      "WK_6ba95267cec724067d58b3186ecbcaa4253ad": 7,
      "u9_698c410308e557c005cda07ba00c564152401": {
        "_id": "_._72191dfc2ed7d9ff4c35d514b103ac114161f"
      },
      "GS_cb0fda15eac732cb08351e71fc359058b93bd": 5,
      "N8_524991e7434b2d3444007782c4cd0cd887261": 9,
      "_._72191dfc2ed7d9ff4c35d514b103ac114161f": {
        "_id": "r._72191dfc2ed7d9ff4c35d514b103ac114161f",
        "_ids": {
          "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd",
          "z": "N8_524991e7434b2d3444007782c4cd0cd887261"
        }
      },
      "_U_ab54a36ac6988bc6722654831fc721f5777ae": {
        "_id": "oU_ab54a36ac6988bc6722654831fc721f5777ae",
        "_ids": {
          "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad",
          "d": "u9_698c410308e557c005cda07ba00c564152401"
        }
      }
    }
    >>> build(b.id, b.ids, cache, b.hosh.ø).evaluated.show(colored=False)
    {
        "y": 7,
        "d": {
            "x": 5,
            "z": 9,
            "_id": "r._72191dfc2ed7d9ff4c35d514b103ac114161f",
            "_ids": {
                "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd",
                "z": "N8_524991e7434b2d3444007782c4cd0cd887261"
            }
        },
        "_id": "oU_ab54a36ac6988bc6722654831fc721f5777ae",
        "_ids": {
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)",
            "d": "u9_698c410308e557c005cda07ba00c564152401 (content: r._72191dfc2ed7d9ff4c35d514b103ac114161f)"
        }
    }
    >>> (a.hosh ** b"d").show(colored=False)
    u9_698c410308e557c005cda07ba00c564152401
    >>> a = idict(x=5)
    >>> b = idict(y=7)
    >>> b["d"] = a
    >>> b >>= [cache := {}]
    >>> print(json.dumps(cache, indent=2))
    {
      "WK_6ba95267cec724067d58b3186ecbcaa4253ad": 7,
      "I0_dac96298c4c5bf8cb0cde8d8eb3e4a78ca1af": {
        "_id": "_S_cb0fda15eac732cb08351e71fc359058b93bd"
      },
      "GS_cb0fda15eac732cb08351e71fc359058b93bd": 5,
      "_S_cb0fda15eac732cb08351e71fc359058b93bd": {
        "_id": "GS_cb0fda15eac732cb08351e71fc359058b93bd",
        "_ids": {
          "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd"
        }
      },
      "_L_a791c4ff8388e3923e169ce05a0a152def44d": {
        "_id": "DL_a791c4ff8388e3923e169ce05a0a152def44d",
        "_ids": {
          "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad",
          "d": "I0_dac96298c4c5bf8cb0cde8d8eb3e4a78ca1af"
        }
      }
    }
    >>> d = build(b.id, b.ids, cache, b.hosh.ø)
    >>> d.show(colored=False)
    {
        "y": "→(↑)",
        "d": "→(↑)",
        "_id": "DL_a791c4ff8388e3923e169ce05a0a152def44d",
        "_ids": {
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)",
            "d": "I0_dac96298c4c5bf8cb0cde8d8eb3e4a78ca1af (content: GS_cb0fda15eac732cb08351e71fc359058b93bd)"
        }
    }
    >>> d.evaluated.show(colored=False)
    {
        "y": 7,
        "d": {
            "x": 5,
            "_id": "GS_cb0fda15eac732cb08351e71fc359058b93bd",
            "_ids": {
                "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd"
            }
        },
        "_id": "DL_a791c4ff8388e3923e169ce05a0a152def44d",
        "_ids": {
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)",
            "d": "I0_dac96298c4c5bf8cb0cde8d8eb3e4a78ca1af (content: GS_cb0fda15eac732cb08351e71fc359058b93bd)"
        }
    }
    >>> (a.hosh ** b"d").show(colored=False)
    I0_dac96298c4c5bf8cb0cde8d8eb3e4a78ca1af
    >>> a = idict(x=5,z=9)
    >>> b = idict(y=7)
    >>> b["d"] = lambda y: a
    >>> b >>= [cache := {}]
    >>> _ = b.d
    >>> print(json.dumps(cache, indent=2))  # doctest:+ELLIPSIS
    {
      "h8xF5VS3x8yt.ZM3I1D1oKzdS6GcYmec-Y0cnAIl": {
        "_id": "_._72191dfc2ed7d9ff4c35d514b103ac114161f"
      },
      "GS_cb0fda15eac732cb08351e71fc359058b93bd": 5,
      "N8_524991e7434b2d3444007782c4cd0cd887261": 9,
      "_._72191dfc2ed7d9ff4c35d514b103ac114161f": {
        "_id": "r._72191dfc2ed7d9ff4c35d514b103ac114161f",
        "_ids": {
          "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd",
          "z": "N8_524991e7434b2d3444007782c4cd0cd887261"
        }
      },
      "WK_6ba95267cec724067d58b3186ecbcaa4253ad": 7,
      "_P9idohZcsojDgKThROI-YoSzRBcYmec-Y0cnAIl": {
        "_id": "UP9idohZcsojDgKThROI-YoSzRBcYmec-Y0cnAIl",
        "_ids": {
          "d": "h8xF5VS3x8yt.ZM3I1D1oKzdS6GcYmec-Y0cnAIl",
          "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad"
        }
      }
    }
    >>> build(b.id, b.ids, cache, b.hosh.ø).evaluated.show(colored=False)  # doctest:+ELLIPSIS
    {
        "d": {
            "x": 5,
            "z": 9,
            "_id": "r._72191dfc2ed7d9ff4c35d514b103ac114161f",
            "_ids": {
                "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd",
                "z": "N8_524991e7434b2d3444007782c4cd0cd887261"
            }
        },
        "y": 7,
        "_id": "...",
        "_ids": {
            "d": "...",
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> (a.hosh ** b"d").show(colored=False)
    u9_698c410308e557c005cda07ba00c564152401
    >>> a = idict(x=5)
    >>> b = idict(y=7)
    >>> b["d"] = lambda y: a
    >>> b >>= [cache := {}]
    >>> _ = b.d
    >>> print(json.dumps(cache, indent=2))  # doctest:+ELLIPSIS
    {
      "...": {
        "_id": "_S_cb0fda15eac732cb08351e71fc359058b93bd"
      },
      "GS_cb0fda15eac732cb08351e71fc359058b93bd": 5,
      "_S_cb0fda15eac732cb08351e71fc359058b93bd": {
        "_id": "GS_cb0fda15eac732cb08351e71fc359058b93bd",
        "_ids": {
          "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd"
        }
      },
      "WK_6ba95267cec724067d58b3186ecbcaa4253ad": 7,
      "...": {
        "_id": "...",
        "_ids": {
          "d": "...",
          "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad"
        }
      }
    }
    >>> d = build(b.id, b.ids, cache, b.hosh.ø)
    >>> d.show(colored=False)  # doctest:+ELLIPSIS
    {
        "d": "→(↑)",
        "y": "→(↑)",
        "_id": "...",
        "_ids": {
            "d": "...",
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> d.evaluated.show(colored=False)  # doctest:+ELLIPSIS
    {
        "d": {
            "x": 5,
            "_id": "GS_cb0fda15eac732cb08351e71fc359058b93bd",
            "_ids": {
                "x": "GS_cb0fda15eac732cb08351e71fc359058b93bd"
            }
        },
        "y": 7,
        "_id": "...",
        "_ids": {
            "d": "...",
            "y": "WK_6ba95267cec724067d58b3186ecbcaa4253ad (content: 3m_131910d18a892d1b64285250092a4967c8065)"
        }
    }
    >>> (a.hosh ** b"d").show(colored=False)
    I0_dac96298c4c5bf8cb0cde8d8eb3e4a78ca1af
    """
    from idict.core.frozenidentifieddict import FrozenIdentifiedDict

    if include_blobs:
        raise NotImplementedError
    hosh = identity * id
    data, hashes, hoshes = {}, {}, {}
    for k, fid in ids.items():
        # REMINDER: An item id will never start with '_'. That only happens with singleton-idict id translated to cache.
        if fid in cache:
            value = get_following_pointers(fid, cache)
            # WARN: The closures bellow assume items will not be removed from 'cache' in the meantime.
            if isinstance(value, dict) and list(value.keys()) == ["_id", "_ids"]:
                closure = lambda value_: lambda **kwargs: build(value_["_id"], value_["_ids"], cache, identity)
                data[k] = LazyVal(k, closure(value), {"↑": None}, {}, None)
            else:
                closure = lambda fid_: lambda **kwargs: cache[fid_]
                data[k] = LazyVal(k, closure(fid), {"↑": None}, {}, None)
        else:  # pragma: no cover
            raise Exception(f"Missing key={fid} or singleton key=_{fid[1:]}.\n{json.dumps(cache, indent=2)}")
        hoshes[k] = identity * fid
        if fid[2] == "_":
            hashes[k] = hoshes[k] // k.encode()

    internals = dict(blobs={}, hashes=hashes, hoshes=hoshes, hosh=hosh)
    return FrozenIdentifiedDict(data, identity=identity, _cloned=internals)


def get_following_pointers(fid, cache):
    """Fetch item value from cache following pointers"""
    result = cache[fid]
    while isinstance(result, dict) and list(result.keys()) == ["_id"]:
        result = cache[result["_id"]]
    return result


class LockedEntryException(Exception):
    pass
