# Copyright (c) 2013 Qumulo, Inc.
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

import argparse
import time

from typing import List, Optional, Tuple

import qumulo.lib.opts
import qumulo.lib.util
import qumulo.rest.cluster as cluster
import qumulo.rest.node_state as node_state
import qumulo.rest.unconfigured_node_operations as unconfigured_node_operations

from qumulo.lib.auth import Credentials
from qumulo.lib.opts import str_decode
from qumulo.lib.request import Connection


class PasswordMismatchError(ValueError):
    pass


def get_admin_password(args: argparse.Namespace) -> str:
    """
    Get the effective admin_password to use for cluster creation

    If @a args.admin_password is None then we will prompt the user for a
    password and confirmation for the admin account (note that the entries
    will be hidden text)

    @param args.admin_password This is the passed in password from the CLI

    @return Effective admin_password to be used for cluster creation
    """
    password = args.admin_password

    if not password:
        password = qumulo.lib.opts.read_password(prompt='Enter password for Admin: ')
        confirm_password = qumulo.lib.opts.read_password(prompt='Confirm password for Admin: ')
        if password != confirm_password:
            raise PasswordMismatchError('The passwords do not match.')
        print('\n', end=' ')

    return password


def get_node_uuids_and_ips(
    args: argparse.Namespace, conninfo: Connection, credentials: Optional[Credentials]
) -> Tuple[List[str], List[str]]:
    """
    Get the actual set of node_uuids and node_ips to send to the rest call

    If the passed in args indicate that nodes should be auto-selected via the
    @a args.all_unconfigured then we perform an unconfigured nodes lookup
    and return all found nodes in the set of node_uuids.

    @param args.all_unconfigured Flag indicating whether or not we should
        utilize auto-node discovery
    @param args.node_uuids Set of manually specified node_uuids to use
    @param args.node_ips Set of manually specified node_ips to use
    @param conninfo Connection to use for the list_unconfigured_nodes rest call
    @param credentials These are the credentials to use for rest requests

    @return Returns tuple (node_uuids, node_ips) where these are the effective
        node_uuids and node_ips to use for the cluster_create rest call
    """
    node_uuids = []
    node_ips = []

    if args.all_unconfigured:
        res = unconfigured_node_operations.list_unconfigured_nodes(conninfo, credentials)

        nodes = res.data['nodes']
        node_uuids = [n['uuid'] for n in nodes]

        print(unconfigured_node_operations.fmt_unconfigured_nodes(res))
        if not qumulo.lib.opts.ask(
            'cluster create', f'\nUse above {len(nodes)} nodes to create cluster?'
        ):
            raise ValueError('No nodes selected')

    else:
        # For backward compatibility, we support multiple instances of
        # --node-uuids to append but we also would like to allow multiple
        # node uuids give to each instance.  Flatten resulting list of
        # lists.
        node_uuids = [x for sublist in args.node_uuids for x in sublist]
        node_ips = [x for sublist in args.node_ips for x in sublist]

    return node_uuids, node_ips


class ListNodesCommand(qumulo.lib.opts.Subcommand):
    NAME = 'nodes_list'
    SYNOPSIS = 'List nodes'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--node', help='Node ID')

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        if args.node is not None:
            print(cluster.list_node(conninfo, credentials, args.node))
        else:
            print(cluster.list_nodes(conninfo, credentials))


class GetClusterConfCommand(qumulo.lib.opts.Subcommand):
    NAME = 'cluster_conf'
    SYNOPSIS = 'Get the cluster config'

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], _args: argparse.Namespace
    ) -> None:
        print(cluster.get_cluster_conf(conninfo, credentials))


class SetClusterConfCommand(qumulo.lib.opts.Subcommand):
    NAME = 'set_cluster_conf'
    SYNOPSIS = 'Set the cluster config'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--cluster-name', help='Cluster Name', required=True)

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        print(cluster.put_cluster_conf(conninfo, credentials, args.cluster_name))


