from simplestr.simplestr import gen_str, gen_repr, gen_eq, gen_str_repr, gen_str_repr_eq

@gen_str
@gen_repr
@gen_eq
class Rect:
    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


@gen_str_repr
class Text:
    def __init__(self, id: int, text: str):
        self.id = id
        self.text = text


def test_str():
    rect1 = Rect(1, 2, 3, 4)
    rect2 = Rect(10, 20, 30, 40)
    print(rect1)
    print(rect2)


def test_repr():
    rect1 = Rect(1, 2, 3, 4)
    rect2 = Rect(10, 20, 30, 40)
    print([rect1, rect2])


def test_eq():
    a1 = Rect(1, 2, 3, 4)
    a2 = Rect(1, 2, 3, 4)
    b1 = Rect(10, 20, 30, 40)
    b2 = Rect(10, 20, 30, 40)

    assert a1 == a1
    assert a1 == a2
    assert a2 == a1
    assert a2 == a2
    assert Rect(1, 2, 3, 4) == a1
    assert Rect(1, 2, 3, 4) == a2
    assert a1 == Rect(1, 2, 3, 4)
    assert a2 == Rect(1, 2, 3, 4)

    assert b1 == b1
    assert b1 == b2
    assert b2 == b1
    assert b2 == b2
    assert Rect(10, 20, 30, 40) == b1
    assert Rect(10, 20, 30, 40) == b2
    assert b1 == Rect(10, 20, 30, 40)
    assert b2 == Rect(10, 20, 30, 40)

    assert a1 != b1
    assert a1 != b2
    assert a2 != b1
    assert a2 != b2

    assert 121878712 != a1
    assert a1 != 121878712
    assert 'some text' != a1
    assert a1 != 'some text'


def test_eq_in():
    a1 = Rect(1, 2, 3, 4)
    a2 = Rect(1, 2, 3, 4)
    b1 = Rect(10, 20, 30, 40)
    b2 = Rect(10, 20, 30, 40)

    list = [a1, b1]

    assert a1 in list
    assert b1 in list
    assert a2 in list
    assert b2 in list
    assert Rect(1, 2, 3, 4) in list
    assert Rect(10, 20, 30, 40) in list
    assert Rect(11, 21, 31, 41) not in list


def test_str_repr():
    a1 = Text(1, 'Sample text 1')
    a2 = Text(2, 'Sample text 2')
    print(a1)
    print(a2)
    print([a1, a2])


test_str()
test_repr()
test_eq()
test_eq_in()
test_str_repr()