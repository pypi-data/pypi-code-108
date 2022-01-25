import os.path as _path
import os
import base64 as _base64
import math as _math
import array as _array
import tarfile as _tarfile
import sys
from pathlib import Path
try:
    import rsa as _rsa
except:
    pass
import time
__version__='1.2.3'
__author__='Blacksong'


def rsa_md5(data):  
    n='52'*32
    e = '1005'
    def modpow(b, e, m):  
        result = 1
        while (e > 0):
            if e & 1:
                result = (result * b) % m
            e = e >> 1
            b = (b * b) % m
        return result
    def bytes_to_int(bytes_):   
        n = 0
        for i in bytes_:
            n = n << 8
            n += i
        return n
    result = modpow(bytes_to_int(data), int(e, 16), int(n, 16))
    return int(result).to_bytes(32,'big')

def _data_type():
    x=_array.array('L')
    if x.itemsize==8:return 'L'
    else:return 'Q'
_array_type=_data_type()
def _bytes8(b,m=8):
    n=m-len(b)%m
    b+=(chr(n)*n).encode()
    return b
def _compress_tarfile(dirname,outfile=None):
    '''make a direct to a tar.gz file'''
    ss=time.clock()
    dirname=_path.normpath(dirname)
    if outfile is None:
        outfile = dirname + '.tar.gz'
    tar=_tarfile.open(outfile,'w:gz',compresslevel=9)
    dr=_path.dirname(dirname)+os.sep
    for r,d,fs in os.walk(dirname):
        for f in fs:
            af=r+os.sep+f
            print('compress ',f)
            tar.add(af,af.replace(dr,''))
    tar.close()
    print(time.clock()-ss)
    return outfile
def _extarct_tarfile(filename,target_path=None):
    '''make a direct to a tar.gz file'''
    if target_path is None:target_path=_path.dirname(_path.abspath(filename))
    tar=_tarfile.open(filename,'r:gz')
    for f in tar.getnames():
        tar.extract(f,target_path)
        print('extract ',target_path+os.sep+f)
    tar.close()

def _getkey(passwd):
    if passwd is None:passwd=b'SGZ'
    if isinstance(passwd,str):passwd=passwd.encode()
    key=rsa_md5(passwd)[:32]
    s=[key[i]*key[8+i]*key[16+i]*key[24+i]+(i*37) for i in range(8)]
    return s
def _enpt(x,key,order=None):
    n1,n2,n3,a,b,c,d,m=key
    if order!=None:n1,n2,n3=order
    for i in range(len(x)):
        n1,n2,n3=n2,n3,(a*n1+b*n2+c*n3+d)%m
        x[i]=(x[i]+n3)%0xffffffffffffffff
    return n1,n2,n3
def encrypt(parameter,output=None,passwd=None):
    if passwd is None:
        passwd = '11'*16
    if _path.isdir(parameter):
        istar = True
        parameter=_compress_tarfile(parameter)
    else:
        istar=False
    key0=_getkey(passwd)
    if output==None:
        output=parameter+'.yxs'
    size=_path.getsize(parameter)
    filename=_path.split(parameter)[1]
    size_name=len(filename.encode())
    size_bu=8-(size+size_name+3)%8
    b=bytearray(3+size_bu)
    b[0]=size_bu
    b[1]=size_name//256
    b[2]=size_name%256
    b+=filename.encode()
    data=open(parameter,'rb')
    length=8*1024*1024
    b+=data.read(length-size_bu-size_name-3)
    order0=key0[:3]
    fp=open(output,'wb')
    size0=0
    while True:
        x=_array.array(_array_type)
        x.frombytes(b)
        order0=_enpt(x,key=key0,order=order0)
        fp.write(x.tobytes())
        b=data.read(length)
        if not b:break
        size0+=length
        sys.stdout.write('\b\b\b\b\b\b\b\b\b\b{:.2f}'.format(size0/size))
    fp.close()
    data.close()
    if istar:os.remove(parameter)
def _deph(x,key,order=None):
    n1,n2,n3,a,b,c,d,m=key
    if order!=None:n1,n2,n3=order
    for i in range(len(x)):
        n1,n2,n3=n2,n3,(a*n1+b*n2+c*n3+d)%m
        x[i]=(x[i]-n3)%0xffffffffffffffff
    return n1,n2,n3

def decipher(parameter,output=None,passwd=None):
    if passwd is None:
        passwd = '11'*16
    key0=_getkey(passwd)
    data=open(parameter,'rb')
    size=_path.getsize(parameter)
    length=8*1024*1024
    b=data.read(8*1024)
    x=_array.array(_array_type)
    x.frombytes(b)
    order0=key0[:3]
    order0=_deph(x,key=key0,order=order0)
    b=x.tobytes()
    size_bu=b[0]
    size_name=b[1]*256+b[2]
    o_name=b[3+size_bu:3+size_bu+size_name].decode('utf8')
    if output is None:
        output=o_name
    fp=open(output,'wb')
    fp.write(b[3+size_bu+size_name:])
    size0=8*1024-3-size_bu-size_name
    while True:
        b=data.read(length)
        if not b:break
        size0+=length
        sys.stdout.write('\b\b\b\b\b\b\b\b\b\b{:.2f}'.format(size0/size))
        x=_array.array(_array_type)
        x.frombytes(b)
        order0=_deph(x,key=key0,order=order0)
        fp.write(x.tobytes())
    fp.close()
    if o_name[-7:]=='.tar.gz':
        target_path=_path.dirname(_path.abspath(parameter))
        _extarct_tarfile(output,target_path=target_path)
        os.remove(output)
