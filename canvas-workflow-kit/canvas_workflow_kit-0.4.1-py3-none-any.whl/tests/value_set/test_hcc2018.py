from unittest import TestCase
from canvas_workflow_kit.value_set.hcc2018 import HCCConditions


class TestHCCConditions(TestCase):
    def test_label_hdcc_for(self):
        # code does exist
        result = HCCConditions.label_hdcc_for('M0540')
        expected = 'Rheumatoid Arthritis and Inflammatory Connective Tissue Disease'
        self.assertEqual(expected, result)

        # code does not exist
        result = HCCConditions.label_hdcc_for('XXXX')
        expected = ''
        self.assertEqual(expected, result)

    def test_label_idc10_for(self):
        # code does exist
        result = HCCConditions.label_idc10_for('M0540')
        expected = 'Rheumatoid myopathy with rheumatoid arthritis of unspecified site'
        self.assertEqual(expected, result)

        # code does not exist
        result = HCCConditions.label_idc10_for('XXXX')
        expected = ''
        self.assertEqual(expected, result)

    def test_raf_for(self):
        # code does exist
        result = HCCConditions.raf_for('M0540')
        expected = 0.374
        self.assertEqual(expected, result)

        # code does not exist
        result = HCCConditions.raf_for('XXXX')
        expected = 0
        self.assertEqual(expected, result)
