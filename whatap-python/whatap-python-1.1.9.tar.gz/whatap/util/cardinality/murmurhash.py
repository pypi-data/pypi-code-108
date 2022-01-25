class MurMurHash(object):
    @classmethod
    def hash(cls, data):
        m = 0x5bd1e995
        r = 24
        h = 0
        k = (data * m) & 0xffffffff
        k ^= (k % 0x100000000) >> r
        h ^= (k * m) & 0xffffffff
        
        k = ((data >> 32) * m) & 0xffffffff
        k ^= (k % 0x100000000) >> r
        h *= m
        h ^= k * m
        
        h ^= (h % 0x100000000) >> 13
        h *= m
        h ^= (h % 0x100000000) >> 15
        
        return h
