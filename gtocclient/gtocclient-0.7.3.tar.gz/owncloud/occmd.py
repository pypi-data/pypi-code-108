#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import sys

try:
    ## Our modules
    ## Keep them in try/except block to
    ## detect any syntax errors in there
    from owncloud.exit_codes import *
    from owncloud.config import Config
    from owncloud.utils import *
    from owncloud.oc import Client, ResponseError, HTTPResponseError, OCSResponseError,FileInfo
    from owncloud import pkg_info
    from owncloud.exceptions import *
except Exception as e:
    print(e, "Error loading some components of occmd (Import Error)")
    sys.exit(1)

if sys.version_info < (2, 6):
    sys.stderr.write(u"ERROR: Python 2.6 or higher required, sorry.\n")
    # from .exit_codes import EX_OSFILE
    sys.exit(EX_OSFILE)

PY3 = (sys.version_info >= (3, 0))

import codecs
import errno
import glob
import io
import logging
import re
import socket
import traceback
from collections import deque
import getpass

from optparse import OptionParser, Option, OptionValueError, IndentedHelpFormatter
from logging import debug, info, warning, error
from ssl import SSLError, CertificateError


try:
    FileNotFoundError
except NameError:
    # py2.X
    FileNotFoundError = (IOError, OSError)

try:
    import htmlentitydefs
except Exception:
    # python 3 support
    import html.entities as htmlentitydefs

try:
    unicode
except NameError:
    # python 3 support
    # In python 3, unicode -> str, and str -> bytes
    unicode = str

try:
    from shutil import which
except ImportError:
    # python2 fallback code
    from distutils.spawn import find_executable as which


def output(message):
    sys.stdout.write(message + "\n")
    sys.stdout.flush()


def run_configure(config_file, args):
    cfg = Config()
    options = [
        ("url", "Owncloud url", "Your owncloud website address."),
        ("user_id", "User ID", "User ID is your identity for Owncloud."),
        ("password", "Password", "Your password."),
        ("proxy_host", "HTTP Proxy server name", "On some networks all internet access must go through a HTTP proxy.\nTry setting it here if you can't connect to Owncloud directly"),
        ("proxy_port", "HTTP Proxy server port"),
        ]

    if getattr(cfg, "proxy_host") == "" and os.getenv("http_proxy"):
        autodetected_encoding = locale.getpreferredencoding() or "UTF-8"
        re_match=re.match(r"(http://)?([^:]+):(\d+)",
                          unicodise_s(os.getenv("http_proxy"), autodetected_encoding))
        if re_match:
            setattr(cfg, "proxy_host", re_match.groups()[1])
            setattr(cfg, "proxy_port", re_match.groups()[2])

    try:
        # Support for python3
        # raw_input only exists in py2 and was renamed to input in py3
        global input
        input = raw_input
    except NameError:
        pass

    try:
        while True:
            output(u"\nEnter new values or accept defaults in brackets with Enter.")
            output(u"Refer to user manual for detailed description of all options.")
            for option in options:
                prompt = option[1]
                ## Option-specific handling
                if option[0] == 'proxy_host' and getattr(cfg, 'use_https') == True and sys.hexversion < 0x02070000:
                    setattr(cfg, option[0], "")
                    continue
                if option[0] == 'proxy_port' and getattr(cfg, 'proxy_host') == "":
                    setattr(cfg, option[0], 0)
                    continue

                try:
                    val = getattr(cfg, option[0])
                    if type(val) is bool:
                        val = val and "Yes" or "No"
                    if val not in (None, ""):
                        if option[0] == 'password':
                            prompt += " [*]"
                        else:
                            prompt += " [%s]" % val
                except AttributeError:
                    pass

                if len(option) >= 3:
                    output(u"\n%s" % option[2])
                if option[0] == 'password':
                    val = unicodise_s(getpass.getpass(prompt + ": "))
                else:
                    val = unicodise_s(input(prompt + ": "))
                if val != "":
                    if type(getattr(cfg, option[0])) is bool:
                        # Turn 'Yes' into True, everything else into False
                        val = val.lower().startswith('y')
                    setattr(cfg, option[0], val)
            output(u"\nNew settings:")
            for option in options:
                if option[0] == 'password':
                    output(u"%s:" % (option[1]))
                else:
                    output(u"  %s: %s" % (option[1], getattr(cfg, option[0])))
            val = input("\nTest access with supplied credentials? [Y/n] ")
            if val.lower().startswith("y") or val == "":
                try:
                    path = "/"

                    if len(args) > 0:
                        path = args[0]
                    output(u"Please wait, attempting to list files or directories: " + path)
                    client = Client(cfg.url)
                    client.login(cfg.user_id,cfg.password)
                    client.list(path,1)

                    output(u"Success. Your user ID and password worked fine :-)")

                except Exception as e:
                    error(u"Test failed: %s" % (e))
                    val = input("\nRetry configuration? [Y/n] ")
                    if val.lower().startswith("y") or val == "":
                        continue


            val = input("\nSave settings? [y/N] ")
            if val.lower().startswith("y"):
                break
            val = input("Retry configuration? [Y/n] ")
            if val.lower().startswith("n"):
                raise EOFError()

        ## Overwrite existing config file, make it user-readable only
        old_mask = os.umask(0o077)
        try:
            os.remove(deunicodise(config_file))
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise
        try:
            with io.open(deunicodise(config_file), "w", encoding=cfg.encoding) as fp:
                cfg.dump_config(fp)
        finally:
            os.umask(old_mask)
        output(u"Configuration saved to '%s'" % config_file)

    except (EOFError, KeyboardInterrupt):
        output(u"\nConfiguration aborted. Changes were NOT saved.")
        return

    except IOError as e:
        error(u"Writing config file failed: %s: %s" % (config_file, e.strerror))
        sys.exit(EX_IOERR)


