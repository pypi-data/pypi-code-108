# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.

import requests

from soufi import exceptions, finder

SNAPSHOT_API = "https://snapshot.debian.org/"
API_TIMEOUT = 30  # seconds


class DebianFinder(finder.SourceFinder):
    """Find Debian source files.

    Uses the API documented at
    https://salsa.debian.org/snapshot-team/snapshot/blob/master/API
    """

    distro = finder.Distro.debian.value

    def _find(self):
        source_info = self.get_source_info()
        hashes = self.get_hashes(source_info)
        urls = self.get_urls(hashes)
        return DebianDiscoveredSource(urls)

    def get_source_info(self):
        """Return a dict of {name, version} of the source."""
        # This API returns ALL versions of binary packages, you can't
        # put a version in the API. Here, we grab the output and go
        # spelunking.
        url = f"{SNAPSHOT_API}mr/binary/{self.name}/"
        response = requests.get(url, timeout=API_TIMEOUT)
        if response.status_code != requests.codes.ok:
            raise exceptions.SourceNotFound
        data = response.json()
        all_versions = data['result']
        for info in all_versions:
            if info['binary_version'] == self.version:
                return dict(name=info['source'], version=info['version'])
        raise exceptions.SourceNotFound

    def get_hashes(self, source_info):
        # Return a list of file hashes as used by Snapshot.
        url = (
            f"{SNAPSHOT_API}mr/package/"
            f"{source_info['name']}/{source_info['version']}/srcfiles"
        )
        response = requests.get(url, timeout=API_TIMEOUT)
        if response.status_code != requests.codes.ok:
            raise exceptions.SourceNotFound
        data = response.json()
        try:
            return [r['hash'] for r in data['result']]
        except (IndexError, TypeError):
            raise exceptions.SourceNotFound

    def get_urls(self, hashes):
        # Get file name and return (name, url) pairs
        urls = []
        for hash in hashes:
            url = f"{SNAPSHOT_API}mr/file/{hash}/info"
            response = requests.get(url, timeout=API_TIMEOUT)
            if response.status_code != requests.codes.ok:
                raise exceptions.DownloadError(response.reason)
            data = response.json()
            # The result data is a list. I am unsure what each element
            # of the list can be, but it seems like taking the first
            # returns a valid source file name, which is all we want.
            result = data['result'][0]
            name = result['name']
            urls.append((name, f"{SNAPSHOT_API}file/{hash}"))
        return urls


class DebianDiscoveredSource(finder.DiscoveredSource):
    """A discovered Debian source package.

    This class differs from the Ubuntu one in that it is required
    to separately store the final names of the files we're downloading,
    as they cannot be ascertained from the URL alone.
    """

    def __init__(self, urls):
        names, _urls = zip(*urls)
        super().__init__(_urls)
        self.names = names

    def populate_archive(self, temp_dir, tar):
        for name, url in zip(self.names, self.urls):
            arcfile_name = self.download_file(
                temp_dir, name, url, timeout=API_TIMEOUT
            )
            tar.add(arcfile_name, arcname=name, filter=self.reset_tarinfo)

    def __repr__(self):
        output = []
        for name, url in zip(self.names, self.urls):
            output.append(f"{name}: {url}")
        return "\n".join(output)
