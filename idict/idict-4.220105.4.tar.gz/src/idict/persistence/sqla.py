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
from contextlib import contextmanager
from typing import TypeVar

from garoupa import ø
from ldict.core.appearance import decolorize
from sqlalchemy import Column, String, BLOB, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from idict.data.compression import pack, unpack
from idict.persistence.compressedcache import CompressedCache

VT = TypeVar("VT")
Base = declarative_base()


class Content(Base):
    __tablename__ = "content"
    id = Column(String(40), primary_key=True)
    blob = Column(BLOB)


def check(key):
    if not isinstance(key, str):
        raise WrongKeyType(f"Key must be string, not {type(key)}.", key)


@contextmanager
def sqla(url="sqlite+pysqlite:///:memory:", user_id=None, autopack=True, debug=False):
    engine = create_engine(url, echo=debug)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield SQLA(session, user_id, autopack)


class SQLA(CompressedCache):
    r"""
    Dict-like persistence based on SQLAlchemy

    40-digit keys only

    Usage:

    >>> d = SQLA("sqlite+pysqlite:////tmp/sqla-test.db")
    >>> d["x"] = 5
    >>> d["x"]
    5
    >>> for k,v in d.items():
    ...     print(k, v)
    x 5
    >>> "x" in d
    True
    >>> len(d)
    1
    >>> del d["x"]
    >>> "x" in d
    False
    >>> d
    {}
    >>> with sqla() as db:
    ...     "x" in db
    ...     db
    ...     db["x"] = b"asd"
    ...     db
    ...     "x" in db
    ...     db.x == b"asd"
    ...     del db["x"]
    ...     "x" in db
    False
    {}
    {'x': b'asd'}
    True
    True
    False
    >>> from idict import idict
    >>> with sqla() as cache:
    ...     d = idict.fromminiarff(output_format="arff") >> {"x": 3} >> [cache]
    ...     d.show(colored=False)
    ...     for i, id in enumerate(cache):
    ...         print(i, id)
    ...     a = idict(d.id, cache)  # >> arff2df
    ...     print("a", a.arff)  # doctest: +NORMALIZE_WHITESPACE
    {
        "arff": "@RELATION mini\n@ATTRIBUTE attr1\tREAL\n@ATTRIBUTE attr2 \tREAL\n@ATTRIBUTE class \t{0,1}\n@DATA\n5.1,3.5,0\n3.1,4.5,1",
        "x": 3,
        "_id": "KE_5f2a999248a1cab1e81cb79f66772a3be8025",
        "_ids": {
            "arff": "Z._c3e2b235b697e9734b9ec13084129dc30e45b (content: Ev_8bb973161e5ae900c5743b3c332b4a64d1955)",
            "x": "ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9 (content: S5_331b7e710abd1443cd82d6b5cdafb9f04d5ab)"
        }
    }
    0 Z._c3e2b235b697e9734b9ec13084129dc30e45b
    1 ME_bd0a8d9d8158cdbb9d7d4c7af1659ca1dabc9
    2 _E_5f2a999248a1cab1e81cb79f66772a3be8025
    a @RELATION mini
    @ATTRIBUTE attr1	REAL
    @ATTRIBUTE attr2 	REAL
    @ATTRIBUTE class 	{0,1}
    @DATA
    5.1,3.5,0
    3.1,4.5,1
    """

    def copy(self):
        raise NotImplementedError

    def __init__(
        self,
        session="sqlite+pysqlite:///:memory:",
        user_id=None,
        autopack=True,
        deterministic_packing=False,
        debug=False,
    ):
        if isinstance(session, str):

            @contextmanager
            def sessionctx():
                engine = create_engine(url=session, echo=debug)
                Base.metadata.create_all(engine)
                session_ = Session(engine)
                yield session_
                session_.close()

        else:

            @contextmanager
            def sessionctx():
                yield session

        self.sessionctx = sessionctx
        self.user_id = user_id
        if user_id:
            self.user_hosh = ø * (user_id if len(user_id) == 40 else user_id.encode())
        self.autopack = autopack
        self.deterministic_packing = deterministic_packing

    def __contains__(self, key):
        check(key)
        with self.sessionctx() as session:
            return session.query(Content).filter_by(id=key).first() is not None

    def __iter__(self):
        with self.sessionctx() as session:
            return (c.id for c in session.query(Content).all())

    def __setitem__(self, key: str, value, packing=True):
        check(key)
        if self.autopack and packing:
            value = pack(value, ensure_determinism=self.deterministic_packing)
        content = Content(id=key, blob=value)
        with self.sessionctx() as session:
            session.add(content)
            session.commit()

    def __getitem__(self, key, packing=True):
        check(key)
        with self.sessionctx() as session:
            if ret := session.query(Content).get(key):
                if ret is not None:
                    ret = ret.blob
                    if self.autopack and packing:
                        ret = unpack(ret)
        return ret

    def __delitem__(self, key):
        check(key)
        with self.sessionctx() as session:
            session.query(Content).filter_by(id=key).delete()
            session.commit()

    def __getattr__(self, key):
        check(key)
        if key in self:
            return self[key]
        return self.__getattribute__(key)

    def __len__(self):
        with self.sessionctx() as session:
            return session.query(Content).count()

    def __repr__(self):
        return repr(self.asdict)

    def __str__(self):
        return decolorize(repr(self))

    @property
    def asdict(self):
        return {k: self[k] for k in self}


# TODO (minor): convert this annotation to a document somewhere else:
"""
multiuser                   |   single user
----------------------------------------------
cache = SQLA(session)       |               ->  for already opened/permanent/global sessions
with sqla(url) as cache:    |   shelve      ->  a single session taht open/close automatically
cache = SQLA(DBMS url)      |   Disk        ->
----------------------------------------------
Oka(web url); cache         |   dict        -> dict-like cache  
"""


class WrongKeyType(Exception):
    pass
