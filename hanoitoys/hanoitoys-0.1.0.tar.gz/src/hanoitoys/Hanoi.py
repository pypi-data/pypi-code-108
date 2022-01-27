#! Python
'''
Class to represent a Hanoi Tower puzzle. The solving of
Classic Hanoi and Hanoi on steroids (number of needles > 3).
Moves to solve and number of moves calculator est (memoized)

Usage:
    Hanoi(start, set of storage, goal)
examples:
    a = Hanoi('A', OrderedSet(4,1)), 'F', 4)

    experiments have shown 1 << n is much faster than 2 ** n.
    So we use this with the intent pow(2, n)

This has been tested and is equivalent to the Frame-Stewart algorithm.
It was independently developed by self, prior to finding out there
was a Frame-Stewart algorithm.

Note: An earlier version of this used the standard type set
to keep track of available storage needles.
Keeping the available storage needles in a set is problematic
for comparing to Frame-Steward solutions.
A OrderedSet which only holds Natural Numbers defined ISO 80000-2
which includes zero.
'''

import functools    # need @lru_cache for this to work in a reasonable time.
import turtle as T  # Turtle graphics, each disc is a independent turtle.
from tkinter import messagebox

# Greek Letters
# Needles (pegs) labeled A-Z then a-z then alpha-omega

Greek = {'alpha' : '\u03B1', 'beta'    : '\u03B2', 'gamma'   : '\u03B3',
         'delta' : '\u03B4', 'epsilon' : '\u03B5', 'zeta'    : '\u03B6',
         'eta'   : '\u03B7', 'theta'   : '\u03B8', 'iota'    : '\u03B9',
         'kappa' : '\u03BA', 'lambda'  : '\u03BB', 'mu'      : '\u03BC',
         'nu'    : '\u03BD', 'xi'      : '\u03BE', 'omicron' : '\u03BF',
         'pi'    : '\u03C0', 'rho'     : '\u03C1', 'sigma'   : '\u03C2',
         'sigma2': '\u03C3', 'tau'     : '\u03C4', 'upsilon' : '\u03C5',
         'phi'   : '\u03C6', 'chi'     : '\u03C7', 'omega'   : '\u03C7'}

# name space


class Namespace ():
    '''A Namespace is a place to hide variables. The namespace may be global,
    but the contents of the Namespace are not global'''


G = Namespace()  # share data between graphic object and hanoi object


class OrderedSet ():
    '''
    This set only holds non-negative integers. In this case a Needle number.
    The storage for the set is a bit array (like ancient Pascal) stored in
    an int.

    constructor OrderedSet(a, b) sets bits a through b in a new ordered set.
    OrderedSet(a,a) bit with bit number a is set.
    OrderedSet(a,b) with a == b < 0 makes an empty set/
    '''
    def __init__ (self, a, b):
        if a == b < 0:
            self.bitarray = 0
            return
        if a == b:
            self.bitarray = 1 << a
            return
        a, b = sorted([a, b])
        self.bitarray = (1 << b) - (1 << a)

    '''
    os.copy() A shallow copy of the ordered set
    '''
    def copy (self):
        the_copy = OrderedSet(-1, -1)
        the_copy.bitarray = self.bitarray
        return the_copy

    '''
    os.isempty() A predicate returning that there are no elements in os
    '''
    def isempty (self):
        return self.bitarray == 0

    '''
    os.look() returns lowest bit sets number
    and does not modify the bit array
    '''
    def look (self):
        assert not self.isempty()
        k = self.bitarray
        k &= -k
        return k.bit_length() - 1

    '''
    os.pop() returns lowest bit sets number and
    clearing that bit in the bit array.
    '''
    def pop (self):
        assert not self.isempty()
        k = self.bitarray
        k = k & -k
        self.bitarray &= ~k
        return k.bit_length() - 1

    '''
    os.put(n) takes number n and puts it back in the os ordered set.
    '''
    def put (self, n):
        k = 1 << n
        self.bitarray |= k
        return self

    '''
    os.list() returns an ordered list of int s which are the needle
    numbers in os bitarray
    '''
    def list (self):
        x = self.copy()
        L = list()
        while not x.isempty():
            L.append(x.pop())
        return L

    '''
    __len__ another population count how many one bits set in bitarray
    alternatively we could keep track of length. I regard this as safer.
    even though slower.
    '''
    def __len__ (self):
        x = self.bitarray
        population_count = 0
        while x > 0:
            b = x & 0xffffffffffffffff
            x >>= 64
            b -= (b & 0xaaaaaaaaaaaaaaaa) >> 1
            b = ((b & 0xcccccccccccccccc) >> 2) + (b & 0x3333333333333333)
            b = ((b & 0xf0f0f0f0f0f0f0f0) >> 4) + (b & 0x0f0f0f0f0f0f0f0f)
            r = b * 0x0101010101010101
            population_count += (r >> 56) & 0xff
        return population_count


