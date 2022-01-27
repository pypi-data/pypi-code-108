# -*- coding: utf-8 -*-
# Copyright 2007-2019 The Wazo Authors
# SPDX-License-Identifier: GPL-3.0-or-later
"""sonicprobe.libs.network"""

import re
import socket
import struct

from six import ensure_binary, ensure_str, ensure_text, integer_types, string_types, text_type as stext_type

from sonicprobe.helpers import maketrans


HEXDIG                  = "0123456789abcdefABCDEF"
BYTES_VAL               = ''.join(map(chr, range(0, 256)))

ATOM                    = r'\!#\$%&\'\*\+\-\/0-9\=\?A-Z\^_`a-z\{\|\}~'
QTEXT                   = r'\x20\x21\x23-\x5B\x5D-\x7E'
QUOTEDPAIR              = r'\(\)\<\>\[\]\:;@\,\."\\'

DOMAIN_PART             = r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'

MASK_IPV4_DOTDEC        = 1
MASK_IPV4               = 2
MASK_IPV6               = 4
MASK_DOMAIN             = 256
MASK_DOMAIN_TLD         = 512
MASK_DOMAIN_IDN         = 1024
MASK_SUB_DOMAIN_TLD     = 2048

MASK_IP_ALL             = (MASK_IPV4 |
                           MASK_IPV6)

MASK_DOMAIN_ALL         = (MASK_DOMAIN |
                           MASK_DOMAIN_TLD |
                           MASK_DOMAIN_IDN)

MASK_HOST_ALL           = (MASK_IP_ALL |
                           MASK_DOMAIN_ALL)

MASK_EMAIL_HOST_ALL     = (MASK_DOMAIN_TLD |
                           MASK_DOMAIN_IDN)

RE_DOMAIN_PART          = re.compile(r'^(' + DOMAIN_PART + r')$').match
RE_DOMAIN               = re.compile(r'^(?:' + DOMAIN_PART + r'\.)*(?:' + DOMAIN_PART + r')$').match
RE_DOMAIN_TLD           = re.compile(r'^(?:' + DOMAIN_PART + r'\.)+(?:' + DOMAIN_PART + r')$').match
RE_SUB_DOMAIN_TLD       = re.compile(r'^(?:' + DOMAIN_PART + r'\.){2,}(?:' + DOMAIN_PART + r')$').match
RE_EMAIL_LOCALPART      = re.compile(r'^(?:[' + ATOM + r']+(?:\.[' + ATOM + r']+)*|' + \
                                         r'"(?:[' + QTEXT + r']|' + \
                                             r'\\[' + QUOTEDPAIR + r'])+")$').match
RE_MAC_ADDR_NORMALIZE   = re.compile(r'([A-F0-9]{1,2})[-: ]?', re.I).findall
RE_MAC_ADDRESS          = re.compile(r'^([A-F0-9]{2}:){5}([A-F0-9]{2})$', re.I).match


def __all_in(s, charset):
    if not isinstance(s, stext_type):
        s = str(s)
    else:
        s = ensure_str(s, 'utf8')
    return not s.translate(*maketrans(BYTES_VAL, charset))

def __split_sz(s, n):
    return [s[b:b + n] for b in range(0, len(s), n)]

def ipv4_to_long(addr):
    return struct.unpack('!L', socket.inet_aton(addr))[0]

def long_to_ipv4(addr):
    return socket.inet_ntoa(struct.pack('!L', addr))

def normalize_ipv4_dotdec(addr):
    try:
        return socket.inet_ntoa(socket.inet_aton(addr))
    except socket.error:
        return False

def valid_bitmask_ipv4(bit):
    if isinstance(bit, integer_types):
        bit = str(bit)

    if not isinstance(bit, string_types):
        return False

    return bit.isdigit() and 0 < int(bit) < 33

def bitmask_to_netmask_ipv4(bit):
    if not valid_bitmask_ipv4(bit):
        return False

    return long_to_ipv4((0xFFFFFFFF >> (32 - int(bit))) << (32 - int(bit)))

