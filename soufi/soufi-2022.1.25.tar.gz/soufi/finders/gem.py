# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.

import requests

from soufi import exceptions, finder

GEM_DOWNLOADS = 'https://rubygems.org/downloads/'
API_TIMEOUT = 30  # seconds


class GemFinder(finder.SourceFinder):
    """Find Gem files.

    Finds files at https://rubygems.org/downloads
    """

    distro = finder.SourceType.gem.value

    def _find(self):
        source_url = self.get_source_url()
        return GemDiscoveredSource([source_url])

    def get_source_url(self):
        url = f"{GEM_DOWNLOADS}{self.name}-{self.version}.gem"
        response = requests.head(url, timeout=API_TIMEOUT)
        if response.status_code != requests.codes.ok:
            raise exceptions.SourceNotFound
        return url


class GemDiscoveredSource(finder.DiscoveredSource):
    """A discovered Gem package."""

    make_archive = finder.DiscoveredSource.remote_url_is_archive
    # NOTE(nic): `distro` and `archive_extension` are the same,
    # so auto-output mode will name these things `.gem.gem`.  The
    # recommended workaround is to not use auto-output mode :-)
    archive_extension = '.gem'

    def populate_archive(self, *args, **kwargs):  # pragma: no cover
        # Required by the base class but Gems are already tarballs so
        # nothing to do.
        pass

    def __repr__(self):
        return self.urls[0]
