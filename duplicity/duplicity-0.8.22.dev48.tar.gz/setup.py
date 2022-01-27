#!/usr/bin/env python3
# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4; encoding:utf8 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
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

import os
import re
import shutil
import subprocess
import sys
import time

from distutils.command.build_scripts import build_scripts
from distutils.command.install_data import install_data
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install
from setuptools.command.sdist import sdist
from setuptools.command.test import test


# check that we can function here
if not (sys.version_info[:2] >= (3, 5) or (sys.version_info[0] == 2 and sys.version_info[:2] >= (2, 7))):
    print(u"Sorry, duplicity requires version 2.7 or version 3.5 or later of Python.")
    sys.exit(1)


scm_version_args = {
    u'tag_regex': r'^(?P<prefix>rel.)?(?P<version>[^\+]+)(?P<suffix>.*)?$',
    u'local_scheme': u'no-local-version',
    }

try:
    from setuptools_scm import get_version  # pylint: disable=import-error
    Version = get_version(**scm_version_args)
except Exception as e:
    Version = u"0.8.22.dev"
    print(u"Unable to get SCM version: defaulting to %s" % (Version,))
Reldate = time.strftime(u"%B %d, %Y", time.gmtime(int(os.environ.get(u'SOURCE_DATE_EPOCH', time.time()))))


# READTHEDOCS uses setup.py sdist but can't handle extensions
ext_modules = list()
incdir_list = list()
libdir_list = list()
if not os.environ.get(u'READTHEDOCS') == u'True':
    # set incdir and libdir for librsync
    if os.name == u'posix':
        LIBRSYNC_DIR = os.environ.get(u'LIBRSYNC_DIR', u'')
        args = sys.argv[:]
        for arg in args:
            if arg.startswith(u'--librsync-dir='):
                LIBRSYNC_DIR = arg.split(u'=')[1]
                sys.argv.remove(arg)
        if LIBRSYNC_DIR:
            incdir_list = [os.path.join(LIBRSYNC_DIR, u'include')]
            libdir_list = [os.path.join(LIBRSYNC_DIR, u'lib')]

    # build the librsync extension
    ext_modules=[Extension(name=r"duplicity._librsync",
                           sources=[r"duplicity/_librsyncmodule.c"],
                           include_dirs=incdir_list,
                           library_dirs=libdir_list,
                           libraries=[u"rsync"])]


def get_data_files():
    u'''gen list of data files'''

    # static data files
    data_files = [
            (u'share/man/man1',
                [
                u'bin/duplicity.1',
                u'bin/rdiffdir.1'
                ]
            ),
            (u'share/doc/duplicity-%s' % Version,
                [
                u'CHANGELOG.md',
                u'CONTRIBUTING.md',
                u'COPYING',
                u'README.md',
                u'README-LOG.md',
                u'README-REPO.md',
                u'README-TESTING.md',
                ],
            ),
        ]

    if not os.environ.get(u'READTHEDOCS') == u'True':
        # msgfmt the translation files
        assert os.path.exists(u"po"), u"Missing 'po' directory."

        if os.path.exists(u'po/LINGUAS'):
            linguas = open(u'po/LINGUAS').readlines()
            for line in linguas:
                langs = line.split()
                for lang in langs:
                    try:
                        os.mkdir(os.path.join(u"po", lang))
                    except os.error:
                        pass
                    assert not os.system(u"cp po/%s.po po/%s" % (lang, lang)), lang
                    assert not os.system(u"msgfmt po/%s.po -o po/%s/duplicity.mo" % (lang, lang)), lang

        for root, dirs, files in os.walk(u"po"):
            for file in files:
                path = os.path.join(root, file)
                if path.endswith(u"duplicity.mo"):
                    lang = os.path.split(root)[-1]
                    data_files.append(
                        (u'share/locale/%s/LC_MESSAGES' % lang,
                         [u"po/%s/duplicity.mo" % lang]))

    return data_files


def VersionedCopy(source, dest):
    u"""
    Copy source to dest, substituting $version with version
    $reldate with today's date, i.e. December 28, 2008.
    """
    with open(source, u"rt") as fd:
        buffer = fd.read()

    buffer = re.sub(u"\$version", Version, buffer)
    buffer = re.sub(u"\$reldate", Reldate, buffer)

    with open(dest, u"wt") as fd:
        fd.write(buffer)


class SdistCommand(sdist):

    def run(self):
        sdist.run(self)

        orig = u"%s/duplicity-%s.tar.gz" % (self.dist_dir, Version)
        tardir = u"duplicity-%s" % (Version)
        tarfile = u"%s/duplicity-%s.tar.gz" % (self.dist_dir, Version)

        assert not os.system(u"tar -xf %s" % orig)
        assert not os.remove(orig)

        # make sure executables are
        assert not os.chmod(os.path.join(tardir, u"setup.py"), 0o755)
        assert not os.chmod(os.path.join(tardir, u"bin", u"duplicity"), 0o755)
        assert not os.chmod(os.path.join(tardir, u"bin", u"rdiffdir"), 0o755)

        # recopy the unversioned files and add correct version
        VersionedCopy(os.path.join(u"bin", u"duplicity.1"),
                      os.path.join(tardir, u"bin", u"duplicity.1"))
        VersionedCopy(os.path.join(u"bin", u"rdiffdir.1"),
                      os.path.join(tardir, u"bin", u"rdiffdir.1"))
        VersionedCopy(os.path.join(u"duplicity", u"__init__.py"),
                      os.path.join(tardir, u"duplicity", u"__init__.py"))
        VersionedCopy(os.path.join(u"snap", u"snapcraft.yaml"),
                      os.path.join(tardir, u"snap", u"snapcraft.yaml"))

        # set COPYFILE_DISABLE to disable appledouble file creation
        os.environ[u'COPYFILE_DISABLE'] = u'true'

        # make the new tarfile and remove tardir
        assert not os.system(u"tar czf %s %s" % (tarfile, tardir))
        assert not shutil.rmtree(tardir)