def process_patterns_from_file(fname, patterns_list):
    try:
        with open(deunicodise(fname), "rt") as fn:
            for pattern in fn:
                pattern = unicodise(pattern).strip()
                if re.match("^#", pattern) or re.match(r"^\s*$", pattern):
                    continue
                debug(u"%s: adding rule: %s" % (fname, pattern))
                patterns_list.append(pattern)
    except IOError as e:
        error(e)
        sys.exit(EX_IOERR)

    return patterns_list


def process_patterns(patterns_list, patterns_from, is_glob, option_txt = ""):
    r"""
    process_patterns(patterns, patterns_from, is_glob, option_txt = "")
    Process --exclude / --include GLOB and REGEXP patterns.
    'option_txt' is 'exclude' / 'include' / 'rexclude' / 'rinclude'
    Returns: patterns_compiled, patterns_text
    Note: process_patterns_from_file will ignore lines starting with # as these
    are comments. To target escape the initial #, to use it in a file name, one
    can use: "[#]" (for exclude) or "\#" (for rexclude).
    """

    patterns_compiled = []
    patterns_textual = {}

    if patterns_list is None:
        patterns_list = []

    if patterns_from:
        ## Append patterns from glob_from
        for fname in patterns_from:
            debug(u"processing --%s-from %s" % (option_txt, fname))
            patterns_list = process_patterns_from_file(fname, patterns_list)

    for pattern in patterns_list:
        debug(u"processing %s rule: %s" % (option_txt, patterns_list))
        if is_glob:
            pattern = glob.fnmatch.translate(pattern)
        r = re.compile(pattern)
        patterns_compiled.append(r)
        patterns_textual[r] = pattern

    return patterns_compiled, patterns_textual


def test(args):
    cfg = Config()
    client = Client(cfg.url, progress=cfg.progress_meter, progress_class=cfg.progress_class, oc_path_format=True)
    client.login(cfg.user_id, cfg.password)
    client.copy("/DLP", "/tes/test")


def cmd_info(args):
    destination = normalize_oc_path(args.pop())
    cfg = Config()
    client = Client(cfg.url, progress=cfg.progress_meter, progress_class=cfg.progress_class, oc_path_format=True)
    client.login(cfg.user_id, cfg.password)
    if not client.exists(destination):
        raise ParameterError("No such file or directory: %s" % format_oc_path_output(convert(destination)))
    props = client.file_info(destination, FileInfo.get_all_property_arguments())
    file_name = convert(props.name)
    last_modified = props.attributes.get('{DAV:}getlastmodified')
    if last_modified:
        last_modified = format_oc_last_modified_time(last_modified)
    etag = props.attributes.get('{DAV:}getetag')
    if etag.startswith('"'): etag = etag[1:]
    if etag.endswith('"'): etag = etag[:-1]
    content_type = props.attributes.get('{DAV:}getcontenttype')
    content_length = props.attributes.get('{DAV:}getcontentlength')
    id = props.attributes.get('{http://owncloud.org/ns}id')
    file_id = props.attributes.get('{http://owncloud.org/ns}fileid')
    favorite = props.attributes.get('{http://owncloud.org/ns}favorite')
    comments_href = props.attributes.get('{http://owncloud.org/ns}comments-href')
    comments_count = props.attributes.get('{http://owncloud.org/ns}comments-count')
    comments_unread = props.attributes.get('{http://owncloud.org/ns}comments-unread')
    owner_id = props.attributes.get('{http://owncloud.org/ns}owner-id')
    owner_name = convert(props.attributes.get('{http://owncloud.org/ns}owner-display-name'))
    permissions = props.attributes.get('{http://owncloud.org/ns}permissions')
    size = props.attributes.get('{http://owncloud.org/ns}size')
    if props.file_type == 'file':
        format_string = \
u'''Name              %(filename)s
Type              File
Last Modified     %(last_modified)s
ETag              %(etag)s
Content Type      %(content_type)s
Content Length    %(content_length)s
ID                %(id)s
File ID           %(file_id)s
Favorite          %(favorite)s
Comments-href     %(comments_href)s
Comments-count    %(comments_count)s
Comments-unread   %(comments_unread)s
Owner ID          %(owner_id)s
Owner Name        %(owner_name)s
Checksums         %(sha1)s (SHA1)
                  %(md5)s (MD5)
                  %(adler32)s (ADLER32)
Permissions       %(permissions)s'''
        checksums = props.attributes.get('{http://owncloud.org/ns}checksums')
        sha1 = md5 = adler32 = None
        if checksums:
            checksums = checksums.get('{http://owncloud.org/ns}checksum')[0].split(' ')
            sha1 = checksums[0].split(':')[1]
            md5 = checksums[1].split(':')[1]
            adler32 = checksums[2].split(':')[1]
        output(format_string % {
            "last_modified": last_modified,
            "filename": file_name,
            "etag": etag,
            "content_type": content_type,
            "content_length": content_length,
            "id": id,
            "file_id": file_id,
            "favorite": favorite,
            "comments_href": comments_href,
            "comments_count": comments_count,
            "comments_unread": comments_unread,
            "owner_id": owner_id,
            "owner_name": owner_name,
            "sha1": sha1,
            "md5": md5,
            "adler32": adler32,
            "permissions": permissions,
        })
    else:
        format_string = \
