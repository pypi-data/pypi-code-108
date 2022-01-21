# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
from logging import debug, warning, error
import re
import os
import io
import sys
import json
from . import progress
import datetime
from .exit_codes import *

# try:
#     import dateutil.parser
#     import dateutil.tz
# except ImportError:
#     sys.stderr.write(u"""
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ImportError trying to import dateutil.parser and dateutil.tz.
# Please install the python dateutil module:
# $ sudo apt-get install python-dateutil
#   or
# $ sudo yum install python-dateutil
#   or
# $ pip install python-dateutil
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# """)
#     sys.stderr.flush()
#     sys.exit(EX_OSFILE)

try:
    # python 3 support
    import httplib
except ImportError:
    import http.client as httplib
import locale

try:
 from configparser import (NoOptionError, NoSectionError,
                           MissingSectionHeaderError, ParsingError,
                           ConfigParser as PyConfigParser)
except ImportError:
  # Python2 fallback code
  from ConfigParser import (NoOptionError, NoSectionError,
                            MissingSectionHeaderError, ParsingError,
                            ConfigParser as PyConfigParser)

try:
    unicode
except NameError:
    # python 3 support
    # In python 3, unicode -> str, and str -> bytes
    unicode = str

def config_unicodise(string, encoding = "utf-8", errors = "replace"):
    """
    Convert 'string' to Unicode or raise an exception.
    Config can't use toolbox from Utils that is itself using Config
    """
    if type(string) == unicode:
        return string

    try:
        return unicode(string, encoding, errors)
    except UnicodeDecodeError:
        raise UnicodeDecodeError("Conversion to unicode failed: %r" % string)

# def config_date_to_python(date):
#     """
#     Convert a string formated like '2020-06-27T15:56:34Z' into a python datetime
#     """
#     return dateutil.parser.parse(date, fuzzy=True)

def is_bool_true(value):
    """Check to see if a string is true, yes, on, or 1

    value may be a str, or unicode.

    Return True if it is
    """
    if type(value) == unicode:
        return value.lower() in ["true", "yes", "on", "1"]
    elif type(value) == bool and value == True:
        return True
    else:
        return False

def is_bool_false(value):
    """Check to see if a string is false, no, off, or 0

    value may be a str, or unicode.

    Return True if it is
    """
    if type(value) == unicode:
        return value.lower() in ["false", "no", "off", "0"]
    elif type(value) == bool and value == False:
        return True
    else:
        return False

def is_bool(value):
    """Check a string value to see if it is bool"""
    return is_bool_true(value) or is_bool_false(value)