class TestCommand(test):

    def run(self):
        # Make sure all modules are ready
        build_cmd = self.get_finalized_command(u"build_py")
        build_cmd.run()
        # And make sure our scripts are ready
        build_scripts_cmd = self.get_finalized_command(u"build_scripts")
        build_scripts_cmd.run()

        # make symlinks for test data
        if build_cmd.build_lib != top_dir:
            for path in [u'source_files.tar.gz', u'gnupg']:
                src = os.path.join(top_dir, u'testing', path)
                target = os.path.join(build_cmd.build_lib, u'testing', path)
                try:
                    os.symlink(src, target)
                except Exception:
                    pass

        os.environ[u'PATH'] = u"%s:%s" % (
            os.path.abspath(build_scripts_cmd.build_dir),
            os.environ.get(u'PATH'))

        test.run(self)


class InstallCommand(install):

    def run(self):
        # Normally, install will call build().  But we want to delete the
        # testing dir between building and installing.  So we manually build
        # and mark ourselves to skip building when we run() for real.
        self.run_command(u'build')
        self.skip_build = True

        # remove testing dir
        top_dir = os.path.dirname(os.path.abspath(__file__))
        if self.build_lib != top_dir:
            testing_dir = os.path.join(self.build_lib, u'testing')
            shutil.rmtree(testing_dir)

        install.run(self)


class InstallDataCommand(install_data):

    def run(self):
        install_data.run(self)

        # version the man pages
        for tup in self.data_files:
            base, filenames = tup
            if base == u'share/man/man1':
                for fn in filenames:
                    fn = os.path.split(fn)[-1]
                    path = os.path.join(self.install_dir, base, fn)
                    VersionedCopy(path, path)


class BuildExtCommand(build_ext):
    u'''Build extension modules.'''

    def run(self):
        # build the _librsync.so module
        print(u"Building extension for librsync...")
        self.inplace = True
        build_ext.run(self)


with open(u"README.md") as fh:
    long_description = fh.read()


setup(name=u"duplicity",
    version=Version,
    description=u"Encrypted backup using rsync algorithm",
    long_description=long_description,
    long_description_content_type=u"text/plain",
    author=u"Ben Escoto <ben@emrose.org>",
    author_email=u"ben@emrose.org",
    maintainer=u"Kenneth Loafman <kenneth@loafman.com>",
    maintainer_email=u"kenneth@loafman.com",
    url=u"http://duplicity.nongnu.org/index.html",
    python_requires=u">2.6, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4",
    platforms=[u"any"],
    packages=[
        u"duplicity",
        u"duplicity.backends",
        u"duplicity.backends.pyrax_identity",
        u"testing",
        u"testing.functional",
        u"testing.overrides",
        u"testing.unit",
        ],
    package_dir={
        u"duplicity": u"duplicity",
        u"duplicity.backends": u"duplicity/backends",
        },
    ext_modules=ext_modules,
    scripts=[
        u"bin/rdiffdir",
        u"bin/duplicity",
        ],
    data_files=get_data_files(),
    include_package_data=True,
    setup_requires=[
        u"setuptools",
        u"setuptools_scm",
        ],
    install_requires=[
        u"fasteners",
        u"future",
        ],
    tests_require=[
        u"fasteners",
        u"future",
        u"mock",
        u"pexpect",
        u"pytest",
        u"pytest-runner",
        ],
    test_suite=u"testing",
    cmdclass={
        u"build_ext": BuildExtCommand,
        u"install": InstallCommand,
        u"install_data": InstallDataCommand,
        u"sdist": SdistCommand,
        u"test": TestCommand,
        },
    classifiers=[
        u"Development Status :: 6 - Mature",
        u"Environment :: Console",
        u"License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        u"Operating System :: MacOS",
        u"Operating System :: POSIX",
        u"Programming Language :: C",
        u"Programming Language :: Python :: 2",
        u"Programming Language :: Python :: 2.7",
        u"Programming Language :: Python :: 3",
        u"Programming Language :: Python :: 3.5",
        u"Programming Language :: Python :: 3.6",
        u"Programming Language :: Python :: 3.7",
        u"Programming Language :: Python :: 3.8",
        u"Programming Language :: Python :: 3.9",
        u"Topic :: System :: Archiving :: Backup"
        ],
    )


# TODO: Find best way to clean up afterwards.
if os.path.exists(u'po/LINGUAS'):
    linguas = open(u'po/LINGUAS').readlines()
    for line in linguas:
        langs = line.split()
        for lang in langs:
            try:
                shutil.rmtree(os.path.join(u"po", lang))
            except Exception:
                pass
