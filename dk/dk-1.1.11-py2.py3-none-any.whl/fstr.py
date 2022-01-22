# -*- coding: utf-8 -*-


class fstr(str):
    """String sub-class with a split() method that splits a given indexes
       ('fields').

       Usage::

          >>> r = fstr('D2008022002')
          >>> print r.split(1, 5, 7, 9)
          ['D', '2008', '02', '20', '02']
          >>> _, year, _ = r.split(1,5)
          >>> year
          '2008'

    """
    def split(self, *ndxs):
        if len(ndxs) == 0:
            return [self]
        if len(ndxs) == 1:
            i = ndxs[0]
            return [self[:i], self[i:]]

        res = []
        b = 0
        while ndxs:
            a, b, ndxs = b, ndxs[0], ndxs[1:]
            res.append(self[a:b])
        res.append(self[b:])

        return res


def _index(s, v, start=None):
    # print 'start:', start, v
    try:
        if start is None:
            return s.lower().index(v)
        else:
            return s.lower().index(v, start)
    except ValueError as e:
        raise IndexError(str(e) + ' "%s"' % v)


class sindex(str):
    """Use words for index/substring operations.

       Usage::

           sindex('a b c')['b':]  == 'c'
           sindex('a b c')[:'b']  == 'a'
           sindex('a b c')['a':'c']  == 'a'
    """
    def __getitem__(self, key):
        """Return the substring defined by two substrings:

            >>> s = sindex('Hello Fine World')
            >>> print repr(s['hello':'world'])
            'Fine'
            >>> print repr(s['hello':('fine','world')])
            ''
            >>> print s['fine':]
            World
            >>> print s[:'fine']
            Hello

        """
        if isinstance(key, slice):
            if key.start is None:
                start = 0
            else:
                start = _index(self, key.start) + len(key.start)

            if key.stop is None:
                stop = len(self)

            elif isinstance(key.stop, tuple):
                indices = []
                for end in key.stop:
                    try:
                        indices.append(_index(self, end))
                    except IndexError:
                        pass

                if len(indices) == 0:
                    raise IndexError(
                        "IndexError: none of '%s' found." % key.stop)

                stop = min(indices)
            else:
                stop = _index(self, key.stop, start)

            return super(sindex, self).__getitem__(slice(start, stop)).strip()

        else:
            return super(sindex, self).__getitem__(key)
