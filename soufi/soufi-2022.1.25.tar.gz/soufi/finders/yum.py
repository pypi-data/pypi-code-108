# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.

import abc
import functools
import urllib

import repomd
import requests

from soufi import exceptions, finder

TIMEOUT = 30  # seconds


class YumFinder(finder.SourceFinder, metaclass=abc.ABCMeta):
    """An abstract base class for making Yum-based finders.

    Subclasses of this should provide methods for setting up the repository
    search lists to pass to __init__.

    The lookup is a 2-stage process:
        1. Attempt to look up the SRPM directly from the sources repository.
           In these cases, we use the name only and ignore the version,
           since it is a very common practice for repositories to only
           publish repodata for the "current" version, while still
           providing older sources.
        2. Attempt to look up the name of the source RPM from the binary
           repository.  This will catch packages where the source and
           binary package names do not match.  The version is also ignored
           in this step, for the same reasons.  Then backtrack and attempt
           to lookup that package in the source repos.
    """

    def __init__(self, *args, source_repos=None, binary_repos=None, **kwargs):
        self.source_repos = source_repos
        if not self.source_repos:
            self.source_repos = self.get_source_repos()

        self.binary_repos = binary_repos
        if not self.binary_repos:
            self.binary_repos = self.get_binary_repos()

        super().__init__(*args, **kwargs)

    @abc.abstractmethod
    def get_source_repos(self):
        raise NotImplementedError  # pragma: nocover

    @abc.abstractmethod
    def get_binary_repos(self):
        raise NotImplementedError  # pragma: nocover

    def _find(self):
        source_url = self.get_source_url()
        return YumDiscoveredSource([source_url])

    def get_source_url(self):
        # The easy part: try to find the package in the source repos.
        url = self._walk_source_repos(self.name)
        if url is None:
            # The hard part: try to find the package in the binary repos,
            # then backtrack into the source repos with the name and version
            # of the SRPM provided
            source_name, source_ver = self._walk_binary_repos(self.name)
            if source_name is None:
                raise exceptions.SourceNotFound

            url = self._walk_source_repos(source_name, source_ver)
        if url is None:
            raise exceptions.SourceNotFound

        # If we have a URL, but it's no good, we don't have a URL.
        if not self.test_url(url):
            raise exceptions.SourceNotFound

        return url

    def _walk_source_repos(self, name, version=None):
        if version is None:
            version = self.version
        packages = []
        for repo_url in self.source_repos:
            repo = self._get_repo(repo_url)
            if repo is None:
                continue
            for package in repo.findall(name):
                # If the package version in the repomd is our version,
                # it's easy.  Note that we want to match epoch-full and
                # epoch-less version formats.
                if version in (package.evr, package.vr):
                    return repo.baseurl + package.location
                # Otherwise let's make it weird
                packages.append(package)

            # If we've made it here, things have gotten weird.  Replace the
            # version+release info in all unique package locations with our
            # version and see if they exist.  This should find superseded
            # packages that are present in the repo, but not in the repomd.
            locs = set(p.location.replace(p.vr, version) for p in packages)
            for loc in locs:
                if self.test_url(repo.baseurl + loc):
                    return repo.baseurl + loc
        return None

    def _walk_binary_repos(self, name):
        packages = []
        for repo_url in self.binary_repos:
            repo = self._get_repo(repo_url)
            if repo is None:
                continue
            for package in repo.findall(name):
                # If we have a binary package matching our version, but with
                # a different name than the corresponding source package,
                # return the NVR fields
                if self.version in (package.evr, package.vr):
                    return self._nevra_or_none(package)
                # Otherwise let's make it weird
                packages.append(package)

        # If we've made it here, things have gotten weird; this should be
        # the case of a source RPM that produces binary RPMs with different
        # names *and* versions (the lvm2 package from Red Hat is a good example
        # of this).  In this case, we won't be able to make heads or tails of
        # the response, unless (and only unless) it contains a single package.
        try:
            [package] = packages
        except ValueError:
            return None, None
        return self._nevra_or_none(package)

    def _nevra_or_none(self, package):
        if package.sourcerpm == '':
            # It's here, but has no sources defined!  Bummer...
            return None, None
        nevra = self._get_nevra(package.sourcerpm)
        return nevra['name'], f"{nevra['ver']}-{nevra['rel']}"

    # Cache repo downloads as they are slow and network-bound.
    @classmethod
    @functools.lru_cache(maxsize=1024)
    def _get_repo(cls, url):
        if not url.endswith('/'):
            url += '/'
        try:
            return repomd.load(url)
        except urllib.error.HTTPError:
            return None

    # TODO(nic): throw this out and use hawkey/libdnf whenever that finally
    #  stabilizes.  See: https://github.com/juledwar/soufi/issues/13
    @staticmethod
    def _get_nevra(filename):
        """Split out the NEVRA fields from an RPM filename."""

        # It's easiest to do this by eating the filename backwards, dropping
        # offset pointers as we go
        if filename.endswith('.rpm'):
            filename = filename[:-4]
        arch_offset = filename.rfind('.')
        arch = filename[1 + arch_offset :]
        rel_offset = filename[:arch_offset].rfind('-')
        rel = filename[1 + rel_offset : arch_offset]
        ver_offset = filename[:rel_offset].rfind('-')
        ver = filename[1 + ver_offset : rel_offset]
        name = filename[:ver_offset]
        # Sometimes the epoch is before the name, sometimes it's before the
        # version.  Support both.
        if ':' in ver:
            epoch, ver = ver.split(':', maxsplit=1)
        elif ':' in name:
            epoch, name = name.split(':', maxsplit=1)
        else:
            epoch = ''
        return dict(name=name, ver=ver, rel=rel, epoch=epoch, arch=arch)

    # Use this wrapper for doing HTTP HEAD requests, as it will swallow
    # Timeout exceptions, but cache other lookups.
    @classmethod
    def test_url(cls, url):
        try:
            return cls._head_url(url)
        except requests.exceptions.Timeout:
            return False

    # Generally we just want functools.cache here, but a strictly unbounded
    # cache is just a bad idea
    @classmethod
    @functools.lru_cache(maxsize=1048576)
    def _head_url(cls, url):
        response = requests.head(url, timeout=TIMEOUT)
        return response.status_code == requests.codes.ok

    @classmethod
    @functools.lru_cache(maxsize=128)
    def get_url(cls, url):
        # Not used directly by this class, but subclasses tend to need it.
        response = requests.get(url, timeout=TIMEOUT)
        if response.status_code != requests.codes.ok:
            raise exceptions.DownloadError(response.reason)
        return response.content


class YumDiscoveredSource(finder.DiscoveredSource):
    """A discovered Red Hat source package."""

    make_archive = finder.DiscoveredSource.remote_url_is_archive
    archive_extension = '.src.rpm'

    def populate_archive(self, *args, **kwargs):  # pragma: no cover
        # Src RPMs are already compressed archives, nothing to do.
        pass

    def __repr__(self):
        return self.urls[0]
