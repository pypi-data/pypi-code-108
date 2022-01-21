#!/usr/bin/env python
# Connect to Pinata nodes
# Copyright (C) 2021  Nguyễn Gia Phong
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from contextlib import suppress
from subprocess import SubprocessError

from misc import ipfs

NYC = [f'/dnsaddr/nyc1-{i}.hostnodes.pinata.cloud/p2p/{pid}'
       for i, pid in ((1, 'QmRjLSisUCHVpFa5ELVvX3qVPfdxajxWJEHs9kN3EcxAW6'),
                      (2, 'QmPySsdmbczdZYBpbi2oq2WMJ8ErbfxtkG8Mo192UHkfGP'),
                      (3, 'QmSarArpxemsPESa6FNkmuu9iSE1QWqPX2R3Aw6f5jq4D5'))]

if __name__ == '__main__':
    while True:
        with suppress(SubprocessError):
            for address in NYC: ipfs('swarm', 'connect', address)
            break
