

def rshift(val, n):
    """Zero-fill right shift bit-wise operator

    Equivalent of >>> in javascript

    Args:
        val ([type]): [description]
        n ([type]): [description]

    Returns:
        [type]: [description]
    """
    return (val % 0x100000000) >> n

class JSF32(object):
    """Pure-python implementation of JSF32

    Takes 1.22 ms

    Usage:
        gen = JSF32(4058668781, 0, 0, 0) ## aka 0xF1EA5EED
        print(gen.next())
        print(gen.next())
    """
    def __init__(self, a,b,c,d):
        self.a =a
        self.b = b
        self.c = c
        self.d = d

    def next(self):
        self.a = self.a | 0
        self.b = self.b |  0
        self.c = self.c |  0
        self.d = self.d |  0
        t = self.a - (self.b << 27 | rshift(self.b,5) ) | 0
        self.a = self.b ^ (self.c << 17 | rshift(self.c,15) )
        self.b = self.c + self.d | 0
        self.c = self.d + t | 0
        self.d = self.a + t | 0
        return rshift(self.d, 0) / 4294967296