class SetSSLCertificateCommand(qumulo.lib.opts.Subcommand):
    NAME = 'ssl_modify_certificate'
    SYNOPSIS = 'Set the SSL certificate chain and private key for the web UI and REST servers'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '-c',
            '--certificate',
            type=str_decode,
            required=True,
            help=(
                'SSL certificate chain in PEM format. Must contain '
                'entire certificate chain up to the root CA'
            ),
        )
        parser.add_argument(
            '-k',
            '--private-key',
            type=str_decode,
            required=True,
            help='RSA private key file in PEM format',
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        cert, key = None, None

        with open(args.certificate) as cert_f, open(args.private_key) as key_f:
            cert, key = cert_f.read(), key_f.read()

        print(cluster.set_ssl_certificate(conninfo, credentials, cert, key))


class SetSSLCACertificateCommand(qumulo.lib.opts.Subcommand):
    NAME = 'ssl_modify_ca_certificate'
    SYNOPSIS = (
        'Set SSL CA certificate. This certificate is used to '
        'authenticate connections to external LDAP servers.'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '-c',
            '--certificate',
            type=str_decode,
            required=True,
            help='SSL CA certificate file in PEM format',
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        with open(args.certificate) as f:
            cert = f.read()
        print(cluster.set_ssl_ca_certificate(conninfo, credentials, cert))


class GetSSLCACertificateCommand(qumulo.lib.opts.Subcommand):
    NAME = 'ssl_get_ca_certificate'
    SYNOPSIS = (
        'Get SSL CA certificate. This certificate is used to '
        'authenticate connections to external LDAP servers.'
    )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], _args: argparse.Namespace
    ) -> None:
        print(cluster.get_ssl_ca_certificate(conninfo, credentials))


class DeleteSSLCACertificateCommand(qumulo.lib.opts.Subcommand):
    NAME = 'ssl_delete_ca_certificate'
    SYNOPSIS = (
        'Delete SSL CA certificate. This certificate is used to '
        'authenticate connections to external LDAP servers.'
    )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], _args: argparse.Namespace
    ) -> None:
        print(cluster.delete_ssl_ca_certificate(conninfo, credentials))


class GetClusterSlotStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = 'cluster_slots'
    SYNOPSIS = 'Get the cluster disk slots status'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--slot', help='Slot ID')

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        if args.slot is not None:
            print(cluster.get_cluster_slot_status(conninfo, credentials, args.slot))
        else:
            print(cluster.get_cluster_slots_status(conninfo, credentials))


class SetClusterSlotConfigCommand(qumulo.lib.opts.Subcommand):
    NAME = 'cluster_slot_set_config'
    SYNOPSIS = (
        'Set the attributes for the given cluster slot. Currently only led_pattern may be set.'
    )

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--slot', required=True, help='Slot ID')
        led_group = parser.add_mutually_exclusive_group()
        led_group.add_argument(
            '--locate',
            help="Turn on the slot's locate LED.",
            dest='locate',
            action='store_const',
            const='LED_PATTERN_LOCATE',
        )
        led_group.add_argument(
            '--no-locate',
            help="Turn off the slot's locate LED.",
            dest='locate',
            action='store_const',
            const='LED_PATTERN_NORMAL',
        )

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        print(cluster.set_cluster_slot_config(conninfo, credentials, args.slot, args.locate))


class GetRestriperStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = 'restriper_status'
    SYNOPSIS = 'Get restriper status'

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], _args: argparse.Namespace
    ) -> None:
        print(cluster.get_restriper_status(conninfo, credentials))


class GetProtectionStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = 'protection_status_get'
    SYNOPSIS = 'Get cluster protection status'

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], _args: argparse.Namespace
    ) -> None:
        print(cluster.get_protection_status(conninfo, credentials))


class SetNodeUidLight(qumulo.lib.opts.Subcommand):
    NAME = 'set_node_identify_light'
    SYNOPSIS = 'Turn node identification light on or off'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--node', help='Node ID', required=True)
        parser.add_argument('light_state', choices=['on', 'off'], help='Should light be visible')

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        light_visible = args.light_state == 'on'
        print(cluster.set_node_identify_light(conninfo, credentials, args.node, light_visible))


class GetNodeChassisStatus(qumulo.lib.opts.Subcommand):
    NAME = 'node_chassis_status_get'
    SYNOPSIS = 'Get the status of node chassis'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--node', help='Node ID')

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        print(cluster.get_node_chassis_status(conninfo, credentials, args.node))


