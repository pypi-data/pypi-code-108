#!/usr/bin/env python3


from flashcam.version import __version__
from fire import Fire
from flashcam import config
import os

import mmap
import time

MMAPFILE = os.path.expanduser("~/.config/flashcam/mmapfile")


# -------------------------------------------------------------------------

def mmcreate(filename=MMAPFILE):
    with open(filename, "w") as f:
        f.write("-"*100)


def mmwrite(text, filename = MMAPFILE):
    """
    write text to filename
    """
    if not os.path.exists(filename):
        mmcreate(filename)
    with open(filename, mode="r+", encoding="utf8") as file_obj:
        with mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_WRITE, offset=0) as mmap_obj:
            #print(" WRITING: ",text)
            mmap_obj.write(str(text).encode("utf8") )  # 2ms
            mmap_obj.flush()





# -------------------------------------------------------------------------

def mmread(filename = MMAPFILE):
    with open(filename, mode="r", encoding="utf8") as file_obj:
        with mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_READ) as mmap_obj:
            text = mmap_obj.read()
            print("READTEXT =",text)

def mmread_n_clear(  filename = MMAPFILE ):
    """
    read and clear  filename
    """
    if not os.path.exists(filename):
        return  "xxxxxx","1"
    with open(filename, mode="r+", encoding="utf8") as file_obj:
        with mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_WRITE, offset=0) as mmap_obj:
            text = mmap_obj.read().decode("utf8")
            # print("READTEXT: ",text)


            # execute(text.decode("utf8"))
            if text[0] == "*":
                response = "xxxxxx","1"
            else:
                response = text.split("*")[0]
                response = f"{response.split()[0].strip()}",f"{response.split()[1].strip()}"
                print("i... returning ", response)
                print("i... returning ", response)
                print("i... returning ", response)

            text = "*"*50
            # print("CLEARING: ",text)
            mmap_obj[:len(text)] = str(text).encode("utf8")
            mmap_obj.flush()
            return response
# -------------------------------------------------------------------------

if __name__ == "__main__":
    Fire()
    print("... sleeping 2")
    time.sleep(2)
