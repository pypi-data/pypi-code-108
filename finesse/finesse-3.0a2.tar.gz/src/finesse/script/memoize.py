"""Memoize wrappers for the parser.

Based on https://github.com/we-like-parsers/pegen/blob/main/story5/memo.py by Guido van
Rossum.

Copyright (c) 2021 we-like-parsers

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""


def memoize(func):
    """Memoize a parsing method.

    The functon must be a method on a class deriving from Parser. The method must have
    either no arguments or a single argument that is an int or str (the latter being the
    case for expect()). It must return either None or an object that is not modified (at
    least not while we're parsing). We memoize positive and negative outcomes per input
    position. The function is expected to move the input position iff it returns a not-
    None value. The memo is structured as a dict of dict, the outer dict indexed by
    input position, the inner by function and arguments.
    """

    def memoize_wrapper(self, *args):
        pos = self.mark()
        memo = self.memos.get(pos)
        if memo is None:
            memo = self.memos[pos] = {}
        key = (func, args)
        if key in memo:
            res, endpos = memo[key]
            self.reset(endpos)
        else:
            res = func(self, *args)
            endpos = self.mark()
            if res is None:
                assert endpos == pos
            else:
                assert endpos > pos
            memo[key] = res, endpos
        return res

    return memoize_wrapper


def memoize_left_rec(func):
    """Memoize a left-recursive parsing method.

    This is similar to @memoize but loops until no longer parse is obtained. Inspired by
    https://github.com/PhilippeSigaud/Pegged/wiki/Left-Recursion
    """

    def memoize_left_rec_wrapper(self, *args):
        pos = self.mark()
        memo = self.memos.get(pos)
        if memo is None:
            memo = self.memos[pos] = {}
        key = (func, args)
        if key in memo:
            res, endpos = memo[key]
            self.reset(endpos)
        else:
            # This is where we deviate from @memoize.

            # Prime the cache with a failure.
            memo[key] = lastres, lastpos = None, pos

            # Loop until no longer parse is obtained.
            while True:
                self.reset(pos)
                res = func(self, *args)
                endpos = self.mark()
                if endpos <= lastpos:
                    break
                memo[key] = lastres, lastpos = res, endpos

            res = lastres
            self.reset(lastpos)

        return res

    return memoize_left_rec_wrapper
