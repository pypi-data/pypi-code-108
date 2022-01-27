import seutils
from seutils import run_command, get_exitcode, Inode, split_mgm
logger = seutils.logger

IS_INSTALLED = None
def is_installed():
    """
    Checks whether eos is on the path
    """
    global IS_INSTALLED
    if IS_INSTALLED is None: IS_INSTALLED = seutils.cmd_exists('eos')
    return IS_INSTALLED

def rm(path, recursive):
    mgm, lfn = split_mgm(path)
    if seutils.isdir(path):
        if not recursive:
            raise RuntimeError('{} is a directory but rm instruction is not recursive'.format(path))
    cmd = [ 'eos', mgm, 'rm', lfn ]
    if recursive: cmd.insert(-1, '-r')
    run_command(cmd)