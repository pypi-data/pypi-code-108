import seutils


class XrdImplementation(seutils.Implementation):

    rcodes = {
        54 : seutils.NoSuchPath,
        52 : seutils.PermissionDenied,
        51 : seutils.HostUnreachable
        }

    def check_is_installed(self):
        return seutils.cmd_exists('xrdfs')

    @seutils.add_env_kwarg
    def stat(self, path):
        import datetime
        fullpath = path
        mgm, path = seutils.split_mgm(path)
        cmd = [ 'xrdfs', mgm, 'stat', path ]
        output = self.run_command(cmd, path=path)
        # Parse output to an Inode instance
        size = None
        modtime = None
        isdir = None
        for l in output:
            l = l.strip()
            if l.startswith('Size:'):
                size = int(l.split()[1])
            elif l.startswith('MTime:'):
                timestamp = l.replace('MTime:', '').strip()
                modtime = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            elif l.startswith('Flags:'):
                isdir = 'IsDir' in l
        if size is None: raise RuntimeError('Could not extract size from stat:\n{0}'.format(output))
        if modtime is None: raise RuntimeError('Could not extract modtime from stat:\n{0}'.format(output))
        if isdir is None: raise RuntimeError('Could not extract isdir from stat:\n{0}'.format(output))
        return seutils.Inode(fullpath, modtime, isdir, size)

    @seutils.add_env_kwarg
    def mkdir(self, directory):
        mgm, directory = seutils.split_mgm(directory)
        self.run_command([ 'xrdfs', mgm, 'mkdir', '-p', directory ], path=directory)

    @seutils.rm_safety
    @seutils.add_env_kwarg
    def rm(self, path, recursive=False):
        # NB: xrdfs cannot recursively delete contents of directories, so this is not the preferred tool
        mgm, lfn = seutils.split_mgm(path)
        if self.isdir(path):
            if not recursive:
                raise RuntimeError('{} is a directory but rm instruction is not recursive'.format(path))
            rm = 'rmdir'
        else:
            rm = 'rm'
        self.run_command([ 'xrdfs', mgm, rm, lfn ], path=path)

    @seutils.add_env_kwarg
    def cat(self, path):
        mgm, path = seutils.split_mgm(path)
        return ''.join(self.run_command([ 'xrdfs', mgm, 'cat', path ], path=path))

    @seutils.listdir_check_isdir
    @seutils.add_env_kwarg
    def listdir(self, directory, stat=False):
        mgm, path = seutils.split_mgm(directory)
        cmd = [ 'xrdfs', mgm, 'ls', path ]
        if stat: cmd.append('-l')
        output = self.run_command(cmd, path=directory)
        contents = []
        for l in output:
            l = l.strip()
            if not len(l): continue
            if stat:
                contents.append(xrdstatline_to_inode(l, mgm))
            else:
                contents.append(seutils.format(l, mgm))
        return contents

    @seutils.add_env_kwarg
    def cp(self, src, dst, n_attempts=None, create_parent_directory=True, verbose=True, force=False):
        if n_attempts is None: n_attempts = seutils.N_COPY_ATTEMPTS
        cmd = [ 'xrdcp', src, dst ]
        if not verbose: cmd.insert(1, '-s')
        if create_parent_directory: cmd.insert(1, '-p')
        if force: cmd.insert(1, '-f')
        self.run_command(cmd, n_attempts=n_attempts, path=src+' -> '+dst)


def xrdstatline_to_inode(statline, mgm):
    """
    Converts a plain line as outputted by `xrdfs <mgm> ls -l <path>` into an Inode object
    """
    import datetime
    components = statline.strip().split()
    if not len(components) == 5:
        raise RuntimeError(
            'Expected 5 components for stat line:\n{0}'
            .format(statline)
            )
    isdir = components[0].startswith('d')
    modtime = datetime.datetime.strptime(components[1] + ' ' + components[2], '%Y-%m-%d %H:%M:%S')
    size = int(components[3])
    path = seutils.format(components[4], mgm)
    return seutils.Inode(path, modtime, isdir, size)
