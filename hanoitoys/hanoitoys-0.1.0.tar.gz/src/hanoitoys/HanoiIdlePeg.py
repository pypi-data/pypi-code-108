#! Python
'''
HanoiIdlePeg.py  Tower of Hanoi Non Recursive Solution.
    Using an algorithm called the Idle Peg algorithm

    This algorithm numbers the needles 0, 1, 2

    Classical Hanoi 3-peg n discs

    my variation - smallest disc is numbered 0.

    We use PegName make the output of this
    identical to our other Hanoi programs
'''

PegName = "ABC"


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
        print(f"{mn}: Move Disc {k} from {PegName[i]} to {PegName[j]}")
    else:
        states[j] &= ~topj  # take disc from top of peg j
        states[i] |= topj   # and place it on peg i
        k = topj.bit_length() - 1
        print(f"{mn}: Move Disc {k} from {PegName[j]} to {PegName[i]}")


def DoIdlePeg (n, i, j):
    global states
    states = [0] * 3
    nMoves = 2 ** n - 1  # number of moves and also a bitmask of all discs.
    states[i] = nMoves
    idle = i
    d = ((-1) ** n) * (j - i)  # <-- This does work for me
    mn = 0
    while states[j] != nMoves:
        mn += 1
        idle = (idle + d) % 3
        # make legal move between pegs which do not include idle peg
        DoMove(mn, (idle + 1) % 3, (idle - 1) % 3)


if __name__ == '__main__':
    while True:
        n = int(input("\nHow many discs (0 to halt):"))
        if n == 0:
            break
        DoIdlePeg(n, 0, 2)
