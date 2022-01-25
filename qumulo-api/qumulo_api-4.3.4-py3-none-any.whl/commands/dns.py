# Copyright (c) 2015 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

# XXX: Please add types to the functions in this file. Static type checking in
# Python prevents bugs!
# mypy: ignore-errors

import json
import sys
import textwrap

from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter

import qumulo.lib.opts
import qumulo.lib.util
import qumulo.rest.dns as dns

from qumulo.lib.auth import Credentials
from qumulo.lib.opts import str_decode
from qumulo.lib.request import Connection


class ResolveIpAddresses(qumulo.lib.opts.Subcommand):
    NAME = 'dns_resolve_ips'
    SYNOPSIS = 'Resolve IP addresses to hostnames'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument('--ips', required=True, nargs='+', help='IP addresses to resolve')

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        print(dns.resolve_ips_to_names(conninfo, credentials, args.ips))


class ResolveHostnames(qumulo.lib.opts.Subcommand):
    NAME = 'dns_resolve_hostnames'
    SYNOPSIS = 'Resolve hostnames to IP addresses'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument('--hosts', required=True, nargs='+', help='Hostnames to resolve')

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        print(dns.resolve_names_to_ips(conninfo, credentials, args.hosts))


#  _             _
# | | ___   ___ | | ___   _ _ __
# | |/ _ \ / _ \| |/ / | | | '_ \
# | | (_) | (_) |   <| |_| | |_) |
# |_|\___/ \___/|_|\_\\__,_| .__/____
#                          |_| |_____|
#                           _     _
#   _____   _____ _ __ _ __(_) __| | ___  ___
#  / _ \ \ / / _ \ '__| '__| |/ _` |/ _ \/ __|
# | (_) \ V /  __/ |  | |  | | (_| |  __/\__ \
#  \___/ \_/ \___|_|  |_|  |_|\__,_|\___||___/
#  FIGLET: lookup_overrides
#


class DNSLookupOverridesGetCommand(qumulo.lib.opts.Subcommand):
    NAME = 'dns_get_lookup_overrides'
    SYNOPSIS = 'List the configured set of DNS lookup overrides.'
    DESCRIPTION = textwrap.dedent(
        """\
        List the configured set of DNS lookup overrides.

        These rules override any lookup results from the configured DNS servers
        and serve as static mappings between IP address and hostname."""
    )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, _args: Namespace) -> None:
        print(dns.lookup_overrides_get(conninfo, credentials))


class DNSLookupOverridesSetCommand(qumulo.lib.opts.Subcommand):
    NAME = 'dns_set_lookup_overrides'
    SYNOPSIS = 'Replace the configured set of DNS lookup overrides.'
    DESCRIPTION = textwrap.dedent(
        """\
        Replace the configured set of DNS lookup overrides.

        These rules override any lookup results from the configured DNS
        servers and serve as static mappings between IP address and hostname.
        The provided overrides document should have the following structure:

        {
          "lookup_overrides": [
              {"ip_address": "1.2.3.4", "aliases": ["foo.com", "www.foo.com"]},
              {"ip_address": "2.3.4.5", "aliases": ["bar.com", "www.bar.com"]}
          ]
        }

        The first hostname in the "aliases" list is what will be resolved
        when doing reverse lookups from IP address to hostname."""
    )

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.formatter_class = RawDescriptionHelpFormatter
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '--file', help='JSON-encoded file containing overrides.', type=str_decode
        )
        group.add_argument(
            '--stdin', action='store_true', help='Read JSON-encoded overrides from stdin'
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        infile = open(args.file, 'rb') if args.file else sys.stdin
        overrides = json.load(infile)
        dns.lookup_overrides_set(conninfo, credentials, overrides)
