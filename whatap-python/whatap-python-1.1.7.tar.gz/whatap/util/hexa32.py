class Hexa32(object):
    PLUS = 'x'
    MINUS = 'z'
    min = "z8000000000000"
    
    @classmethod
    def toString32(cls, num):
        minus = num < 0
        if minus:
            if num == cls.MINUS:
                return cls.min
            return cls.MINUS + encode(-num)
        else:
            if num < 10:
                return encode(num)
            else:
                return cls.PLUS + encode(num)
    
    @classmethod
    def toLong32(cls, str):
        if not str or not len(str):
            return 0
        
        first_str = str[0]
        if first_str == cls.MINUS:
            return -1 * decode(str[1:])
        elif first_str == cls.PLUS:
            return decode(str[1:])
        else:
            return decode(str)


CHARS = "0123456789abcdefghijklmnopqrstuvwxyz"


def encode(num):
    encoded_chars = []
    while num > 0:
        remainder = num % 32
        num //= 32
        encoded_chars.append(CHARS[remainder])
    return ''.join(encoded_chars[::-1])


def decode(string):
    num = 0
    for power, char in enumerate(string[::-1]):
        try:
            val = CHARS.index(char)
        except ValueError:
            raise ValueError('invalid character: %s' % char)
        num += 32 ** power * val
    return num


if __name__=='__main__':

    n=-7329592890664812990
    s = 'z6bdvhspq4s0du'


    print(Hexa32.toString32(n))
    print(Hexa32.toLong32(s))
    
    print(s==Hexa32.toString32(n))
    print(n == Hexa32.toLong32(s))
