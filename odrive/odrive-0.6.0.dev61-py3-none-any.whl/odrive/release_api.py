import enum
import hashlib
import os
from typing import Optional

import appdirs

from odrive.api_client import ApiClient
from odrive.crypto import safe_b64decode, safe_b64encode

class ReleaseApi():
    BASE_URL = '/releases'

    def __init__(self, api_client: 'ApiClient'):
        self._api_client = api_client

    async def get_index(self, release_type: str):
        outputs = await self._api_client.call('GET', ReleaseApi.BASE_URL + '/' + release_type + '/index')
        return ReleaseIndex(outputs['files'], outputs['commits'], outputs['channels'])

    async def load(self, manifest: dict, force_download: bool = False):
        """
        Downloads a firmware file and saves it in a cache directory.
        If the file was already cached before, it is loaded from disk instead
        (unless force_download is True).
        Returns the path of the cached file.
        """
        cache_dir = os.path.join(appdirs.user_cache_dir("odrivetool", "ODrive Robotics"), 'firmware')
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, manifest['content_key'] + '.elf')

        if force_download or not os.path.isfile(cache_path):
            with open(cache_path, 'wb') as fp:
                fp.write(await self._api_client.download(manifest['url']))

        return cache_path


class VersionRelationship(enum.Enum):
    UNKNOWN = enum.auto()
    EQUAL = enum.auto()
    UPGRADE = enum.auto()
    DOWNGRADE = enum.auto()

class ChannelNotFoundError(Exception):
    pass

class ChannelEmptyError(Exception):
    pass

class ReleaseIndex():
    def __init__(self, files, commits, channels):
        self._files = {safe_b64decode(f['content']): f for f in files}
        self._commits = commits
        for c in commits:
            c['content'] = safe_b64decode(c['content'])
        self._open_channels = {c['channel']: c['commits'] for c in channels if not c['closed']}
        self._closed_channels = {c['channel']: c['commits'] for c in channels if c['closed']}

    @property
    def open_channel_names(self):
        return list(self._open_channels.keys())

    def _get_filtered_commits(self, **qualifiers: dict):
        return {
            c['commit_hash']: c['content']
            for c in self._commits if all(c[k] == v for k, v in qualifiers.items())
        }

    def _get_filtered_channel_commits(self, channel: str, filtered_commits: dict):
        if channel in self._open_channels:
            commit_hashes = self._open_channels[channel]
        elif channel in self._closed_channels:
            commit_hashes = self._closed_channels[channel]
        else:
            raise ChannelNotFoundError(f"Channel {channel} not found.")

        return [c for c in commit_hashes if c in filtered_commits]

    def get_latest(self, channel: str, **qualifiers: dict):
        """
        Checks for the latest firmware on the specified channel with the specified
        qualifiers (product, app).

        If the specified channel is not found or empty, an exception is thrown.
        Returns a metadata manifest for the release that was found.
        """
        filtered_commits = self._get_filtered_commits(**qualifiers)
        filtered_channel_commits = self._get_filtered_channel_commits(channel, filtered_commits)

        if len(filtered_channel_commits) == 0:
            raise ChannelEmptyError()

        commit_hash = filtered_channel_commits[-1]
        return self.get_commit(commit_hash, **qualifiers)

    def get_commit(self, commit_hash: str, **qualifiers):
        """
        Looks up the release information for the specified commit with the
        specified qualifiers (product, app).

        Returns a metadata manifest for the release that was found.
        """
        filtered_commits = self._get_filtered_commits(**qualifiers)
        content_key = filtered_commits[commit_hash]

        return {
            'content_key': safe_b64encode(content_key),
            'commit_hash': commit_hash,
            'release_date': self._files[content_key]['release_date'],
            'url': self._files[content_key]['url']
        }

    def compare(self, from_commit: Optional[str], to_commit: str, channel: str, **qualifiers: dict):
        """
        Checks if the specified transition is an upgrade or not.
        """
        if from_commit is None:
            return VersionRelationship.UNKNOWN

        filtered_commits = self._get_filtered_commits(**qualifiers)

        short_hashes = {h[:8]: h for h in filtered_commits.keys()}
        from_commit = short_hashes.get(from_commit, from_commit)
        
        if not from_commit in filtered_commits or not to_commit in filtered_commits:
            return VersionRelationship.UNKNOWN
        
        from_file = filtered_commits[from_commit]
        to_file = filtered_commits[to_commit]

        if from_file == to_file:
            return VersionRelationship.EQUAL
        
        filtered_channel_commits = self._get_filtered_channel_commits(channel, filtered_commits)

        if not from_file in filtered_channel_commits or not to_file in filtered_channel_commits:
            return VersionRelationship.UNKNOWN
        
        if filtered_channel_commits.index(from_file) < filtered_channel_commits.index(to_file):
            return VersionRelationship.UPGRADE
        else:
            return VersionRelationship.DOWNGRADE
