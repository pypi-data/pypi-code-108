from pytest import raises

from qpd.specs import (
    AggFunctionSpec,
    ArgumentSpec,
    IsInSpec,
    IsValueSpec,
    NoWindowFrame,
    OrderBySpec,
    OrderItemSpec,
    RollingWindowFrame,
    WindowFunctionSpec,
    WindowSpec,
    make_windowframe_spec,
)


def test_argument_spec():
    a = ArgumentSpec(True, "x")
    assert a.is_col
    assert "x" == a.value


def test_agg_function_spec():
    f = AggFunctionSpec("max", unique=False, dropna=True)
    assert "max" == f.name
    assert not f.unique
    assert f.dropna
    print(f)
    assert f == f
    assert f != AggFunctionSpec("max", unique=True, dropna=True)
    s = set([f, f])
    assert len(s) == 1
    assert f in s
    assert AggFunctionSpec("max", unique=True, dropna=True) not in s


def test_order_item_spec():
    o = OrderItemSpec("x")
    assert o.asc
    assert "auto" == o.na_position
    assert "first" == o.pd_na_position
    o = OrderItemSpec("x", False)
    assert not o.asc
    assert "auto" == o.na_position
    assert "last" == o.pd_na_position
    o = OrderItemSpec("x", False, na_position="first")
    assert not o.asc
    assert "first" == o.na_position
    assert "first" == o.pd_na_position
    o = OrderItemSpec("x", True, na_position="last")
    assert o.asc
    assert "last" == o.na_position
    assert "last" == o.pd_na_position
    raises(ValueError, lambda: OrderItemSpec("x", True, na_position="x"))


def test_order_by_spec():
    a = OrderItemSpec("a")
    b = OrderItemSpec("b", False)
    c = OrderItemSpec("a", False, "last")
    d = OrderItemSpec("b", True, "first")
    e = OrderItemSpec("a", True, "last")
    f = OrderItemSpec("b", False, "first")
    o = OrderBySpec(a, b)
    assert len(o) == 2
    assert ["a", "b"] == o.keys
    assert [True, False] == o.asc
    assert "first" == o.pd_na_position
    o = OrderBySpec(b, e)
    assert "last" == o.pd_na_position
    o = OrderBySpec(a, f)
    assert "first" == o.pd_na_position
    raises(ValueError, lambda: OrderBySpec(c, d, e))
    assert "first" == OrderBySpec(a).pd_na_position
    assert "last" == OrderBySpec(b).pd_na_position
    assert "first" == OrderBySpec("a").pd_na_position
    assert "last" == OrderBySpec(("b", False)).pd_na_position
    assert "first" == OrderBySpec(("b", False, "first")).pd_na_position


def test_make_windowframe_spec():
    assert isinstance(make_windowframe_spec(""), NoWindowFrame)
    assert isinstance(make_windowframe_spec("rows", None, None), NoWindowFrame)
    assert isinstance(make_windowframe_spec("rows", None, 0), RollingWindowFrame)
    assert isinstance(make_windowframe_spec("rows", None, "0"), RollingWindowFrame)
    assert isinstance(make_windowframe_spec("rows", -1, "2"), RollingWindowFrame)
    w = make_windowframe_spec("rows", None, -5)
    assert w.start is None
    assert -5 == w.end
    assert w.window is None
    w = make_windowframe_spec("rows", "-6", 5)
    assert isinstance(w, RollingWindowFrame)
    assert -6 == w.start
    assert 5 == w.end
    assert 12 == w.window
    raises(NotImplementedError, lambda: make_windowframe_spec("x"))


def test_window_spec():
    wf = make_windowframe_spec("rows", -2, 0)
    w = WindowSpec("", ["a", "b"], OrderBySpec("c", ("d", False)), wf)
    assert w.name != ""
    assert ["a", "b"] == w.partition_keys
    assert ["c", "d"] == w.order_by.keys
    assert wf == w.windowframe
    w2 = WindowSpec("xy", ["a", "b"], OrderBySpec("c", ("d", False)), wf)
    assert w == w and w != w2
    assert "xy" == w2.name


def test_window_function():
    wf = make_windowframe_spec("rows", -2, 0)
    w = WindowSpec("", ["a", "b"], [("c", True, True), ("d", False, True)], wf)
    f = WindowFunctionSpec("sum", unique=True, dropna=False, window=w)
    assert f.window is w
    assert f.has_windowframe
    assert f.has_partition_by
    assert f.has_order_by


def test_is():
    v = IsValueSpec("NULL", False)
    assert "null" == v.name
    assert not v.positive
    assert "null" == v.value_expr

    v = IsInSpec("beTween", False)
    assert "between" == v.name
    assert v.is_between
    assert not v.positive
    assert 0 == len(v.values)

    a1 = ArgumentSpec(False, 1)
    a2 = ArgumentSpec(False, 2)
    v = IsInSpec("beTween", False, a1, a2)
    assert a1 is v.values[0]
    assert a2 is v.values[1]