u'''Name              %(filename)s
Type              Directory
Last Modified     %(last_modified)s
ETag              %(etag)s
ID                %(id)s
File ID           %(file_id)s
Favorite          %(favorite)s
Comments-href     %(comments_href)s
Comments-count    %(comments_count)s
Comments-unread   %(comments_unread)s
Owner ID          %(owner_id)s
Owner Name        %(owner_name)s
Permissions       %(permissions)s
Size              %(size)s'''
        output(format_string % {
            "last_modified": last_modified,
            "filename": file_name,
            "etag": etag,
            "id": id,
            "file_id": file_id,
            "favorite": favorite,
            "comments_href": comments_href,
            "comments_count": comments_count,
            "comments_unread": comments_unread,
            "owner_id": owner_id,
            "owner_name": owner_name,
            "permissions": permissions,
            "size": size
        })


def subcmd_mv_cp(source, destination_base, func):
    cfg = Config()
    client = Client(cfg.url, progress=cfg.progress_meter, progress_class=cfg.progress_class, oc_path_format=True)
    client.login(cfg.user_id, cfg.password)
    if not client.exists(source):
        raise ParameterError("No such directory: %s" % format_oc_path_output(convert(source)))
    prop = client.file_info(source)
    if prop.file_type == 'file':
        if client.exists(destination_base):
            dst_prop = client.file_info(destination_base)
            if dst_prop.file_type == 'file':
                if not cfg.force:
                    raise ParameterError(u"File %s already exists. Use either of --force." % format_oc_path_output(
                        convert(destination_base)))
                destination = destination_base
            else:
                destination = dst_prop.path + prop.name
                if client.exists(destination):
                    dst_prop = client.file_info(destination)
                    if dst_prop.file_type == 'file':
                        if not cfg.force:
                            raise ParameterError(
                                u"File %s already exists. Use either of --force." % format_oc_path_output(
                                    convert(destination)))
                    else:
                        raise ParameterError(
                            u"Dir %s already exists." % format_oc_path_output(
                                convert(destination)))
        else:
            destination = destination_base
    else:
        if client.exists(destination_base):
            dst_prop = client.file_info(destination_base)
            if dst_prop.file_type == 'file':
                raise ParameterError(
                    u"Dest path %s must be a directory. Try mkdir before copying." % format_oc_path_output(
                        convert(destination_base)))
            else:
                if not prop.name:
                    destination = destination_base
                else:
                    destination = dst_prop.path + prop.name
                    if client.exists(destination):
                        raise ParameterError(
                            u"Dir %s already exists." % format_oc_path_output(
                                convert(destination)))
        else:
            destination = destination_base
    func(client, source, destination)


def cmd_cp(args):
    destination_base = normalize_oc_path(args.pop())
    source = normalize_oc_path(args.pop())
    subcmd_mv_cp(source, destination_base, Client.copy)
    return EX_OK


def cmd_mv(args):
    destination_base = normalize_oc_path(args.pop())
    source = normalize_oc_path(args.pop())
    subcmd_mv_cp(source, destination_base, Client.move)
    return EX_OK


def cmd_rm(args):
    remote_path = normalize_oc_path(args.pop())
    cfg = Config()
    client = Client(cfg.url, progress=cfg.progress_meter, progress_class=cfg.progress_class, oc_path_format=True)
    client.login(cfg.user_id, cfg.password)
    if not client.exists(remote_path):
        raise ParameterError("No such directory: %s" % format_oc_path_output(convert(remote_path)))
    prop = client.file_info(remote_path)
    if prop.file_type == 'file':
        client.delete(remote_path)
    elif not cfg.recursive:
        raise ParameterError("%s is a directory. Try again with --recursive" % format_oc_path_output(convert(remote_path)))
    else:
        client.delete(remote_path)
    return EX_OK


def cmd_rmdir(args):
    destination = normalize_oc_path(args.pop())
    cfg = Config()
    client = Client(cfg.url, progress=cfg.progress_meter, progress_class=cfg.progress_class, oc_path_format=True)
    client.login(cfg.user_id, cfg.password)
    if not client.exists(destination):
        raise ParameterError("No such directory: %s" % format_oc_path_output(convert(destination)))
    props = client.file_info(destination)
    if props.file_type == 'file':
        raise ParameterError("%s is a file. Try remove a directory" % format_oc_path_output(convert(destination)))
    res = client.list(destination)
    if res:
        raise ParameterError("Directory %s not empty." % format_oc_path_output(convert(destination)))
    client.delete(destination)
    return EX_OK


