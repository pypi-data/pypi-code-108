# DQSEGDB2
# Copyright (C) 2018  Duncan Macleod
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

"""Tests for :mod:`dqsegdb.api`
"""

import pytest

from .. import query

KNOWN = [(0, 10)]
ACTIVE = [(1, 3), (3, 4), (6, 10)]
QUERY_SEGMENT = (2, 8)
KNOWN_COALESCED = [(2, 8)]
ACTIVE_COALESCED = [(2, 4), (6, 8)]


def test_query_names(requests_mock):
    names = ['name1', 'name2', 'name2']
    requests_mock.get(
        "https://segments.ligo.org/dq/X1",
        json={"results": names},
    )
    assert query.query_names(
        "X1",
        host="https://segments.ligo.org",
    ) == set(map('X1:{0}'.format, names))


def test_query_versions(requests_mock):
    versions = [1, 2, 3, 4]
    requests_mock.get(
        "https://segments.ligo.org/dq/X1/test",
        json={"version": versions},
    )
    assert query.query_versions(
        "X1:test",
        host="https://segments.ligo.org",
    ) == sorted(versions)


@pytest.mark.parametrize('flag, coalesce, known, active', [
    ("X1:TEST:1", False, KNOWN, ACTIVE),
    ("X1:TEST:1", True, KNOWN_COALESCED, ACTIVE_COALESCED),
    ("X1:TEST:*", False, KNOWN + KNOWN, ACTIVE + ACTIVE),
    ("X1:TEST:*", True, KNOWN_COALESCED, ACTIVE_COALESCED),
])
def test_query_segments(flag, coalesce, known, active, requests_mock):
    # mock the request
    result = {
        'ifo': 'X1',
        'name': 'TEST',
        'version': 1,
        'known': KNOWN,
        'active': ACTIVE
    }
    versions = (1, 2)
    requests_mock.get(
        "https://segments.ligo.org/dq/X1/TEST",
        json={"version": versions},
    )
    for ver in versions:
        requests_mock.get(
            "https://segments.ligo.org/dq/X1/TEST/"
            "{}?e=8&include=metadata,known,active&s=2".format(ver),
            json=result,
        )

    # check that we get the result we expect
    out = query.query_segments(
        flag,
        2,
        8,
        coalesce=coalesce,
        host="https://segments.ligo.org",
    )
    assert out.pop('version') is (None if flag.endswith('*') else 1)
    assert out.pop('known') == known
    assert out.pop('active') == active
    for key in set(result) & set(out):
        assert out[key] == result[key]
