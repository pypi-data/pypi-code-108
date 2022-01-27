#!/usr/bin/env python3

import re
import os
import sys
import termios
import argparse
import subprocess
from math import ceil
from os import environ
from getpass import getpass
from inspect import signature
from ipaddress import ip_address, IPv4Network, IPv6Network


SAMBA_TOOL = 'samba-tool'
SOA_RE = re.compile(r"([\w^.]+)\.\s+IN\s+SOA")
ENTRY_RE = re.compile(
    r"\A\s*([a-zA-Z0-9-.]+)\.?\s+(?:\d*\s*?)?(?:IN)?\s+(AAAA|A|CNAME|PTR|MX)\s+([^;]+)")


def samba_tool():
    st_env = environ.get('SAMBA_TOOL')
    return st_env if st_env else SAMBA_TOOL

def args_parser():
    parser = argparse.ArgumentParser(description=\
        'Convert data in BIND zone format to calls to samba-tool.')
    parser.add_argument("--zone")
    parser.add_argument("--ipv4-subnet",
                        action="append",
                        default=[],
                        help="Subnet for IPv4 reverse DNS lookups; "
                             "can be given multiple times ")
    parser.add_argument("--ipv6-subnet",
                        action="append",
                        default=[],
                        help="Subnet for IPv6 reverse DNS lookups; "
                             "can be given multiple times")
    parser.add_argument("--password",
                        help="Administrator password for samba-tool")
    parser.add_argument("--filter",
                        action="store",
                        nargs=1,
                        default=list(HANDLERS.keys()),
                        help="Only handle records of the given type(s)")
    parser.add_argument("--dry-run",
                        "-n",
                        action="store_true",
                        help="Only show commands, do not execute")
    parser.add_argument("--force",
                        "-f",
                        action="store_true",
                        help="Continue execution even if an invocation of "
                             "samba-tool fails")
    parser.add_argument("zonefile",
                        nargs='?',
                        type=argparse.FileType('r'),
                        default=sys.stdin)
    return parser

def filter_matching_subnet(address, subnets):
    """Returns the subnet containing the given address.

    Given an addres and a list of subnets, this method returns the smallest
    subnet that contains the given address.
    """
    filtered_subnets = sorted([s for s in subnets if address in s],
                              key=lambda x: x.prefixlen)
    if filtered_subnets:
        return filtered_subnets[-1]
    return None

def rev4_from_network(subnet):
    octets = subnet.network_address.packed[0:ceil(subnet.prefixlen/8)]
    octets = [str(int(i)) for i in octets]
    octets.reverse()
    return "%s.in-addr.arpa" % ".".join(octets)

def rev6_from_network(subnet):
    s = str(subnet.network_address.exploded).replace(":", "")
    nibbles = [i for i in s[0:ceil(subnet.prefixlen/4)]]
    nibbles.reverse()
    return "%s.ip6.arpa" % ".".join(nibbles)

def cmd(zone, name, type, *data):
    return [samba_tool(),
            'dns',
            'add',
            'localhost',
            zone,
            name,
            type,
            *data]

def expand_name(name, domainname):
    if name[-1] == ".":
        name = name[0:-1]
    else:
        name = "%s.%s" % (name, domainname)
    return name

def strip_domain(name, domain):
    """Checks ::`name` for ::``domain`` and strips it."""
    return re.sub(r"\." + re.escape(domain) + r"\.?\Z", "", name)

def add_cname(name, target, domainname):
    return [cmd(domainname, name, 'CNAME', expand_name(target, domainname))]

def add_a(name, address, domainname, rev4=list()):
    c = [cmd(domainname, strip_domain(name, domainname), 'A', str(address))]
    rev4 = filter_matching_subnet(address, rev4)
    if rev4:
        c += [
            cmd(
                rev4_from_network(rev4),
                str(address.reverse_pointer),
                'PTR',
                "%s.%s" % (strip_domain(name, domainname), domainname)
            )
        ]
    return c