def YorN(question):
    '''
    The Yes or No predicate. Yorn asks a question. Gets a Response
    If the response is affirmate returns True.
    If the reaponse is negative return False.
    Otherwise an error message, list of responses and try again.
    '''
    affirmative = ['affirmative',  'afirmative', 'amen', 'assuredly', 'aye',
                   'certainly', 'definitely', 'exactly', 'fine', 'gladly',
                   'good', 'granted', 'hi', 'indubitably', 'naturally',
                   'okay', 'positively', 'precisely', 'si', 'sure', 'surely',
                   't', 'true', 'undoubtedly', 'unquestionably', 'willingly',
                   'y', 'yah', 'yea', 'yep', 'yes']
    negative =  ['n', 'nay', 'nix', 'never', 'not', 'negative', 'negatory',
                 'nein', 'no', 'noway']
    while True:
        response = input(question).lower().split()
        if response[0] in affirmative:
            return True
        if response[0] in negative:
            return False
        print("This is a yes or no question!")


@functools.lru_cache(maxsize=3000)
def est (NumDiscs: int, NumStore: int) -> tuple:
    '''
    This makes Hanoi on steroids possible. A recursive estimator,
    returns least number of moves and size of pile to get out of
    the way to make this possible.

    Note lru_cache makes this possible. Without that the computation time
    is excessive.

    Number of needles is NumStore + 2.

    idealy this should be a staticmethod of the Hanoi class. However lru_cache
    and static methods mixed together seem to have problems.
    a class method is inappropriate.
    a instance method might have self as part of the cache key, need to
    research this.

    An alternative implementation is not to use a list. Default running best
    to Classic Hanoi to start. And iterate as before. At each iteration, if
    it returns less than running best, then replace running best.
    Finally return running best.
    '''
    # returned tuple (num of moves, first move this many to storage needle
    # can use min on list of these tuples to get tuple to return.
    if NumStore == 1 or NumDiscs < 3:    # base case is classic Hanoi.
        return ((1 << NumDiscs) - 1, 1)  # 2 ** NumDiscs - 1; this is faster.
    possibilities = list()               # build a list of sub problems
    for n in range(1, NumDiscs):
        moves  = est(n, NumStore)[0] << 1           # n src->stor, n stor->dest
        moves += est(NumDiscs - n, NumStore - 1)[0]  # NumDiscs-n src->dest
        possibilities.append((moves, n))  # ok in list see if it is best later
    return min(possibilities)


def info ():
    ''' Show the lru cache information for est()
    Only of interest until cache size tuned.
    '''
    print(f'est.cache_info()={est.cache_info()}')