def cmd_mkdir(args):
    destination = normalize_oc_path(args.pop())
    cfg = Config()
    client = Client(cfg.url, progress=cfg.progress_meter, progress_class=cfg.progress_class, oc_path_format=True)
    client.login(cfg.user_id, cfg.password)
    if client.exists(destination):
        raise ParameterError("Remote path %s already exists. Give it a new name" % format_oc_path_output(convert(destination)))
    client.mkdir(destination)
    return EX_OK


def cmd_put(args):
    local_path = args[0]
    cfg = Config()
    client = Client(cfg.url, progress=cfg.progress_meter, progress_class=cfg.progress_class, oc_path_format=True)
    client.login(cfg.user_id, cfg.password)

    if len(args) > 1:
        destination_base = normalize_oc_path(args.pop())
    else:
        destination_base = '/'
    existing = client.exists(destination_base)

    if local_path == '-':
        if existing:
            props = client.file_info(destination_base)
            if props.file_type == 'dir':
                raise ParameterError("Remote path %s must be file." % format_oc_path_output(convert(destination_base)))
            else:
                if cfg.skip_existing:
                    output(u"Skipping over existing dir: %s" % format_oc_path_output(convert(destination_base)))
                    return EX_OK
                if not cfg.force:
                    raise ParameterError(
                        u"File %s already exists. Use either of --force or --skip-existing." % format_oc_path_output(convert(destination_base)))
                client.delete(destination_base)

        src_stream = io.open(sys.stdin.fileno(), mode='rb', closefd=False)
        client.put_file_contents(destination_base, src_stream)
    elif os.path.isfile(local_path):
        try:
            client.put_file(destination_base, local_path, force=cfg.force, skip_existing=cfg.skip_existing,
                            put_continue=cfg.put_continue, chunked=cfg.chunked,
                            chunked_size=cfg.chunk_size_mb*1024*1024, cache_valid_hour=cfg.cache_valid_hour)
        except OCFileExistsError as e:
            raise ParameterError(
                u"File %s already exists. Use either of --force or --skip-existing." % format_oc_path_output(convert(e.path)))
        except OCUnexpectedDirError as e:
            raise ParameterError(
                u"Dir %s already exists. Give it a new name" % format_oc_path_output(convert(e.path)))
        return EX_OK
    elif os.path.isdir(local_path):
        if not existing:
            raise ParameterError(u"Remote path %s must be a directory when uploading directory." % format_oc_path_output(convert(destination_base)))
        else:
            props = client.file_info(destination_base)
            if props.file_type == 'file':
                raise ParameterError(u"Remote path must be a directory when uploading directory.")
        try:
            client.put_directory(destination_base, local_path, force=cfg.force, skip_existing=cfg.skip_existing,
                                 put_continue=cfg.put_continue, chunked=cfg.chunked,
                                 chunked_size=cfg.chunk_size_mb*1024*1024,cache_valid_hour=cfg.cache_valid_hour)
        except (OCFileExistsError, OCDirExistsError) as e:
            raise ParameterError(
                u"%s already exists. Use either of --force or --skip-existing or --put-continue" % format_oc_path_output(convert(e.path)))
        except OCUnexpectedDirError as e:
            raise ParameterError(
                u"Dir %s already exists. Give it a new name" % format_oc_path_output(convert(e.path)))
        return EX_OK
    else:
        raise ParameterError("No such file or directory: %s" % convert(local_path))


def cmd_get(args):
    remote_path = normalize_oc_path(args[0])
    cfg = Config()
    client = Client(cfg.url, progress=cfg.progress_meter, progress_class=cfg.progress_class, oc_path_format=True)
    client.login(cfg.user_id, cfg.password)
    props = client.file_info(remote_path)
    if len(args) > 1:
        destination_base = args.pop()
    else:
        destination_base = '.'
    if props.file_type == 'file':
        return subcmd_get_file(client,remote_path,destination_base)
    else:
        if not remote_path.endswith('/'):
            remote_path = remote_path + '/'
        if destination_base == "-":
            raise ParameterError(u"Unsupported standard output for directory: %s." % convert(destination_base))
        elif not os.path.isdir(destination_base):
            raise ParameterError(u"Local path must be a directory when downloading directory.")
        else:
            if cfg.download_as_zip:
                return subcmd_get_directory_as_zip(client, remote_path, destination_base)
            if remote_path != '/':
                basename = remote_path.split('/')[-2]
                if not destination_base.endswith(os.path.sep):
                    destination_base = destination_base + os.path.sep
                destination_base = destination_base + basename
            res = client.file_info(remote_path)
            q = deque([res])
            while q:
                sub_file = q.pop()
                destination_path = os.path.join(destination_base, sub_file.path[len(remote_path):].replace('/',os.path.sep))
                if sub_file.file_type == 'file':
                    subcmd_get_file(client, sub_file.path, destination_path)
                else:
                    if os.path.exists(destination_path):
                        if cfg.skip_existing:
                            output(u"Skipping over existing dir: %s" % convert(destination_path))
                        elif not cfg.force:
                            raise ParameterError(
                                u"Dir %s already exists. Use either of --force or --skip-existing." % convert(destination_path))
                        # else: 不删除已有文件，只覆盖
                        #     shutil.rmtree(destination_path)
                        #     os.mkdir(destination_path)
                    else:
                        info(u'Making dir: %s' % destination_path)
                        os.mkdir(destination_path)
                    _res = client.list(sub_file.path)
                    q.extend(_res)
        return EX_OK


