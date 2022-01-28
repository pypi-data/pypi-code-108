import seutils
import os, os.path as osp, datetime, shutil

class LocalImplementation(seutils.Implementation):

    def check_is_installed(self):
        return True

    @seutils.add_env_kwarg
    def exists(self, path):
        return osp.exists(path)

    @seutils.add_env_kwarg
    def isdir(self, path):
        return osp.isdir(path)

    @seutils.add_env_kwarg
    def isfile(self, path):
        return osp.isfile(path)

    @seutils.add_env_kwarg
    def stat(self, path):
        try:
            stat_result = os.stat(path)
        except FileNotFoundError:
            raise seutils.NoSuchPath(path)
        return seutils.Inode(
            path, datetime.datetime.fromtimestamp(stat_result.st_mtime),
            self.isdir(path), stat_result.st_size
            )

    @seutils.add_env_kwarg
    def mkdir(self, directory):
        os.makedirs(directory)

    @seutils.rm_safety
    @seutils.add_env_kwarg
    def rm(self, path, recursive=False):
        if self.isfile(path):
            os.remove(path)
        elif recursive:
            shutil.rmtree(path)
        else:
            raise RuntimeError('{} is a directory but rm instruction is not recursive'.format(path))

    @seutils.add_env_kwarg
    def cat(self, path):
        try:
            with open(path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise seutils.NoSuchPath(path)

    @seutils.listdir_check_isdir
    @seutils.add_env_kwarg
    def listdir(self, directory, stat=False):
        paths = os.listdir(directory)
        if stat:
            paths = [ self.stat(p) for p in paths ]
        return paths

    @seutils.add_env_kwarg
    def cp(self, src, dst, n_attempts=None, create_parent_directory=True, verbose=True, force=False):
        for path in [src, dst]:
            if seutils.has_protocol(path):
                raise NotImplementedError(
                    'Remote paths not allowed for local cp implementation: {0}'
                    .format(path)
                    )
        if n_attempts is not None:
            seutils.logger.warning('n_attempts keyword ignored for local implementation')
        if create_parent_directory and not self.isdir(seutils.dirname(dst)):
            self.mkdir(seutils.dirname(dst))
        shutil.copy(src, dst)
