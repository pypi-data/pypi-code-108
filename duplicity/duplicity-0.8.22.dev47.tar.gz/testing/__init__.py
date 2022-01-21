# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4; encoding:utf8 -*-
#
# Copyright 2012 Canonical Ltd
#
# This file is part of duplicity.
#
# Duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# Duplicity is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with duplicity; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()

import gettext
import os
import platform
import subprocess
import sys
import time
import unittest

from duplicity import backend
from duplicity import config
from duplicity import log
from duplicity import util

util.start_debugger()

if sys.version_info.major >= 3:
    gettext.install(u'duplicity', names=[u'ngettext'])
else:
    gettext.install(u'duplicity', names=[u'ngettext'], unicode=True)  # pylint: disable=unexpected-keyword-arg

_testing_dir = os.path.dirname(os.path.abspath(__file__))
_top_dir = os.path.dirname(_testing_dir)
_overrides_dir = os.path.join(_testing_dir, u'overrides')
_bin_dir = os.path.join(_testing_dir, u'overrides', u'bin')

if platform.system().startswith(u'Darwin'):
    # Use temp space from getconf, never /tmp
    _runtest_dir = subprocess.check_output([u'getconf', u'DARWIN_USER_TEMP_DIR'])
    _runtest_dir = util.fsdecode(_runtest_dir).rstrip().rstrip(u'/')
else:
    _runtest_dir = os.getenv(u'TMPDIR', False) or os.getenv(u'TEMP', False) or u'/tmp'

# Adjust python path for duplicity and override modules
sys.path = [_overrides_dir, _top_dir, _bin_dir] + sys.path

# Also set PYTHONPATH for any subprocesses
os.environ[u'PYTHONPATH'] = _overrides_dir + u":" + _top_dir + u":" + os.environ.get(u'PYTHONPATH', u'')

# And PATH for any subprocesses
os.environ[u'PATH'] = _bin_dir + u":" + os.environ.get(u'PATH', u'')

# Now set some variables that help standardize test behavior
os.environ[u'LANG'] = u''
os.environ[u'GNUPGHOME'] = os.path.join(_testing_dir, u'gnupg')

# bzr does not honor perms so fix the perms and avoid annoying error
os.system(u"chmod 700 %s" % os.path.join(_testing_dir, u'gnupg'))

# Standardize time
os.environ[u'TZ'] = u'US/Central'
time.tzset()

# TODO: find place in setup.py to do this
# fix shebangs in _bin_dir to be current python
if sys.version_info.major == 2:
    files = os.listdir(_bin_dir)
    for file in files:
        print(u"converting %s to python2" % file, file=sys.stderr)
        with open(os.path.join(_bin_dir, file), u"r") as f:
            p2 = f.read().replace(u"python3", u"python")
        with open(os.path.join(_bin_dir, file), u"w") as f:
            p2 = f.write(p2)

class DuplicityTestCase(unittest.TestCase):

    sign_key = u'839E6A2856538CCF'
    sign_passphrase = u'test'
    encrypt_key1 = u'839E6A2856538CCF'
    encrypt_key2 = u'453005CE9B736B2A'

    def setUp(self):
        super(DuplicityTestCase, self).setUp()
        self.savedEnviron = {}
        self.savedConfig = {}

        log.setup()
        log.setverbosity(log.WARNING)
        self.set_config(u'print_statistics', 0)
        backend.import_backends()

        self.remove_testfiles()
        self.unpack_testfiles()

        # Have all file references in tests relative to our runtest dir
        os.chdir(_runtest_dir)

    def tearDown(self):
        for key in self.savedEnviron:
            self._update_env(key, self.savedEnviron[key])

        for key in self.savedConfig:
            setattr(config, key, self.savedConfig[key])

        self.remove_testfiles()

        os.chdir(_testing_dir)
        super(DuplicityTestCase, self).tearDown()

    def unpack_testfiles(self):
        assert not os.system(u"rm -rf {0}/testfiles".format(_runtest_dir))
        assert not os.system(u"tar xzf {0}/testfiles.tar.gz -C {1} > /dev/null 2>&1".format(_testing_dir, _runtest_dir))
        assert not os.system(u"mkdir {0}/testfiles/output {0}/testfiles/cache".format(_runtest_dir))

    def remove_testfiles(self):
        assert not os.system(u"rm -rf {0}/testfiles".format(_runtest_dir))

    def _update_env(self, key, value):
        if value is not None:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]

    def set_environ(self, key, value):
        if key not in self.savedEnviron:
            self.savedEnviron[key] = os.environ.get(key)
        self._update_env(key, value)

    def set_config(self, key, value):
        assert hasattr(config, key)
        if key not in self.savedConfig:
            self.savedConfig[key] = getattr(config, key)
        setattr(config, key, value)
