from unittest import TestCase

from NagiosCheckHelper import NagErrors

class TestNagErrors(TestCase):

    def test_addCritical(self):
        eo = NagErrors()
        eo.addCritical('Critical Error')
        self.assertEqual(len(eo.critical), 1)
        self.assertEqual(len(eo.warning), 0)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 2)

    def test_addWarning(self):
        eo = NagErrors()
        eo.addWarning('Warning Error')
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 1)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 1)
    
    def test_addUnknown(self):
        eo = NagErrors()
        eo.addUnknown('Unknown Error')
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 0)
        self.assertEqual(len(eo.unknown), 1)
        self.assertEqual(eo.getExitCode(), 3)
    
    def test_okStatus(self):
        eo = NagErrors()
        self.assertEqual(len(eo.critical), 0)
        self.assertEqual(len(eo.warning), 0)
        self.assertEqual(len(eo.unknown), 0)
        self.assertEqual(eo.getExitCode(), 0)

    def test_formatStatus(self):
        eo = NagErrors()
        self.assertEqual(eo.formatStatus('WARNING', ['String1']), "WARNING String1\r\n")
        self.assertEqual(eo.formatStatus('WARNING', ['String1', 'String2']), "WARNING:\r\n    String1\r\n    String2\r\n")
