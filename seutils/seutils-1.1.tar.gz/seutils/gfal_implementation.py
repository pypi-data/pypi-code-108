import seutils
import os.path as osp
logger = seutils.logger
import datetime


class GfalImplementation(seutils.Implementation):

    rcodes = {
        2 : seutils.NoSuchPath,
        13 : seutils.PermissionDenied,
        113 : seutils.HostUnreachable
        }

    def check_is_installed(self):
        return seutils.cmd_exists('gfal-ls')

    @seutils.add_env_kwarg
    def stat(self, path):
        cmd = ['gfal-stat', path]
        output = self.run_command(cmd, path=path)
        # Interpret the output to create an Inode object
        size = None
        modtime = None
        isdir = None
        for line in output:
            line = line.strip()
            if len(line) == 0:
                continue
            elif line.startswith('Size:'):
                isdir = ('directory' in line)
                size = int(line.replace('Size:','').strip().split()[0])
            elif line.startswith('Modify:'):
                timestamp = line.replace('Modify:','').strip()
                # Strip off microseconds if they're there
                if '.' in timestamp: timestamp = timestamp.split('.')[0]
                modtime = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        if size is None: raise RuntimeError('Could not extract size from stat:\n{0}'.format(output))
        if modtime is None: raise RuntimeError('Could not extract modtime from stat:\n{0}'.format(output))
        if isdir is None: raise RuntimeError('Could not extract isdir from stat:\n{0}'.format(output))
        return seutils.Inode(path, modtime, isdir, size)        

    @seutils.add_env_kwarg
    def mkdir(self, path):
        self.run_command(['gfal-mkdir', '-p', path], path=path)

    @seutils.add_env_kwarg
    def exists(self, path):
        return seutils.get_exitcode(['gfal-stat', path]) == 0

    @seutils.listdir_check_isdir
    @seutils.add_env_kwarg
    def listdir(self, directory, stat=False):
        cmd = [ 'gfal-ls', format(directory) ]
        if stat: cmd.append('-l')
        output = self.run_command(cmd, path=directory)
        contents = []
        for l in output:
            l = l.strip()
            if not len(l): continue
            if stat:
                contents.append(statline_to_inode(l, directory))
            else:
                contents.append(format(osp.join(directory, l)))
        return contents

    @seutils.rm_safety
    @seutils.add_env_kwarg
    def rm(self, path, recursive=False):
        cmd = [ 'gfal-rm', path ]
        if recursive: cmd.insert(-1, '-r')
        self.run_command(cmd, path=path)

    @seutils.add_env_kwarg
    def cp(self, src, dst, n_attempts=None, create_parent_directory=True, verbose=True, force=False):
        if n_attempts is None: n_attempts = seutils.N_COPY_ATTEMPTS
        cmd = [ 'gfal-copy', '-t', '180', src, dst ]
        if create_parent_directory: cmd.insert(1, '-p')
        if verbose: cmd.insert(1, '-v')
        if force: cmd.insert(1, '-f')
        self.run_command(cmd, n_attempts=n_attempts, path=src+' -> '+dst)

    @seutils.add_env_kwarg
    def cat(self, path):
        return ''.join(self.run_command(['gfal-cat', path], path=path))


def statline_to_inode(statline, parent_directory):
    """
    Converts a plain line as outputted by `gfal-ls -l` into an Inode object.
    `gfal-ls -l` returns only basenames, so the parent_directory from which the
    statline originated is needed as an argument.
    """
    import datetime
    components = statline.strip().split()
    if not len(components) >= 9:
        raise RuntimeError(
            'Expected at least 9 components for stat line:\n{0}'
            .format(statline)
            )
    try:
        isdir = components[0].startswith('d')
        timestamp = ' '.join(components[5:8])
        try:
            modtime = datetime.datetime.strptime(timestamp, '%b %d %H:%M')
        except ValueError:
            modtime = datetime.datetime.strptime(timestamp, '%b %d %Y')
        size = int(components[4])
        path = osp.join(parent_directory, components[8])
        return seutils.Inode(path, modtime, isdir, size)
    except:
        logger.error('Error parsing statline: %s', statline)
        raise
