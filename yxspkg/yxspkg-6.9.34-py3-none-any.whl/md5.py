import hashlib,sys
from pathlib import Path
def main(filenames = None):
    '''计算文件的md5值，并输出'''
    if filenames is None:
        filenames = sys.argv[1:]
    for filename in filenames:
        fp = open(filename,'rb')
        md5 = hashlib.md5()
        while True:
            t = fp.read(1024*1024*4)
            if t == b'':
                break
            md5.update(t)
        print(Path(filename).name,md5.hexdigest())
if __name__=='__main__':
    main()