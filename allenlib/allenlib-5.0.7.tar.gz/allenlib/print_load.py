import os
import time
def progess_bar(title,rangenum):
    ii=0
    iii=0
    for i in range(int(rangenum-1)):
        print(str(title)+str(':| '),end='')
        temp=100/rangenum
        ii=temp+ii
        iii=iii+1
        for ia in range(iii):
            print('█',end='')
        print(' |',end='')
        strii=str(ii)
        print(str(' eta ')+strii+str('%'))
        time.sleep(0.1)
        os.system('clear')
    print(str(title)+str(':| '),end='')
    temp=100/rangenum
    ii=100
    iii=iii+1
    for ia in range(iii):
        print('█',end='')
    print(' |',end='')
    strii=str(ii)
    print(str(' eta ')+strii+str('%'))
    time.sleep(0.1)
    ii=0
    iii=0
def progess_bar_win(title,rangenum):
    ii=0
    iii=0
    for i in range(int(rangenum-1)):
        print(str(title)+str(':| '),end='')
        temp=100/rangenum
        ii=temp+ii
        iii=iii+1
        for ia in range(iii):
            print('█',end='')
        print(' |',end='')
        strii=str(ii)
        print(str(' eta ')+strii+str('%'))
        time.sleep(0.1)
        os.system('cls')
    print(str(title)+str(':| '),end='')
    temp=100/rangenum
    ii=100
    iii=iii+1
    for ia in range(iii):
        print('█',end='')
    print(' |',end='')
    strii=str(ii)
    print(str(' eta ')+strii+str('%'))
    time.sleep(0.1)
    ii=0
    iii=0
if (__name__=='__main__'):
    progess_bar_win('title',30)
    print('done!')