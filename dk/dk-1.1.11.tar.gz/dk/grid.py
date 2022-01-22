"""A 2D grid with slicing.

   Usage::

       >>> t = grid(emptyval=0)
       >>> t.apply[:5,:5] = lambda v, (y,x):y*x
       >>> t
        0 0 0  0  0
        0 1 2  3  4
        0 2 4  6  8
        0 3 6  9 12
        0 4 8 12 16
       >>> t.apply[:5,:5] = lambda v, p:v*2
       >>> t
        0 0  0  0  0
        0 2  4  6  8
        0 4  8 12 16
        0 6 12 18 24
        0 8 16 24 32
       >>> t2 = grid.copy(t, lambda orig, (y,x):orig[y,x] / 2)
       >>> t2
        0 0 0  0  0
        0 1 2  3  4
        0 2 4  6  8
        0 3 6  9 12
        0 4 8 12 16

"""
# pylint: disable=R0903,W0141,E1102,W0201
# R0903: Too few public methods
# W0141: Used builtin map
# E1102: grid.copy_area t is not callable (t is derived from __sub__)
# W0201: attribute defined outside __init__ (descriptors).
from builtins import str
from types import MethodType
from . import proxy
newmethod = lambda m, o, c: MethodType(m, o)  # noqa


def _direction(start, end):
    x = y = 1
    if start.x > end.x:
        x = -1
    if start.y > end.y:
        y = -1
    return y, x


try:
    cmp
except NameError:
    def cmp(a, b):
        return a - b


def point_xiter(start, end):
    y, x = _direction(start, end)
    _y, _x = start.y, start.x

    while 1:
        yield (_y, _x)
        _x += x
        if cmp(_x, end.x) == x:
            _x = start.x
            _y += y
            if cmp(_y, end.y) == y:
                break


def point_yiter(start, end):
    y, x = _direction(start, end)
    _y, _x = start.y, start.x

    while 1:
        yield (_y, _x)
        _y += y
        if cmp(_y, end.y) == y:
            _y = start.y
            _x += x
            if cmp(_x, end.x) == x:
                break


def indexiter(length, ndx):
    def _indxiter(length, ndx):
        if isinstance(ndx, slice):
            for x in range(*ndx.indices(length)):
                yield x
        elif isinstance(ndx, int):
            if ndx < 0:
                yield length + ndx
            else:
                yield ndx
        else:
            raise ValueError("illegal index key %s", ndx)

    ix = list(_indxiter(length, ndx))
    if ix:
        return ix, min(ix), max(ix)
    else:
        return [], 0, 0


class point(tuple):
    def __new__(cls, y=0, x=0):
        return super(point, cls).__new__(cls, (y, x))

    @property
    def y(self):
        return self[0]

    @property
    def x(self):
        return self[1]

    def __repr__(self):
        return 'point(%s,%s)' % (repr(self.y), repr(self.x))


class rect(object):
    def __init__(self, x, y, w, h):
        self.orig = point(y=y, x=x)
        self.w = w
        self.h = h

    def isomorphic(self, other):
        "Same shape?"
        return ((self.w == other.w) and (self.h == other.h) or
                (self.w == other.h) and (self.h == other.w))

    def __contains__(self, yx):
        y, x = yx
        return ((self.y <= y < self.y + self.h) and
                (self.x <= x < self.x + self.w))

    def __sub__(self, other):
        sx, sy = self.x, self.y
        ox, oy = other.x, other.y

        def transpose(yx):
            y, x = yx
            if self.w == other.w:
                return point(y + sy - oy, x + sx - ox)
            else:
                return point(x + sy - ox, y + sx - oy)

        return transpose

    def __repr__(self):
        return 'rect(x=%s, y=%s, w=%s, h=%s)' % (
            repr(self.x),
            repr(self.y),
            repr(self.w),
            repr(self.h))

    @property
    def x(self):
        return self.orig.x

    @property
    def y(self):
        return self.orig.y

    @property
    def x2(self):
        return self.x + self.w - 1

    @property
    def y2(self):
        return self.y + self.h - 1

    @property
    def NW(self):
        return point(self.y, self.x)

    @property
    def NE(self):
        return point(self.y, self.x2)

    @property
    def SW(self):
        return point(self.y2, self.x)

    @property
    def SE(self):
        return point(self.y2, self.x2)

    @property
    def corners(self):
        return [self.NW, self.NE, self.SW, self.SE]

    def opposite(self, corner):
        return {
            self.NW: self.SE,
            self.NE: self.SW,
            self.SW: self.NE,
            self.SE: self.NW
        }[corner]


