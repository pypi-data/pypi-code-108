# coding:utf-8
import re

from .inflect import (
    camelize,
    dasherize,
    humanize,
    ordinal,
    ordinalize,
    parameterize,
    pluralize,
    singularize,
    titleize,
    transliterate,
    underscore,
)


def convert_keys(m, to=None, recurse=1, in_place=0):
    """ The main function to be used.
    Converts the structure m to intended key format
    The conversion is NOT done inplace, new structures are returned

    in_place: We replace the keys of the given structure

    to: None -> we return available converters
        (custom_callable, 'camel') -> call the custom one, then to camel
        'snake, title' -> convert to snake, then titlelize


    in_place: 0 -> new structure returned, type type of old
              1 -> replacement of keys
              2 -> adding of converted keys
    """
    # no conversion of simple types, these are normally values and not structs
    # with keys:
    if isinstance(m, (basestring, bool, int, float)):
        return m
    if not to:
        return CONVERTERS.keys()
    if isinstance(to, basestring):
        to = to.split(',')
    for _to in to:
        if isinstance(_to, basestring):
            _to = _to.strip()
            if not _to:
                continue
            converter = CONVERTERS[_to]
        else:
            # converter is given as callable:
            converter = _to
        m = _convert_keys(m, converter, recurse, in_place)
    return m


def _convert_keys(m, converter, recurse, in_place):
    if isinstance(m, tuple):
        # in place makes no sense here but we rather don't except but return a
        # new one
        l = ()
        for k in m:
            if isinstance(k, dict):
                l += (
                    _convert_keys(
                        k, recurse=recurse, converter=converter, in_place=in_place
                    ),
                )
            else:
                l += (k,)
        return l

    if isinstance(m, list):
        if not in_place:
            l = type(m)()
            l.extend(m)
        else:
            l = m
        for i in xrange(len(l)):
            k = l[i]
            if isinstance(k, dict):
                l[i] = _convert_keys(
                    k, recurse=recurse, converter=converter, in_place=in_place
                )
        return l

    if isinstance(m, dict):
        if not in_place:
            n = type(m)()
        else:
            n = m
        for k, v in m.items():
            if recurse and isinstance(v, (list, tuple, dict)):
                v = _convert_keys(v, recurse=1, converter=converter, in_place=in_place)
            if in_place == 1:
                m.pop(k)
            k = converter(k)
            n[k] = v
        return n
    else:
        # string, int?
        return converter(m)


def camel_1(string):
    """ this does numbers seperated, Foo12Bar -> foo_12_bar """
    string = string.replace(' ', '')
    string = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    string = re.sub('(.)([0-9]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', string).lower()


def camel(string, uc=False):
    if not isinstance(string, basestring):
        return string
    string = string.replace(' ', '_')
    # underscore first to prevent 'HTTPAuthPassword -> hTTPAuthPassword:
    return camelize(underscore(string), uppercase_first_letter=uc)


def upper_camel(string):
    return camel(string, uc=True)


def ordinal(nr):
    if not isinstance(nr, int):
        return nr
    return ordinalize(nr)


def snake(string):
    if not isinstance(string, basestring):
        return string
    string = string.replace(' ', '_')
    return underscore(string)


def title(string):
    if not isinstance(string, basestring):
        return string
    return titleize(string)


def plural(string):
    if not isinstance(string, basestring):
        return string
    return pluralize(string)


def ascii(string):
    if not isinstance(string, basestring):
        return string
    return str(transliterate(unicode(string)))


def snake_plural(string):
    return plural(snake(string))


def singular(string):
    if not isinstance(string, basestring):
        return string
    return singularize(string)


def param_dash(string, d='-'):
    if not isinstance(string, basestring):
        return string
    return str(parameterize(unicode(string), d))


def param_under(string):
    return param_dash(string, d='_')


def param_space(string):
    return param_dash(string, d=' ')


def human(string):
    if not isinstance(string, basestring):
        return string
    # want fooBar -> Foo bar
    return humanize(snake(string))


def dash(string):
    if not isinstance(string, basestring):
        return string
    return dasherize(snake(string))


# ----------------------------------------- All funcs below compat with old API:
def camel_to_snake(name):
    return camel_1(name)


under_pat = re.compile(r'_([a-z])')


def snake_to_camel(name):
    return under_pat.sub(lambda x: x.group(1).upper(), name)


def convert(s, remove_spaces=1):
    a = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
    res = a.sub(r'_\1', s).lower()
    # keys like 'Foo Bar' -> foo_bar
    if remove_spaces:
        res = res.replace(' ', '')
    return res


def convertSnake(j):
    """ this is convert FROM snake to json(camel) """
    out = {}
    for k in j:
        new_k = k.split('_')
        out[new_k[0] + ''.join(x.title() for x in new_k[1:])] = j[k]
    return out


def convertJSON(j, remove_spaces=1):
    """ this is convert FROM JSON to snake """
    out = {}
    for k in j:
        newK = convert(k, remove_spaces)
        if isinstance(j[k], dict):
            out[newK] = convertJSON(j[k], remove_spaces)
        elif isinstance(j[k], list):
            out[newK] = convertArray(j[k], remove_spaces)
        else:
            out[newK] = j[k]
    return out


def convertArray(a, remove_spaces=1):
    newArr = []
    for i in a:
        if isinstance(i, list):
            newArr.append(convertArray(i))
        elif isinstance(i, dict):
            newArr.append(convertJSON(i))
        else:
            newArr.append(i)
    return newArr