def wait_for_first_quorum_following_cluster_create(
    conninfo: Connection, credentials: Optional[Credentials]
) -> None:
    """
    It's generally a good idea to wait for the first full quorum before doing anything with the
    cluster. If you don't, you may get disconnects and errors as the API switches from unconfigured
    to configured mode. You can also cause problems if you do things like `create && reboot` without
    waiting. This may cause filesystem creation to fail because the admin credentials were lost
    before ever being persisted to disk.

    Note that this method waits for a full quorum (not a degraded quorum) because the initial quorum
    for the cluster requires all nodes be present for filesystem creation, and it won't proceed
    until this is the case.
    """
    print('Cluster create command issued, waiting for initial quorum to form...')

    while True:
        try:
            state = node_state.get_node_state(conninfo, credentials).lookup('state')
            print(f'Initiator node quorum state: {state}')
            if state == 'ACTIVE':
                break
        except Exception as e:
            print(f'Transient error waiting for quorum: {e}')
        time.sleep(1)

    print('Success!')


class CreateCluster(qumulo.lib.opts.Subcommand):
    NAME = 'cluster_create'
    SYNOPSIS = 'Creates a Qumulo Cluster'

    @classmethod
    def options(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--cluster-name', '-n', help='Cluster Name', required=True)
        parser.add_argument('--admin-password', '-p', help='Administrator Password')
        parser.add_argument(
            '--blocks-per-stripe', help='Erasure coding stripe width', required=False, type=int
        )
        parser.add_argument(
            '--max-drive-failures',
            help='Maximum allowable drive failures',
            required=False,
            type=int,
        )
        parser.add_argument(
            '--max-node-failures', help='Maximum allowable node failures', required=False, type=int
        )
        parser.add_argument(
            '--accept-eula', help='Accept the EULA', dest='accept_eula', action='store_true'
        )
        parser.add_argument(
            '--reject-eula', help='Reject the EULA', dest='accept_eula', action='store_false'
        )
        parser.add_argument(
            '--host-instance-id',
            help='EC2 Instance ID of node receiving this request. AWS only.',
            default='',
        )

        node_group = parser.add_mutually_exclusive_group(required=True)
        node_group.add_argument(
            '--node-uuids', '-U', help='Cluster node UUIDs', action='append', default=[], nargs='+'
        )
        node_group.add_argument(
            '--node-ips',
            '-I',
            help='Cluster node IPv4 addresses',
            action='append',
            default=[],
            nargs='+',
        )
        node_group.add_argument(
            '--all-unconfigured',
            '-A',
            help='Use all discoverable unconfigured nodes to make cluster',
            action='store_true',
            default=False,
        )

    @classmethod
    def main(
        cls, conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        admin_password = get_admin_password(args)
        node_uuids, node_ips = get_node_uuids_and_ips(args, conninfo, credentials)

        cluster.create_cluster(
            conninfo,
            credentials,
            cluster_name=args.cluster_name,
            admin_password=admin_password,
            host_instance_id=args.host_instance_id,
            node_uuids=node_uuids,
            node_ips=node_ips,
            blocks_per_stripe=args.blocks_per_stripe,
            max_drive_failures=args.max_drive_failures,
            max_node_failures=args.max_node_failures,
            eula_accepted=args.accept_eula,
        )

        wait_for_first_quorum_following_cluster_create(conninfo, credentials)


class AddNode(qumulo.lib.opts.Subcommand):
    NAME = 'add_nodes'
    SYNOPSIS = 'Add unconfigured nodes to a Qumulo Cluster'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        nodes_group = parser.add_mutually_exclusive_group(required=True)
        nodes_group.add_argument(
            '--node-uuids',
            help='Unconfigured node uuids to add',
            action='append',
            nargs='+',
            default=[],
        )
        nodes_group.add_argument(
            '--node-ips',
            help='Unconfigured node ips to add',
            action='append',
            nargs='+',
            default=[],
        )

        # Calculate and return changes to cluster usable capacity only
        parser.add_argument('--dry-run', action='store_true')

    @staticmethod
    def main(
        conninfo: Connection, credentials: Optional[Credentials], args: argparse.Namespace
    ) -> None:
        # For backward compatibility, we support multiple instances of
        # --node-uuids to append but we also would like to allow multiple node
        # uuids give to each instance.  Flatten resulting list of lists.
        args.node_uuids = [x for sublist in args.node_uuids for x in sublist]
        args.node_ips = [x for sublist in args.node_ips for x in sublist]

        if args.dry_run:
            print(
                cluster.calculate_node_add_capacity(
                    conninfo, credentials, node_uuids=args.node_uuids, node_ips=args.node_ips
                )
            )
        else:
            print(
                cluster.add_node(
                    conninfo, credentials, node_uuids=args.node_uuids, node_ips=args.node_ips
                )
            )
