#! Python
'''
HanoiClassical.py  Classical Tower of Hanoi Recursive Solution.

    Classical Hanoi
    Base condition n = 1. Just move the disc from source to dest.
    n > 1
    move n-1 from source to store using dest for storage.
    move 1 from source to dest, no store needed.
    move n-1 from store to dest using source for storage.
    smallest disc is numbered 0.
'''


def DoHanoi (n, level, source, store, dest):
    global nmove
    if n == 1:
        print(f'{nmove}:Move Disc {totn - level - 1} from {source} to {dest}')
        nmove += 1
        return
    DoHanoi(n - 1, level + 1, source, dest,   store)
    DoHanoi(1,     level,     source, store,  dest)
    DoHanoi(n - 1, level + 1, store,  source, dest)


def Go ():
    global totn, nmove
    while True:
        n = int(input("\nHow many discs (0 to halt):"))
        if n == 0:
            break
        nmove = 0
        totn = n
        DoHanoi(n, 0, 'Source', 'Store', 'Destination')

if __name__ == '__main__':
    Go()

