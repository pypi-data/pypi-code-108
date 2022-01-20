from fs.errors import ResourceNotFound
from fs.opener import Opener

__all__ = ['MSGraphyOneDriveFSOpener']

from msgraphy.fs.onedrivefs import MSGraphyOneDriveFS


class MSGraphyOneDriveFSOpener(Opener):
    protocols = ['o365']

    def open_fs(self, fs_url, parse_result, writeable, create, cwd):
        url = fs_url[7:]
        root, path = url.split(':', 1)

        fs = MSGraphyOneDriveFS(f'{root}:/', writeable)
        if path not in ('', '/'):
            if create:
                fs = fs.makedirs(path, recreate=True)
            else:
                fs = fs.opendir(path)
        return fs
