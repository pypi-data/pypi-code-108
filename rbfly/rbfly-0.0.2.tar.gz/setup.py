#!/usr/bin/env python
#
# rbfly - a library for RabbitMQ Streams using Python asyncio
#
# Copyright (C) 2021-2022 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from setuptools import setup, Extension
from Cython.Build import cythonize

setup(
    ext_modules=cythonize([
        Extension('rbfly._codec', ['rbfly/_codec.pyx']),
        Extension('rbfly.amqp._message', ['rbfly/amqp/_message.pyx']),
        Extension('rbfly.streams._client', ['rbfly/streams/_client.pyx']),
        Extension('rbfly.streams._codec', ['rbfly/streams/_codec.pyx']),
    ]),
)

# vim: sw=4:et:ai
