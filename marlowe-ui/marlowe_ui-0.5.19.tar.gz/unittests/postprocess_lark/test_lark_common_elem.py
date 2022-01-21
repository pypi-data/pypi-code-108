import unittest
from parameterized import parameterized
from marlowe_ui.physics import element

import lark

from marlowe_ui.postprocess_lark import lark_common


grammar = '''start: ELEM (_S ELEM)* _NL'''
grammar += lark_common.grammar + lark_common.grammar_elem 

class Transformer(lark_common.Transformer):
    def __init__(self):
        super().__init__()

    def start(self, args):
        return [a.value for a in args]
                

class Parser():
    def __init__(self):
        self.transformer = Transformer()
        self.parser = lark.Lark(grammar=grammar, parser='lalr',
                transformer=self.transformer,
                start='start')

    def parse(self, text):
        return self.parser.parse(text)

class TestLarkCommonElem1(unittest.TestCase):
    def setUp(self):
        self.parser = Parser()

    @parameterized.expand([
        ('I Ir\n', ['I', 'Ir']),
        ('Ir I\n', ['Ir',  'I'])])
    def test_lark_common_elem1(self, in_, out):
        result = self.parser.parse(in_)
        self.assertEqual(result, out)

    def test_lark_common_elem2(self):
        list_of_symbols = [a.sym for a in element.table_bynum[1:]]
        in_ = ' '.join(list_of_symbols) + '\n'

        result = self.parser.parse(in_)

        self.assertEqual(list_of_symbols, result)

