import unittest
import pandas as pd
import warnings
from bwgds.berryworld.xml_parser import XMLparser

warnings.filterwarnings('ignore')


class TestXMLParser(unittest.TestCase):
    """ Testing the implemented classes """

    def test_xml_parser(self):
        dict_df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6], 'col3': [7, 8, 9]})
        xml_sample = XMLparser(dict_df).xml
        xml_res = '<?xml version="1.0" encoding="UTF-8"?>\n<report>\n<records>\n  <col1>1</col1>\n  <col2>4</col2>\n ' \
                  ' <col3>7</col3>\n</records>\n<records>\n  <col1>2</col1>\n  <col2>5</col2>\n  <col3>8</col3>\n' \
                  '</records>\n<records>\n  <col1>3</col1>\n  <col2>6</col2>\n  <col3>9</col3>\n</records>\n</report>'
        self.assertEqual(xml_sample, xml_res)


if __name__ == '__main__':
    TestXMLParser().test_xml_parser()
