# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
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

"""
Flow elements UUID handling
"""
import uuid
import re


_uuid_re_str = '[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'
_sy_uuid_re_str = f'^{{{_uuid_re_str}}}$'
_sy_uuid_re = re.compile(_sy_uuid_re_str, re.IGNORECASE)
_sy_joined_uuid_re_str = f'^{{{_uuid_re_str}}}\\.{{{_uuid_re_str}}}$'
_sy_joined_uuid_re = re.compile(_sy_joined_uuid_re_str)


def generate_uuid():
    """
    Generate a unique UUID.
    :return: Unique UUID.
    """
    # The UUID version 1 algorithm is based on a hardware node and a clock.
    # It is guaranteed not to produce any duplicates as long as less than
    # 2**14 UUID:s are generated in 100ns.
    # http://stackoverflow.com/questions/1785503/when-should-i-use-uuid-uuid1-vs-uuid-uuid4-in-python
    # There are no privacy issues with using this UUID which means that
    # there is no problem basing it on the current hardware.
    # generate_uuid.counter += 1L
    return generate_uuid.new_uuid()


generate_uuid.new_uuid = lambda: str(u'{{{}}}'.format(uuid.uuid4()))


def join_uuid(namespace_uuid, item_uuid):
    """
    Join an instance UUID and an item UUID to one single string.
    :param namespace_uuid: String containing UUID for namespace.
    :param item_uuid: String containing UUID for item.
    :return: String with joined UUID.
    """
    return '.'.join((namespace_uuid, item_uuid))


def join_uuids(uuid_parts):
    """
    Join a list of UUIDs to a single string.
    :param uuid_parts: Sequence of strings, each containing a UUID.
    :return: String with joined UUIDs.
    """
    return '.'.join(uuid_parts)


def split_uuid(joined_uuid):
    """
    Split an instance UUID and an item UUID into components.
    :param joined_uuid: String containing joined UUID:s.
    :return: Tuple with two UUID:s.
    """
    return tuple(joined_uuid.split('.'))


def is_joined_uuid(joined_uuid):
    return bool(_sy_joined_uuid_re.match(joined_uuid or ''))
