"""
invent a quick version of pytest autouse fixtures as pytest's unacceptably slow
collection/high memory use in pytest 4.6.11, which is the highest version that
works in py2k.

by "too-slow" we mean the test suite can't even manage to be collected for a
single process in less than 70 seconds or so and memory use seems to be very
high as well.   for two or four workers the job just times out after ten
minutes.

so instead we have invented a very limited form of these fixtures, as our
current use of "autouse" fixtures are limited to those in fixtures.py.

assumptions for these fixtures:

1. we are only using "function" or "class" scope

2. the functions must be associated with a test class

3. the fixture functions cannot themselves use pytest fixtures

4. the fixture functions must use yield, not return

When py2k support is removed and we can stay on a modern pytest version, this
can all be removed.


"""
import collections


_py2k_fixture_fn_names = collections.defaultdict(set)
_py2k_class_fixtures = collections.defaultdict(
    lambda: collections.defaultdict(set)
)
_py2k_function_fixtures = collections.defaultdict(
    lambda: collections.defaultdict(set)
)

_py2k_cls_fixture_stack = []
_py2k_fn_fixture_stack = []


def add_fixture(fn, fixture):
    assert fixture.scope in ("class", "function")
    _py2k_fixture_fn_names[fn.__name__].add((fn, fixture.scope))


def scan_for_fixtures_to_use_for_class(item):
    test_class = item.parent.parent.obj

    for name in _py2k_fixture_fn_names:
        for fixture_fn, scope in _py2k_fixture_fn_names[name]:
            meth = getattr(test_class, name, None)
            if meth and meth.im_func is fixture_fn:
                for sup in test_class.__mro__:
                    if name in sup.__dict__:
                        if scope == "class":
                            _py2k_class_fixtures[test_class][sup].add(meth)
                        elif scope == "function":
                            _py2k_function_fixtures[test_class][sup].add(meth)
                        break
                break


def run_class_fixture_setup(request):

    cls = request.cls
    self = cls.__new__(cls)

    fixtures_for_this_class = _py2k_class_fixtures.get(cls)

    if fixtures_for_this_class:
        for sup_ in cls.__mro__:
            for fn in fixtures_for_this_class.get(sup_, ()):
                iter_ = fn(self)
                next(iter_)

                _py2k_cls_fixture_stack.append(iter_)


def run_class_fixture_teardown(request):
    while _py2k_cls_fixture_stack:
        iter_ = _py2k_cls_fixture_stack.pop(-1)
        try:
            next(iter_)
        except StopIteration:
            pass


def run_fn_fixture_setup(request):
    cls = request.cls
    self = request.instance

    fixtures_for_this_class = _py2k_function_fixtures.get(cls)

    if fixtures_for_this_class:
        for sup_ in reversed(cls.__mro__):
            for fn in fixtures_for_this_class.get(sup_, ()):
                iter_ = fn(self)
                next(iter_)

                _py2k_fn_fixture_stack.append(iter_)


def run_fn_fixture_teardown(request):
    while _py2k_fn_fixture_stack:
        iter_ = _py2k_fn_fixture_stack.pop(-1)
        try:
            next(iter_)
        except StopIteration:
            pass
