# copyright: (c) 2021 by Jesse Johnson.
# license: MPL-2.0, see LICENSE for more details.
"""Manage version numbers."""

# import logging
from typing import Any, List, Optional, Tuple

from packaging.version import Version as PackageVersion
from packaging.version import _cmpkey, _parse_local_version, _Version
from transitions import Machine


class Version(PackageVersion):
    """Provide PEP440 compliant versioning."""

    def __init__(self, version: str, **kwargs: Any) -> None:
        """Initialize version object."""
        # self.kind = kwargs.pop('version_system', 'semver')
        self.compat = kwargs.pop('compat', 'pep440')
        super().__init__(version=version)

        # TODO: transitions here should be populated by VCS workflow
        self.enable_devreleases = kwargs.get('enable_devreleases', True)
        self.enable_prereleases = kwargs.get('enable_prereleases', True)
        self.enable_postreleases = kwargs.get('enable_postreleases', True)

        self.machine = Machine(
            self, states=self.states, initial=self.release_type
        )

        # dev-releases
        devrelease_sources = ['final']
        if self.enable_postreleases:
            devrelease_sources.append('post')
        self.machine.add_transition(
            trigger='start_devrelease',
            source=devrelease_sources,
            dest='development',
            before='new_devrelease',
            conditions=['enable_devreleases'],
        )

        # pre-releases
        prerelease_sources = []
        if self.enable_devreleases:
            prerelease_sources.append('development')
        else:
            prerelease_sources.append('final')
            if self.enable_postreleases:
                prerelease_sources.append('post')
        self.machine.add_transition(
            trigger='start_alpha',
            source=prerelease_sources,
            dest='alpha',
            before='new_prerelease',
            conditions=['enable_prereleases'],
        )
        self.machine.add_transition(
            trigger='start_beta',
            source='alpha',
            dest='beta',
            before='new_prerelease',
            conditions=['enable_prereleases'],
        )
        self.machine.add_transition(
            trigger='start_release',
            source='beta',
            dest='release',
            before='new_prerelease',
            conditions=['enable_prereleases'],
        )

        # final release
        final_sources = []
        if self.enable_prereleases:
            final_sources.append('release')
        elif self.enable_devreleases:
            final_sources.append('development')
        else:
            final_sources.append('final')
            if self.enable_postreleases:
                final_sources.append('post')
        self.machine.add_transition(
            trigger='finish_release',
            source=final_sources,
            dest='final' if 'final' not in final_sources else None,
            before='finalize_release',
        )

        # post-releases
        self.machine.add_transition(
            trigger='start_postrelease',
            source='final',
            dest='post',
            before='new_postrelease',
            conditions=['enable_postreleases'],
        )

        self.machine.add_transition(
            trigger='bump_release',
            source='*',
            dest=None,
            before='_bump_release',
        )

    def __str__(self) -> str:
        """Handle version formatting."""
        parts = []

        # Epoch
        if self.epoch != 0:
            parts.append(f"{self.epoch}!")

        # Release segment
        parts.append('.'.join(str(x) for x in self.release))

        # Pre-release
        if self.pre is not None:
            if self.compat == 'semver':
                separator = '-'
            else:
                separator = ''
            parts.append(
                f"{separator}{self.pre[0]}{str(self.pre[1])}"
            )

        # Post-release
        if self.post is not None:
            if self.compat == 'semver':
                separator = '-'
            else:
                separator = '.post'
            parts.append(f"{separator}{self.post}")

        # Development release
        if self.dev is not None:
            if self.compat == 'semver':
                separator = '-'
            else:
                separator = '.'
            parts.append(f"{separator}dev{self.dev}")

        # Local version segment
        if self.local is not None:
            parts.append(f"+{self.local}")

        return ''.join(parts)

    @property
    def states(self) -> List[str]:
        """List all states."""
        states = ['final']
        if self.enable_devreleases:
            states += ['development']
        if self.enable_prereleases:
            states += ['alpha', 'beta', 'release']
        if self.enable_postreleases:
            states += ['post']
        return states

    @property
    def release_type(self) -> str:
        """Get the current state of package release."""
        if self.is_devrelease:
            state = 'development'
        elif self.is_prerelease and self.pre:
            if self.pre[0] == 'a':
                return 'alpha'
            elif self.pre[0] == 'b':
                return 'beta'
            elif self.pre[0] == 'rc':
                return 'release'
        elif self.is_postrelease:
            state = 'post'
        else:
            state = 'final'
        return state

    def __update_version(
        self,
        epoch: Optional[int] = None,
        release: Optional[Tuple[Any, ...]] = None,
        pre: Optional[Tuple[str, Optional[int]]] = None,
        post: Optional[Tuple[Optional[str], Optional[int]]] = None,
        dev: Optional[Tuple[str, Optional[int]]] = None,
        local: Optional[str] = None,
    ) -> None:
        """Update the internal version state."""
        if not (epoch or release):
            pre = pre or self.pre
            post = post or (None if self.post is None else ('post', self.post))
            dev = dev or (None if self.dev is None else ('dev', self.dev))

        self._version = _Version(
            epoch=epoch or self.epoch,
            release=release or self.release,
            pre=pre,
            post=post,
            dev=dev,
            local=_parse_local_version(local) if local else None,
        )

        self._key = _cmpkey(
            self._version.epoch,
            self._version.release,
            self._version.pre,
            self._version.post,
            self._version.dev,
            self._version.local,
        )

    def bump_epoch(self) -> None:
        """Update epoch releaes for version system changes."""
        self.__update_version(epoch=self.epoch + 1)
        self.machine.set_state('final')

    def bump_major(self) -> None:
        """Update major release to next version number."""
        self.__update_version(release=(self.major + 1, 0, 0))
        self.machine.set_state('final')

    def bump_minor(self) -> None:
        """Update minor release to next version number."""
        self.__update_version(release=(self.major, self.minor + 1, 0))
        self.machine.set_state('final')

    def bump_micro(self) -> None:
        """Update micro release to next version number."""
        self.__update_version(release=(self.major, self.minor, self.micro + 1))

    def __bump_version(self, kind: str) -> None:
        """Bump version based on version kind."""
        if kind == 'major':
            self.bump_major()
        if kind == 'minor':
            self.bump_minor()
        if kind == 'micro':
            self.bump_micro()

    def _bump_release(self, *args: Any, **kwargs: Any) -> None:
        """Update to the next development release version number."""
        if self.enable_devreleases and self.dev is not None:
            dev = self.dev + 1
            self.__update_version(dev=('dev', dev))
        if self.enable_prereleases and self.pre is not None:
            pre = (self.pre[0], self.pre[1] + 1)
            self.__update_version(pre=pre)
        if self.enable_postreleases:
            if self.release_type == 'final':
                self.__update_version(post=('post', 0))
            elif self.post is not None:
                post = self.post + 1
                self.__update_version(post=('post', post))

    def new_devrelease(self, kind: str = 'minor') -> None:
        """Update to the next development release version number."""
        if self.dev is None:
            self.__bump_version(kind)
            self.__update_version(dev=('dev', 0))

    def new_prerelease(self, kind: Optional[str] = None) -> None:
        """Update to next prerelease version type."""
        if self.pre is not None:
            if self.pre[0] == 'a':
                pre = ('b', 0)
            elif self.pre[0] == 'b':
                pre = ('rc', 0)
        else:
            if kind:
                self.__bump_version(kind)
            else:
                self.finalize_release()
            pre = ('a', 0)
        self.__update_version(pre=pre)

    def new_postrelease(self) -> None:
        """Update the post release version number."""
        if self.release_type == 'final':
            self.__update_version(post=('post', 0))

    def new_local(self, build: str = 'build-0') -> None:
        """Create new local version instance number."""
        self.__update_version(local=build)

    def finalize_release(self) -> None:
        """Update to next prerelease version type."""
        if self.is_devrelease or self.is_prerelease:
            self.__update_version(release=(self.major, self.minor, self.micro))
