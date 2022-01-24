import unittest

from nehushtan.cli.NehushtanArgumentParser import NehushtanArgumentParser


class TestForArgumentParser(unittest.TestCase):

    def test_for_parse(self):
        parser = NehushtanArgumentParser(['-a', 'aa', '--dd', 'ee', '--gg-hh', 'ii', '-i', '--jj', '--k-ll']) \
            .add_option('A', 'Option A', short='a') \
            .add_option('D', 'Option D', long='dd') \
            .add_option('G', 'Option G', prefix='gg') \
            .add_option('I', 'Flag I', short='i', is_flag=True) \
            .add_option('J', 'Flag J', long='jj', is_flag=True) \
            .add_option('K', 'Flag K', prefix='k', is_flag=True) \
            .add_option('L', 'Flag L', short='l', is_flag=True) \
            .parse()

        print(parser.get_usage_text())
        print(parser.get_raw_option_dict())

        parsed = parser.get_parsed_option_dict()
        expected = {'A': 'aa', 'D': 'ee', 'G': {'hh': 'ii'}, 'I': True, 'J': True, 'K': {"ll": True}}
        self.assertEqual(expected, parsed)

    def test_for_later_parse(self):
        try:
            NehushtanArgumentParser() \
                .add_option('A', 'arg A', short='a') \
                .add_option('D', 'arg D', short='a', long='dd') \
                .add_option('G', 'arg G', prefix='gg') \
                .set_arg_list(['-a', 'aa', '--dd', 'ee', '--gg-hh', 'ii', 'j', 'k']) \
                .parse()
        except RuntimeError as e:
            self.assertEqual('Short Key [-a] Already Existed', e.__str__())
        else:
            self.fail('Did not seek out the duplicated key')
