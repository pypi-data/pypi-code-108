from os import path
import random
import os
from . import myhash
pth = path.join(path.expanduser("~"), "meowMemo")


def ensure_dir(pth):
    if(not path.exists(path.dirname(pth))):
        os.makedirs(path.dirname(pth))


def get_temp_file(ext='.in'):
    filename = myhash.base32(random.randrange(1 << 40), length=8)
    return path.join(pth, 'temp', filename+ext)


if(__name__ == '__main__'):   # unit test
    print(get_temp_file())

    print(get_temp_file())