class Hanoi():

    def __init__ (self        : object,
                  source      : str,  # Discs on this  initially: is name
                  storage     : OrderedSet,  # use these as storage in solution
                  goal        : str,  # Final state all Discs on this needle
                  numberDiscs : int)  ->  object:  # how many discs
        G.storage         = storage.copy()
        G.source          = source
        G.dest            = goal
        G.doGraphics      = False
        G.actualNoofmoves = 0
        G.fast_move       = False
        # ListNeedles maps a Needle number 0 through numberNeedles-1
        #   the appropriate needle name
        G.ListNeedles = [source] + storage.list() + [goal]
        # Top most (smallest) Disc number 0
        # Bottom most (biggest) number numberDiscs - 1
        G.M = dict()    # This is a mapping from needle name to needle number.
        for n, k in enumerate(G.ListNeedles):
            G.M[k] = n
        G.M[source] = 0
        G.towers = list()    # A mapping of needle numbers to Needle objects

    @staticmethod
    def MoveOneDisc (src, dest):
        ''' Perform the operations needed to move the top disc on
        needle named src to needle named dest. including graphics.
        and counting the number of moves.
        This is handles the Base case of a solve_helper()'''
        msrc     =  G.M[src]        # number of needle named by src
        mdest    =  G.M[dest]       # number of needle named by dest
        G.actualNoofmoves += 1      # we have and est. see if it is right.
        print(f'{G.actualNoofmoves}:Moving disc from {LP[src]} to {LP[dest]}')
        if not G.doGraphics:        # if no graphics we are done
            return
        #
        # From here on only needed for Graphics.
        #
        source = G.towers[msrc]     # object needle named by src
        target = G.towers[mdest]    # object needle names by dest
        x0, y0 = source.location    # base location of source needle
        disk = source.remove()      # grab hold of top disc on needle
        target.place(disk)          # place on top of of target needle
        # Now the geometry of moving.
        x1, y1 = target.location    # base location of the dest needle
        ny1 = target.top()[1]       # y component of top of target needle
        # Take disk up to the skyway channel at top free of obstructions.
        if not G.fast_move:
            disk.setposition(x0, y0 + G.skyway)  # up to the skyway
            if source.row != target.row:
                # More moves is a dest needle which is on a different row
                #      than source needle
                # Move disk to the right (the elevator channel)
                disk.setposition(G.elevator, y0 + G.skyway)
                # Move disk up/down to the skyway channel of the elevator
                disk.setposition(G.elevator, y1 + G.skyway)
            # Move disk to the left/right to x position of dest needle
            else:
                # move keeping height
                disk.setposition(x1, y0 + G.skyway)
            if x1 != G.elevator:
                disk.setposition(x1, y1 + G.skyway)
        # Move disk down to top of dest needle
        disk.setposition(x1, ny1)   # if G.fast_move this is it.

    @staticmethod
    def solve_helper (src, stor, dest, nstor, ndiscs):
        ''' the guts of the solution. move n discs to a temporary place,
        move ndiscs-n to  dest. Then move n discs from temporary place
        to dest. n determined by est(...)'''
        if ndiscs == 1:
            Hanoi.MoveOneDisc(src, dest)     # Base Case to stop recursion
            return
        # and another base case. reduce problem to classical.
        if nstor == 1:         # degenerate to regular Hanoi Have only 1 stor.
            where = stor.look()  # no loop just 1 element to worry about
            Hanoi.solve_helper(src,   OrderedSet(dest, dest),
                               where, 1, ndiscs - 1)
            Hanoi.MoveOneDisc(src, dest)
            Hanoi.solve_helper(where, OrderedSet(src, src),
                               dest,  1, ndiscs - 1)
            return

        # Not classic Hanoi, the Frame-Stewart algorithm
        st    = stor.copy()  # do not hurt stor it is a by reference argument
        first = est(ndiscs, nstor)[1]   # always guided by estimator
        last  = ndiscs - first          # size of other stack to move
        first_dest = st.pop()           # get one needle from stor set
        # from src using depleted stor w/dest as storage and final dest as goal
        Hanoi.solve_helper(src, st.copy().put(dest), first_dest, nstor, first)
        # from src using depleted stor as storage agoal is dest
        Hanoi.solve_helper(src, st.copy(),  dest,  nstor - 1, last)
        # from first_dest using depleted stor w/src as storage, dest as goal
        Hanoi.solve_helper(first_dest, st.copy().put(src), dest, nstor, first)

    def solve (self):
        '''
        The member function that does setup for the solution.
        and calls a recursive helper.
        '''
        if G.doGraphics:
            GraphicsSetup()
        G.actualNoofmoves = 0       # a good place to start a counter from.
        # here we separate what has to be recursive.
        self.solve_helper(G.source, G.storage, G.dest,
                          len(G.storage), G.NumberDiscs)
        k = est(G.NumberDiscs, len(G.storage))[0]
        assert G.actualNoofmoves == k, f'predict={k} took={G.actualNoofmoves}'


def redo ():
    '''
    The only thing main calls is redo(). This lets the user execute rerun()
    within an IDE for other test runs.
    '''
    global a, G, L, LP
    while(True):
        G.NumberNeedles = int(input('Enter Number of Needles : '))
        if G.NumberNeedles > 2:
            break
        print('Must have 3 or more Needles!')
    while(True):
        G.NumberDiscs = int(input('Enter Number of Discs : '))
        if G.NumberDiscs > 0:
            break
        print('Number of Discs must be greater than zero!')
    L  = list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz')
    LP = L[:]
    for GreekKey, GreekLetter in Greek.items():
        L.append(GreekLetter)
        LP.append(GreekKey)
    src = 0
    dst = G.NumberNeedles - 1
    storage = OrderedSet(1, G.NumberNeedles - 1)
    a = Hanoi(src, storage, dst, G.NumberDiscs)
    G.doGraphics = YorN('Do you want a graphical representation?')
    if G.doGraphics:
        if G.NumberNeedles == 3:
            G.NumberCols = 2
        else:
            while(True):
                G.NumberCols = int(input("How many Columns : "))
                if G.NumberCols > 1:
                    break
                print("Number of Cols must be greater than one")
        G.fast_move = YorN("Do you want a faster move of discs?")

        T.setup(width=1.0, height=1.0, startx=None, starty=None)
        GraphicsPreSetUp()
    a.solve()
    if G.doGraphics:
        messagebox.showinfo("Done", "Press Ok")
        T.bye()

