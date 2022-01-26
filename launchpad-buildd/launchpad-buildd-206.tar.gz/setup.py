#!/usr/bin/python3

# Copyright 2015-2019 Canonical Ltd.  All rights reserved.
#
# This file is part of launchpad-buildd.
#
# launchpad-buildd is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, version 3 of the License.
#
# launchpad-buildd is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with launchpad-buildd.  If not, see <http://www.gnu.org/licenses/>.

import re
from textwrap import dedent

from setuptools import (
    find_packages,
    setup,
    )


changelog_heading = re.compile(r'\w[-+0-9a-z.]* \(([^\(\) \t]+)\)')

with open('debian/changelog') as changelog:
    line = changelog.readline()
    match = changelog_heading.match(line)
    if match is None:
        raise ValueError(
            "Failed to parse first line of debian/changelog: '%s'" % line)
    version = match.group(1)


setup(
    name='launchpad-buildd',
    version=version,
    description='Launchpad buildd slave',
    long_description=dedent("""
        The Launchpad buildd slave libraries.  The PyPI version of this
        package will not produce a complete installation on its own, and is
        mostly useful for testing other pieces of software against
        launchpad-buildd; for a real Launchpad buildd slave, install the
        launchpad-buildd package from ppa:launchpad/ubuntu/ppa.
        """).strip(),
    url='https://launchpad.net/launchpad-buildd',
    packages=find_packages(),
    include_package_data=True,
    maintainer='Launchpad Developers',
    maintainer_email='launchpad-dev@lists.launchpad.net',
    license='Affero GPL v3',
    install_requires=[
        # XXX cjwatson 2015-11-04: This does in fact require python-apt, but
        # that's normally shipped as a system package and specifying it here
        # causes problems for Launchpad's build system.
        # 'python-apt',
        'python-debian>=0.1.23',
        'requests',
        'six',
        'Twisted',
        'zope.interface',
        ],
    extras_require={
        'lxd': ['netaddr', 'pylxd'],
        },
    test_suite='lpbuildd',
    tests_require=[
        'fixtures',
        'mock; python_version<"3"',
        'responses',
        'systemfixtures',
        'testtools',
        'txfixtures',
        ],
    )
