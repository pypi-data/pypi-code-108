from multiprocessing import context

class NoDaemonProcess(context.SpawnProcess):
    # make 'daemon' attribute always return False
    # needed for multiprocessing child processes
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)