def subcmd_get_directory_as_zip(client, remote_path, destination_base):
    cfg = Config()
    if os.path.isdir(destination_base):
        destination = os.path.join(destination_base, os.path.basename(remote_path[:-1])+'.zip')
    else:
        destination = destination_base
    if os.path.exists(destination):
        if cfg.skip_existing:
            output(u"Skipping over existing file: %s" % convert(destination))
            return EX_OK
        if not cfg.force:
            raise ParameterError(
                u"File %s already exists. Use either of --force or --skip-existing." % convert(destination))
    client.get_directory_as_zip(remote_path, destination)
    return EX_OK


def subcmd_get_file(client,remote_path,destination_base):
    cfg = Config()
    if destination_base == "-":
        dst_stream = io.open(sys.__stdout__.fileno(), mode='wb', closefd=False)
        client.get_file_contents(remote_path, dest_stream=dst_stream)
        output("")
        return EX_OK
    if os.path.isdir(destination_base):
        destination = os.path.join(destination_base, os.path.basename(remote_path))
    else:
        destination = destination_base
    if os.path.exists(destination):
        if cfg.skip_existing:
            output(u"Skipping over existing file: %s" % convert(destination))
            return EX_OK
        if not cfg.force:
            raise ParameterError(
                u"File %s already exists. Use either of --force, --skip-existing or give it a new name." % convert(destination))
    client.get_file(remote_path, destination)
    return EX_OK


def cmd_la(args):
    cfg = Config()
    cfg.depth = -1
    cmd_ls(args)


def cmd_ls(args):
    cfg = Config()
    client = Client(cfg.url, oc_path_format=True)
    client.login(cfg.user_id,cfg.password)
    path = "/"
    if len(args) > 0:
        path = normalize_oc_path(args[0])

    if cfg.long_listing:
        res = client.list(path, cfg.depth,
                          ['oc:checksums', 'd:getlastmodified', 'd:getcontentlength', 'oc:owner-id', 'oc:permissions'])

        max_len = 0
        for item in res:
            owner_id = item.attributes.get('{http://owncloud.org/ns}owner-id')
            if owner_id and len(owner_id) > max_len:
                max_len = len(owner_id)
        format_string = u"%(timestamp)16s %(permissions)-8s %(owner)"+str(max_len+1) + u"s %(size)s  %(md5)-33s  %(uri)s"
    elif cfg.list_md5:
        res = client.list(path, cfg.depth,
                          ['oc:checksums','d:getlastmodified','d:getcontentlength'])
        format_string = u"%(timestamp)16s %(size)s  %(md5)-33s  %(uri)s"
    else:
        res = client.list(path, cfg.depth)
        format_string = u"%(timestamp)16s %(size)s %(uri)s"

    if cfg.human_readable_sizes:
        size_format = u"%5d%1s"
        dir_str = u"DIR".rjust(6)
    else:
        size_format = u"%12d%s"
        dir_str = u"DIR".rjust(12)
    for item in res:
        file_lmt = item.attributes.get('{DAV:}getlastmodified')
        owner_id = item.attributes.get('{http://owncloud.org/ns}owner-id')
        permissions = item.attributes.get('{http://owncloud.org/ns}permissions')
        if item.file_type == 'file':
            size = item.attributes.get('{DAV:}getcontentlength')
            file_md5 = ""
            if item.attributes.get('{http://owncloud.org/ns}checksums'):
                checksums = item.attributes['{http://owncloud.org/ns}checksums']['{http://owncloud.org/ns}checksum'][0]
                file_md5 = checksums.split(' ')[1].split(':')[1]
            output(format_string % {
                "timestamp": format_oc_last_modified_time(file_lmt) if file_lmt else None,
                "size": size_format % format_size(size,cfg.human_readable_sizes) if size else None,
                "md5": file_md5,
                "owner": owner_id,
                "permissions": permissions,
                "uri": format_oc_path_output(convert(item.path))
            })
        if item.file_type == 'dir':
            output(format_string % {
                "timestamp": format_oc_last_modified_time(file_lmt) if file_lmt else None,
                "size": dir_str,
                "md5": '',
                "owner": owner_id,
                "permissions": permissions,
                "uri": format_oc_path_output(convert(item.path))
            })
    return EX_OK


