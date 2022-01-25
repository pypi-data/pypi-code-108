# Copyright (c) 2017 Qumulo, Inc.
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

import datetime
import textwrap

from argparse import ArgumentParser, Namespace
from typing import Dict, List

import qumulo.lib.auth
import qumulo.lib.opts
import qumulo.rest.replication as replication

from qumulo.lib.auth import Credentials
from qumulo.lib.opts import str_decode
from qumulo.lib.request import Connection
from qumulo.lib.rfc3339 import parse_rfc3339_time
from qumulo.lib.util import bool_from_string

DELETE_CONFIRMATION = (
    'This will delete the relationship without modifying the contents of '
    'the source or target directories. Note that there might be '
    'inconsistent (i.e. partially-replicated) data in the target directory '
    'if a job is currently running or if the previous job was '
    'incomplete.\n\n'
    'Proceed with deletion?'
)


class ReplicationReplicate(qumulo.lib.opts.Subcommand):
    NAME = 'replication_replicate'
    SYNOPSIS = 'Replicate from the source to the target of the specified relationship.'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the source replication relationship'
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        print(replication.replicate(conninfo, credentials, args.id))


class ReplicationCreateSourceRelationship(qumulo.lib.opts.Subcommand):
    NAME = 'replication_create_source_relationship'
    SYNOPSIS = 'Create a new replication relationship.'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--source-id', type=str_decode, help='File ID of the source directory')
        group.add_argument('--source-path', type=str_decode, help='Path to the source directory')

        parser.add_argument('--target-path', required=True, help='Path to the target directory')
        parser.add_argument('--target-address', required=True, help='The target IP address')
        parser.add_argument(
            '--target-port',
            type=int,
            required=False,
            help='Network port to replicate to on the target (overriding default)',
        )

        parser.add_argument(
            '--enable-replication', type=bool_from_string, metavar='{true,false}', required=False
        )
        parser.add_argument(
            '--set-source-directory-read-only',
            type=bool_from_string,
            metavar='{true,false}',
            required=False,
        )
        parser.add_argument(
            '--map-local-ids-to-nfs-ids',
            type=bool_from_string,
            metavar='{true,false}',
            required=False,
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        optional_args = {}
        if args.target_port is not None:
            optional_args['target_port'] = args.target_port

        if args.enable_replication is not None:
            optional_args['replication_enabled'] = args.enable_replication

        if args.set_source_directory_read_only is not None:
            optional_args['source_root_read_only'] = args.set_source_directory_read_only

        if args.map_local_ids_to_nfs_ids is not None:
            optional_args['map_local_ids_to_nfs_ids'] = args.map_local_ids_to_nfs_ids

        print(
            replication.create_source_relationship(
                conninfo,
                credentials,
                args.target_path,
                args.target_address,
                source_id=args.source_id,
                source_path=args.source_path,
                **optional_args,
            )
        )


class ReplicationListSourceRelationships(qumulo.lib.opts.Subcommand):
    NAME = 'replication_list_source_relationships'
    SYNOPSIS = 'List existing source replication relationships.'

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, _args: Namespace) -> None:
        print(replication.list_source_relationships(conninfo, credentials))


class ReplicationGetSourceRelationship(qumulo.lib.opts.Subcommand):
    NAME = 'replication_get_source_relationship'
    SYNOPSIS = 'Get information about the specified source replication relationship.'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the source replication relationship'
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        print(replication.get_source_relationship(conninfo, credentials, args.id))


class ReplicationDeleteSourceRelationship(qumulo.lib.opts.Subcommand):
    NAME = 'replication_delete_source_relationship'
    SYNOPSIS = 'Delete the specified source replication relationship.'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the source replication relationship'
        )
        parser.add_argument('--force', action='store_true', help='Do not prompt')

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        if args.force or qumulo.lib.opts.ask(
            ReplicationDeleteSourceRelationship.NAME, DELETE_CONFIRMATION
        ):
            replication.delete_source_relationship(conninfo, credentials, args.id)


