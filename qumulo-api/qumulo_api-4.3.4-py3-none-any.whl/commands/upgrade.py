# Copyright (c) 2021 Qumulo, Inc.
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
import contextlib
import time

from typing import Callable, cast, Iterator, Optional

from tqdm import tqdm
from typing_extensions import Protocol

import qumulo.rest.upgrade as unconfigured_upgrade
import qumulo.rest.upgrade_v2 as upgrade_v2
import qumulo.rest.version as version

from qumulo.lib.auth import Credentials
from qumulo.lib.opts import str_decode, Subcommand
from qumulo.lib.request import Connection, RequestError, RestResponse


class UpgradeError(Exception):
    def __init__(self, status: upgrade_v2.ApiV2UpgradeStatus) -> None:
        super().__init__()
        self.status = status


class ProgressDisplay(Protocol):
    """Base class for things that display progress."""

    def start(self) -> None:
        """Shows the progress display."""
        ...

    def update(self, progress: int) -> None:
        """Updates the progress display."""
        ...

    def stop(self) -> None:
        """Terminates the progress display."""
        ...


class TqdmPercentageProgressBar:
    """Creates and updates a tqdm progress bar."""

    def __init__(self) -> None:
        super().__init__()
        self.pbar: Optional[tqdm] = None

    def start(self) -> None:
        self.pbar = tqdm(total=100)

    def update(self, progress: int) -> None:
        assert self.pbar is not None

        assert progress >= 0, 'Must provide positive percentage value'
        assert progress >= self.pbar.n, 'Cannot regress percent complete'

        self.pbar.update(progress - self.pbar.n)

    def stop(self) -> None:
        assert self.pbar is not None
        self.pbar.close()


class DotSpinner:
    """Simply prints a dot on every update()."""

    def start(self) -> None:
        pass  # Nothing to do

    def update(self, _progress: int) -> None:
        print('.', end='', flush=True)

    def stop(self) -> None:
        print()


@contextlib.contextmanager
def progress_context(progress: ProgressDisplay) -> Iterator[ProgressDisplay]:
    progress.start()
    try:
        yield progress
    finally:
        progress.stop()


def fetch_status(conninfo: Connection, credentials: Credentials) -> upgrade_v2.ApiV2UpgradeStatus:
    status: upgrade_v2.ApiV2UpgradeStatus = upgrade_v2.status(conninfo, credentials).data
    if status['error_info'] is not None:
        raise UpgradeError(status)

    return status


def print_upgrade_settings(status: upgrade_v2.ApiV2UpgradeStatus, from_version: str) -> None:
    settings = status['settings']
    assert settings is not None
    to_version = settings['target_version']
    upgrade_type = settings['upgrade_type']

    msg = (
        f'Upgrade from version {from_version} to {to_version} in progress. '
        + f'This will be a {upgrade_type} upgrade.'
    )
    print(msg)


def print_reboot_message(status: upgrade_v2.ApiV2UpgradeStatus) -> None:
    settings = status['settings']
    assert settings is not None

    if settings['upgrade_type'] == 'SOFTWARE_ONLY':
        print('Qumulo containers across the cluster will restart shortly')
    else:
        print('Cluster will reboot shortly')


