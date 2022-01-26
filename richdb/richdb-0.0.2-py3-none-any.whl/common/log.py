#-*- coding=utf-8 -*-
from datetime import datetime
def log(file, info):
    data = '\n'.join( [str(datetime.now())+':'+i for i in info.split()] )
    with open(file, 'a+') as f :
        f.writelines(data)


if __name__ == '__main__':
    log("c:/home/db.log", "abc\nbcd\ncde\ndef")