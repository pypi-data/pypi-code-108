import unittest
import subprocess
import shlex
from reprox import core


class TestHelp(unittest.TestCase):
    """Test that the help function works on all the scripts"""

    def _exec_help(self, cmd):
        ret = subprocess.Popen(shlex.split(cmd))
        ret.communicate()
        core.log.info(f'{cmd} returned {ret}')
        assert ret.returncode == 0, ret

    def test_find_data(self):
        self._exec_help('reprox-find-data --help')

    def test_move_folders(self):
        self._exec_help('reprox-move-folders --help')

    def test_reprocess(self):
        self._exec_help('reprox-reprocess --help')

    def test_start_jobs(self):
        self._exec_help('reprox-start-jobs --help')
