#!/usr/bin/env python3
# coding: utf-8

import base64
import binascii
import urllib.parse
from urllib.parse import ParseResult


def parse_qs_flat(query: str):
    d = urllib.parse.parse_qs(query, keep_blank_values=True)
    return {k: v[0] for k, v in d.items()}


def parse_url(url) -> (ParseResult, dict):
    pr = urllib.parse.urlparse(url)
    d = parse_qs_flat(pr.query)
    return pr, d


def parse_url_to_dict(url, component_prefix='@') -> dict:
    pr = urllib.parse.urlparse(url)
    d = parse_qs_flat(pr.query)
    # noinspection PyProtectedMember
    d.update({component_prefix + k: v for k, v in pr._asdict().items()})
    return d


def _base32(bs):
    return base64.b32encode(bs).decode().replace('=', '').lower()


def _base64_encode(s):
    return base64.urlsafe_b64encode(s.encode()).decode().replace('=', '')


def _base64_decode(s):
    padded = s[::-1] + '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(padded).decode()


def url_obfuscate(s):
    ss = base64.urlsafe_b64encode(s.encode())
    return ss.decode().replace('=', '')[::-1]


def url_deobfuscate(s):
    try:
        padded = s[::-1] + '=' * (-len(s) % 4)
        return base64.urlsafe_b64decode(padded).decode()
    except (UnicodeDecodeError, binascii.Error):
        pass