def valid_ipv4(addr):
    "True <=> valid"
    try:
        socket.inet_aton(addr)
        return True
    except socket.error:
        return False

def valid_ipv4_dotdec(potential_ipv4):
    if not isinstance(potential_ipv4, string_types):
        return False

    if potential_ipv4[0] not in (HEXDIG + "xX") \
       or not __all_in(potential_ipv4[1:], (HEXDIG + ".xX")):
        return False

    s_ipv4 = potential_ipv4.split('.', 4)
    if len(s_ipv4) != 4:
        return False

    try:
        for s in s_ipv4:
            if not 0 <= int(s, 0) <= 255:
                return False
    except ValueError:
        return False

    return True

def valid_ipv6_h16(h16):
    try:
        i = int(h16, 16)
        return 0 <= i <= 65535
    except ValueError:
        return False

def valid_ipv6_right(right_v6):
    if not isinstance(right_v6, string_types):
        return False

    if right_v6 == '':
        return 0

    array_v6 = right_v6.split(':', 8)
    if len(array_v6) > 8 \
       or (len(array_v6) > 7 and ('.' in right_v6)) \
       or (not __all_in(''.join(array_v6[:-1]), HEXDIG)):
        return False

    if '.' in array_v6[-1]:
        if not valid_ipv4_dotdec(array_v6[-1]):
            return False
        h16_count = 2
        array_v6 = array_v6[:-1]
    else:
        h16_count = 0

    for h16 in array_v6:
        if not valid_ipv6_h16(h16):
            return False

    return h16_count + len(array_v6)

def valid_ipv6_left(left_v6):
    if not isinstance(left_v6, string_types):
        return False

    if left_v6 == '':
        return 0

    array_v6 = left_v6.split(':', 7)
    if len(array_v6) > 7 \
       or (not __all_in(''.join(array_v6), HEXDIG)):
        return False

    for h16 in array_v6:
        if not valid_ipv6_h16(h16):
            return False

    return len(array_v6)

def valid_ipv6_address(potential_ipv6):
    if not isinstance(potential_ipv6, string_types):
        return False

    sep_pos     = potential_ipv6.find('::')
    sep_count   = potential_ipv6.count('::')

    if sep_pos < 0:
        return valid_ipv6_right(potential_ipv6) == 8

    if sep_count == 1:
        right = valid_ipv6_right(potential_ipv6[sep_pos + 2:])
        if right is False:
            return False

        left = valid_ipv6_left(potential_ipv6[:sep_pos])
        if left is False:
            return False

        return right + left <= 7

    return False

def parse_ipv4_cidr(cidr):
    if not isinstance(cidr, string_types):
        return False

    r = cidr.split('/', 1)
    if len(r) == 1:
        r.append('32')

    if not valid_ipv4_dotdec(r[0]) or not bitmask_to_netmask_ipv4(r[1]):
        return False

    return r

def encode_idn(value, text_type = False):
    if not isinstance(value, string_types):
        return False

    if not isinstance(value, stext_type):
        value = ensure_str(value)

    if text_type:
        return ensure_text(value.encode('idna'))

    return ensure_binary(value.encode('idna'))

def decode_idn(value):
    if not isinstance(value, string_types):
        return False

    value = ensure_binary(value)

    try:
        value = value.decode('idna')
    except UnicodeDecodeError:
        pass

    return ensure_text(value)

def valid_domain_part(domain_part):
    if isinstance(domain_part, string_types) \
       and RE_DOMAIN_PART(domain_part):
        return True

    return False

def valid_domain(domain):
    if isinstance(domain, string_types) \
       and len(domain) < 256 \
       and RE_DOMAIN(domain):
        return True

    return False

def valid_domain_tld(domain_tld):
    if isinstance(domain_tld, string_types) \
       and len(domain_tld) < 256 \
       and RE_DOMAIN_TLD(domain_tld):
        return True

    return False

def valid_sub_domain_tld(sub_domain_tld):
    if isinstance(sub_domain_tld, string_types) \
       and len(sub_domain_tld) < 256 \
       and RE_SUB_DOMAIN_TLD(sub_domain_tld):
        return True

    return False