def add_aaaa(name, address, domainname, rev6=list()):
    c = [cmd(domainname, strip_domain(name, domainname), 'AAAA', str(address))]
    rev6 = filter_matching_subnet(address, rev6)
    if rev6:
        c += [
            cmd(
                rev6_from_network(rev6),
                str(address.reverse_pointer),
                'PTR',
                "%s.%s" % (strip_domain(name, domainname), domainname)
            )
        ]
    return c

def add_mx(name, target, domainname):
    if name[-1] == ".":
        name = name[0:-1]
    preference, target = target.split(" ")
    return [cmd(domainname,
                '@',
                'MX',
                "%s %s" % (expand_name(target, domainname), preference))]

HANDLERS = {
    'A': add_a,
    'AAAA': add_aaaa,
    'CNAME': add_cname,
    'MX': add_mx
}

def handle_record(line, zone, rev4, rev6, records_accepted):
    match = ENTRY_RE.match(line)
    if not match:
        return None
    typ = match.group(2)
    if not typ in records_accepted:
        return None
    if not typ in HANDLERS.keys():
        print("ERROR: Unknown entry type \"%s\", ignoring" % typ,
              file=sys.stderr)
        return None
    fun = HANDLERS[typ]
    sig = signature(fun)
    if 'rev4' in sig.parameters:
        return fun(match.group(1),
                   ip_address(match.group(3).rstrip()),
                   zone,
                   rev4=rev4)
    elif 'rev6' in sig.parameters:
        return fun(match.group(1),
                   ip_address(match.group(3).rstrip()),
                   zone,
                   rev6=rev6)
    else:
        return fun(match.group(1),
                   match.group(3).rstrip(),
                   zone)
    return None

def read_file(in_file, zone, rev4, rev6, records_accepted):
    cmds = []
    for line in in_file:
        line = line.rstrip()
        if zone is None:
            match = SOA_RE.match(line)
            if match:
                zone = match.group(1)
            continue
        cmds += [handle_record(line, zone, rev4, rev6, records_accepted)]
    cmds = [i for i in cmds if i is not None]
    return [i for c in cmds for i in c]

def print_commands(cmds):
    for c in cmds:
        print(*c, sep=" ")

def main():
    args = args_parser().parse_args()
    admin_password = args.password
    records_accepted = args.filter
    rev4 = [IPv4Network(x) for x in args.ipv4_subnet]
    rev6 = [IPv6Network(x) for x in args.ipv6_subnet]
    cmds = read_file(args.zonefile, args.zone, rev4, rev6, records_accepted)
    sys.stdin.close()
    sys.stdin = os.fdopen(1)

    if sys.stdout.isatty() and not args.dry_run:
        print("I would run the following commands:")
    print_commands(cmds)
    if args.dry_run:
        exit(0)
    if sys.stdout.isatty():
        answer = input("Does this look reasonable? [yN] ")
        if not answer or (answer[0] != 'y' and answer[0] != 'Y'):
            exit(1)
        if not admin_password:
            admin_password = getpass("Please enter the password for Administrator:")

    if not admin_password:
        exit(0)

    if sys.stdout.isatty():
        print("Running %d commands: " % len(cmds), end="")
        sys.stdout.flush()
    for i, c in enumerate(cmds, start=1):
        c += ["-U", "Administrator", "--password=%s" % admin_password]
        rc = subprocess.run(c, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if rc.returncode != 0:
            print("\nError: Running command '%s' failed:" % " ".join(c[0:-1]),
                  file=sys.stderr)
            err = rc.stderr.decode("utf-8")
            out = rc.stdout.decode("utf-8")
            print(err, out)
            if "WERR_DNS_ERROR_RECORD_ALREADY_EXISTS" in err:
                print('!', end='')
            elif args.force:
                continue
            else:
                exit(2)
        if sys.stdout.isatty():
            if i % 10 == 0:
                print(i, end='')
            else:
                print('.', end='')
            sys.stdout.flush()
    if sys.stdout.isatty():
        print()

if __name__ == '__main__':
    main()
