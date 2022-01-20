from jcutil.chalk import *


def test_chalk_init():
    red = Chalk('hello', Color.RED)
    assert len(red.__chains__) > 0
    print(red)
    assert len(red) > 0
    green = GreenChalk('oh, it is a ').use(FontFormat.BOLD).text('green').end(EndFlag.B_END).text(' chalk.')
    print(repr(green))
    print(green)
    merge = red + green
    print(repr(merge))
    print(merge)


def test_add():
    red = RedChalk('hello')
    r = red + ' world'
    assert isinstance(r, str), 'return a star when add a str'
    assert r == '\033[31mhello\033[0m world'
    print(r)
    r = red + GreenChalk('|Mo')
    assert str(r) == '\033[31mhello\033[0m\033[32m|Mo\033[0m'
    print(r)

def test_mod():
    red = RedChalk('hello %s')
    print(red)
    r = red % 'world'
    assert r == '\033[31mhello world\033[0m'
    print(r)
    print(red % 111)


def test_wrapper():
    red = RedChalk('[wappered]')
    r = GreenChalk(f'a {red} b')
    print(repr(r))
    print(r)
    br = YellowChalk().bold('bold string')
    print(repr(br), br)