class Deleted(object):
    def __repr__(self):
        return '<->'


Deleted = Deleted()


class Empty(proxy.proxy):
    def __init__(self, emptyval=None):
        super(Empty, self).__init__(emptyval)

    def setval(self, v):
        self._value = v

    def __repr__(self):
        return repr(self._value)


class value_iterator(object):
    def __init__(self, gridobj, ykey, xkey):
        self.g = gridobj
        self.yy, self.ymin, self.ymax = indexiter(self.g.y, ykey)
        self.xx, self.xmin, self.xmax = indexiter(self.g.x, xkey)
        self.direction = 'RD'
        self.g.resize(self.ymax, self.xmax)

    def __repr__(self):
        res = []
        a, b = self.ndx_base()
        for y in a:
            t = []
            for x in b:
                t.append(self.g._rows[y][x])
            res.append(t)
        return '\n'.join(map(str, res)) + str(self.rect())

    def ndx_base(self, direction='RD'):
        first, then = direction
        if first in 'LR':
            a = self.yy if then == 'D' else reversed(self.yy)
            b = self.xx if first == 'R' else reversed(self.xx)

        if first in 'UD':
            b = self.yy if first == 'D' else reversed(self.yy)
            a = self.xx if then == 'R' else reversed(self.xx)
        return a, b

    def indices(self, direction='RD'):
        a, b = self.ndx_base(direction)
        return [(y, x) for y in a for x in b]

    def iter(self, direction='RD'):
        ndx = self.indices(direction)
        for y, x in ndx:
            yield self.g._rows[y][x]

    def rect(self):
        i = self.indices()
        y, x = i[0]
        yy, xx = i[-1]
        w = xx - x + 1
        h = yy - y + 1
        return rect(x, y, w, h)

    def __iter__(self):
        return self.iter(self.direction)


class table_iterator(object):
    def __init__(self, iterfn):
        self.iterfn = iterfn
        self.iterator = None

    def __get__(self, instance, owner):
        if instance is None:
            raise AttributeError('keys is an instance method.')
        self.instance = instance
        self.iterator = newmethod(self.iterfn, instance, owner)
        return self

    def __iter__(self):
        return self.iterator((slice(None), slice(None)))

    def __getitem__(self, yx):
        ykey, xkey = yx
        if self.instance._ispoint(ykey, xkey):
            return self.instance.get_cell(ykey, xkey)
        else:
            return self.iterator((ykey, xkey))

    def __delitem__(self, key):
        for y, x in self.iterator(key):
            self.instance.del_cell(y, x)

    def __setitem__(self, yx, val):
        ykey, xkey = yx
        ndx = self.iterator((ykey, xkey))
        if self.instance._ispoint(ykey, xkey):
            y, x = ndx[0]
            return self.instance.set_cell(y, x, val)
        else:
            if not isinstance(val, str) and not isinstance(val, bytes):
                try:
                    it = iter(val)
                except TypeError:
                    pass
                else:
                    for (y, x), val in zip(ndx, it):
                        self.instance.set_cell(y, x, val)
                    return

            for y, x in ndx:
                self.instance.set_cell(y, x, val)