def valid_host(host, host_mask = MASK_HOST_ALL):
    if host_mask & MASK_IPV4 and valid_ipv4(host):
        return True

    if host_mask & MASK_IPV4_DOTDEC and valid_ipv4_dotdec(host):
        return True

    if host_mask & MASK_IPV6 and valid_ipv6_address(host):
        return True

    if host_mask & MASK_DOMAIN_IDN:
        host = encode_idn(host)

    if host_mask & MASK_DOMAIN and valid_domain(host):
        return True

    if host_mask & MASK_DOMAIN_TLD and valid_domain_tld(host):
        return True

    if host_mask & MASK_SUB_DOMAIN_TLD and valid_sub_domain_tld(host):
        return True

    return False

def parse_domain_cert(domain, domain_mask = MASK_DOMAIN_ALL):
    r = {'domain':   domain,
         'wildcard': True}

    if not isinstance(r['domain'], string_types):
        return False

    if r['domain'].startswith('*.'):
        r['domain']   = r['domain'][2:]
        r['wildcard'] = True

    if domain_mask & MASK_DOMAIN_IDN:
        r['domain'] = encode_idn(r['domain'])

    if domain_mask & MASK_DOMAIN and valid_domain(r['domain']):
        return r

    if domain_mask & MASK_DOMAIN_TLD and valid_domain_tld(r['domain']):
        return r

    if domain_mask & MASK_SUB_DOMAIN_TLD and valid_sub_domain_tld(r['domain']):
        return r

    return False

def valid_domain_cert(domain, domain_mask = MASK_DOMAIN_ALL):
    return bool(parse_domain_cert(domain, domain_mask))

def valid_port_number(port):
    try:
        i = int(port)
        return 0 <= i <= 65535
    except ValueError:
        return False

def valid_email_localpart(localpart):
    if isinstance(localpart, string_types) \
       and 1 <= len(localpart) <= 64 \
       and RE_EMAIL_LOCALPART(localpart):
        return True

    return False

def valid_email_address_literal(address, host_mask = MASK_EMAIL_HOST_ALL):
    if not isinstance(address, string_types) or address == '':
        return False

    if address[0] == '[' and address[-1] == ']':
        if address.startswith('[IPv6:'):
            if not host_mask & MASK_IPV6:
                return False

            address = address[6:-1]

            if not valid_ipv6_address(address):
                return False

            return True

        if not host_mask & MASK_IPV4_DOTDEC:
            return False

        address = address[1:-1]

        if not valid_ipv4_dotdec(address):
            return False

        return True

    mask = 0

    if host_mask & MASK_DOMAIN:
        mask = mask | MASK_DOMAIN

    if host_mask & MASK_DOMAIN_TLD:
        mask = mask | MASK_DOMAIN_TLD

    if host_mask & MASK_DOMAIN_IDN:
        mask = mask | MASK_DOMAIN_IDN

    if host_mask & MASK_SUB_DOMAIN_TLD:
        mask = mask | MASK_SUB_DOMAIN_TLD

    if mask == 0 or not valid_host(address, mask):
        return False

    return True

def valid_email(email, host_mask = MASK_EMAIL_HOST_ALL):
    if not isinstance(email, string_types) \
       or len(email) > 320:
        return False

    pos         = email.rfind('@')
    if pos < 2:
        return False

    localpart   = email[0:pos]
    address     = email[pos + 1:]

    if not valid_email_localpart(localpart) \
       or not valid_email_address_literal(address, host_mask):
        return False

    return True

def normalize_mac_address(macaddr):
    if not isinstance(macaddr, string_types):
        return False

    m = RE_MAC_ADDR_NORMALIZE(macaddr.upper())
    if len(m) != 6:
        return False

    return ':'.join([('%02X' % int(s, 16)) for s in m])

def valid_mac_address(macaddr):
    if isinstance(macaddr, string_types) \
       and RE_MAC_ADDRESS(macaddr) \
       and macaddr != '00:00:00:00:00:00':
        return True

    return False
