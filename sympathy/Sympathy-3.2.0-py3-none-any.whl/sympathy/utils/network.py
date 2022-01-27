# This file is part of Sympathy for Data.
# Copyright (c) 2019, Combine Control Systems AB
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
import select


def send_all(socket, data):
    chunk = 4096
    fileno = socket.fileno()

    for i in range(0, len(data), chunk):
        chunkdata = data[i: i + chunk]
        len_chunk = len(chunkdata)
        sent = 0
        while sent < len_chunk:
            w = select.select([], [fileno], [], 100)[1]
            if fileno in w:
                sent += socket.send(chunkdata[sent:])
