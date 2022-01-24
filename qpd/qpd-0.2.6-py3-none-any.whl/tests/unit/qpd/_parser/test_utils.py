import pandas as pd
from pytest import raises

from qpd.dataframe import DataFrames
from qpd._parser.sql import QPDSql
from qpd._parser.utils import (ColumnMention, ColumnMentions, Join,
                               VisitorContext, is_agg, normalize_join_type)
from qpd_pandas import QPDPandasEngine
from qpd.workflow import QPDWorkflow, QPDWorkflowContext


def test_column_mention():
    a = ColumnMention("a", "b")
    b = ColumnMention("a", "c")
    assert not a == b
    assert a == ColumnMention("a", "b")
    assert "a" == a.df_name
    assert "b" == a.col_name
    assert "_d5f618372100" == a.encoded
    assert "a.b" == a.__repr__()
    s = {a, b}
    assert ColumnMention("a", "c") in s
    assert ColumnMention("a", "d") not in s


def test_column_mentions():
    a = ColumnMention("a", "b")
    m1 = ColumnMentions(a, ("a", "c"), a)
    m2 = ColumnMentions(m1, m1, ColumnMention("b", "a"))
    assert 3 == len(m2)
    assert "a.b,a.c,b.a" == m2.__repr__()
    raises(AssertionError, lambda: m2.single)
    m3 = ColumnMentions(a)
    assert m3.single is a
    raises(ValueError, lambda: ColumnMentions("a.b"))


def test_visitor_context():
    raises(ValueError, lambda: VisitorContext(1))
    v = VisitorContext()
    v.set("x", 1)
    v2 = VisitorContext(v, z=3)
    assert v._data is v2._data
    assert 1 == v2.get("x", 2)
    assert 2 == v2.get("y", 2)
    assert 3 == v2.get("z", 2)
    df1 = _make_df([[0, 1]], ["a", "b"])
    df2 = _make_df([[0, 2]], ["a", "c"])
    dfs = DataFrames(a=df1, b=df2)
    v = VisitorContext(v2, current=df1, dfs=dfs)
    assert v.current is df1
    assert v.dfs is dfs
    sql = QPDSql("SELECT * \n FROM  a", "singleStatement")
    wf = QPDWorkflow(QPDWorkflowContext(QPDPandasEngine(), dfs))
    v = VisitorContext(v, dict(sql=sql, workflow=wf))
    assert v.sql is sql
    assert v.workflow is wf
    v.update_current(df2)
    assert v.current is df2

    assert 0 == len(v.all_column_mentions)
    obj = "a.*"
    m = v.add_column_mentions(obj)
    assert ColumnMention("a", "a") in m
    assert ColumnMention("a", "b") in m
    assert len(m) == 2
    assert v.get_column_mentions(obj) is m
    obj = "c"
    m = v.add_column_mentions(obj)
    m = v.add_column_mentions(obj)  # will read from cache
    assert ColumnMention("b", "c") in m
    assert len(m) == 1
    assert 3 == len(v.all_column_mentions)

    assert not v.col_encoded
    v.set_col_encoded()
    assert v.col_encoded

    assert "" == v.to_str(None)
    assert "SELECT * FROM a" == v.expr(sql.tree)
    assert "SELECT * FROM a" == v.expr(sql.tree)  # test caching

    sql = QPDSql("a.*", "expression")
    v = VisitorContext(v, sql=sql)
    v.set("col_encoded", False)
    assert ["a.a", "a.b"] == v.ctx_to_col_names(sql.tree)
    v.set_col_encoded()
    assert ['_845ca596baa3', '_d5f618372100'] == v.ctx_to_col_names(sql.tree)

    assert 0 == len(v.joins)
    v.add_join_relation(Join("a", df1))
    v.add_join_relation(Join("b", df2))
    raises(ValueError, lambda: v.add_join_relation(Join("a", df2)))
    assert 2 == len(v.joins)
    v.joins[1].set_conditions([[None, None]])


def test_is_agg():
    assert is_agg("COUNT")
    assert not is_agg("SIN")


def test_normalize_join_type():
    assert "inner" == normalize_join_type(" ")
    assert "inner" == normalize_join_type("")
    assert "inner" == normalize_join_type(" INNER ")
    assert "left_outer" == normalize_join_type("LEFT")
    assert "full_outer" == normalize_join_type("full")
    assert "left_semi" == normalize_join_type("semi")
    assert "left_anti" == normalize_join_type("left   anti")
    raises(ValueError, lambda: normalize_join_type("xyz"))


def _make_df(arr, cols):
    return QPDPandasEngine().to_df(pd.DataFrame(arr, columns=cols))
