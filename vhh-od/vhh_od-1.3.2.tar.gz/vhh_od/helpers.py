import os

def mkdir_if_necessary(dir):
    if not os.path.isdir(dir):
            os.makedirs(dir)
    return dir