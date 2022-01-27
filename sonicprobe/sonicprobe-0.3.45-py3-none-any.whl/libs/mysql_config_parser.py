# -*- coding: utf-8 -*-
# Copyright 2008-2019 Proformatique
# SPDX-License-Identifier: GPL-3.0-or-later
"""sonicprobe.libs.mysql_config_parser"""

import os
import re
import subprocess

# pylint: disable=unused-import
from six.moves.configparser import ConfigParser, Error, NoSectionError, DuplicateSectionError, \
        NoOptionError, InterpolationError, InterpolationMissingOptionError, \
        InterpolationSyntaxError, InterpolationDepthError, ParsingError, \
        MissingSectionHeaderError, _default_dict

try:
    from six.moves import cStringIO as StringIO
except ImportError:
    from six import StringIO

from six import PY2, string_types

import semantic_version

MYSQL_DEFAULT_HOST     = 'localhost'
MYSQL_DEFAULT_PORT     = 3306

MYSQLCLIENT_PARSE_VERS = re.compile(r'^mysql\s+Ver\s+(?P<version>[^\s]+)\s+Distrib\s+(?P<distrib>[^\s,]+)').match
MYSQLDUMP_PARSE_VERS   = re.compile(r'^mysqldump\s+Ver\s+(?P<version>[^\s]+)\s+Distrib\s+(?P<distrib>[^\s,]+)').match


class MySQLConfigVersion(object):
    def __init__(self, default_file = 'client.cnf', custom_file = "", config_dir = None):
        self._config_dir   = config_dir
        self._default_file = default_file or ""
        self._custom_file  = custom_file or ""
        self._myconf       = MySQLConfigParser()

    def _read_file(self, filepath):
        if self._config_dir and not filepath.startswith(os.path.sep):
            filepath = os.path.join(self._config_dir, filepath)

        if not os.path.isfile(filepath):
            return ""

        with open(filepath, 'r') as f:
            return f.read()

    @staticmethod
    def _set_specific_conf(cfg, section, version):
        secname = "%s=%s" % (section, version)
        if cfg.has_section(secname):
            for x in cfg.items(secname):
                cfg.set(*[section] + list(x))

    def _check_conf_versions(self, cfg, section, version, vername = ""):
        ver = semantic_version.Version(version, partial = True)
        for x in ('major', 'minor', 'patch', 'prerelease', 'build'):
            v = getattr(ver, x, None)
            if not v:
                break
            if isinstance(v, tuple):
                v = '.'.join(v)
            vername += "%s." % v
            self._set_specific_conf(cfg, section, vername.rstrip('.'))

    def _get_config(self, section, progpath, parse_vers, check_version = True):
        my_vers = False
        if check_version:
            my_vers = parse_vers(subprocess.check_output((progpath, '--version')).strip())

        myconf = StringIO("%s\n%s" % (self._read_file(self._default_file),
                                      self._read_file(self._custom_file)))
        self._myconf.readfp(myconf)
        myconf.close()

        if my_vers:
            self._check_conf_versions(self._myconf,
                                      section,
                                      my_vers.group('version'),
                                      'ver-')
            self._check_conf_versions(self._myconf,
                                      section,
                                      my_vers.group('distrib'),
                                      'dist-')

        return self._myconf

    def get_client(self, check_version = True):
        return self._get_config('client', 'mysql', MYSQLCLIENT_PARSE_VERS, check_version)

    def get_mysqldump(self, check_version = True):
        return self._get_config('mysqldump', 'mysqldump', MYSQLDUMP_PARSE_VERS, check_version)


class MySQLConfigParser(ConfigParser):
    if os.name == 'nt':
        RE_INCLUDE_FILE = re.compile(r'^[^\.]+(?:\.ini|\.cnf)$').match
    else:
        RE_INCLUDE_FILE = re.compile(r'^[^\.]+\.cnf$').match

    def __init__(self, defaults = None, dict_type = _default_dict, allow_no_value=True):
        ConfigParser.__init__(self, defaults, dict_type, allow_no_value)

    @staticmethod
    def valid_filename(filename):
        if isinstance(filename, string_types) and MySQLConfigParser.RE_INCLUDE_FILE(filename):
            return True

        return False

    def getboolean(self, section, option, retint=False): # pylint: disable=arguments-differ
        ret = ConfigParser.getboolean(self, section, option)

        if not retint:
            return ret

        return int(ret)

    def read(self, filenames, encoding=None): # pylint: disable=arguments-differ
        if isinstance(filenames, string_types):
            filenames = [filenames]

        file_ok = []
        for filename in filenames:
            if self.valid_filename(os.path.basename(filename)):
                file_ok.append(filename)

        if PY2:
            return ConfigParser.read(self, file_ok)

        return ConfigParser.read(self, file_ok, encoding) # pylint: disable=too-many-function-args

    def readfp(self, fp, filename=None):
        return ConfigParser.readfp(self, MySQLConfigParserFilter(fp), filename)

    def read_file(self, f, source=None):
        if PY2:
            return ConfigParser.readfp(self, MySQLConfigParserFilter(f), source)

        return ConfigParser.read_file(self, MySQLConfigParserFilter(f), source) # pylint: disable=no-member


class MySQLConfigParserFilter(object): # pylint: disable=useless-object-inheritance
    RE_HEADER_OPT  = re.compile(r'^\s*\[[^\]]+\]\s*').match
    RE_INCLUDE_OPT = re.compile(r'^\s*!\s*(?:(include|includedir)\s+(.+))$').match

    def __init__(self, fp):
        self.fp     = fp
        self._lines = []

    def readline(self):
        if self._lines:
            line = self._lines.pop(0)
        else:
            line = self.fp.readline()

        sline = line.lstrip()

        if not sline or sline[0] != '!':
            if self.RE_HEADER_OPT(line):
                return line

            if sline.startswith('#'):
                return line

            if sline.startswith(';'):
                return line

            return line

        mline = self.RE_INCLUDE_OPT(sline)

        if not mline:
            raise ParsingError("Unable to parse the line: %r." % line)
            #return "#%s" % line

        opt = mline.group(2).strip()

        if not opt:
            raise ParsingError("Empty path for include or includir option (%r)." % line)
            #return "#%s" % line

        if mline.group(1) == 'include':
            if not MySQLConfigParser.RE_INCLUDE_FILE(opt):
                raise ParsingError("Wrong filename for include option (%r)." % line)
                #return "#%s" % line

            self._add_lines(opt)
        else:
            dirname = os.path.dirname(opt)
            for xfile in os.listdir(opt):
                if MySQLConfigParser.RE_INCLUDE_FILE(xfile):
                    self._add_lines(os.path.join(dirname, xfile))

        return self.readline()

    def _add_lines(self, xfile):
        if not os.path.isfile(xfile) or not os.access(xfile, os.R_OK):
            return

        xfilter = MySQLConfigParserFilter(open(xfile))
        lines = xfilter.fp.readlines()
        xfilter.fp.close()
        lines.extend(self._lines)
        self._lines = lines
