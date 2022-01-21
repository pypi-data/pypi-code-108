import datetime
import tempfile

from io import StringIO

from canvas_workflow_kit import settings
from unittest import TestCase

from canvas_workflow_kit.scripts.generate_hcc_value_set import BuildHccValueSet

HCC_VALUE_SET_TSV = f'{settings.BASE_DIR}/tests/value_set/hcc_sample.tsv'

class TestBuildHccValueSet(TestCase):

    def test___init__(self):
        tested = BuildHccValueSet('a', 'b')

        self.assertEqual('a', tested.from_file)
        self.assertEqual('b', tested.to_file)

    def test_to_float(self):
        tested = BuildHccValueSet('', '')

        result = tested.to_float('123.456789')
        expected = 123.456789
        self.assertEqual(expected, result)

        result = tested.to_float('I23.456789')
        expected = 0
        self.assertEqual(expected, result)

    def test_add_line(self):
        tested = BuildHccValueSet('', '')

        in_memory = StringIO()
        tested.file_handle = in_memory
        tested.add_line(0, 'this is a line')
        result = in_memory.getvalue()
        expected = 'this is a line\n'
        self.assertEqual(expected, result)
        in_memory.close()

        in_memory = StringIO()
        tested.file_handle = in_memory
        tested.add_line(2, 'this is a line')
        result = in_memory.getvalue()
        expected = '        this is a line\n'
        self.assertEqual(expected, result)
        in_memory.close()

        in_memory = StringIO()
        tested.file_handle = in_memory
        tested.add_line(3, 'this is a line')
        result = in_memory.getvalue()
        expected = '            this is a line\n'
        self.assertEqual(expected, result)
        in_memory.close()

    def test_write_codes(self):
        tested = BuildHccValueSet(HCC_VALUE_SET_TSV, '')

        in_memory = StringIO()
        tested.file_handle = in_memory
        tested.write_codes()
        result = in_memory.getvalue()
        expected = open(f'{settings.BASE_DIR}/tests/value_set/hcc_codes.txt', 'r').read()
        self.assertEqual(expected, result)
        in_memory.close()

    def test_write_labels(self):
        tested = BuildHccValueSet(HCC_VALUE_SET_TSV, '')

        in_memory = StringIO()
        tested.file_handle = in_memory
        tested.write_labels()
        result = in_memory.getvalue()
        expected = open(f'{settings.BASE_DIR}/tests/value_set/hcc_labels.txt',
                        'r').read()
        self.assertEqual(expected, result)
        in_memory.close()

    def test_write_methods(self):
        tested = BuildHccValueSet(HCC_VALUE_SET_TSV, '')

        in_memory = StringIO()
        tested.file_handle = in_memory
        tested.write_methods()
        result = in_memory.getvalue()
        expected = open(f'{settings.BASE_DIR}/tests/value_set/hcc_methods.txt',
                        'r').read()
        self.assertEqual(f'{expected}\n', result)
        in_memory.close()

    def test_parse_csv(self):
        tested = BuildHccValueSet(HCC_VALUE_SET_TSV, '')

        expected = {
            'COD01',
            'COD02',
            'COD03',
            'COD04',
        }
        count = 0
        for code in tested.parse_csv(True):
            self.assertIn(code, expected)
            count = count + 1
        self.assertEqual(len(expected), count)

        expected = {
            'COD01': ['HCC 01', "Descri'tion 01", 0.123],
            'COD02': ['HCC 02', 'Description 02', 0.223],
            'COD03': ["HCC'03", 'Description 03', 0.133],
            'COD04': ['HCC 04', 'Description 04', 0.124],
        }
        count = 0
        for code, hcc, label, raf in tested.parse_csv(False):
            self.assertIn(code, expected)
            self.assertEqual(expected[code][0], hcc)
            self.assertEqual(expected[code][1], label)
            self.assertEqual(expected[code][2], raf)
            count = count + 1
        self.assertEqual(len(expected), count)

    def test_run(self):
        file_from = f'{settings.BASE_DIR}/tests/value_set/hcc_sample.tsv'
        file_to = tempfile.NamedTemporaryFile()
        tested = BuildHccValueSet(file_from, file_to.name)

        tested.run()
        result = open(file_to.name, 'r').read()
        today = format(datetime.date.today().strftime('%y-%m-%d'))
        expected = open(f'{settings.BASE_DIR}/tests/value_set/hcc_file.txt',
                        'r').read().replace('18-10-08', today)

        self.assertEqual(f'{expected}\n', result)