def monitor_upgrade(
    conninfo: Connection,
    credentials: Credentials,
    prepare_progress: ProgressDisplay,
    commit_progress: ProgressDisplay,
    prepared_cb: Callable[[], bool],
    poll_interval: float = 1.0,
) -> None:
    printed_settings = False
    disconnect_error_allowed = False
    from_version: Optional[str] = None
    try:
        from_version = version.numeric_version(conninfo, credentials).data
        assert from_version is not None  # Satisfy linter
        status = fetch_status(conninfo, credentials)

        if status['state'] == 'UPGRADE_STATE_IDLE':
            print('No upgrade currently in progress')
            return

        print_upgrade_settings(status, from_version)
        printed_settings = True

        # If preparing, wait until not preparing, and report progress.
        if status['state'] == 'UPGRADE_STATE_PREPARING':
            print('Preparing upgrade:')
            with progress_context(prepare_progress):
                while status['state'] == 'UPGRADE_STATE_PREPARING':
                    if status['progress'] is not None:
                        prepare_progress.update(status['progress'])
                    time.sleep(poll_interval)
                    status = fetch_status(conninfo, credentials)
                prepare_progress.update(100)
            disconnect_error_allowed = True

        # Stop monitoring if the provided prepared_cb specifies to stop, otherwise
        # re-fetch status as the callback may have kicked off a commit, and continue
        # monitoring
        if status['state'] == 'UPGRADE_STATE_PREPARED':
            assert status['settings'] is not None
            # NB: can only reach this state if auto_commit is False
            assert status['settings']['auto_commit'] is False

            should_continue = prepared_cb()
            if not should_continue:
                print('Upgrade prepared, commit it to proceed')
                return

            disconnect_error_allowed = True
            status = fetch_status(conninfo, credentials)

            # NB: this assertion provides a contractual obligation to the caller that
            # the provided callback must progress upgrade in some way if it returns True
            # and causes monitoring to continue. This is because it makes no sense to
            # continually poll status and monitor while sitting in state PREPARED
            assert status['state'] != 'UPGRADE_STATE_PREPARED'

        # NB: We have a few situations we might be in here:
        # 1. We've only polled 'status' once and all of the other if statements failed
        #   a. We're COMMITTING in which case we want to say so
        #   b. We're COMMTTED in which case we pretend like we went through COMMITTING
        # 2. We saw at least one status of PREPARING or PREPARED and then triggered a
        #   commit or auto_commit caused us to advance
        #   a. We may see COMMITTING if we polled fast enough after starting commit
        #   b. We may see COMMITTED if we didn't poll fast enough, so pretend like we
        #       saw COMMITTING
        #   c. We didn't see COMMITTING or COMMITTED and are already at IDLE after a
        #       successful commit and reboot/container restart so pretend we saw it
        #       and it finished immediately
        assert status['state'] in [
            'UPGRADE_STATE_IDLE',
            'UPGRADE_STATE_COMMITTING',
            'UPGRADE_STATE_COMMITTED',
        ]
        print('Committing upgrade:', end='', flush=True)
        disconnect_error_allowed = True

        # If committing, wait until not committing, and report progress.
        with progress_context(commit_progress):
            while status['state'] == 'UPGRADE_STATE_COMMITTING':
                commit_progress.update(0)
                time.sleep(poll_interval)
                status = fetch_status(conninfo, credentials)

        print('Upgrade committed')
        print_reboot_message(status)

    except UpgradeError as e:
        if not printed_settings:
            assert from_version is not None
            print_upgrade_settings(e.status, from_version)
        info = e.status['error_info']
        print(f'Upgrade encountered error: {info}')
    except (RequestError, ConnectionError):
        if disconnect_error_allowed:
            print('Upgrade committed')
            print_reboot_message(status)
        else:
            raise


class UpgradeVerifyImageCommand(Subcommand):
    NAME = 'upgrade_verify_image'
    SYNOPSIS = 'Verify an image path for upgrade'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--path', type=str_decode, required=True, help='FS path to upgrade image'
        )

        # NB: This allows an unsafe upgrade, which can result in corruption if
        # used improperly. It should never be used on a production system.
        # It is useful when upgrading from a non-release build.
        parser.add_argument(
            '--override-compatibility-check',
            action='store_true',
            default=False,
            help=argparse.SUPPRESS,
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: argparse.Namespace) -> None:
        print(
            upgrade_v2.verify_image(
                conninfo, credentials, args.path, args.override_compatibility_check
            )
        )


class UpgradeStatusCommand(Subcommand):
    NAME = 'upgrade_status'
    SYNOPSIS = 'Get the status of the upgrade system'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--raw',
            '--json',
            '--no-monitor',
            dest='raw',
            action='store_true',
            help='Skip montoring an in-flight upgrade and just return the raw status',
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: argparse.Namespace) -> None:
        if args.raw:
            print(upgrade_v2.status(conninfo, credentials))
        else:
            prepare_tqdm = TqdmPercentageProgressBar()
            commit_spinner = DotSpinner()

            # For monitoring status only we don't want to continue if we see
            # PREPARED because there's nothing that will advance the upgrade
            # state machine further (i.e. commit)
            def prepared_cb() -> bool:
                return False

            monitor_upgrade(
                conninfo,
                credentials,
                cast(ProgressDisplay, prepare_tqdm),
                cast(ProgressDisplay, commit_spinner),
                prepared_cb=prepared_cb,
            )


