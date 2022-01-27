#! Python
'''
HanoiOlive.py  Tower of Hanoi Non Recursive Solution.
    Using an algorithm called Olives algorithm

    This algorithm numbers the needles 0, 1, 2

    Classical Hanoi
    my version the smallest disc is numbered 0.
'''

Discnames = "ABC"


def DoMove (mn, i, j):
    # one bit for each disc. bitno is disc number.
    # Determine which direction is legal.
    topi = (states[i] & -states[i])   # isolate smallest disc top of peg i
    topj = (states[j] & -states[j])   # isolate smallest disc top of peg j
    # needle2 empty or (needle1 not empty and smaller disc than needle2).
    if states[j] == 0 or (states[i] != 0 and topi < topj):
        states[i] &= ~topi  # take disc from top of peg i
        states[j] |= topi   # and place it on peg j
        k = topi.bit_length() - 1
        print(f"{mn}: Move Disc {k} from {Discnames[i]} to {Discnames[j]}")
    else:
        states[j] &= ~topj  # take disc from top of peg j
        states[i] |= topj   # and place it on peg i
        k = topj.bit_length() - 1
        print(f"{mn}: Move Disc {k} from {Discnames[j]} to {Discnames[i]}")


def pegof (n: int):
    b = 1 << n
    for i in range(3):
        if states[i] & b != 0:
            return i
    assert False, "this can't be"


def DoOlive (n, i, j):
    global states
    states = [0] * 3
    nMoves = 2 ** n - 1
    states[i] = nMoves
    if n == 0 or i == j:
        print(f"Bad parameters n={n}, i={i}, j={j}")
        return
    if n & 1 == 1:      # when odd number of discs, i to j
        DoMove(1, i, j)
        d = -1
    else:
        x = 3 - i - j
        DoMove(1, i, x)  # even, i to not j not i
        d = 1
    mn = 1
    while states[j] != nMoves:
        mn += 1
        # legal move of peg other than the top peg
        loc_top = pegof(0)
        a = (loc_top + 1) % 3
        b = (loc_top - 1) % 3
        DoMove(mn, a, b)
        # move top peg in a cyclical manner
        mn += 1
        DoMove(mn, loc_top, (loc_top + d) % 3)


if __name__ == '__main__':
    while True:
        n = int(input("\nHow many discs (0 to halt):"))
        if n == 0:
            break
        DoOlive(n, 0, 2)
