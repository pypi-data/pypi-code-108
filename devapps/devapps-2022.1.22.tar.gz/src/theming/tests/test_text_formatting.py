# coding: utf-8
import unittest

# from ax.utils.parsing.parse_text import *
from collections import OrderedDict

from theming import unicode_chars as unic
from theming.pretty_print import *

PY2 = sys.version_info[0] < 3
LS = '\n'


def unspace(s):
    return s.strip().replace(' ', '').replace('\t', '')


def clean(s):
    return unspace(s).replace('\n', '')


class TestUnicode(unittest.TestCase):
    def test_unisplit(self):

        # cannot make an incomplete bytearray witout using b which crashes
        # the python2 compiler. The function is anyway only really needed in2
        if not PY2:
            return 'skipped'
        s = '① ② ③ ④ ⑤ ⑥ ⑦ ⑧ ⑨ ⑩'
        b = unic.bytes_(s) + '\x01'
        res, b1 = unic.split_off_incompl(b)
        assert type(res) == type(unic.unic(''))
        assert b1 == ''

        b = unic.bytes_(s) + '\xe2\x91'
        res, b1 = unic.split_off_incompl(b)

        assert type(res) == type(unic.unic(''))
        assert unic.unic(res) == unic.unic(s)
        assert b1 == unic.bytes_('\xe2\x91')

    def test_str_split(self):

        # cannot make an incomplete bytearray witout using b which crashes
        # the python2 compiler. The function is anyway only really needed in2
        if not PY2:
            return 'skipped'
        s = '① ② ③ ④ ⑤ ⑥ ⑦ ⑧ ⑨ ⑩'

        b = unic.bytes_(s) + '\xe2\x91'
        with self.assertRaises(Exception):
            u = unic.unic(b)
        eq = self.assertEqual
        for i in 0, 1, 2, 10, 100:

            res = unic.read_uni_chars_off_str(b, i)

            orig = unic.unic(s)
            orig_pre = orig[:i]
            orig_native = unic.native(orig_pre)
            eq(res, orig_native)
            assert type(res) == type('')