# NB mkirby: Because we're really creating a command that wants an optional subcommand,
# we have to do some manual argument validation and normalization because argparse
# doesn't directly support such a feature until python 3.7
def normalize_upgrade_cluster_args(args: argparse.Namespace) -> None:
    # Normalize the path arguments (they could be provided before or after the
    # subcommand)
    if args.no_command_path:
        args.path = args.no_command_path
    if 'prepare_path' in args and args.prepare_path:
        args.path = args.prepare_path

    if args.command != 'commit' and ('path' not in args or not args.path):
        raise SystemExit('Must provide --path')
    if args.command == 'commit' and 'path' in args and args.path:
        raise SystemExit("Unknown argument --path received for 'commit' subcommand")

    # Normalize the override-compatibility-check arguments (they could be provided
    # before or after the subcommand)
    if args.no_command_override_compatibility_check is not None:
        args.override_compatibility_check = args.no_command_override_compatibility_check
    if (
        'prepare_override_compatibility_check' in args
        and args.prepare_override_compatibility_check is not None
    ):
        args.override_compatibility_check = args.prepare_override_compatibility_check

    if args.command == 'commit' and 'override_compatibility_check' in args:
        raise SystemExit(
            "Unknown argument --override-compatibility-check received for 'commit' " + 'subcommand'
        )

    # Real default value for override_compatibility_check
    if 'override_compatibility_check' not in args:
        args.override_compatibility_check = False

    # Normalize the no_monitor arguments (they could be provided before or after the
    # subcommand)
    if args.no_command_no_monitor is not None:
        args.no_monitor = args.no_command_no_monitor
    if 'prepare_no_monitor' in args and args.prepare_no_monitor is not None:
        args.no_monitor = args.prepare_no_monitor
    if 'commit_no_monitor' in args and args.commit_no_monitor is not None:
        args.no_monitor = args.commit_no_monitor

    # Real default value for no_monitor
    if 'no_monitor' not in args:
        args.no_monitor = False


class UpgradeClusterCommand(Subcommand):
    NAME = 'upgrade_cluster'
    SYNOPSIS = 'Run a cluster upgrade to the image specified by the provided path'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--path',
            type=str_decode,
            dest='no_command_path',
            metavar='PATH',
            help='FS path to upgrade image',
        )
        parser.add_argument(
            '--no-monitor',
            action='store_true',
            dest='no_command_no_monitor',
            default=None,
            help='Skip monitoring the upgrade',
        )
        # NB: This allows an unsafe upgrade, which can result in corruption if
        # used improperly. It should never be used on a production system.
        # It is useful when upgrading from a non-release build.
        parser.add_argument(
            '--override-compatibility-check',
            action='store_true',
            default=None,
            dest='no_command_override_compatibility_check',
            help=argparse.SUPPRESS,
        )

        subparser = parser.add_subparsers(dest='command')

        prepare_parser = subparser.add_parser('prepare')
        prepare_parser.add_argument(
            '--auto-commit',
            action='store_true',
            help='Trigger commit phase after the prepare has finished',
        )
        prepare_parser.add_argument(
            '--override-compatibility-check',
            action='store_true',
            default=None,
            dest='prepare_override_compatibility_check',
            help=argparse.SUPPRESS,
        )
        prepare_parser.add_argument(
            '--path',
            type=str_decode,
            dest='prepare_path',
            metavar='PATH',
            help='FS path to upgrade image',
        )
        prepare_parser.add_argument(
            '--no-monitor',
            action='store_true',
            dest='prepare_no_monitor',
            default=None,
            help='Skip monitoring the upgrade',
        )

        commit_parser = subparser.add_parser('commit')
        commit_parser.add_argument(
            '--no-monitor',
            action='store_true',
            dest='commit_no_monitor',
            default=None,
            help='Skip monitoring the upgrade',
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: argparse.Namespace) -> None:
        normalize_upgrade_cluster_args(args)

        res: Optional[RestResponse] = None
        if args.command is None:
            res = upgrade_v2.prepare(
                conninfo,
                credentials,
                args.path,
                auto_commit=args.no_monitor,
                override_compatibility_check=args.override_compatibility_check,
            )
        elif args.command == 'prepare':
            res = upgrade_v2.prepare(
                conninfo,
                credentials,
                args.path,
                auto_commit=args.auto_commit,
                override_compatibility_check=args.override_compatibility_check,
            )
        else:
            assert args.command == 'commit'
            res = upgrade_v2.commit(conninfo, credentials)

        if args.no_monitor:
            print(res)
        else:
            prepare_tqdm = TqdmPercentageProgressBar()
            commit_spinner = DotSpinner()

            def prepared_cb() -> bool:
                if args.command is None:
                    upgrade_v2.commit(conninfo, credentials)
                    return True
                return False

            monitor_upgrade(
                conninfo,
                credentials,
                cast(ProgressDisplay, prepare_tqdm),
                cast(ProgressDisplay, commit_spinner),
                prepared_cb=prepared_cb,
            )