def get_commands_list():
    return [
        {"cmd": "ls", "label": "List directories or files", "param": "oc://<REMOTE_PATH>", "func": cmd_ls, "argc": 0},
        {"cmd": "la", "label": "List all directories or files", "param": "oc://<REMOTE_PATH>", "func": cmd_la,
         "argc": 0},
        {"cmd": "get", "label": "Get files from owncloud", "param": "oc://<REMOTE_PATH> <LOCAL_PATH>", "func": cmd_get,
         "argc": 1},
        {"cmd": "put", "label": "Put files to owncloud", "param": "<LOCAL_PATH> oc://<REMOTE_PATH>", "func": cmd_put,
         "argc": 1},
        {"cmd": "mkdir", "label": "Make a directory", "param": "oc://<REMOTE_PATH>", "func": cmd_mkdir,
         "argc": 1},
        {"cmd": "rmdir", "label": "Remove a directory", "param": "oc://<REMOTE_PATH>", "func": cmd_rmdir,
         "argc": 1},
        # {"cmd": "rm", "label": "Remove a file or directory", "param": "oc://<REMOTE_PATH>", "func": cmd_rm,
        #  "argc": 1},
        # {"cmd": "del", "label": "Delete a file or directory (alias for rm)", "param": "oc://<REMOTE_PATH>", "func": cmd_rm,
        #  "argc": 1},
        # {"cmd": "mv", "label": "Move a file", "param": "oc://<REMOTE_SRC_PATH> oc://<REMOTE_DEST_PATH>", "func": cmd_mv,
        #  "argc": 2},
        # {"cmd": "cp", "label": "Copy a file", "param": "oc://<REMOTE_SRC_PATH> oc://<REMOTE_DEST_PATH>", "func": cmd_cp,
        #  "argc": 2},
        {"cmd": "info", "label": "Display details of a file", "param": "oc://<REMOTE_PATH>", "func": cmd_info,
         "argc": 1},
        # {"cmd": "test", "label": "test","param": "None", "func": test, "argc": 0},
    ]


def format_commands(progname, commands_list):
    help = "Commands:\n"
    for cmd in commands_list:
        help += "  %s\n      %s %s %s\n" % (cmd["label"], progname, cmd["cmd"], cmd["param"])
    return help


class MyHelpFormatter(IndentedHelpFormatter):
    def format_epilog(self, epilog):
        if epilog:
            return "\n" + epilog + "\n"
        else:
            return ""

