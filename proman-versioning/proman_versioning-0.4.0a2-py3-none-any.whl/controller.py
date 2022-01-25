# copyright: (c) 2021 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Coordinate actions from commit messages."""

import logging
import os
import re
import sys
from copy import deepcopy
from string import Template
from typing import TYPE_CHECKING, Any, Dict

from versioning.exception import PromanVersioningException
from versioning.grammars.conventional_commits import CommitMessageParser
from versioning.version import Version

if TYPE_CHECKING:
    from versioning.config import Config
    from versioning.vcs import Git

# from transitions import Machine

# TODO: version comparison against previous version
# has API spec been modified?
# has Python version changed?
# has requirements versions changed?

# TODO: build numbers
# git revision
# GNU build ID
# timestamp
# external (ex: CI/CD build number)

log = logging.getLogger(__name__)
# TODO: need to integrate into CLI
# log.setLevel(logging.DEBUG)


# TODO determine relation with state and git hooks
class IntegrationController(CommitMessageParser):
    """Control version releases."""

    # workflow_types = ['rolling', 'sustainment']
    # Trunk Based Development (TBD) - GitHub flow
    # Stage Based Development (SBD) - DTAP
    # Release Branching Strategy (RBS) - PEP440
    # Feature Branching Strategy (FBS) - Agile

    def __init__(
        self,
        config: 'Config',
        repo: 'Git',
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize commit message action object."""
        self.config = config
        # parse_current_branch = kwargs.pop('parse_current_branch', True)
        message = kwargs.pop('message', None)
        super().__init__(*args, **kwargs)

        self.vcs = repo
        if message is None:
            head = self.vcs.repo.head
            target = self.vcs.repo[head.target]
            self.parse(target.message)
            log.debug(f"provided commit message: '{message}'")
        else:
            self.parse(message)
            log.debug(f"found commit message: '{message}'")

    @property
    def release(self) -> str:
        """Get the current version release state."""
        return self.config.version.state  # type: ignore

    def __update_config(
        self,
        config: Dict[str, Any],
        new_version: Version,
        dry_run: bool = False,
    ) -> None:
        """Update target file with new version."""
        if 'release_only' in config and config['release_only']:
            current_release = '.'.join(
                str(x) for x in self.config.version.release
            )
            version = Version(current_release)

            release = '.'.join(
                str(x) for x in new_version.release
            )
            new_version = Version(release)
        else:
            version = deepcopy(self.config.version)

        if 'compat' in config:
            version.compat = config['compat']
            new_version.compat = config['compat']

        pattern = config['pattern']
        filepath = os.path.join(
            self.vcs.working_dir, config['filepath']
        )

        # TODO: handle when file does not exist
        with open(filepath, 'r+') as f:
            file_contents = f.read()

            # prepare source expression match pattern
            template = Template(pattern).substitute(version=version.query)
            match = re.compile(
                # XXX: escape not compiling correctly
                template,  # re.escape(template),
                flags=0,
            )
            log.debug(f"using pattern for source version {match}")

            # substitute the expression in file
            file_contents = match.sub(
                Template(pattern).substitute(version=str(new_version)),
                file_contents,
            )

            if not dry_run:
                # save the file
                try:
                    f.seek(0)
                    f.truncate()
                    f.write(file_contents)
                    log.info(f"writting file at: '{filepath}'")
                except Exception as err:
                    print(err, file=sys.stderr)
            else:
                # print the file changes
                print(file_contents, file=sys.stdout)
                log.info(
                    f"dry-run skipping file write at: '{filepath}'"
                )

    def update_configs(self, new_version: Version, **kwargs: Any) -> None:
        """Update version within config files."""
        dry_run = kwargs.pop('dry_run', False)
        stats = self.vcs.repo.diff('HEAD').stats
        if stats.files_changed == 0 or dry_run:
            if self.config.version != new_version:
                for config in self.config.templates:
                    self.__update_config(
                        config=config,
                        new_version=new_version,
                        dry_run=dry_run,
                    )

                self.config.version = new_version
                make_commit = kwargs.pop('commit', True)
                make_tag = kwargs.pop('tag', False)
                if make_commit or make_tag:
                    # TODO: tie scope to configs, releases or version ranges
                    scope = 'version'
                    self.vcs.commit(
                        filepaths=[
                            f['filepath']
                            for f in self.config.templates
                        ],
                        message=(
                            f"ci({scope}): apply {str(new_version)} updates"
                        ),
                        dry_run=dry_run,
                    )
                    log.info(f"commiting version changes: {str(new_version)}")

                    if make_tag:
                        self.vcs.tag(
                            name=str(new_version),
                            ref='HEAD',
                            message=None,
                            dry_run=dry_run,
                        )
                        log.info(f"applying tag: {str(new_version)}")

                    if kwargs.get('push', False):
                        # TODO: should assemble remote somewhere else maybe
                        remote = kwargs.pop('remote', 'origin')
                        remote_branch = kwargs.pop('remote_branch', None)
                        remote_url = kwargs.pop('remote_url', None)
                        username = kwargs.pop('username', None)
                        password = kwargs.pop('password', None)
                        if remote_url is not None:
                            self.vcs.add_remote(
                                remote,
                                remote_url,
                                # username=username,
                                # password=password,
                            )
                        self.vcs.push(
                            branch='master',
                            remote=remote,
                            remote_branch=remote_branch,
                            username=username,
                            password=password,
                        )
            else:
                raise PromanVersioningException(
                    'no version update could be determined'
                )
        else:
            raise PromanVersioningException('repository is not clean')

    def start_release(self, **kwargs: Any) -> Version:
        """Start a release."""
        new_version = deepcopy(self.config.version)

        if (
            self.config.version.enable_devreleases
            and self.release == 'development'
        ):
            log.info('found devrelease')
            new_version.start_alpha()  # type: ignore

        if self.config.version.enable_prereleases:
            log.info('found prerelease')
            if self.release == 'alpha':
                new_version.start_beta()  # type: ignore
            if self.release == 'beta':
                new_version.start_release()  # type: ignore
            if self.release == 'release':
                new_version.finish_release()  # type: ignore

        if (
            self.release == 'final'
            or (
                self.config.version.enable_postreleases
                and self.release == 'post'
            )
        ):
            log.info(f"found {self.release} release")
            new_version.start_devrelease()  # type: ignore

        return new_version

    def bump_version(self, **kwargs: Any) -> Version:
        """Update the version of the project."""
        if (
            ('type' in self.title and self.title['type'] == 'release')
            or kwargs.get('release') is True
        ):
            new_version = self.start_release(**kwargs)
            self.update_configs(new_version, **kwargs)
        else:
            new_version = deepcopy(self.config.version)
            build = kwargs.pop('build', None)

            # TODO: break, and feat should start devrelease from final or post
            # local number depends on metadata / fork / conflict existing vers
            if self.title['break'] or self.footer['breaking_change']:
                new_version.bump_major()
            elif 'type' in self.title:
                if self.title['type'] == 'feat':
                    new_version.bump_minor()
                elif self.title['type'] == 'fix':
                    new_version.bump_micro()
                elif self.title['type'] in self.config.parser.types:
                    # new_version = self.__bump_release(new_version)
                    new_version.bump_release()  # type: ignore
                else:
                    # TODO: need debug statement here instead
                    raise PromanVersioningException(
                        'received unsupported commit type'
                    )

            # TODO: configure local version handling
            if build is not None:
                new_version.new_local(build=build)
            self.update_configs(new_version, **kwargs)
        return new_version
