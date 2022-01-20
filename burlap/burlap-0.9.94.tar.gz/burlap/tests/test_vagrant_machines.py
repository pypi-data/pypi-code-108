"""
Run test with:

    tox -c tox-full.ini -e py37-ubuntu_18_04_64 -- -s burlap/tests/test_vagrant_machines.py::TestVagrantMachines::test_machines_one

"""

from mock import patch

from burlap.tests.base import TestCase

class TestVagrantMachines(TestCase):

    def test_machines_one(self):
        with patch('burlap.vagrant.vagrant._status') as mock_status:
            mock_status.return_value = [('default', 'running')]
            from burlap.vagrant import vagrant # pylint: disable=import-outside-toplevel
            self.assertEqual(vagrant.machines(), ['default'])
