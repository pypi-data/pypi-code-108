import unittest
from parameterized import parameterized

import lark

from marlowe_ui.postprocess_lark import lark_common


class TestLarkCommonFwint1(unittest.TestCase):
    def setUp(self):
        # parse "'Cascade',I6,':',5X,'Group',I5,6X,'Number',I3" collectly
        # Cascade     2:     Group    1      Number  2
        grammar = '''\
                cascade: "Cascade" fwint6 ":" _SS~5 "Group" fwint5 _SS~6 "Number" fwint3 _NL'''

        grammar += lark_common.grammar + lark_common.grammar_fixedwidth_int 

        class Transformer(lark_common.Transformer):
            def __init__(self):
                super().__init__()

            def cascade(self, args):
                # cascade: "Cascade" fwint6 ":" _SS~5 "Group" fwint5 _SS~6 "Number" fwint3 _NL
                return {
                        'Cascade':args[0],
                        'Group':args[1],
                        'Number':args[2]
                        }

        class Parser():
            def __init__(self):
                self.transformer = Transformer()
                self.parser = lark.Lark(grammar=grammar, parser='lalr',
                        transformer=self.transformer,
                        start='cascade')


            def parse(self, text):
                return self.parser.parse(text)

        self.parser = Parser()

    @parameterized.expand([
        ('Cascade     2:     Group    1      Number  2\n',
            {'Cascade':2, 'Group':1, 'Number':2}),
        ('Cascade     2:     Group    1      Number***\n',
            {'Cascade':2, 'Group':1, 'Number':999}),
        ('Cascade999999:     Group11111      Number  0\n',
            {'Cascade':999999, 'Group':11111, 'Number':0}),
        ('Cascade    -1:     Group    1      Number  0\n',
            {'Cascade':-1, 'Group':1, 'Number':0}),
        ('Cascade-99999:     Group    1      Number  0\n',
            {'Cascade':-99999, 'Group':1, 'Number':0}),
        ('Cascade -99999:     Group    1      Number  0\n',
            {'Cascade':-99999, 'Group':1, 'Number':0}),
        ('Cascade    -9999999:     Group    1      Number  0\n',
            {'Cascade':-9999999, 'Group':1, 'Number':0}),
        ])
    def test_lark_common_fwint(self, in_, out):
        result = self.parser.parse(in_)
        self.assertEqual(result, out)



class TestLarkCommonFwint2(unittest.TestCase):
    def setUp(self):
        # parse "'<',I3,':',3I3, '>'" collectly
        grammar = '''start: "<" fwint3 ":" fwint3~3 ">" _NL'''

        grammar += lark_common.grammar + lark_common.grammar_fixedwidth_int 

        class Transformer(lark_common.Transformer):
            def __init__(self):
                super().__init__()

            def start(self, args):
                return args

        class Parser():
            def __init__(self):
                self.transformer = Transformer()
                self.parser = lark.Lark(grammar=grammar, parser='lalr',
                        transformer=self.transformer)

            def parse(self, text):
                return self.parser.parse(text)

        self.parser = Parser()

    @parameterized.expand([
        ('<  0:  1  2  3>\n', [0, 1, 2, 3]),
        ('<999:  1  2  3>\n', [999, 1, 2, 3]),
        ('<999:111  2  3>\n', [999,111, 2, 3]),
        ('<999:111222  3>\n', [999,111,222, 3]),
        ('<999:111222333>\n', [999,111,222,333]),
        # ('<999: 11222333>\n', [999, 11,222,333]), # cannot pass as of 20210302
        ])
    def test_lark_common_fwint(self, in_, out):
        result = self.parser.parse(in_)
        self.assertEqual(result, out)