def cmd():
    cfg = Config()
    commands_list = get_commands_list()
    commands = {}

    ## Populate "commands" from "commands_list"
    for cmd in commands_list:
        if 'cmd' in cmd:
            commands[cmd['cmd']] = cmd

    optparser = OptionParser(formatter=MyHelpFormatter())
    #optparser.disable_interspersed_args()

    autodetected_encoding = locale.getpreferredencoding() or "UTF-8"

    config_file = None
    if os.getenv("OCCMD_CONFIG"):
        config_file = unicodise_s(os.getenv("OCCMD_CONFIG"),
                                  autodetected_encoding)
    elif os.name == "nt" and os.getenv("USERPROFILE"):
        config_file = os.path.join(
            unicodise_s(os.getenv("USERPROFILE"), autodetected_encoding),
            os.getenv("APPDATA")
               and unicodise_s(os.getenv("APPDATA"), autodetected_encoding)
               or 'Application Data',
            "occmd.ini")
    else:
        from os.path import expanduser
        config_file = os.path.join(expanduser("~"), ".occfg")

    optparser.set_defaults(config = config_file)

    optparser.add_option(      "--configure", dest="run_configure", action="store_true", help="Invoke interactive (re)configuration tool. Optionally use as '--configure PATH' to test access to a specific bucket instead of attempting to list them all.")
    optparser.add_option("-c", "--config", dest="config", metavar="FILE", help="Config file name. Defaults to $HOME/.occfg")
    optparser.add_option(      "--dump-config", dest="dump_config", action="store_true", help="Dump current configuration after parsing config files and command line options and exit.")
    optparser.add_option(      "--user_id", dest="user_id", help="Owncloud user ID")
    optparser.add_option(      "--password", dest="password", help="Owncloud user password")
    optparser.add_option(      "--url", dest="url", help="Owncloud url")
    optparser.add_option(      "--depth", dest="depth", help="The limit depth while traversing directory for [ls] command.", metavar="NUM")
    optparser.add_option(      "--list-md5", dest="list_md5", action="store_true", help="Include MD5 sums in dir listings (only for 'ls' command).")
    optparser.add_option("-l", "--long-listing", dest="long_listing", action="store_true", help="Produce long listing [ls]")
    optparser.add_option("-H", "--human-readable-sizes", dest="human_readable_sizes", action="store_true", help="Print sizes in human readable form (eg 1kB instead of 1024).")
    optparser.add_option("--progress", dest="progress_meter", action="store_true",
                         help="Display progress meter (default on TTY).")
    optparser.add_option("--no-progress", dest="progress_meter", action="store_false",
                         help="Don't display progress meter (default on non-TTY).")
    # optparser.add_option("-r", "--recursive", dest="recursive", action="store_true", help="Recursive upload, download or removal.")
    optparser.add_option("-f", "--force", dest="force", action="store_true",
                         help="Force overwrite and other dangerous operations.")
    optparser.add_option(      "--skip-existing", dest="skip_existing", action="store_true", help="Skip over files that exist at the destination (only for [get] and [sync] commands).")
    optparser.add_option(      "--download-as-zip", dest="download_as_zip", action="store_true",help="Download directory as zip.")
    optparser.add_option(      "--put-continue", dest="put_continue", action="store_true", help="Continue uploading (partially) uploaded files  Restarts files that don't have matching size and md5.  Skips files that do.  Note: md5sum checks are not always sufficient to check (part) file equality.  Enable this at your own risk.")
    optparser.add_option(      "--chunk-size-mb", dest="chunk_size_mb", type="int", action="store", metavar="SIZE", help="Size of each chunk of an upload. Files bigger than SIZE are automatically uploaded as chunk, smaller files are uploaded using the traditional method. SIZE is in Mega-Bytes, default chunk size is 15MB, minimum allowed chunk size is 5MB, maximum is 5GB.")
    optparser.add_option(      "--chunked", dest="chunked", action="store_true", help="Enable chunk upload on files bigger than --chunk-size-mb")
    optparser.add_option(      "--cache_valid_hour", dest="cache_valid_hour", type="int", action="store", metavar="HOUR", help="Cache file valid hour for chunk upload, default hour is 8")
    optparser.add_option("-r", "--recursive", dest="recursive", action="store_true", help="Recursive removal.")
    optparser.add_option("-v", "--verbose", dest="verbosity", action="store_const", const=logging.INFO,
                         help="Enable verbose output.")
    optparser.add_option("-d", "--debug", dest="verbosity", action="store_const", const=logging.DEBUG,
                         help="Enable debug output.")
    optparser.add_option("--version", dest="show_version", action="store_true",
                         help="Show occmd version (%s) and exit." % pkg_info.version)
    optparser.add_option("-q", "--quiet", dest="quiet", action="store_true", default=False, help="Silence output on stdout")


    optparser.set_usage(optparser.usage + " COMMAND [parameters]")
    optparser.set_description('occmd is a tool for managing files or directories in '+
        'Owncloud. It allows for '+
        'uploading, downloading and removing '+
        'files or directories.')
    optparser.epilog = format_commands(optparser.get_prog_name(), commands_list)

    (options, args) = optparser.parse_args()

    ## Some mucking with logging levels to enable
    ## debugging/verbose output for config file parser on request
    logging.basicConfig(level=options.verbosity or Config().verbosity,
                        format='%(levelname)s: %(message)s',
                        stream = sys.stderr)

    if options.show_version:
        output(u"gtocclient version %s" % pkg_info.version)
        sys.exit(EX_OK)
    debug(u"s3cmd version %s" % pkg_info.version)

    if options.quiet:
        try:
            f = open("/dev/null", "w")
            sys.stdout = f
        except IOError:
            warning(u"Unable to open /dev/null: --quiet disabled.")

    ## Now finally parse the config file
    if not options.config:
        error(u"Can't find a config file. Please use --config option.")
        sys.exit(EX_CONFIG)

    try:
        cfg = Config(options.config, options.user_id, options.password)
    except ValueError as exc:
        raise ParameterError(unicode(exc))
    except IOError as e:
        if options.run_configure:
            cfg = Config()
        else:
            error(u"%s: %s"  % (options.config, e.strerror))
            error(u"Configuration file not available.")
            error(u"Consider using --configure parameter to create one.")
            sys.exit(EX_CONFIG)

    # allow commandline verbosity config to override config file
    if options.verbosity is not None:
        cfg.verbosity = options.verbosity
    logging.root.setLevel(cfg.verbosity)

    ## Update Config with other parameters
    for option in cfg.option_list():
        try:
            value = getattr(options, option)
            if value != None:
                if type(value) == type(b''):
                    value = unicodise_s(value)
                debug(u"Updating Config.Config %s -> %s" % (option, value))
                cfg.update_option(option, value)
        except AttributeError:
            ## Some Config() options are not settable from command line
            pass

    ## Check multipart chunk constraints
    if cfg.chunk_size_mb < Client.MIN_CHUNK_SIZE_MB:
        raise ParameterError("Chunk size %d MB is too small, must be >= %d MB. Please adjust --chunk-size-mb" % (cfg.chunk_size_mb, Client.MIN_CHUNK_SIZE_MB))
    if cfg.chunk_size_mb > Client.MAX_CHUNK_SIZE_MB:
        raise ParameterError("Chunk size %d MB is too large, must be <= %d MB. Please adjust --chunk-size-mb" % (cfg.chunk_size_mb, Client.MAX_CHUNK_SIZE_MB))

    ## Set output and filesystem encoding for printing out filenames.
    try:
        # Support for python3
        # That don't need codecs if output is the
        # encoding of the system, but just in case, still use it.
        # For that, we need to use directly the binary buffer
        # of stdout/stderr
        sys.stdout = codecs.getwriter(cfg.encoding)(sys.stdout.buffer, "replace")
        sys.stderr = codecs.getwriter(cfg.encoding)(sys.stderr.buffer, "replace")
        # getwriter with create an "IObuffer" that have not the encoding attribute
        # better to add it to not break some functions like "input".
        sys.stdout.encoding = cfg.encoding
        sys.stderr.encoding = cfg.encoding
    except AttributeError:
        sys.stdout = codecs.getwriter(cfg.encoding)(sys.stdout, "replace")
        sys.stderr = codecs.getwriter(cfg.encoding)(sys.stderr, "replace")

    if options.dump_config:
        cfg.dump_config(sys.stdout)
        sys.exit(EX_OK)

    if options.run_configure:
        # 'args' may contain the test-bucket URI
        run_configure(options.config, args)
        sys.exit(EX_OK)

    if len(args) < 1:
        optparser.print_help()
        sys.exit(EX_USAGE)

    ## Unicodise all remaining arguments:
    args = [unicodise(arg) for arg in args]

    command = args.pop(0)
    try:
        debug(u"Command: %s" % commands[command]["cmd"])
        ## We must do this lookup in extra step to
        ## avoid catching all KeyError exceptions
        ## from inner functions.
        cmd_func = commands[command]["func"]
    except KeyError as e:
        error(u"Invalid command: %s", command)
        sys.exit(EX_USAGE)

    if len(args) < commands[command]["argc"]:
        error(u"Not enough parameters for command '%s'" % command)
        sys.exit(EX_USAGE)

    rc = cmd_func(args)
    if rc is None: # if we missed any cmd_*() returns
        rc = EX_GENERAL
    return rc