class Config(object):
    _instance = None
    _parsed_files = []
    _doc = {}
    user_id = u""
    password = u""
    url = u""
    depth = 1
    download_as_zip = False
    progress_meter = sys.stdout.isatty()
    progress_class = progress.ProgressCR
    list_md5 = False
    long_listing = False
    human_readable_sizes = False
    force = False
    put_continue = False
    chunked = False
    chunk_size_mb = 15
    cache_valid_hour = 8
    skip_existing = False
    recursive = False
    proxy_host = u""
    proxy_port = 3128
    use_https = True
    verbosity = logging.WARNING
    # List of compiled REGEXPs
    exclude = []
    include = []
    # Dict mapping compiled REGEXPs back to their textual form
    debug_exclude = {}
    debug_include = {}
    encoding = locale.getpreferredencoding() or "UTF-8"

    ## Creating a singleton
    def __new__(cls, configfile=None, user_id=None, password=None):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self, configfile=None, user_id=None, password=None):
        if configfile:
            self.read_config_file(configfile)

            # override these if passed on the command-line
            if user_id and password:
                self.user_id = user_id
                self.password = password

    # def role_config(self):
    #     """
    #     Get credentials from IAM authentication
    #     """
    #     try:
    #         conn = httplib.HTTPConnection(host='169.254.169.254', timeout=2)
    #         conn.request('GET', "/latest/meta-data/iam/security-credentials/")
    #         resp = conn.getresponse()
    #         files = resp.read()
    #         if resp.status == 200 and len(files)>1:
    #             conn.request('GET', "/latest/meta-data/iam/security-credentials/%s" % files.decode('utf-8'))
    #             resp=conn.getresponse()
    #             if resp.status == 200:
    #                 resp_content = config_unicodise(resp.read())
    #                 creds=json.loads(resp_content)
    #                 expiration = config_date_to_python(config_unicodise(creds['Expiration']))
    #                 # Add a timedelta to prevent any expiration if the EC2 machine is not at the right date
    #                 self._access_token_expiration = expiration - datetime.timedelta(minutes=15)
    #                 self._access_token_last_update = config_date_to_python(config_unicodise(creds['LastUpdated']))
    #                 # Others variables : Code / Type
    #             else:
    #                 raise IOError
    #         else:
    #             raise IOError
    #     except:
    #         raise

    # def role_refresh(self):
    #     if self._access_token_refresh:
    #         now = datetime.datetime.now(dateutil.tz.tzutc())
    #         if self._access_token_expiration \
    #            and now < self._access_token_expiration \
    #            and self._access_token_last_update \
    #            and self._access_token_last_update <= now:
    #             # current token is still valid. No need to refresh it
    #             return
    #         try:
    #             self.role_config()
    #         except Exception:
    #             warning("Could not refresh role")

    def option_list(self):
        retval = []
        for option in dir(self):
            ## Skip attributes that start with underscore or are not string, int or bool
            option_type = type(getattr(Config, option))
            if option.startswith("_") or \
               not (option_type in (
                    type(u"string"), # str
                        type(42),   # int
                    type(True))):   # bool
                continue
            retval.append(option)
        return retval

    def read_config_file(self, configfile):
        cp = ConfigParser(configfile)
        for option in self.option_list():
            _option = cp.get(option)
            if _option is not None:
                _option = _option.strip()
            self.update_option(option, _option)

        # allow acl_public to be set from the config file too, even though by
        # default it is set to None, and not present in the config file.
        if cp.get('acl_public'):
            self.update_option('acl_public', cp.get('acl_public'))

        if cp.get('add_headers'):
            for option in cp.get('add_headers').split(","):
                (key, value) = option.split(':', 1)
                self.extra_headers[key.strip()] = value.strip()

        self._parsed_files.append(configfile)

    def dump_config(self, stream):
        ConfigDumper(stream).dump(u"default", self)

    def update_option(self, option, value):
        if value is None:
            return

        #### Handle environment reference
        if unicode(value).startswith("$"):
            return self.update_option(option, os.getenv(value[1:]))

        #### Special treatment of some options
        ## verbosity must be known to "logging" module
        if option == "verbosity":
            # support integer verboisities
            try:
                value = int(value)
            except ValueError:
                try:
                    # otherwise it must be a key known to the logging module
                    try:
                        # python 3 support
                        value = logging._levelNames[value]
                    except AttributeError:
                        value = logging._nameToLevel[value]
                except KeyError:
                    raise ValueError("Config: verbosity level '%s' is not valid" % value)

        elif option == "limitrate":
            #convert kb,mb to bytes
            if value.endswith("k") or value.endswith("K"):
                shift = 10
            elif value.endswith("m") or value.endswith("M"):
                shift = 20
            else:
                shift = 0
            try:
                value = shift and int(value[:-1]) << shift or int(value)
            except Exception:
                raise ValueError("Config: value of option %s must have suffix m, k, or nothing, not '%s'" % (option, value))

        ## allow yes/no, true/false, on/off and 1/0 for boolean options
        ## Some options default to None, if that's the case check the value to see if it is bool
        elif (type(getattr(Config, option)) is type(True) or              # Config is bool
             (getattr(Config, option) is None and is_bool(value))):  # Config is None and value is bool
            if is_bool_true(value):
                value = True
            elif is_bool_false(value):
                value = False
            else:
                raise ValueError("Config: value of option '%s' must be Yes or No, not '%s'" % (option, value))

        elif type(getattr(Config, option)) is type(42):     # int
            try:
                value = int(value)
            except ValueError:
                raise ValueError("Config: value of option '%s' must be an integer, not '%s'" % (option, value))

        elif option in ["host_base", "host_bucket", "cloudfront_host"]:
            if value.startswith("http://"):
                value = value[7:]
            elif value.startswith("https://"):
                value = value[8:]


        setattr(Config, option, value)

class ConfigParser(object):
    def __init__(self, file, sections = []):
        self.cfg = {}
        self.parse_file(file, sections)

    def parse_file(self, file, sections = []):
        debug("ConfigParser: Reading file '%s'" % file)
        if type(sections) != type([]):
            sections = [sections]
        in_our_section = True
        r_comment = re.compile("^\s*#.*")
        r_empty = re.compile("^\s*$")
        r_section = re.compile("^\[([^\]]+)\]")
        r_data = re.compile("^\s*(?P<key>\w+)\s*=\s*(?P<value>.*)")
        r_quotes = re.compile("^\"(.*)\"\s*$")
        with io.open(file, "r", encoding=self.get('encoding', 'UTF-8')) as fp:
            for line in fp:
                if r_comment.match(line) or r_empty.match(line):
                    continue
                is_section = r_section.match(line)
                if is_section:
                    section = is_section.groups()[0]
                    in_our_section = (section in sections) or (len(sections) == 0)
                    continue
                is_data = r_data.match(line)
                if is_data and in_our_section:
                    data = is_data.groupdict()
                    if r_quotes.match(data["value"]):
                        data["value"] = data["value"][1:-1]
                    self.__setitem__(data["key"], data["value"])
                    if data["key"] in ("access_key", "secret_key", "gpg_passphrase"):
                        print_value = ("%s...%d_chars...%s") % (data["value"][:2], len(data["value"]) - 3, data["value"][-1:])
                    else:
                        print_value = data["value"]
                    debug("ConfigParser: %s->%s" % (data["key"], print_value))
                    continue
                warning("Ignoring invalid line in '%s': %s" % (file, line))

    def __getitem__(self, name):
        return self.cfg[name]

    def __setitem__(self, name, value):
        self.cfg[name] = value

    def get(self, name, default = None):
        if name in self.cfg:
            return self.cfg[name]
        return default

class ConfigDumper(object):
    def __init__(self, stream):
        self.stream = stream

    def dump(self, section, config):
        self.stream.write(u"[%s]\n" % section)
        for option in config.option_list():
            value = getattr(config, option)
            if option == "verbosity":
                # we turn level numbers back into strings if possible
                if isinstance(value, int):
                    try:
                        try:
                            # python 3 support
                            value = logging._levelNames[value]
                        except AttributeError:
                            value = logging._levelToName[value]
                    except KeyError:
                        pass
            self.stream.write(u"%s = %s\n" % (option, value))

# vim:et:ts=4:sts=4:ai
