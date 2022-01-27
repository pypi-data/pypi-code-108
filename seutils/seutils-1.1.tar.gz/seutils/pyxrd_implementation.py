import seutils
import os.path as osp, math, sys
import datetime

class PyxrdImplementation(seutils.Implementation):

    def __init__(self, *args, **kwargs):
        super(PyxrdImplementation, self).__init__(*args, **kwargs)
        self.clients = {}

    def check_is_installed(self):
        try:
            import XRootD
            return True
        except ImportError:
            return False

    def get_client(self, mgm):
        mgm = mgm.strip('/')
        if mgm not in self.clients:
            seutils.logger.info('Starting new client for %s', mgm)
            from XRootD import client
            filesystem = client.FileSystem(mgm)
            status, _ = filesystem.ping()
            seutils.logger.info('Filesystem %s status: %s', mgm, status)
            if not status.ok:
                raise ValueError(
                    'client {0} is not responsive: {1}'
                    .format(mgm, status)
                    )
            self.clients[mgm] = filesystem
        return self.clients[mgm]

    def mkdir(self, path):
        from XRootD.client import flags
        mgm, directory = seutils.split_mgm(path)
        client = self.get_client(mgm)
        seutils.logger.warning('Creating directory on SE: {0}'.format(path))
        status, _ = client.mkdir(directory, flags.MkDirFlags.MAKEPATH)
        if not status.ok:
            raise ValueError(
                'Directory {0} on {1} could not be created: {2}'
                .format(directory, mgm, status)
                )
        seutils.logger.info('Created directory %s: %s', directory, status)

    def stat(self, path):
        mgm, lpath = seutils.split_mgm(path)
        client = self.get_client(mgm)
        status, statinfo = client.stat(lpath)
        if not status.ok:
            raise seutils.NoSuchPath('stat: Could not access {0}: status {1}'.format(path, status))
        return statinfo_to_inode(path, statinfo)

    def listdir(self, path, stat=False, assume_directory=False):
        from XRootD.client import flags
        # Check whether path is actually a directory
        if not assume_directory and not self.isdir(path):
            raise Exception('Path {0} is not a directory'.format(path))
        # Retrieve listobj
        mgm, directory = seutils.split_mgm(path)
        status, listobj = self.get_client(mgm).dirlist(directory, flags.DirListFlags.STAT if stat else 0)
        if not status.ok:
            raise ValueError(
                'Could not list {0}: {1}'
                .format(directory, status)
                )
        # Transform to desired list of contents
        contents = []
        for item in listobj:
            itempath = osp.join(path, item.name)
            if stat:
                contents.append(statinfo_to_inode(itempath, item.statinfo))
            else:
                contents.append(itempath)
        return contents

    def cat(self, path):
        from XRootD import client
        with client.File() as f:
            f.open(path)
            output = b''.join(f.readlines())
            if sys.version_info < (3,):
                return output
            else:
                return output.decode()


FLAGVALS = list(range(7))
_FLAGVALS_PREPARED = False
def read_statinfoflagenum():
    """
    StatInfoFlags is an enum with 2^n values; transform it to an ordinary
    python list
    """
    global FLAGVALS, _FLAGVALS_PREPARED
    if not _FLAGVALS_PREPARED:
        _FLAGVALS_PREPARED = True
        from XRootD import client
        log = lambda val: int(math.log(val, 2.0))
        FLAGVALS[log(client.flags.StatInfoFlags.X_BIT_SET)] = 'X_BIT_SET'
        FLAGVALS[log(client.flags.StatInfoFlags.IS_DIR)] = 'IS_DIR'
        FLAGVALS[log(client.flags.StatInfoFlags.OTHER)] = 'OTHER'
        FLAGVALS[log(client.flags.StatInfoFlags.OFFLINE)] = 'OFFLINE'
        FLAGVALS[log(client.flags.StatInfoFlags.POSC_PENDING)] = 'POSC_PENDING'
        FLAGVALS[log(client.flags.StatInfoFlags.IS_READABLE)] = 'IS_READABLE'
        FLAGVALS[log(client.flags.StatInfoFlags.IS_WRITABLE)] = 'IS_WRITABLE'

def statinfoflag_to_flags(flag):
    """
    Takes an int and returns a list of flags
    """
    read_statinfoflagenum()
    binary = bin(flag)[2:][::-1]
    flags = []
    for i, val in enumerate(binary):
        if i > len(FLAGVALS):
            seutils.logger.error('binary %s exceeded expected length', binary)
            break
        if val == '1':
            flags.append(FLAGVALS[i])
    return flags

def statinfo_to_inode(path, statinfo):
    """
    Converts a path and a statinfo object to an Inode object
    """
    return seutils.Inode(
        path,
        datetime.datetime.strptime(statinfo.modtimestr, '%Y-%m-%d %H:%M:%S'),
        'IS_DIR' in statinfoflag_to_flags(statinfo.flags),
        statinfo.size
        )