def report_exception(e, msg=u''):
        alert_header = u"""
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    An unexpected error has occurred.
  Please contact support@getui.com
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  %s
"""
        sys.stderr.write(alert_header % (u"\n\n" + msg))
        tb = traceback.format_exc()
        try:
            s = u' '.join([unicodise(a) for a in sys.argv])
        except NameError:
            # Error happened before Utils module was yet imported to provide
            # unicodise
            try:
                s = u' '.join([(a) for a in sys.argv])
            except UnicodeDecodeError:
                s = u'[encoding safe] ' + u' '.join([('%r'%a) for a in sys.argv])
        sys.stderr.write(u"Invoked as: %s\n" % s)

        e_class = str(e.__class__)
        e_class = e_class[e_class.rfind(".")+1 : -2]
        try:
            sys.stderr.write(u"Problem: %s: %s\n" % (e_class, e))
        except UnicodeDecodeError:
            sys.stderr.write(u"Problem: [encoding safe] %r: %r\n"
                             % (e_class, e))
        try:
            sys.stderr.write(u"occmd:   %s\n" % pkg_info.version)
        except NameError:
            sys.stderr.write(u"occmd:   unknown version."
                             "Module import problem?\n")
        sys.stderr.write(u"python:   %s\n" % sys.version)
        try:
            sys.stderr.write(u"environment LANG=%s\n"
                             % unicodise_s(os.getenv("LANG", "NOTSET"),
                                           'ascii'))
        except NameError:
            # Error happened before Utils module was yet imported to provide
            # unicodise
            sys.stderr.write(u"environment LANG=%s\n"
                             % os.getenv("LANG", "NOTSET"))
        sys.stderr.write(u"\n")
        if type(tb) == unicode:
            sys.stderr.write(tb)
        else:
            sys.stderr.write(unicode(tb, errors="replace"))

        if type(e) == ImportError:
            sys.stderr.write("\n")
            sys.stderr.write("Your sys.path contains these entries:\n")
            for path in sys.path:
                sys.stderr.write(u"\t%s\n" % path)
            sys.stderr.write("Now the question is where have the s3cmd modules"
                             " been installed?\n")

        # sys.stderr.write(alert_header % (u"above lines", u""))


def main():
    try:
        rc = cmd()
        sys.exit(rc)

    except ImportError as e:
        report_exception(e)
        sys.exit(EX_GENERAL)

    except (ParameterError, InvalidFileError) as e:
        error(u"Parameter problem: %s" % e)
        sys.exit(EX_USAGE)

    except ValueError as e:
        error(e)
        sys.exit(EX_USAGE)

    except HTTPResponseError as e:
        error(u"Owncloud response error: %s" % e)
        sys.exit(e.get_error_code())

    except SystemExit as e:
        sys.exit(e.code)

    except KeyboardInterrupt:
        sys.stderr.write("See ya!\n")
        sys.exit(EX_BREAK)

    except (SSLError, CertificateError) as e:
        # SSLError is a subtype of IOError
        error("SSL certificate verification failure: %s" % e)
        sys.exit(EX_ACCESSDENIED)

    except socket.gaierror as e:
        # gaierror is a subset of IOError
        # typically encountered error is:
        # gaierror: [Errno -2] Name or service not known
        error(e)
        error("Connection Error: Error resolving a server hostname.\n"
              "Please check the servers address specified in 'url'")
        sys.exit(EX_IOERR)

    except FileNotFoundError as e:
        error(e)
        sys.exit(EX_IOERR)

    except IOError as e:
        if e.errno == errno.EPIPE:
            # Fail silently on SIGPIPE. This likely means we wrote to a closed
            # pipe and user does not care for any more output.
            sys.exit(EX_IOERR)

        report_exception(e)
        sys.exit(EX_IOERR)

    except OSError as e:
        error(e)
        sys.exit(EX_OSERR)

    except MemoryError:
        msg = """
MemoryError!  You have exceeded the amount of memory available for this process.
This usually occurs when syncing >750,000 files on a 32-bit python instance.
The solutions to this are:
1) sync several smaller subtrees; or
2) use a 64-bit python on a 64-bit OS with >8GB RAM
        """
        sys.stderr.write(msg)
        sys.exit(EX_OSERR)

    except UnicodeEncodeError as e:
        lang = unicodise_s(os.getenv("LANG", "NOTSET"), 'ascii')
        msg = """
You have encountered a UnicodeEncodeError.  Your environment
variable LANG=%s may not specify a Unicode encoding (e.g. UTF-8).
Please set LANG=en_US.UTF-8 or similar in your environment before
invoking occmd.
        """ % lang
        report_exception(e, msg)
        sys.exit(EX_GENERAL)

    except Exception as e:
        report_exception(e)
        sys.exit(EX_GENERAL)

if __name__ == '__main__':
    main()
# vim:et:ts=4:sts=4:ai