class ReplicationModifySourceRelationship(qumulo.lib.opts.Subcommand):
    NAME = 'replication_modify_source_relationship'
    SYNOPSIS = 'Modify an existing source replication relationship.'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the source replication relationship'
        )

        parser.add_argument('--new-target-address', required=False, help='The target IP address')
        parser.add_argument(
            '--new-target-port',
            type=int,
            required=False,
            help='Network port to replicate to on the target',
        )
        parser.add_argument(
            '-z',
            '--timezone',
            type=str_decode,
            help=(
                "The timezone for the relationship's blackout windows "
                '(e.g. America/Los_Angeles or UTC). See the '
                'time_list_timezones qq command for a complete list of '
                'supported timezones.'
            ),
        )
        parser.add_argument(
            '--enable-replication', type=bool_from_string, metavar='{true,false}', required=False
        )
        parser.add_argument(
            '--set-source-directory-read-only',
            type=bool_from_string,
            metavar='{true,false}',
            required=False,
        )
        parser.add_argument(
            '--map-local-ids-to-nfs-ids',
            type=bool_from_string,
            metavar='{true,false}',
            required=False,
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        optional_args = {}
        if args.new_target_address is not None:
            optional_args['new_target_address'] = args.new_target_address
        if args.new_target_port is not None:
            optional_args['new_target_port'] = args.new_target_port
        if args.timezone is not None:
            optional_args['blackout_window_timezone'] = args.timezone
        if args.enable_replication is not None:
            optional_args['replication_enabled'] = args.enable_replication
        if args.set_source_directory_read_only is not None:
            optional_args['source_root_read_only'] = args.set_source_directory_read_only
        if args.map_local_ids_to_nfs_ids is not None:
            optional_args['map_local_ids_to_nfs_ids'] = args.map_local_ids_to_nfs_ids

        print(
            replication.modify_source_relationship(conninfo, credentials, args.id, **optional_args)
        )


class ReplicationDeleteTargetRelationship(qumulo.lib.opts.Subcommand):
    NAME = 'replication_delete_target_relationship'
    SYNOPSIS = 'Delete the specified target replication relationship.'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the target replication relationship'
        )
        parser.add_argument('--force', action='store_true', help='Do not prompt')

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        if args.force or qumulo.lib.opts.ask(
            ReplicationDeleteTargetRelationship.NAME, DELETE_CONFIRMATION
        ):
            replication.delete_target_relationship(conninfo, credentials, args.id)


class ReplicationListSourceRelationshipStatuses(qumulo.lib.opts.Subcommand):
    NAME = 'replication_list_source_relationship_statuses'
    SYNOPSIS = 'List statuses for all existing source replication relationships.'

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, _args: Namespace) -> None:
        print(replication.list_source_relationship_statuses(conninfo, credentials))


class ReplicationListTargetRelationshipStatuses(qumulo.lib.opts.Subcommand):
    NAME = 'replication_list_target_relationship_statuses'
    SYNOPSIS = 'List statuses for all existing target replication relationships.'

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, _args: Namespace) -> None:
        print(replication.list_target_relationship_statuses(conninfo, credentials))


class ReplicationGetSourceRelationshipStatus(qumulo.lib.opts.Subcommand):
    NAME = 'replication_get_source_relationship_status'
    SYNOPSIS = 'Get current status of the specified source replication relationship.'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the source replication relationship'
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        print(replication.get_source_relationship_status(conninfo, credentials, args.id))


class ReplicationGetTargetRelationshipStatus(qumulo.lib.opts.Subcommand):
    NAME = 'replication_get_target_relationship_status'
    SYNOPSIS = 'Get current target of the specified source replication relationship.'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the target replication relationship'
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        print(replication.get_target_relationship_status(conninfo, credentials, args.id))


class ReplicationAuthorize(qumulo.lib.opts.Subcommand):
    NAME = 'replication_authorize'
    SYNOPSIS = (
        'Authorize the specified replication relationship, '
        + 'establishing this cluster as the target of replication.'
    )

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the target replication relationship'
        )
        parser.add_argument(
            '--allow-non-empty-directory',
            action='store_true',
            help=(
                'Allow the replication relationship to be authorized on a '
                'target directory containing existing data. Existing data in '
                'the target directory may be deleted or overwritten. If you '
                'wish to preserve this data, consider taking a snapshot'
                ' before authorizing.'
            ),
        )
        parser.add_argument(
            '--allow-fs-path-create',
            action='store_true',
            help=(
                'Allow the target directory to be created with '
                'inherited permissions if it does not already exist'
            ),
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        print(
            replication.authorize(
                conninfo,
                credentials,
                args.id,
                allow_non_empty_directory=args.allow_non_empty_directory,
                allow_fs_path_create=args.allow_fs_path_create,
            )
        )


class ReplicationReconnectTargetRelationship(qumulo.lib.opts.Subcommand):
    NAME = 'replication_reconnect_target_relationship'
    SYNOPSIS = (
        'Make the target directory read-only and revert any '
        'changes made to the target directory since the latest recovery '
        'point. Then reconnect the specified target replication '
        'relationship with its source directory. The revert action may '
        'take some time to complete before replication is resumed.'
    )
    CONFIRMATION = (
        SYNOPSIS + '\n\nData not present on the source will be deleted. Do you want to proceed?'
    )

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the target replication relationship'
        )
        parser.add_argument('--force', action='store_true', help='Do not prompt')

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        if args.force or qumulo.lib.opts.ask(
            ReplicationReconnectTargetRelationship.NAME,
            ReplicationReconnectTargetRelationship.CONFIRMATION,
        ):
            print(replication.reconnect_target_relationship(conninfo, credentials, args.id))


