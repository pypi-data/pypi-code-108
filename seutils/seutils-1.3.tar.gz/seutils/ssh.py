import seutils, os
from seutils import run_command, get_exitcode, Inode, split_mgm
import os.path as osp
logger = seutils.logger

IS_INSTALLED = None
def is_installed():
    """
    Checks whether xrdfs is on the path
    """
    global IS_INSTALLED
    if IS_INSTALLED is None: IS_INSTALLED = seutils.cmd_exists('ssh')
    return IS_INSTALLED

def _is_remote(path):
    return ':' in path

def _split_remote(path):
    return path.split(':', 1)

def _lsstatline_to_inode(l, server, parent_path):
    import datetime
    components = l.strip().split()
    isdir = components[0].startswith('d')
    timestamp = ' '.join(components[5:8])
    try:
        modtime = datetime.datetime.strptime(timestamp, '%b %d %H:%M')
    except ValueError:
        try:
            modtime = datetime.datetime.strptime(timestamp, '%b %d %Y')
        except ValueError:
            logger.error(
                'Tried multiple patterns but failed to get date from {0}'
                .format(timestamp)
                )
            raise
    size = int(components[4])
    path = server + ':' + osp.join(parent_path, ' '.join(components[8:]))
    return Inode(path, modtime, isdir, size)

def cp(src, dst, n_attempts=seutils.N_COPY_ATTEMPTS, create_parent_directory=True, verbose=True, force=False):
    cmd = [ 'scp', src, dst ]
    if verbose: cmd.insert(1, '-v')
    if create_parent_directory:
        parent_dir = osp.dirname(dst)
        if _is_remote(dst):
            mkdir(parent_dir)
        elif not osp.isdir(parent_dir):
            os.makedirs(osp.dirname(dst))
    run_command(cmd, n_attempts=n_attempts)

def listdir(directory, stat=False):
    server, path = _split_remote(directory)
    cmd = [ 'ssh', server, 'test -d {0} && ls {1} {0}'.format(path, '-l' if stat else '') ]
    output = run_command(cmd)
    contents = []
    for l in output:
        l = l.strip()
        if l.startswith('total '): continue
        if l.startswith('Warning'): continue
        if not len(l): continue
        if stat:
            if not(l.startswith('d') or l.startswith('-')): continue
            contents.append(_lsstatline_to_inode(l, server, path))
        else:
            contents.append(server + ':' + osp.join(path, l))
    return contents

def exists(path):
    server, path = _split_remote(path)
    return get_exitcode(['ssh', server, 'ls {0}'.format(path)]) == 0

def isfile(path):
    server, path = _split_remote(path)
    return get_exitcode(['ssh', server, 'test -f {0}'.format(path)]) == 0

def isdir(path):
    server, path = _split_remote(path)
    return get_exitcode(['ssh', server, 'test -d {0}'.format(path)]) == 0

def stat(fullpath):
    server, path = _split_remote(fullpath)
    cmd = [ 'ssh', server, 'ls -ld {0}'.format(path) ]
    output = run_command(cmd)
    contents = []
    for l in output:
        l = l.strip()
        if not len(l): continue
        if not(l.startswith('d') or l.startswith('-')): continue
        return _lsstatline_to_inode(l, server, path)

def is_file_or_dir(path):
    try:
        inode = stat(path)
        return 1 if inode.isdir else 2
    except Exception as e:
        logger.debug('Path {0} does not exist: {1}'.format(path, e))
        return 0

def mkdir(path):
    server, lpath = _split_remote(path)
    cmd = [ 'ssh', server, 'mkdir -p {0}'.format(lpath) ]
    run_command(cmd)

def rm(path, recursive=False):
    server, path = _split_remote(directory)
    cmd = [ 'ssh', server, 'rm {1} {0}'.format(path, '-rf' if recursive else '') ]
    run_command(cmd)


# _________________________________

def listdir_recursive(path):
    """
    Specific for ssh: Flat list of all files in a remote directory
    """
    server, lpath = _split_remote(path)
    cmd = [ 'ssh', server, 'find {0} -printf \'%y %s %A@ %p\n\''.format(lpath) ]
    logger.info('Gathering all inodes recursively in %s', path)
    output = run_command(cmd)
    contents = []
    for l in output:
        l = l.strip()
        if not len(l): continue
        if not(l.startswith('d') or l.startswith('f')): continue
        contents.append(_findline_to_inode(l, server))
    return contents

def _findline_to_inode(line, server):
    import datetime
    components = line.strip().split()
    path = server + ':' + ' '.join(components[3:])
    isdir = components[0] == 'd'
    size = int(components[1])
    modtime = datetime.datetime.fromtimestamp(float(components[2]))
    return Inode(path, modtime, isdir, size)