def convert_target(target: str) -> str:
    convert = {
        'idle': 'UPGRADE_TARGET_IDLE',
        'prepare': 'UPGRADE_TARGET_PREPARE',
        'arm': 'UPGRADE_TARGET_ARM',
        'upgrade_target_idle': 'UPGRADE_TARGET_IDLE',
        'upgrade_target_prepare': 'UPGRADE_TARGET_PREPARE',
        'upgrade_target_arm': 'UPGRADE_TARGET_ARM',
    }

    if target.lower() not in convert:
        raise ValueError(f'{target} not one of idle, prepare, or arm')
    return convert[target.lower()]


class UnconfiguredUpgradeConfigCommand(Subcommand):
    NAME = 'unconfigured_upgrade_config'
    SYNOPSIS = 'List current upgrade prepare config for an unconfigured node'

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, _args: argparse.Namespace) -> None:
        print(unconfigured_upgrade.config_get(conninfo, credentials))


class UnconfiguredUpgradeCommand(Subcommand):
    NAME = 'unconfigured_upgrade_config_set'
    SYNOPSIS = 'Upgrade on an unconfigured node with the FS path to an upgrade image'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--path', type=str_decode, default=None, required=True, help='FS path to upgrade image'
        )
        parser.add_argument(
            '--target', type=str_decode, default='idle', help='Target: idle, prepare, arm.'
        )

        # NB: This allows an unsafe upgrade, which can result in corruption if
        # used improperly. It should never be used on a production system.
        # It is useful when upgrading from a non-release build.
        parser.add_argument(
            '--override-compatibility-check',
            action='store_true',
            default=False,
            help=argparse.SUPPRESS,
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: argparse.Namespace) -> None:
        target = convert_target(args.target)

        print(
            unconfigured_upgrade.config_put(
                conninfo, credentials, args.path, target, args.override_compatibility_check
            )
        )


class UnconfiguredUpgradeError(Exception):
    pass


class UnconfiguredUpgradeStatusCommand(Subcommand):
    NAME = 'unconfigured_upgrade_status'
    SYNOPSIS = 'List the current upgrade status for an unconfigured node'

    @staticmethod
    def options(parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            '--wait-until-prepared',
            '--monitor',
            action='store_true',
            help='Monitor the upgrade status until the PREPARING state is complete.',
            dest='monitor',
        )

    @staticmethod
    def main(conninfo: Connection, credentials: Credentials, args: argparse.Namespace) -> None:
        repeat = True
        repeat_count = 0
        while repeat:
            # Timeout while PREPARING.
            if repeat_count > (60 * 60):
                raise UnconfiguredUpgradeError('PREPARING state timed out. Retry the command.')

            repeat = False

            status = unconfigured_upgrade.status_get(conninfo, credentials)
            if args.monitor and status.lookup('state') == 'UPGRADE_PREPARING':
                repeat = True
                repeat_count += 1
                time.sleep(1)

        print(status)

        # Raise an error if monitoring for PREPARED and the final state was
        # different so that callers know we didn't reach PREPARED.
        if args.monitor and status.lookup('state') != 'UPGRADE_PREPARED':
            raise UnconfiguredUpgradeError('Upgrade could not reach PREPARED state.')
