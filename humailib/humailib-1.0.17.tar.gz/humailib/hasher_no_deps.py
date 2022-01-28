import binascii

class XORHasher:
    
    def __init__(self, key='12345678901234567892123456789312'):
        self.key = bytes(key, 'utf-8')
        self.n = len(self.key)
        
    def encryptInt(self, value):
        res = self.__encrdecr( bytearray(str(value).encode("utf-8")) )
        return binascii.hexlify( res ).decode('utf-8')
    
    def encryptStr(self, string):
        res = self.__encrdecr( bytearray(string, 'utf-8') )
        return binascii.hexlify( res ).decode('utf-8')
    
    def decrypt(self, hexstring):
        if len(hexstring) % 2 == 1:
            return ''
        seq = binascii.unhexlify(bytearray(hexstring, 'utf-8'))
        return self.__encrdecr( bytearray(seq) ).decode('utf-8')
    
    def __encrdecr(self, sequence):
        i = 0
        for c in sequence:
            sequence[i] = sequence[i] ^ self.key[i % self.n]
            i = 1 + i
            
        return sequence

def decrypt_columns(df, columns=[]):
    
    hh = XORHasher('SB-Humai-Fernet-Key-ABCDEFGHIJKL')
    
    for c in columns:
        df.loc[:,c] = df[c].astype(str, skipna=True)
        df.loc[:,c].fillna('', inplace=True)
        df.loc[:,c] = df[c].apply(lambda x: hh.decrypt(x)) 

def encrypt_columns(df, columns=[]):
    
    hh = XORHasher('SB-Humai-Fernet-Key-ABCDEFGHIJKL')
    
    for c in columns:
        df.loc[:,c] = df[c].astype(str, skipna=True)
        df.loc[:,c].fillna('', inplace=True)
        df.loc[:,c] = df[c].astype(str).apply(lambda x: hh.encryptStr(x))   
