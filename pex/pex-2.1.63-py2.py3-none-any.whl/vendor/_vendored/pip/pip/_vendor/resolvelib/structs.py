from .compat import collections_abc


class DirectedGraph(object):
    """A graph structure with directed edges."""

    def __init__(self):
        self._vertices = set()
        self._forwards = {}  # <key> -> Set[<key>]
        self._backwards = {}  # <key> -> Set[<key>]

    def __iter__(self):
        return iter(self._vertices)

    def __len__(self):
        return len(self._vertices)

    def __contains__(self, key):
        return key in self._vertices

    def copy(self):
        """Return a shallow copy of this graph."""
        other = DirectedGraph()
        other._vertices = set(self._vertices)
        other._forwards = {k: set(v) for k, v in self._forwards.items()}
        other._backwards = {k: set(v) for k, v in self._backwards.items()}
        return other

    def add(self, key):
        """Add a new vertex to the graph."""
        if key in self._vertices:
            raise ValueError("vertex exists")
        self._vertices.add(key)
        self._forwards[key] = set()
        self._backwards[key] = set()

    def remove(self, key):
        """Remove a vertex from the graph, disconnecting all edges from/to it."""
        self._vertices.remove(key)
        for f in self._forwards.pop(key):
            self._backwards[f].remove(key)
        for t in self._backwards.pop(key):
            self._forwards[t].remove(key)

    def connected(self, f, t):
        return f in self._backwards[t] and t in self._forwards[f]

    def connect(self, f, t):
        """Connect two existing vertices.

        Nothing happens if the vertices are already connected.
        """
        if t not in self._vertices:
            raise KeyError(t)
        self._forwards[f].add(t)
        self._backwards[t].add(f)

    def iter_edges(self):
        for f, children in self._forwards.items():
            for t in children:
                yield f, t

    def iter_children(self, key):
        return iter(self._forwards[key])

    def iter_parents(self, key):
        return iter(self._backwards[key])


class _FactoryIterableView(object):
    """Wrap an iterator factory returned by `find_matches()`.

    Calling `iter()` on this class would invoke the underlying iterator
    factory, making it a "collection with ordering" that can be iterated
    through multiple times, but lacks random access methods presented in
    built-in Python sequence types.
    """

    def __init__(self, factory):
        self._factory = factory

    def __repr__(self):
        return "{}({})".format(type(self).__name__, list(self._factory()))

    def __bool__(self):
        try:
            next(self._factory())
        except StopIteration:
            return False
        return True

    __nonzero__ = __bool__  # XXX: Python 2.

    def __iter__(self):
        return self._factory()

    def for_preference(self):
        """Provide an candidate iterable for `get_preference()`"""
        return self._factory()

    def excluding(self, candidates):
        """Create a new instance excluding specified candidates."""

        def factory():
            return (c for c in self._factory() if c not in candidates)

        return type(self)(factory)


class _SequenceIterableView(object):
    """Wrap an iterable returned by find_matches().

    This is essentially just a proxy to the underlying sequence that provides
    the same interface as `_FactoryIterableView`.
    """

    def __init__(self, sequence):
        self._sequence = sequence

    def __repr__(self):
        return "{}({})".format(type(self).__name__, self._sequence)

    def __bool__(self):
        return bool(self._sequence)

    __nonzero__ = __bool__  # XXX: Python 2.

    def __iter__(self):
        return iter(self._sequence)

    def __len__(self):
        return len(self._sequence)

    def for_preference(self):
        """Provide an candidate iterable for `get_preference()`"""
        return self._sequence

    def excluding(self, candidates):
        """Create a new instance excluding specified candidates."""
        return type(self)([c for c in self._sequence if c not in candidates])


def build_iter_view(matches):
    """Build an iterable view from the value returned by `find_matches()`."""
    if callable(matches):
        return _FactoryIterableView(matches)
    if not isinstance(matches, collections_abc.Sequence):
        matches = list(matches)
    return _SequenceIterableView(matches)
