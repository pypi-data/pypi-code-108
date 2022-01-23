try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

__all__ = ['OMFITenv']


class OMFITenv(SortedDict):
    """
    This class is used to retrieve and parse environmental variables on a server

    :param server: server from which to retrieve the environmental variables

    :param tunnel: tunnel to reach the server

    :param loadStartupFiles: whether the user startup files should be parsed

    :param string: string to be parsed instead of conneting to a server
    """

    def __init__(self, server='localhost', tunnel='', loadStartupFiles=True, string=None):
        SortedDict.__init__(self)

        if string is None:
            # fetch environmental variables
            ssh = ''
            if not loadStartupFiles:
                ssh = 'ssh localhost '
            std_out = []
            OMFITx.remote_execute(server, ssh + 'env', './', tunnel, std_out=std_out, quiet=True, use_bang_command=False)
        else:
            # use external string
            std_out = string.split('\n')

        # parse environmental variables
        for k in std_out:
            k = k.strip()
            if not len(k):
                continue
            tmp = k.split('=')
            self[tmp[0]] = '='.join(tmp[1:])