class ReplicationAbortReplication(qumulo.lib.opts.Subcommand):
    NAME = 'replication_abort_replication'
    SYNOPSIS = 'Abort ongoing replication work for the specified source replication relationship.'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the source replication relationship'
        )
        parser.add_argument(
            '--skip-active-policy-snapshot',
            type=bool_from_string,
            metavar='{true,false}',
            help=(
                'If set to true and the currently replicating snapshot was '
                'created by a policy, the next replication job will use the '
                'next queued snapshot instead of retrying the current one '
                '(default: false).'
            ),
            default=None,
            required=False,
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        replication.abort_replication(
            conninfo, credentials, args.id, args.skip_active_policy_snapshot
        )


ALLOWED_DAYS = ['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'ALL']


def get_on_days(days_of_week: str) -> List[str]:
    days = [day.strip().upper() for day in days_of_week.split(',')]

    if 'ALL' in days:
        if len(days) > 1:
            raise ValueError('ALL cannot be used in conjunction with other days')

        # API parlance for "ALL"
        return ['EVERY_DAY']

    if not set(days).issubset(set(ALLOWED_DAYS)):
        raise ValueError(f'Invalid days: {days}; allowed days are: {ALLOWED_DAYS}')

    return days


def get_blackout_window(args: Namespace) -> Dict[str, object]:
    try:
        start_time = datetime.datetime.strptime(args.start_time, '%H:%M')
        end_time = datetime.datetime.strptime(args.end_time, '%H:%M')
    except ValueError:
        raise ValueError('Bad format for start/end time')

    return {
        'start_hour': start_time.hour,
        'start_minute': start_time.minute,
        'end_hour': end_time.hour,
        'end_minute': end_time.minute,
        'on_days': get_on_days(args.days_of_week),
    }


class ReplicationAddBlackoutWindow(qumulo.lib.opts.Subcommand):
    NAME = 'replication_add_blackout_window'
    SYNOPSIS = 'Add a blackout window to the specified source replication relationship.'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the source replication relationship.'
        )

        parser.add_argument(
            '--start-time',
            required=True,
            type=str_decode,
            help=(
                'The 24 hour time of day start time for the blackout '
                'window (e.g. 15:30). Time is always in the timezone configured on the '
                'specified source replication relationship.'
            ),
        )

        parser.add_argument(
            '--end-time',
            required=True,
            type=str_decode,
            help=(
                'The 24 hour time of day end time for the blackout '
                'window (e.g. 18:30) -- on the following day if earlier than '
                'the --start-time parameter.'
            ),
        )

        parser.add_argument(
            '--days-of-week',
            required=True,
            type=str_decode,
            help=(
                'Days of the week the window applies to. Comma separated '
                'list (e.g. MON,TUE,WED,THU,FRI,SAT,SUN) or ALL.'
            ),
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        window_to_add = get_blackout_window(args)

        relationship, etag = replication.get_source_relationship(conninfo, credentials, args.id)

        blackout_windows = relationship['blackout_windows']
        blackout_windows.append(window_to_add)

        print(
            replication.modify_source_relationship(
                conninfo, credentials, args.id, blackout_windows=blackout_windows, if_match=etag
            )
        )


class ReplicationDeleteBlackoutWindows(qumulo.lib.opts.Subcommand):
    NAME = 'replication_delete_blackout_windows'
    SYNOPSIS = 'Delete blackout windows of the specified source replication relationship.'

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the source replication relationship'
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        _, etag = replication.get_source_relationship(conninfo, credentials, args.id)

        print(
            replication.modify_source_relationship(
                conninfo, credentials, args.id, blackout_windows=[], if_match=etag
            )
        )


class ReplicationMakeTargetWritable(qumulo.lib.opts.Subcommand):
    NAME = 'replication_make_target_writable'
    SYNOPSIS = 'Revert target directory to the latest recovery point.'
    DESCRIPTION = textwrap.dedent(
        """\
        Revert target directory to the latest recovery point to ensure that
        it is in a point-in-time consistent state. Then disconnect the
        specified target replication relationship, breaking the relationship
        with the source and making the target directory writable. The revert
        action may take some time to complete. If the relationship is later
        reconnected, any changes made to the target directory since the
        relationship was disconnected will be reverted upon reconnecting.
    """
    )

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the target replication relationship'
        )
        parser.add_argument('--force', action='store_true', help='Do not prompt')

    CONFIRMATION_TEMPLATE = (
        'This action will revert the target directory to the latest recovery '
        'point to ensure that it is in a point-in-time consistent state. '
        'Then, it will disconnect the replication relationship, making the '
        'target directory writable. The revert action may take some time to '
        'complete.\n\n'
        'This action will revert the target directory of {root} to the '
        'recovery point from {timestamp} UTC. Do you want to proceed?'
    )

    NO_RECOVERY_POINT_TEMPLATE = (
        'Target directory {root} cannot be made writable because initial '
        'replication has not completed. If you would like to make the target '
        'directory writable, you will need to delete the replication '
        'relationship. Deleting the replication relationship can leave '
        'partially-replicated data in an inconsistent state.'
    )

    @staticmethod
    def _ask_confirmation(
        conninfo: Connection, credentials: Credentials, relationship_id: str
    ) -> bool:
        cls = ReplicationMakeTargetWritable
        status = replication.get_target_relationship_status(
            conninfo, credentials, relationship_id
        ).data
        root = status['target_root_path']
        timestamp = status['recovery_point']
        if not timestamp:
            print(
                '\n'.join(
                    textwrap.fill(line)
                    for line in cls.NO_RECOVERY_POINT_TEMPLATE.format(root=root).splitlines()
                )
            )
            return False
        else:
            confirmation = cls.CONFIRMATION_TEMPLATE.format(
                root=root, timestamp=parse_rfc3339_time(timestamp).strftime('%b %d %Y, %I:%M %p')
            )
        return qumulo.lib.opts.ask(cls.NAME, confirmation)

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        if args.force or ReplicationMakeTargetWritable._ask_confirmation(
            conninfo, credentials, args.id
        ):
            print(replication.make_target_writable(conninfo, credentials, args.id))


class ReplicationReverseTargetRelationship(qumulo.lib.opts.Subcommand):
    NAME = 'replication_reverse_target_relationship'
    SYNOPSIS = 'Reverse source and target for a replication relationship.'
    DESCRIPTION = textwrap.dedent(
        """\
        Reverse source and target for the specified replication relationship.
        This operation is initiated on the target cluster. The previous
        target directory will be made the new source, and the previous source
        directory will be made the new target. Any relationship
        configurations on the source will be retained, and any configurations
        on the target that have been retained from a previous reversal will
        be reapplied. To resume replication after reversal, edit any
        relationship configurations if desired and reconnect the relationship
        from the new target cluster.
    """
    )

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the target replication relationship'
        )
        parser.add_argument(
            '--source-address', required=True, help='The IP address of the current source cluster'
        )
        parser.add_argument(
            '--source-port',
            type=int,
            required=False,
            help='Network port of the current source cluster (defaults to 3712)',
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        optional_args = {}
        if args.source_port:
            optional_args['source_port'] = args.source_port
        print(
            replication.reverse_target_relationship(
                conninfo, credentials, args.id, args.source_address, **optional_args
            )
        )


class ReplicationLinkSnapshotPolicy(qumulo.lib.opts.Subcommand):
    NAME = 'replication_link_snapshot_policy'
    SYNOPSIS = 'Link a snapshot policy to a source replication relationship.'
    DESCRIPTION = textwrap.dedent(
        """\
        Link a snapshot policy to the specified source replication
        relationship to replicate snapshots taken by the policy. The
        replication mode will be set to
        REPLICATION_SNAPSHOT_POLICY_WITH_CONTINUOUS when linking the first
        policy, otherwise the existing mode will be preserved. The mode can
        be modified with the replication_set_snapshot_policy_replication_mode
        command or by removing all linked snapshot policies.
    """
    )

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--relationship-id',
            required=True,
            help='Unique identifier of the source replication relationship.',
        )
        parser.add_argument(
            '--snapshot-policy-id', required=True, help='Identifier of the snapshot policy to link.'
        )
        parser.add_argument(
            '-t',
            '--target-expiration',
            type=str_decode,
            default=None,
            help=(
                'Duration after which to expire snapshots on the target '
                'cluster that were replicated from this snapshot '
                'policy, in format <quantity><units>, where <quantity> '
                'is a positive integer less than 100 and <units> is one '
                'of [months, weeks, days, hours, minutes], e.g. 5days '
                "or 1hours. 'never' indicates snapshots should never expire "
                "and 'same_as_policy' indicates snapshots should expire at the "
                'same time as the snapshot policy specifies. '
                '(default: same_as_policy)'
            ),
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        relationship, etag = replication.get_source_relationship(
            conninfo, credentials, args.relationship_id
        )

        snapshot_policies = relationship['snapshot_policies']

        replication_mode = None
        if len(snapshot_policies) == 0:
            replication_mode = 'REPLICATION_SNAPSHOT_POLICY_WITH_CONTINUOUS'

        target_ttl = args.target_expiration
        if target_ttl is None:
            target_ttl = 'same_as_policy'
        snapshot_policies.append(
            {'id': int(args.snapshot_policy_id), 'target_expiration': target_ttl}
        )

        print(
            replication.modify_source_relationship(
                conninfo,
                credentials,
                args.relationship_id,
                replication_mode=replication_mode,
                snapshot_policies=snapshot_policies,
                if_match=etag,
            )
        )


class ReplicationUnlinkSnapshotPolicy(qumulo.lib.opts.Subcommand):
    NAME = 'replication_unlink_snapshot_policy'
    SYNOPSIS = 'Unlink a snapshot policy from a source replication relationship.'
    DESCRIPTION = textwrap.dedent(
        """\
        Unlink a linked snapshot policy from the specified source replication
        relationship. The replication mode will be set to
        REPLICATION_CONTINUOUS when unlinking the last policy, otherwise the
        existing mode will be preserved.
    """
    )

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--relationship-id',
            required=True,
            help='Unique identifier of the source replication relationship.',
        )
        parser.add_argument(
            '--snapshot-policy-id',
            required=True,
            help='Identifier of the snapshot policy to unlink.',
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        relationship, etag = replication.get_source_relationship(
            conninfo, credentials, args.relationship_id
        )

        old_policies = relationship['snapshot_policies']
        new_policies = [
            policy for policy in old_policies if policy['id'] != int(args.snapshot_policy_id)
        ]

        replication_mode = None
        if len(new_policies) == 0:
            replication_mode = 'REPLICATION_CONTINUOUS'

        print(
            replication.modify_source_relationship(
                conninfo,
                credentials,
                args.relationship_id,
                replication_mode=replication_mode,
                snapshot_policies=new_policies,
                if_match=etag,
            )
        )


class ReplicationSetSnapshotPolicyReplicationMode(qumulo.lib.opts.Subcommand):
    NAME = 'replication_set_snapshot_policy_replication_mode'
    SYNOPSIS = (
        'Set the replication mode of the specified source replication '
        'relationship. This command is only for a relationship that has linked '
        'snapshot policies.'
    )

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the source replication relationship.'
        )
        parser.add_argument(
            '--mode',
            required=True,
            choices=('REPLICATION_SNAPSHOT_POLICY', 'REPLICATION_SNAPSHOT_POLICY_WITH_CONTINUOUS'),
            help='Replication mode to set.',
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        print(
            replication.modify_source_relationship(
                conninfo, credentials, args.id, replication_mode=args.mode
            )
        )


class ReplicationListQueuedSnapshots(qumulo.lib.opts.Subcommand):
    NAME = 'replication_list_queued_snapshots'
    SYNOPSIS = (
        'List information for all snapshots awaiting replication '
        'by the specified source replication relationship.'
    )

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--id', required=True, help='Unique identifier of the source replication relationship.'
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        print(replication.list_queued_snapshots(conninfo, credentials, args.id))


class ReplicationReleaseQueuedSnapshot(qumulo.lib.opts.Subcommand):
    NAME = 'replication_release_queued_snapshot'
    SYNOPSIS = (
        'Release a snapshot queued for replication from the queue '
        'of the specified source replication relationship.'
    )

    @staticmethod
    def options(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--relationship-id',
            required=True,
            help='Unique identifier of the source replication relationship.',
        )
        parser.add_argument(
            '--snapshot-id', required=True, help='Unique identifier of the snapshot to release.'
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: Namespace) -> None:
        replication.release_queued_snapshot(
            conninfo, credentials, args.relationship_id, args.snapshot_id
        )
