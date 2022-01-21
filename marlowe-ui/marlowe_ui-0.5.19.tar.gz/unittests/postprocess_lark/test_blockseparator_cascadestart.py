import unittest
from parameterized import parameterized

from marlowe_ui.postprocess_lark import blockseparator

class TestCascade(unittest.TestCase):
    def setUp(self):
        self.cascadestart = blockseparator.Cascade()

    # in cascades/detail.mfs DETL2880
    # 'Cascade',I6,':',5X,'Group',I5,6X,'Number',I3
    @parameterized.expand([
        ('Cascade   123:     Group   45      Number  6',
            {'Cascade':123, 'Group':45, 'Number':6}),
        ('Cascade123123:     Group45454      Number666',
            {'Cascade':123123, 'Group':45454, 'Number':666}),
        # Also match with 'Cascade',I12,':',5X,'Group',I12,6X,'Number',I12
        ('Cascade      123123:     Group       45454      Number         666',
            {'Cascade':123123, 'Group':45454, 'Number':666}),
        ])
    def test_startswith(self, text, index):
        m = self.cascadestart.startswith(text)
        self.assertIsNotNone(m)
        self.assertEqual(int(m['Cascade']), index['Cascade'])
        self.assertEqual(int(m['Group']), index['Group'])
        self.assertEqual(int(m['Number']), index['Number'])
