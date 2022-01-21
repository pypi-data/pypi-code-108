from git import RemoteProgress
from tqdm import tqdm

from ..utils import logger


class GitProgressPrinter(RemoteProgress):
    """
    Handler implementing GitPython's RemoteProgress delegate
    so as to print git operation progress.
    """

    """Reformed possible operations"""
    OPS = {
        RemoteProgress.COUNTING: "COUNTING",
        RemoteProgress.COMPRESSING: "COMPRESSING",
        RemoteProgress.WRITING: "WRITING",
        RemoteProgress.RECEIVING: "RECEIVING",
        RemoteProgress.RESOLVING: "RESOLVING",
        RemoteProgress.FINDING_SOURCES: "FINDING SOURCES",
        RemoteProgress.CHECKING_OUT: "CHECKING OUT",
    }

    """Progress bar object (tqdm instance)"""
    pbar = None

    def update(self, op_code, cur_count, max_count=None, message=''):
        """
        Delegate method to handle git progress update
        """
        # Determine the right operation
        op = -1
        for _op in self.OPS.keys():
            if op_code in [
                _op,
                _op + RemoteProgress.BEGIN,
                _op + RemoteProgress.END,
            ]:
                op = _op
                break
        if op == -1:
            logger.warning("Broken progress")

        # New operation: init tqdm
        if op_code == op + RemoteProgress.BEGIN:
            self.pbar = tqdm(total=(int(max_count) or 100),
                             initial=(int(cur_count) or 0),
                             desc=self.OPS[op])
        # End of operation: close tqdm
        elif op_code == op + RemoteProgress.END and self.pbar is not None:
            self.pbar.update(int(cur_count) - self.pbar.n)
            self.pbar.close()
        # Progressing: update tqdm
        elif self.pbar is not None:
            self.pbar.update(int(cur_count) - self.pbar.n)
        else:
            logger.warning("Broken progress")