class TextFormatting(unittest.TestCase):
    def setUp(self):
        self.eq = self.assertEqual
        self.deq = self.assertDictEqual

        address = OrderedDict()
        address['bytes'] = 1.1
        address['city'] = 'anycity'
        address['on'] = True
        address['postal'] = 1234
        address['street'] = 'some road'

        data = OrderedDict()
        data['address'] = address
        data['id'] = [1, 'someid']
        data['title'] = 'home'

        self.z = {'data': data}

    def test_simple(s):
        z = {}
        ax = dict_to_txt(z, fmt={'ax': 1})
        assert type(ax) == str and not ax

    def test_list(s):
        z = ['axtest']
        ax = dict_to_txt(z, fmt={'ax': 1})
        assert ax == 'axtest\n-\n'

    def test_simple2(s):
        z = 'axtest'
        ax = dict_to_txt(z, fmt={'ax': 1})
        assert ax == 'axtest\n'

    def test_tuple(s):
        t = [1, [2, 3, 4], 3]
        assert obj_to_html_list(t) == (
            '\n<ul>\n<li>1</li>\n<li>\n<ul>\n<li>2</li>\n<li>3</li>'
            '\n<li>4</li>\n</ul>\n</li>\n<li>3</li>\n</ul>\n'
        )

    def test_map1(s):
        ax = dict_to_txt(s.z, fmt={'ax': 1})
        assert unspace(ax) == unspace(
            '''
data:
    address:
        bytes:  1.1
        city:   anycity
        on: True
        postal: 1234
        street: some road
    id:
        1
        someid
    title:  home
'''
        )

    def test_html(s):
        """ s.z =
{'data': {'address': {'bytes': 1.1,
                      'city': 'anycity',
                      'on': True,
                      'postal': 1234,
                      'street': 'some road'},
          'id': [1, 'someid'],
          'title': 'home'}}
        """
        assert clean(obj_to_html_list(s.z)) == clean(
            '''
<ul>
    <li>data:</li>
        <ul>
            <li>address:</li>
            <ul>
                <li>bytes: 1.1</li>
                <li>city: anycity</li>
                <li>on: True</li>
                <li>postal: 1234</li>
                <li>street: some road</li>
            </ul>
            <li>id:</li>
            <ul>
                <li>1</li>
                <li>someid</li>
            </ul>
            <li>title: home</li>
        </ul>
</ul>
'''
        )

    def test_plain(s):
        assert unspace(dict_to_txt(s.z)) == unspace(
            '''
data:
  address:
    bytes:1.1
    city:anycity
    on:True
    postal:1234
    street:some road
  id:
    1
    someid
  title:home
'''
        )
        s.assertNotIn(dict_to_txt(s.z), '\t')

    def test_plain_ax(s):
        ax = dict_to_txt(s.z, fmt={'ax': 1})
        assert unspace(ax) == unspace(
            '''
data:
    address:
        bytes:  1.1
        city:   anycity
        on: True
        postal: 1234
        street: some road
    id:
        1
        someid
    title:  home
'''
        )
        assert len(ax.split('\t')) == 27

    def test_tuple1(s):
        t = [1, [2, 3, 4], 3]
        assert (
            dict_to_txt(t, fmt={'ax': 1}).strip()
            == '''
1
-
2
3
4
-
3
'''.strip()
        )

    def test_wiki(s):
        p = dict_to_txt(s.z, fmt={'wiki': 1})
        assert (
            p.strip()
            == '''
 || data ||  ||
 ||  ||  || address ||  ||
 ||  ||  ||  || bytes || 1.1 ||
 ||  ||  || city || anycity ||
 ||  ||  || on || True ||
 ||  ||  || postal || 1234 ||
 ||  ||  || street || some road ||
 ||  || id ||  ||
 ||  ||  || 1 ||
 ||  ||  || someid ||
 ||  || title || home ||
'''.strip()
        )

    def test_html2(s):
        html = dict_to_txt(s.z, fmt={'html': 1})
        assert clean(html) == clean(
            '''
<table >
  <tr ><td >data</td><td ></td><td colspan="100" ></td></tr>
  <tr ><td ></td><td>
      <table >
        <tr ><td >address</td><td ></td><td colspan="100" ></td></tr>
        <tr ><td ></td><td>
            <table >
              <tr ><td >bytes</td><td >1.1</td><td colspan="100" ></td></tr>
              <tr ><td >city</td><td >anycity</td><td colspan="100" ></td></tr>
              <tr ><td >on</td><td >True</td><td colspan="100" ></td></tr>
              <tr ><td >postal</td><td >1234</td><td colspan="100" ></td></tr>
              <tr ><td >street</td><td >some road</td><td colspan="100" ></td></tr>
            </table>
            </td><td colspan="100" ></td></tr>
        <tr ><td >id</td><td ></td><td colspan="100" ></td></tr>
</td><td>
            <table >
              <tr ><td >1</td><td colspan="100" ></td></tr>
              <tr ><td >someid</td><td colspan="100" ></td></tr>
            </table>
            </td><td colspan="100" ></td></tr>
        <tr ><td >title</td><td >home</td><td colspan="100" ></td></tr>
      </table>
      </td><td colspan="100" ></td></tr>
</table>
'''
        )

    def test_html2_style(s):
        html = dict_to_txt(s.z, fmt={'html': 1, 'styles': {}})
        assert clean(html).startswith(
            clean(
                '''
<table class="table0">
  <tr class="tr0"><td class="td10">data</td><td class="td20"></td><td colspan="100" class="td30"></td></tr>
  <tr class="tr0"><td class="td10"></td><td>
      <table class="table1">
        <tr class="tr1"><td class="td11">address</td><td class="td21"></td><td colspan="100" class="td31"></td></tr>
        <tr class="tr1"><td class="td11"></td><td>
            <table class="table2">
'''
            )
        )

    def test_html_style(s):
        m = {'1': '2', 'sub': {1: '2', 2: 3}}
        html = dict_to_txt(m, fmt={'html': 1, 'styles': {'td': 'report3'}})
        assert clean(html) == clean(
            '''
<table class="table0">
  <tr class="tr0"><td class="report3">1</td><td class="report3">2</td><td colspan="100" class="report3"></td></tr>
  <tr class="tr0"><td class="report3">sub</td><td class="report3"></td><td colspan="100" class="report3"></td></tr>
  <tr class="tr0"><td class="report3"></td><td>
      <table class="table1">
        <tr class="tr1"><td class="report3">1</td><td class="report3">2</td><td colspan="100" class="report3"></td></tr>
        <tr class="tr1"><td class="report3">2</td><td class="report3">3</td><td colspan="100" class="report3"></td></tr>
      </table>
      </td><td colspan="100" class="report3"></td></tr>
</table>
'''
        )

    def test_mix(s):
        p2 = dict_to_txt([{2: [3, 3]}, {'sdf': 'asdfas'}], fmt={'ax': 1})
        assert p2 == '2:\t\n\t3\n\t3\n-\nsdf:\tasdfas\n'

    def test_tuple2(s):
        m = ['foo', ['foo', 'bar']]
        assert (
            dict_to_txt(m, fmt={'ax': 1}).strip()
            == '''
foo
-
foo
bar
    '''.strip()
        )

    def test_dict5(s):

        m = {
            'Operations': [
                {
                    'URL': 'http://your.url.com',
                    'Username': '',
                    'Password': '',
                    'UUID': '',
                    'ExecutionEnvRef': '',
                },
                {
                    'URL': 'http://your.url.com',
                    'Username': '',
                    'Password': '',
                    'Version': '',
                    'UUID': '',
                },
                {'Version': '', 'UUID': '', 'ExecutionEnvRef    ': ''},
            ],
            'CommandKey': '',
        }
        pretty = dict_to_txt(m, fmt={'ax': 1})
        assert (
            pretty
            == 'CommandKey:\t\nOperations:\t\n\tExecutionEnvRef:\t\n\tPassword:\t\n\tURL:\thttp://your.url.com\n\tUUID:\t\n\tUsername:\t\n\t-\n\tPassword:\t\n\tURL:\thttp://your.url.com\n\tUUID:\t\n\tUsername:\t\n\tVersion:\t\n\t-\n\tExecutionEnvRef    :\t\n\tUUID:\t\n\tVersion:\t\n'
        )


if __name__ == '__main__':
    unittest.main()