class grid(object):
    """
       This is a tabular object of two dimensions that supports slice
       notation.
    """
    Deleted = Deleted

    ####################################################################
    # constructors

    @classmethod
    def copy(cls, tgrid, fn=None):
        t = cls(emptyval=tgrid.empty._value)
        for k in tgrid.keys[:, :]:
            if fn is None:
                t[k] = tgrid[k]
            else:
                t[k] = fn(tgrid, k)
        return t

    def __init__(self, rows=0, cols=0, emptyval=None):
        self.empty = Empty(emptyval)
        self._rows = []  # y direction
        self.y = 0
        self.x = 0
        self.resize(max(0, rows - 1), max(0, cols - 1))

    ####################################################################
    def transpose(self):
        self._rows = zip(*self._rows)
        self.x, self.y = self.y, self.x
        return self

    ####################################################################
    # accessors

    @property
    def size(self):
        return self.y, self.x

    @property
    def width(self):
        return self.x

    @property
    def height(self):
        return self.y

    @property
    def lastcol(self):
        return self.x - 1

    @property
    def lastrow(self):
        return self.y - 1

    #
    # To add a column at the end:
    #
    # t[0, t.width] = 4
    #

    def get_cell(self, y, x):
        self.resize(y, x)
        return self._rows[y][x]

    def del_cell(self, y, x):
        self.resize(y, x)
        self._rows[y][x] = Deleted
        return self

    def set_cell(self, y, x, v):
        self.resize(y, x)
        self._rows[y][x] = v
        return self

    def apply_cell(self, y, x, fn):
        self.resize(y, x)
        self._rows[y][x] = fn(self._rows[y][x], (y, x))
        return self

    def get_row(self, y):
        self.resize(y, 0)
        return [v for v in self._rows[y] if v is not Deleted]

    def get_col(self, x):
        self.resize(0, x)
        return [r[x] for r in self._rows if r[x] is not Deleted]

    def empty_row(self, y):
        return all(v is self.empty for v in self.get_row(y))

    def empty_col(self, x):
        return all(v is self.empty for v in self.get_col(x))

    ####################################################################
    # mutation

    def copy_area(self, _src, _dst):
        srcy, srcx, h, w = _src
        dsty, dstx = _dst
        src = rect(y=srcy, x=srcx, w=w, h=h)
        dst = rect(y=dsty, x=dstx, w=w, h=h)
        t = dst - src
        corner = point(0, 0)

        for corner in src.corners:
            if corner in dst:
                break

        for p in point_xiter(corner, src.opposite(corner)):
            self[t(p)] = self[p]

    def move_area(self, _src, _dst):
        srcy, srcx, h, w = _src
        dsty, dstx = _dst

        src = rect(y=srcy, x=srcx, w=w, h=h)
        dst = rect(y=dsty, x=dstx, w=w, h=h)
        t = dst - src
        corner = point(0, 0)
        i = 0

        for corner in src.corners:
            if corner in dst:
                break

        for i, p in enumerate(point_xiter(corner, src.opposite(corner))):
            self[t(p)] = self[p]
            self[p] = self.empty

        return i

    def insert_row(self, ypos=None, count=1):
        if ypos is None:
            ypos = self.y
        if ypos >= self.y:
            self.resize(ypos + count - 1, 0)
        else:
            self.move_area((ypos, 0, self.y - ypos, self.x), (ypos + count, 0))
        return ypos

    def remove_row(self, ypos, count=1):
        i = 0
        if ypos < 1:
            ypos = self.y + ypos
        if ypos > self.y:
            return
        for i in range(count):
            try:
                del self._rows[ypos]
            except IndexError:
                break
        self.y -= i + 1

    def insert_col(self, xpos=None, count=1):
        if xpos is None:
            xpos = self.x
        if xpos >= self.x:
            self.resize(0, xpos + count - 1)
        else:
            self.move_area((0, xpos, self.y, self.x - xpos), (0, xpos + count))
        return xpos

    def remove_col(self, xpos, count=1):
        i = 0
        if xpos < 0:
            xpos = self.x + xpos
        if xpos > self.x:
            return
        for row in self._rows:
            for i in range(count):
                try:
                    del row[xpos]
                except IndexError:
                    break
        self.x -= i + 1

    def purge(self):
        "Remove rows and columns that are empty."
        rows = cols = 0
        for y in reversed(range(self.y)):
            if self.empty_row(y):
                self.remove_row(y)
                rows += 1

        for x in reversed(range(self.x)):
            if self.empty_col(x):
                self.remove_col(x)
                cols += 1

        return rows, cols

    ####################################################################
    # representation

    def __repr__(self):
        widths = [0] * self.x
        for i in range(self.x):
            col = [r[i] for r in self._rows]
            widths[i] = max(len(repr(v)) for v in col) + 1

        res = []
        for r in self._rows:
            row = ''
            for x in range(self.x):
                row += repr(r[x]).rjust(widths[x])
            res.append(row)

        return '\n'.join(res)

    def stringrep(self):
        widths = [0] * self.x
        for i in range(self.x):
            col = [r[i] for r in self._rows]
            widths[i] = max(len(str(v)) for v in col) + 1

        res = []
        for r in self._rows:
            row = ''
            for x in range(self.x):
                row += str(r[x]).rjust(widths[x])
            res.append(row)

        return u'\n'.join(res)

    def __str__(self):
        return self.stringrep()

    def print_row(self, y):
        rows = [self._rows[y]]
        widths = [0] * self.x
        for i in range(self.x):
            col = [r[i] for r in rows]
            widths[i] = max(len(str(v)) for v in col) + 1

        res = []
        for r in rows:
            row = ''
            for x in range(self.x):
                row += str(r[x]).rjust(widths[x])
            res.append(row)

        return '\n'.join(res)

    ####################################################################
    # utility

    def resize(self, yndx, xndx, pr=False):
        """Resize so that self[yndx,xndx] is valid.
        """
        if pr:
            print("RESIZE", yndx, xndx)
        y, x = yndx + 1, xndx + 1  # lengths are one more than the index

        if self.y < y:
            for _i in range(y - self.y):
                self._rows.append([self.empty] * self.x)
            self.y = y
        if self.x < x:
            for row in self._rows:
                row.extend([self.empty] * (x - self.x))
            self.x = x

    def isempty(self, y1, x1, y2, x2):
        for y in range(y1, y2):
            for x in range(x1, x2):
                if self.range_check(y, x, throw=False):
                    if self._rows[y][x] is not self.empty:
                        return False
        return True

    def notempty(self, y1, x1, y2, x2):
        return all(self[k] is not self.empty
                   for k in self.keys[y1:y2, x1:x2])

    def range_check(self, y, x, throw=True):
        # this part must be quick
        if y < self.y and x < self.x:
            return True
        if throw:
            self.raise_indexerror(y, x)
        else:
            return False

    def raise_indexerror(self, y, x):
        # now we can take our time providing useful diagnostics.
        def oor_dimensions():
            if y >= self.y:
                yield 'y'
            if x >= self.x:
                yield 'x'

        msg = ''
        dims = ' and '.join(oor_dimensions())
        if dims:
            msg += '%s dimension out of range. ' % dims

        bot = (self.y - 1, self.x - 1)
        index = (y, x)
        msg += 'Tried %s, but last cell is %s.'
        raise IndexError(msg % (index, bot))

    def next_nonempty_right(self, ykey, xkey):  # XXX: remove?
        self.range_check(ykey, xkey)
        y = x = 0
        for y, x in self.keys[ykey, xkey:]:
            if self[y, x] is not self.empty:
                return x
        self.raise_indexerror(y, x)

    def next_nonempty_down(self, ykey, xkey):   # XXX: remove?
        self.range_check(ykey, xkey)
        y = x = 0
        for y, x in self.keys[ykey:, xkey]:
            self.range_check(y, x)
            if self[y, x] is not self.empty:
                return y
        self.raise_indexerror(y, x)

    ####################################################################
    # iterators

    @property
    def rows(self):
        for y in range(self.y):
            yield self.get_row(y)

    @property
    def columns(self):
        for x in range(self.x):
            yield self.get_col(x)

    def key_iterator(self, yx):
        ys, xs = yx
        return iter(self.keyiter(ys, xs))

    def reverse_key_iterator(self, yx):
        ykey, xkey = yx
        yx, ymin, ymax = indexiter(self.y, ykey)
        xx, xmin, xmax = indexiter(self.x, xkey)
        self.resize(ymax, xmax)
        indexes = [(y, x) for x in reversed(xx) for y in reversed(yx)
                   if self._rows[y][x] is not Deleted]
        return iter(indexes)

    reversed = table_iterator(reverse_key_iterator)
    keys = table_iterator(key_iterator)

    def value_iterator(self, yx):
        ykey, xkey = yx
        for y, x in self.keyiter(ykey, xkey):
            yield self._rows[y][x]

    values = table_iterator(value_iterator)

    def apply_iterator(self, yx):
        """You can implement the game of life style actions with this
           iterator::

              def average((y,x)):
                  return sum(t[y-1:y+1, x-1:x+1]) / 9.0
              t.apply[:2, :2] = lambda value, key: average(key)

        """
        ykey, xkey = yx
        for y, x in self.keyiter(ykey, xkey):
            yield self, y, x, self._rows[y][x]

    apply = table_iterator(apply_iterator)

    ####################################################################
    # slice operations

    def _ispoint(self, y, x):
        return not (isinstance(y, slice) or isinstance(x, slice))

    def keyiter(self, ykey, xkey, debug=False):
        yx, _ymin, ymax = indexiter(self.y, ykey)
        xx, _xmin, xmax = indexiter(self.x, xkey)
        self.resize(ymax, xmax)
        res = []
        fail = []
        for y in yx:
            for x in xx:
                try:
                    if self._rows[y][x] is not Deleted:
                        res.append((y, x))
                except IndexError:
                    fail.append((y, x))
        if fail:
            raise IndexError(repr(fail))
        return res

    def _keyiterrect(self, kiter):
        y, x = kiter[0]
        yy, xx = kiter[-1]
        w = xx - x + 1
        h = yy - y + 1
        return rect(x, y, w, h)

    def __getitem__(self, yx):
        ykey, xkey = yx
        if self._ispoint(ykey, xkey):
            y, x = self.keyiter(ykey, xkey)[0]
            return self.get_cell(y, x)
        else:
            return value_iterator(self, ykey, xkey)

    def __setitem__(self, yx, val):
        ykey, xkey = yx
        ndx = self.keyiter(ykey, xkey)

        if len(ndx) == 1:
            y, x = ndx[0]
            return self.set_cell(y, x, val)
        else:
            if isinstance(val, value_iterator):
                krect = self._keyiterrect(ndx)
                vrect = val.rect()

                if krect.isomorphic(vrect):
                    transl = krect - vrect
                    for oy, ox in val.indices():
                        sy, sx = transl((oy, ox))
                        self.set_cell(sy, sx, val.g[oy, ox])
                else:
                    raise ValueError('Different sizes in assignment.')
                return
            elif not isinstance(val, str) and not isinstance(val, bytes):
                try:
                    it = iter(val)
                except TypeError:
                    pass
                else:
                    for (y, x), val in zip(ndx, it):
                        self.set_cell(y, x, val)
                    return

            for y, x in ndx:
                self.set_cell(y, x, val)

    def __delitem__(self, yx):
        ykey, xkey = yx
        for y, x in self.keyiter(ykey, xkey):
            self.del_cell(y, x)
