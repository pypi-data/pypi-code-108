def shashi(s:str, length=128) -> int:
    ret=0
    mask=(1<<length)-1
    for ch in s.encode('utf-8'):
        ret^=int(ch)
        ret<<=13
        ret=(ret&mask)^(ret>>length)
    return ret
def hashi(x, length=128) -> int:
    if(isinstance(x,str)):
        return shashi(x, length=length)
    else:
        return NotImplemented
def base32(x,length=8):
    ch='0123456789abcdefghijklmnopqrstuvwxyz'
    if(not isinstance(x,int)):
        x = hashi(x, length=length*5)
    blength=length*5
    mask=(1<<blength)-1
    while(x>>blength):
        x = (x>>blength)^(x&mask)
    ret=[]
    for i in range(length):
        ret.append(ch[x & 31])
        x>>=5
    return "".join(ret[::-1])