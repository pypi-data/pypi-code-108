#!/usr/bin/env python3
# coding: utf-8

from __future__ import print_function

import sys

codename_of_vers = {
    '4': 'etch',
    '5': 'lenny',
    '6': 'squeeze',
    '7': 'wheezy',
    '8': 'jessie',
    '9': 'stretch',
    '10': 'buster',
    '11': 'bullseye',
    '12': 'bookworm',
    '13': 'trixie',
    '4.10': 'warty',
    '5.04': 'hoary',
    '5.10': 'breezy',
    '6.06': 'dapper',
    '6.10': 'edgy',
    '7.04': 'feisty',
    '7.10': 'gutsy',
    '8.04': 'hardy',
    '8.10': 'intrepid',
    '9.04': 'jaunty',
    '9.10': 'karmic',
    '10.04': 'lucid',
    '10.10': 'maverick',
    '11.04': 'natty',
    '11.10': 'oneiric',
    '12.04': 'precise',
    '12.10': 'quantal',
    '13.04': 'raring',
    '13.10': 'saucy',
    '14.04': 'trusty',
    '14.10': 'utopic',
    '15.04': 'vivid',
    '15.10': 'wily',
    '16.04': 'xenial',
    '16.10': 'yakkety',
    '17.04': 'zesty',
    '17.10': 'artful',
    '18.04': 'bionic',
    '18.10': 'cosmic',
    '19.04': 'disco',
    '19.10': 'eoan',
    '20.04': 'focal',
    '20.10': 'groovy',
}

ver_of_codenames = {v: k for k, v in codename_of_vers.items()}

apt_debian = """\
deb http{s}://{host}/debian/ {codename} main contrib non-free
deb http{s}://{host}/debian/ {codename}-updates main contrib non-free
deb http{s}://{host}/debian/ {codename}-backports main contrib non-free
deb http{s}://{host}/debian-security/ {codename}/updates main contrib non-free
"""

apt_ubuntu = """\
deb http{s}://{host}/ubuntu/ {codename} main restricted universe multiverse
deb http{s}://{host}/ubuntu/ {codename}-security main restricted universe multiverse
deb http{s}://{host}/ubuntu/ {codename}-updates main restricted universe multiverse
deb http{s}://{host}/ubuntu/ {codename}-backports main restricted universe multiverse
"""


def fmt_sources_file(host: str, version: str, https: bool):
    if version in codename_of_vers:
        v = version
        c = codename_of_vers[version]
    elif version in ver_of_codenames:
        v = ver_of_codenames[version]
        c = version
    else:
        raise ValueError('unknown version {}'.format(version))
    if v.isdecimal():
        tmpl = apt_debian
    else:
        tmpl = apt_ubuntu
    kw = {
        's': 's' if https else '',
        'host': host, 'codename': c,
    }
    return tmpl.format(**kw)


def run(prog, args):
    import argparse
    desc = 'Generate an apt-get sources.list file'
    pr = argparse.ArgumentParser(prog=prog, description=desc)
    add = pr.add_argument
    add('-H', '--host', required=True,
        help='e.g. mirror.example.com')
    add('-v', '--version', required=True,
        help='codename or version numbers')
    add('-s', '--https', action='store_true',
        help='use https:// instead of http://')
    ns = pr.parse_args(args)
    try:
        text = fmt_sources_file(**vars(ns))
    except ValueError as e:
        print('error:', e, file=sys.stderr)
        return
    print(text)
