from fs.opener import Opener

__all__ = ['MSGraphyOneDriveFSOpener']

from msgraphy.fs.onedrivefs import MSGraphyOneDriveFS


class MSGraphyOneDriveFSOpener(Opener):
    protocols = ['o365']

    def open_fs(self, fs_url, parse_result, writeable, create, cwd):
        if parse_result.username:
            resource = f"{parse_result.username}@{parse_result.resource}"
        else:
            resource = parse_result.resource

        return MSGraphyOneDriveFS(resource, writeable)