#
# The following is a Turtle Graphics interface
# Turtle graphics will not be explained at this
# time. Turtle Graphics is a Volume 2 topic.
#


class Needle (list):
    "object of class Needle are Hanoi objects to place Discs On"""
    def __init__ (self, number, label, location, row):
        # empty Needle
        self.number   = number      # What is this needles number.
        self.label    = label       # What is this needles name.
        self.location = location    # Where on the Canvas is this needle at.
        self.row      = row         # Which row is needle on.

    def top (self) -> list:
        x, y = self.location
        return [x, y + (len(self) - 1) * G.discthick]

    def place (self, disk):
        self.append(disk)   # push to end of list self

    def remove (self):
        disk = self.pop()   # pop from end of list self
        return disk


class Disc (T.Turtle):
    ''' makings of a disc '''
    def __init__ (self, n):
        # Actual shape is usually a rectangle a resize stretches square.
        T.Turtle.__init__(self, shape='square', visible=False)
        self.penup()
        self.resizemode('user')
        self.shapesize(G.discthick / 20,
                       ((n + 1) / G.NumberDiscs) * G.discwidth / 20)
        colors = ['red', 'orange', 'yellow',
                  'green', 'blue', 'indigo', 'violet']
        el = len(colors)
        self.fillcolor(colors[n % el])
        self.showturtle()


def GraphicsPreSetUp ():
    # don't you just hate it when the setup has a setup
    G.textsize = 20
    G.Nrows = (G.NumberNeedles + G.NumberCols - 2) // G.NumberCols
    t = T.Turtle()
    screen      = t.getscreen()
    G.screenx   = screen.window_width() - 40
    G.screeny   = screen.window_height() - 80
#    G.screenx   = screen.window_width() - 20
#    G.screeny   = screen.window_height() - 40
    xsize = G.screenx // (G.NumberCols + 1)
    ysize = (G.screeny // G.Nrows) // G.NumberDiscs
    G.discwidth = xsize
    G.discthick = min(20, ysize)    # no less than 20, otherwise ysize
    G.skyway = G.discthick * G.NumberDiscs  # skyway: height where discs fly
    del t


def GraphicsSetup ():

    # Needles only need to be drawn once. before we start the solution.
    def DrawNeedle (t, needle, x, y):
        ytop = y + G.NumberDiscs * G.discthick
        t.setposition(x, ytop)
        t.pendown()
        t.setposition(x, y)
        t.penup()
        t.setposition(x - 20, y)
        t.pendown()
        t.setposition(x + 20, y)
        t.penup()
        t.write(needle.label, move=False, align='center',
                font=("Arial", 8, "normal"))

    T.clearscreen()
    t = T.Turtle()
    T.title("Hanoi on steroids.")
    G.height = G.screeny // G.Nrows
    startx = -(G.screenx - G.discwidth) // 2
    starty = -(G.screeny) // 2 + 33
    # elevator is where discs can go up or down
    G.elevator = startx + G.discwidth * G.NumberCols
    for i, needleno in enumerate(G.ListNeedles):
        x = startx + G.discwidth  * (i % G.NumberCols)
        y = starty + G.height * (i // G.NumberCols)
        needle = Needle(i, L[needleno], [x, y], i // G.NumberCols)
        G.towers.append(needle)
        t.hideturtle()
        t.penup()
        if i == len(G.ListNeedles) - 1:
            x, y = G.elevator, starty
            needle.row = 0
        else:
            x, y = needle.location
        DrawNeedle(t, needle, x, y)
        needle.location = [x, y]
    x0, y0 = G.towers[0].location
    for i in range(G.NumberDiscs, 0, -1):
        j = i - 1
        disc = Disc(j)
        disc.penup()
        disc.hideturtle()
        disc.setposition(x0, y0)
        disc.showturtle()
        G.towers[0].place(disc)
        y0 += G.discthick
    messagebox.showinfo("To Start", "Press Ok")
    del t   # t is turtle used to draw needles.

# main


redo()
