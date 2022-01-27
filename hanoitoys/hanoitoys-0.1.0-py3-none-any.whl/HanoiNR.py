#! Python
'''
HanoiNR.py  Tower of Hanoi Non Recursive Solution.

    Classical Hanoi
    Uses move number modulus three to determine Move.
    smallest disc is numbered 0.
'''


def DoMove (i, states, label1, label2):
    # one bit for each disc. bitno is disc number.
    # Determine which direction is legal.
    # states comes in as a tuple and are returned as a tuple.
    state1, state2 = states
    top1 = (state1 & -state1)   # isolate smallest disc top of needle1
    top2 = (state2 & -state2)   # isolate smallest disc top of needle2
    # needle2 empty or (needle1 not empty and smaller disc than needle2).
    if top2 == 0 or (top1 != 0 and top1 < top2):
        state1 &= ~top1  # take disc from top of needle1
        state2 |= top1   # and place it on needle2
        k = top1.bit_length() - 1
        print(f'{i}: Move Disc {k} from {label1} to {label2}')
    else:
        state2 &= ~top2  # take disc from top of needle2
        state1 |= top2   # and place it on needle1
        k = top2.bit_length() - 1
        print(f'{i}: Move Disc {k} from {label2} to {label1}')
    return (state1, state2)  # modified state of two needles


def DoHanoi (n, source, store, destination):
    nMoves = 2 ** n - 1
    if n & 1 == 0:      # when even number of discs relabel needles
        store, destination = destination, store
    #  Source, Temp (not Store), Dest
    #   This algorithm only determines which two needles involved
    #   in next move. Of two possible moves only one is valid.
    S, T, D = nMoves, 0, 0
    action = 0
    for i in range(nMoves):
        action = (action + 1) % 3
        if action == 1:
            S, D = DoMove(i, (S, D), source, destination)
        elif action == 2:
            S, T = DoMove(i, (S, T), source, store)
        elif action == 0:
            T, D = DoMove(i, (T, D), store, destination)
        else:
            assert False


if __name__ == '__main__':
    while True:
        n = int(input("\nHow many discs (0 to halt):"))
        if n == 0:
            break
        DoHanoi(n, 'Source', 'Store', 'Destination')
