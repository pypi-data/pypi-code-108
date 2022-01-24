from pytest import raises
from triad.utils.hash import to_uuid

from qpd.dataframe import Column, DataFrame, DataFrames, ColumnNameResolver


def test_column():
    obj = "xx"
    c = Column(obj)
    assert obj is c.native
    assert "" == c.name
    assert not c.has_name
    raises(AssertionError, lambda: c.assert_has_name())
    c2 = c.rename("x")
    assert obj is c2.native
    assert "x" == c2.name
    assert to_uuid(c) != to_uuid(c2)
    c2.assert_has_name()
    c3 = Column(obj, "x")
    assert to_uuid(c3) == to_uuid(c2)


def test_dataframe():
    c1 = Column(1, "a")
    c2 = Column(1, "b")
    d = DataFrame(c1, c2)
    assert ["a", "b"] == list(d.keys())
    c3 = Column(1, "c")
    d2 = DataFrame(d, c3)
    assert ["a", "b", "c"] == list(d2.keys())
    d3 = DataFrame(c1, c2, c3)
    d4 = DataFrame(c1, [c2, c3])
    assert to_uuid(d2) != to_uuid(d)
    assert to_uuid(d2) == to_uuid(d3)
    assert to_uuid(d2) == to_uuid(d4)
    raises(ValueError, lambda: DataFrame(1))


def test_dataframe_get():
    c1 = Column(1, "a")
    c2 = Column(1, "b")
    d = DataFrame(c1, c2)
    assert d["a"] is c1
    assert d["*"] is d
    d2 = d[["b", "a"]]
    assert isinstance(d2, DataFrame)
    assert ["b", "a"] == list(d2.keys())
    assert to_uuid(d) != to_uuid(d2)
    d3 = d[["*"]]
    assert to_uuid(d3) == to_uuid(d)
    raises(ValueError, lambda: DataFrame(c1, c1))
    with raises(KeyError):
        d["x"]
    with raises(KeyError):
        d[["a", "x"]]
    with raises(ValueError):
        d[["a", "*"]]


def test_dataframes():
    c1 = Column(1, "a")
    c2 = Column(1, "b")
    c3 = Column(1, "a")
    c4 = Column(1, "c")
    df1 = DataFrame(c1, c2)
    df2 = DataFrame(c3, c4)
    df3 = DataFrame(c4)
    dfs1 = DataFrames(a=df1, b=df3)
    assert dfs1["a"] is df1
    assert dfs1["b"] is df3
    dfs2 = DataFrames(dict(a=df1), b=df3)
    assert to_uuid(dfs1) == to_uuid(dfs2)
    with raises(ValueError):
        DataFrames(1)
    dfs3 = DataFrames(dfs2, c=df2)
    assert dfs3["a"] is df1
    assert dfs3["b"] is df3
    assert dfs3["c"] is df2
    assert to_uuid(dfs1) != to_uuid(dfs3)


def test_dataframes_get():
    def assert_eq(df1, df2):
        assert list(df1.keys()) == list(df2.keys())
        assert to_uuid(df1) == to_uuid(df2)

    c1 = Column(1, "a")
    c2 = Column(1, "b")
    c3 = Column(1, "a")
    c4 = Column(1, "c")
    df1 = DataFrame(c1, c2)
    df2 = DataFrame(c3, c4)
    df3 = DataFrame(c4)
    dfs1 = DataFrames(a=df1, b=df3)
    assert_eq(dfs1.get("*"), DataFrame(c1, c2, c4))
    assert_eq(dfs1.get(["*"]), DataFrame(c1, c2, c4))
    assert_eq(dfs1.get(["c", "b"]), DataFrame(c4, c2))
    assert_eq(dfs1.get("a.*"), DataFrame(c1, c2))
    assert dfs1.get("a") is c1
    assert dfs1.get("a.a") is c1
    dfs2 = DataFrames(a=df1, b=df2)
    raises(ValueError, lambda: dfs2.get("*"))
    raises(ValueError, lambda: dfs2.get(["*"]))
    assert_eq(dfs2.get("a.*"), DataFrame(c1, c2))
    assert_eq(dfs2.get("b.*"), DataFrame(c3, c4))


def test_column_name_resolver():
    def assert_eq(expected, actual):
        s = [x[0] + "." + x[1] for x in actual]
        assert expected == ",".join(s)

    c = ColumnNameResolver(dict(a=["x", "y"]), b=["x", "z"])
    assert c.has_overlap
    assert_eq("a.x,a.y", c.get_cols("a.*", ensure_single_df=True))
    assert_eq("b.x,b.z", c.get_cols("b.x", "z", ensure_single_df=True))
    assert_eq("b.z,a.x,a.y", c.get_cols("z", "a.x", "y"))
    assert_eq("b.z,a.x,b.z", c.get_cols("z", "a.x", "z"))
    raises(AssertionError, lambda: c.get_cols("z", "a.x", "z", ensure_distinct=True))
    raises(AssertionError, lambda: c.get_cols("z", "a.x", ensure_single_df=True))
    raises(ValueError, lambda: c.get_cols("t"))
    raises(ValueError, lambda: c.get_cols("*"))

    assert ("a", "y") == c.get_col("y")
    raises(ValueError, lambda: c.get_col("x"))
    raises(ValueError, lambda: c.get_col("*"))
    raises(ValueError, lambda: c.get_col("a.*"))

    raises(ValueError, lambda: ColumnNameResolver(1))
    raises(ValueError, lambda: ColumnNameResolver(a=1))

    c1 = Column(1, "x")
    c2 = Column(1, "y")
    df = DataFrame(c1, c2)
    c = ColumnNameResolver(dict(b=df), a=["m", "n"])
    assert_eq("b.x,b.y,a.m,a.n", c.get_cols("*"))