def encode(b,passwd):
    key0=_getkey(passwd)
    x=_array.array(_array_type)
    x.frombytes(_bytes8(b))
    _enpt(x,key=key0)
    return x.tobytes()
def decode(b,passwd):
    key0=_getkey(passwd)
    x=_array.array(_array_type)
    x.frombytes(b)
    _deph(x,key=key0)
    b=x.tobytes()
    return b[:-b[-1]]
def b64encode(b,passwd=None):
    return _base64.b64encode(encode(b,passwd))
def b64decode(b,passwd=None):
    return decode(_base64.b64decode(b),passwd)
def spencode(b,passwd=None,str_set=b''):
    if not b:return b
    if len(str_set)<2:
        str_set=list(range(ord('A'),ord('A')+26))+list(range(ord('a'),ord('a')+26))+list(range(ord('0'),ord('0')+10))
    if passwd is None:b=_bytes8(b)
    else:b=encode(b,passwd)
    str_set=bytearray(str_set)
    nb,ns=len(b),len(str_set)
    x=_array.array(_array_type)
    w=_math.ceil(x.itemsize*_math.log(256)/_math.log(ns))
    x.frombytes(b)
    y=bytearray(len(x)*w)
    t=0
    for i in x:
        for j in range(w-1,-1,-1):
            y[t+j]=str_set[i%ns]
            i=i//ns
        t+=w
    return y
def spdecode(b,passwd=None,str_set=b''):
    if not b:return b
    if len(str_set)<2:
        str_set=list(range(ord('A'),ord('A')+26))+list(range(ord('a'),ord('a')+26))+list(range(ord('0'),ord('0')+10))
    str_set=bytearray(str_set)
    t_set=bytearray(256)
    for i,j in enumerate(str_set):
        t_set[j]=i
    nb,ns=len(b),len(str_set)
    x=_array.array(_array_type,[0])
    w=_math.ceil(x.itemsize*_math.log(256)/_math.log(ns))
    b=bytearray(b)
    x*=nb//w
    t=0
    for i in range(nb//w):
        s=0
        for j in range(t,t+w):
            s=s*ns+t_set[b[j]]
        t+=w
        x[i]=s
    b=x.tobytes()
    if passwd is None:b=b[:-b[-1]]
    else:b=decode(b,passwd)
    return b
def newkeys(n):#产生rsa秘钥
    return _rsa.newkeys(n)
def rsaencode(b,public):
    length = (len(bin(public.n))-2)//8-11
    crypt_list = [_rsa.encrypt(b[i-length:i],public) for i in range(length,len(b)+1,length)]
    leaved = len(b) % length
    if leaved>0:
        crypt_list.append(_rsa.encrypt(b[-leaved:],public))
    return b''.join(crypt_list)
def rsadecode(b,private):
    length = (len(bin(private.n))-2)//8
    assert len(b) % length == 0
    decrypt_list = [_rsa.decrypt(b[i-length:i],private) for i in range(length,len(b)+1,length)]
    return b''.join(decrypt_list)
def parse_commands(args):
    d = dict()
    i = 0
    while True:
        if i>=len(args):
            break
        if args[i].startswith('--'):
            d[args[i][2:]] = True 
            i+=1
        elif args[i].startswith('-'):
            d[args[i][1:]] = args[i+1]
            i += 2
        else:
            d[args[i]] = True
            i += 1
    return d
def run_git(args):
    def get_files():
        files = os.popen('git ls-files').read()
        return files.split()
    # passwd = args['p']
    if args.get('push') is not None:
        files = get_files()
        print(files)
def main(args = None):
    if args is None:
        args = sys.argv[1:]
    d = parse_commands(args)
    if d.get('e') is not None:
        print('encrypt')
        encrypt(d.get('e'),d.get('o'),d.get('p'))
    elif d.get('d') is not None:
        print('decipher')
        decipher(d.get('d'),d.get('o'),d.get('p'))
    elif d.get('git') is not None:
        run_git(d)
def get_default_passwd(saved_passwd = []):
    if len(saved_passwd) > 0:
        return saved_passwd[0]
    yxsdir = Path.home() / '.yxspkg'
    if not yxsdir.exists():
        os.makedirs(yxsdir)
    passwd_file = yxsdir / 'encrypt_passwd'
    if passwd_file.is_file():
        passwd = open(passwd_file).read().strip()
    else:
        passwd = 'abcdefgh'
        open(passwd_file,'w').write(passwd)
    saved_passwd.append(passwd)
    return passwd
if __name__=='__main__':
    main()