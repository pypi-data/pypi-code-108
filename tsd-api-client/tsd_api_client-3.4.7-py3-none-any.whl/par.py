
from multiprocessing import Process

def no(arg):
    print('I started!')
    time.sleep(2)
    print(arg)

def fun(arg):
    p = Process(target=no, args=(arg,))
    p.start()
    return p

def main():
    p = fun('leon')
    print('line')
    p.join()

