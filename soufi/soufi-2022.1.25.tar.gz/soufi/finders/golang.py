# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.

import requests

from soufi import exceptions, finder

PUBLIC_PROXY = 'https://proxy.golang.org/'
PROXY_TIMEOUT = 30  # seconds


class GolangFinder(finder.SourceFinder):
    """Find Golang modules.

    A simple HEAD request is made to the Goproxy, which will indicate
    whether the module is available or not.

    The proxy used defaults to the public https://proxy.golang.org/.
    """

    distro = finder.SourceType.go.value

    def __init__(self, *args, goproxy=PUBLIC_PROXY, **kwargs):
        super().__init__(*args, **kwargs)
        self.goproxy = goproxy

    @property
    def original_url(self):
        # It seems as though the proxy only works if the name gets lower-cased.
        # So Github repos such as Shopify/sarama don't work as-is. This Is The
        # Go Way and it must not be questioned.
        return f"{self.goproxy}{self.name.lower()}/@v/{self.version}.zip"

    def _find(self):
        # Main entrypoint from the parent class.
        if self._proxy_find():
            return GolangDiscoveredSource([self.original_url])
        raise exceptions.SourceNotFound()

    def _proxy_find(self):
        response = requests.head(self.original_url, timeout=PROXY_TIMEOUT)
        if response.status_code == requests.codes.not_allowed:
            # HEAD not available; we can try to download it instead and abort
            # before starting the stream.
            response = requests.get(
                self.original_url, stream=True, timeout=PROXY_TIMEOUT
            )
            response.close()
        return response.ok


class GolangDiscoveredSource(finder.DiscoveredSource):
    """A discovered Golang source module."""

    archive_extension = '.zip'
    make_archive = finder.DiscoveredSource.remote_url_is_archive

    # We *might* want to add `Disable-Module-Fetch: true` to the download
    # headers as recommended by the docs. This is left as a future exercise as
    # needed.

    def populate_archive(self, *args, **kwargs):
        pass  # pragma: no cover

    def __repr__(self):
        return self.urls[0]