l = list(globals())
CONVERTERS = {}
for k in l:
    if (
        k.startswith('convert')
        or k.startswith('_')
        or '_to_' in k
        or k.startswith('re')
        or k.endswith('ize')
    ):
        continue
    CONVERTERS[k] = globals()[k]

if __name__ == '__main__':
    print(convert_keys(''))

    def custom_conv(s):
        return 'Aaa'

    m = {'fooBar': 1}
    n = convert_keys(m, (custom_conv, 'snake'))
    assert n == {'aaa': 1}

    n = convert_keys(m, 'camel')
    # not in place, so:
    m[1] = 2
    assert m != n

    m = {'FooBar': 1}
    n = convert_keys(m, 'camel', in_place=1)
    assert len(n) == 1
    m[1] = 2
    assert n == m

    m = {'FooBar': 1}
    n = convert_keys(m, 'camel', in_place=2)
    assert len(n) == 2
    m[1] = 2
    assert n == m

    l = convert_keys([1, 2, m], 'snake')
    assert l == [1, 2, {1: 2, 'foo_bar': 1}]
    assert l[2] != m

    l1 = convert_keys([1, 2, m], 'snake', in_place=1)
    assert l1[2] == m
    assert l1 == l

    m = {'foo_bar': {'FooBar': 23, 23: 23}}

    n = convert_keys(m, 'camel')
    assert n == {'fooBar': {23: 23, 'fooBar': 23}}

    n = convert_keys(m, 'camel', recurse=0)
    assert n == {'fooBar': {23: 23, 'FooBar': 23}}

    n = convert_keys(m, 'ordinal')
    assert n == {'foo_bar': {'23rd': 23, 'FooBar': 23}}

    n = convert_keys(m, 'camel, ordinal')
    assert n == {'fooBar': {'23rd': 23, 'fooBar': 23}}

    n = convert_keys(m, 'upper_camel')
    assert n == {'FooBar': {23: 23, 'FooBar': 23}}

    n = convert_keys(m, 'title')
    assert n == {'Foo Bar': {23: 23, 'Foo Bar': 23}}

    n = convert_keys(m, 'plural')
    assert n == {'foo_bars': {23: 23, 'FooBars': 23}}

    n = convert_keys(m, 'plural')
    assert n == {'foo_bars': {23: 23, 'FooBars': 23}}

    n = convert_keys(m, 'snake_plural')
    assert n == {'foo_bars': {'foo_bars': 23, 23: 23}}
    assert plural('category') == 'categories'

    pl = convert_keys(m, 'plural')
    n = convert_keys(pl, 'singular')
    assert n == m

    u = {'Donald E. Knuth': {'!foo': 23}}
    assert convert_keys(u, 'param_dash') == {'donald-e-knuth': {'foo': 23}}

    u = {'Donald E. Knuth': {'!foo': 23}}
    assert convert_keys(u, 'param_under') == {'donald_e_knuth': {'foo': 23}}

    u = {'Donald E. Knuth': {'!foo': 23}}
    assert convert_keys(u, 'param_space') == {'donald e knuth': {'foo': 23}}

    n = convert_keys(m, 'human')
    assert n == {'Foo bar': {23: 23, 'Foo bar': 23}}

    n = convert_keys(m, 'dash')
    assert n == {'foo-bar': {23: 23, 'foo-bar': 23}}

    u = {'älämölö': {'Ærøskøbing': 23, 2: 23}}
    assert convert_keys(u, 'ascii') == {'alamolo': {2: 23, 'rskbing': 23}}

    test_cases = list()
    test_cases.append(('camelCase', 'camel_case'))
    test_cases.append(('camelCaseCase', 'camel_case_case'))
    test_cases.append(('camel2Case', 'camel_2_case'))
    test_cases.append(('camel12Case', 'camel_12_case'))
    test_cases.append(('camel12Case', 'camel_12_case'))
    test_cases.append(('camelCaseURL', 'camel_case_url'))
    test_cases.append(('camel2CaseURL', 'camel_2_case_url'))
    test_cases.append(('camel12CaseURL', 'camel_12_case_url'))
    test_cases.append(('camel12Case2URL', 'camel_12_case_2_url'))
    test_cases.append(('camel12Case12URL', 'camel_12_case_12_url'))
    test_cases.append(('CamelCase', 'camel_case'))
    test_cases.append(('CamelCaseCase', 'camel_case_case'))
    test_cases.append(('URL CamelCase', 'url_camel_case'))
    test_cases.append(('Spaced URL Casea', 'spaced_url_casea'))
    for string, res in test_cases:
        print(string + ' -> ' + camel_1(string))
        try:
            assert camel_1(string) == res
        except Exception as ex:
            import pdb

            pdb.set_trace()

    assert camel_to_snake('asdf') == 'asdf'
    assert camel_to_snake('asdfAsBs') == 'asdf_as_bs'
    assert camel_to_snake('AsdfAsBs') == 'asdf_as_bs'
    assert camel_to_snake('fooBar') == 'foo_bar'
    assert snake_to_camel('foo_bar') == 'fooBar'

    m = {
        'someObject': [
            {'anotherObject': 'CamelCaseValue'},
            {'anotherObject': 'AnotherCamelCaseValue'},
        ]
    }
    assert convertJSON(m) == {
        'some_object': [
            {'another_object': 'CamelCaseValue'},
            {'another_object': 'AnotherCamelCaseValue'},
        ]
    }
