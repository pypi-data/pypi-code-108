#! /usr/bin/env python3
"""
Module _TESTS -- Standalone tests of collections
Sub-Package STDLIB.COLL of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Tests of alternate collections provided in this
sub-package.
"""

from ._tuples import *


if __name__ == '__main__':
    from sys import argv as _argv
    verbose = ('-p' in _argv)
    
    from pickle import loads, dumps
    
    ### NAMEDTUPLE DEMOS
    
    # verify that instances can be pickled
    Point = namedtuple('Point', 'x, y')
    p = Point(x=10, y=20)
    assert p == loads(dumps(p))
    
    # test and demonstrate ability to override methods
    class Point(namedtuple('Point', 'x y')):
        
        __slots__ = ()
        
        @property
        def hypot(self):
            return (self.x ** 2 + self.y ** 2) ** 0.5
        
        def __str__(self):
            return 'Point: x=%6.3f  y=%6.3f  hypot=%6.3f' % (self.x, self.y, self.hypot)
    
    for p in Point(3, 4), Point(14, 5/7.):
        if verbose:
            print(p)
    
    class Point(namedtuple('Point', ('x', 'y'))):
        """Point class with optimized _make() and _replace() without error-checking"""
        
        __slots__ = ()
        
        _make = classmethod(tuple.__new__)
        
        def _replace(self, _map=map, **kwds):
            return self._make(_map(kwds.get, ('x', 'y'), self))
    
    _output = Point(11, 22)._replace(x=100)
    if verbose:
        print(_output)
    
    Point3D = namedtuple('Point3D', Point._fields + ('z',))
    if verbose:
        print(Point3D.__doc__)
    
    ### TYPED_NAMEDTUPLE DEMOS
    
    # verify that instances can be pickled
    Point = typed_namedtuple('Point', 'x int, y int')
    p = Point(x=10, y=20)
    assert p == loads(dumps(p))
    
    # test and demonstrate ability to override methods
    class Point(typed_namedtuple('Point', 'x float y float')):
        
        __slots__ = ()
        
        @property
        def hypot(self):
            return (self.x ** 2 + self.y ** 2) ** 0.5
        
        def __str__(self):
            return 'Point: x=%6.3f y=%6.3f hypot=%6.3f' % (
                self.x, self.y, self.hypot)
    
    for p in Point(3, 4), Point(14, 5), Point(9. / 7, 6):
        if verbose:
            print(p)
    
    class Point(typed_namedtuple('Point', (('x', int), ('y', int)))):
        """Point class with optimized _make() and _replace() without error-checking"""
        
        __slots__ = ()
        
        _make = classmethod(tuple.__new__)
        
        def _replace(self, _map=map, **kwds):
            return self._make(_map(kwds.get, ('x', 'y'), self))
    
    _output = Point(11, 22)._replace(x=100)
    if verbose:
        print(_output)
    
    Point3D = typed_namedtuple('Point3D', Point._fieldspecs + (('z', int),))
    if verbose:
        print(Point3D.__doc__)
