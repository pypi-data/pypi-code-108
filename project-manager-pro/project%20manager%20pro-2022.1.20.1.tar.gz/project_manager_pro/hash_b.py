def hash_b(word, base):

    h = 0
    b = 101

    if len(word):
        h = (10 + ord(word[0])) % base

        for i in range(1, len(word)):
            h += (ord(word[i]) * (b**i)) % base

    if h % base < 10:
        h = h % base + 10

    return h % base


def hash_4(word):
    return hash_b(word=word, base=10000)
