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
import time
from abc import abstractmethod

from idict.persistence.cache import Cache


from threading import Thread


def alive(n):
    """Based on https://www.geeksforgeeks.org/start-and-stop-a-thread-in-python/"""
    while n > 0:
        print("contando", n)
        n -= 1
        time.sleep(5)


class CompressedCache(Cache):  # pragma: no cover
    def setblob(self, id, blob):
        # REMINDER: Cannot declare __setitem__ as abstract in this class since SQLA access it from its parent.
        # noinspection PyArgumentList
        self.__setitem__(id, blob, packing=False)

    def getblob(self, id):
        # noinspection PyArgumentList
        return self.__getitem__(id, packing=False)

    def lockid(self, id):
        # TODO (minor):  launch thread at cached (to allow non redundant distributed processing)
        pass
        # t = Thread(target=alive, args=(10,))
        # t.start()

    def unlockid(self, id):
        pass

    @abstractmethod
    def copy(self):
        raise NotImplementedError
