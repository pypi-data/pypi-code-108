import pandas as pd
from pytest import raises
from qpd._parser.sql import QPDSql
from qpd._parser.utils import VisitorContext
from qpd._parser.visitors import PreScan, StatementVisitor
from qpd.workflow import QPDWorkflow, QPDWorkflowContext, WorkflowDataFrame
from qpd_pandas import QPDPandasEngine
from qpd_test import assert_df_eq


def test_pre_scan():
    def assert_eq(dfs, sql, mentions):
        sql = QPDSql(sql, "singleStatement")
        ctx = QPDWorkflowContext(QPDPandasEngine(), dfs)
        wf = QPDWorkflow(ctx)
        v = PreScan(
            VisitorContext(),
            sql=sql,
            workflow=wf,
            current=wf.dfs[list(dfs.keys())[0]],
            dfs=wf.dfs,
        )
        v.visit(sql.tree)
        m = set(x.__repr__() for x in v.all_column_mentions)
        if mentions == "":
            assert len(m) == 0
        else:
            assert set(mentions.split(",")) == m
        return v

    def not_support(dfs, sql):
        with raises(NotImplementedError):
            assert_eq(dfs, sql, "")

    a = pd.DataFrame([[0, 1], [0, 2], [1, 3]], columns=["a", "b"])
    b = pd.DataFrame([[0, 20], [2, 3]], columns=["a", "c"])
    c = pd.DataFrame([[0, 1, 2, 3, 4, 5]], columns=["a", "b", "c", "d", "e", "f"])
    v = assert_eq(dict(a=a, b=b), "SELECT a.* FROM a", "a.a,a.b")
    assert set(v.get("dfs").keys()) == {"a"}
    assert not v.get("has_agg_func", False)
    v = assert_eq(dict(a=a, b=b), "SELECT * FROM a", "")
    assert v.get("select_all", False)
    assert_eq(dict(c=c), "SELECT a+1+b AS x,b AS y FROM c", "c.a,c.b")
    v = assert_eq(
        dict(a=a, b=b, c=c),
        """
        SELECT a.a AS x,SUM(c.b) AS y
        FROM c INNER JOIN a
            ON c.b=a.b
        WHERE e=10
        GROUP BY a.b
        HAVING SUM(c.c)>0
        ORDER BY c.d
        LIMIT 10
        """,
        "a.a,a.b,c.b,c.c,c.d,c.e",
    )
    assert set(v.get("dfs").keys()) == {"a", "c"}
    assert v.get("has_agg_func", False)
    v = assert_eq(
        dict(a=a, b=b, c=c),
        """
        SELECT a, LEAD(e,1) OVER(PARTITION BY b ORDER BY c) FROM c
        """,
        "c.a,c.b,c.c,c.e",
    )
    assert v.get("has_window", False)
    v = assert_eq(
        dict(c=c),
        "SELECT a+1+b AS x,SUM(b) AS y FROM c AS cc WHERE e=10",
        "cc.a,cc.b,cc.e",
    )
    assert set(v.get("dfs").keys()) == {"cc"}
    v = assert_eq(
        dict(c=c),
        "SELECT a+1+b AS x,SUM(b) AS y FROM (c AS cc) AS x WHERE e=10",
        "x.a,x.b,x.e",
    )
    assert set(v.get("dfs").keys()) == {"x"}

    # prescan argument types
    v = assert_eq(
        dict(c=c),
        """SELECT f(a, a+a, a+1, -1 , 1+1) AS x,
                  g('str', NOT a, sin( sin(a))) AS x FROM c""",
        "c.a",
    )
    d = {v.to_str(x[0], ""): (x[1], x[2]) for x in v._func_args}
    assert {
        "a": (True, True),
        "a+a": (True, False),
        "a+1": (True, False),
        "-1": (False, True),
        "1+1": (False, False),
        "'str'": (False, True),
        "NOTa": (True, False),
        "sin(a)": (True, False),
        "sin(sin(a))": (True, False),
    } == d

    not_support(dict(c=c), "SELECT *, SUM(a) FROM c")
    not_support(
        dict(c=c), "SELECT SUM(a), ROW_NUMBER() OVER(PARTITION BY b ORDER BY c) FROM c"
    )


def test_pre_scan_join():
    def assert_eq(dfs, sql, *joins):
        sql = QPDSql(sql, "singleStatement")
        ctx = QPDWorkflowContext(QPDPandasEngine(), dfs)
        wf = QPDWorkflow(ctx)
        v = PreScan(
            VisitorContext(),
            sql=sql,
            workflow=wf,
            current=wf.dfs[list(dfs.keys())[0]],
            dfs=wf.dfs,
        )
        v.visit(sql.tree)
        for e, a in zip(joins, v.joins[1:]):
            c = [[v.to_str(x[0], ""), v.to_str(x[1], "")] for x in a.conditions]
            assert e == [a.df_name, a.join_type, a.natural] + c
        return v

    def bad(dfs, sql):
        with raises(Exception):
            assert_eq(dfs, sql)

    a = pd.DataFrame([[0, 1], [0, 2], [1, 3]], columns=["a", "b"])
    b = pd.DataFrame([[0, 20], [2, 3]], columns=["a", "c"])
    c = pd.DataFrame([[0, 1], [0, 2], [1, 3]], columns=["a", "d"])
    d = pd.DataFrame([[0, 20], [2, 3]], columns=["a", "e"])
    e = pd.DataFrame([[0, 1], [0, 2], [1, 3]], columns=["a", "f"])
    dfs = dict(a=a, b=b, c=c, d=d, e=e)
    assert_eq(
        dfs,
        """
        SELECT * FROM a
        """,
    )
    assert_eq(
        dfs,
        """
        SELECT a.*,c FROM a JOIN b ON a.a=b.a
        """,
        ["b", "inner", False, ["a.a", "b.a"]],
    )
    # order of on comparison will be corrected
    assert_eq(
        dfs,
        """
        SELECT a.*,c FROM a LEFT JOIN b ON c=a.a
        """,
        ["b", "left_outer", False, ["a.a", "c"]],
    )
    # alias of table can be handled
    assert_eq(
        dfs,
        """
        SELECT aa.*,c FROM a AS aa FULL JOIN b AS bb ON bb.c=aa.a
        """,
        ["bb", "full_outer", False, ["aa.a", "bb.c"]],
    )
    # multiple joins and multiple conditions
    assert_eq(
        dfs,
        """
        SELECT a.*,b FROM a
            JOIN b ON b.a=a.a
            SEMI JOIN c ON a.a=c.a
            ANTI JOIN d ON e = b AND d.a=a.a
        """,
        ["b", "inner", False, ["a.a", "b.a"]],
        ["c", "left_semi", False, ["a.a", "c.a"]],
        ["d", "left_anti", False, ["b", "e"], ["a.a", "d.a"]],
    )
    # multiple tables in condition
    assert_eq(
        dfs,
        """
        SELECT a.*,b FROM a
            JOIN b ON b.a=a.a
            RIGHT JOIN c ON c.a=a.a+b.c
        """,
        ["b", "inner", False, ["a.a", "b.a"]],
        ["c", "right_outer", False, ["a.a+b.c", "c.a"]],
    )
    # cross join
    assert_eq(
        dfs,
        """
        SELECT a.*,c FROM a CROSS JOIN b
        """,
        ["b", "cross", False],
    )
    # natural join
    assert_eq(
        dfs,
        """
        SELECT a.*,c FROM a NATURAL LEFT JOIN b
        """,
        ["b", "left_outer", True],
    )

    # # * is ambiguous. this should be captured after prescan
    # bad(dfs, """
    # SELECT * FROM a JOIN c ON a.a=c.a
    # """)
    # wrong condition
    bad(
        dfs,
        """
    SELECT a.* FROM a JOIN c ON a.a=b.a
    """,
    )
    # wrong condition
    bad(
        dfs,
        """
    SELECT a.* FROM a JOIN c ON a.a=a.a
    """,
    )
    # invalid condition
    bad(
        dfs,
        """
    SELECT a.* FROM a JOIN c ON a.a>b.a
    """,
    )


def test_op_precedence():
    a = pd.DataFrame([[1, 4], [2, 5]], columns=["a", "b"])
    assert_eq(
        dict(a=a),
        "SELECT a+1 AS a, b FROM a",
        [[2, 4], [3, 5]],
        ["a", "b"],
    )
    assert_eq(
        dict(a=a),
        "SELECT a+2*3 AS a, b FROM a",
        [[7, 4], [8, 5]],
        ["a", "b"],
    )
    assert_eq(
        dict(a=a),
        "SELECT a+1-2*3/4 AS a, b FROM a",
        [[0.5, 4], [1.5, 5]],
        ["a", "b"],
    )


def test_const_select():
    assert_eq(
        {},
        "SELECT 1 AS a, 1.5 AS b, TRUE AS c",
        [[1, 1.5, True]],
        ["a", "b", "c"],
    )
    assert_eq(
        {},
        "SELECT 1+2 AS a, 1.5*3 AS b, 'x' AS c",
        [[3, 4.5, "x"]],
        ["a", "b", "c"],
    )


def test_case_when():
    a = pd.DataFrame([[1, "a", 4], [2, "a", 5], [2, "b", 6]], columns=["a", "b", "c"])
    assert_eq(
        dict(a=a),
        """
        SELECT a,b,
            CASE
                WHEN a=1 THEN 10+c
                WHEN b='b' AND a=2 THEN 20+c
                ELSE 30*2
            END AS c
        FROM a
        """,
        [[1, "a", 14], [2, "a", 60], [2, "b", 26]],
        ["a", "b", "c"],
    )


def test_is_value():
    a = pd.DataFrame([[True], [False], [None]], columns=["a"])
    assert_eq(
        dict(a=a),
        """
        SELECT a,
            NOT a AS b,
            a IS NULL AS c,
            a IS NOT NULL AS d,
            a IS TRUE AS e,
            a IS NOT TRUE AS f,
            a IS FALSE AS g,
            a IS NOT FALSE AS h,
            CASE
                WHEN a IS NULL THEN 0
                WHEN a IS TRUE THEN 1
                ELSE 2
            END AS i
        FROM a
        """,
        [
            [True, False, False, True, True, False, False, True, 1],
            [False, True, False, True, False, True, True, False, 2],
            [None, None, True, False, False, True, False, True, 0],
        ],
        list("abcdefghi"),
    )


def test_is_in():
    a = pd.DataFrame([[0, 1, 1], [2, 3, 4]], columns=["a", "b", "c"])
    assert_eq(
        dict(a=a),
        """
        SELECT *,
            c IN (1,5) AS d,
            c NOT IN (1,5) AS e,
            c IN (7+2,a+b) AS f
        FROM a
        """,
        [[0, 1, 1, True, False, True], [2, 3, 4, False, True, False]],
        list("abcdef"),
    )


def test_is_between():
    a = pd.DataFrame([[0, 1, 1], [2, 3, 4], [1, 2, None]], columns=["a", "b", "c"])
    assert_eq(
        dict(a=a),
        """
        SELECT *,
            c BETWEEN 0 AND 1 AS d,
            c NOT BETWEEN 0 AND 1 AS e,
            c BETWEEN a AND b AS f,
            c NOT BETWEEN a AND b AS g
        FROM a
        """,
        [
            [0, 1, 1, True, False, True, False],
            [2, 3, 4, False, True, False, True],
            [1, 2, None, None, None, None, None],
        ],
        list("abcdefg"),
    )
    assert_eq(
        dict(a=a),
        """
        SELECT * FROM a
        WHERE c BETWEEN 0 AND 1
        """,
        [[0, 1, 1]],
        list("abc"),
    )
    assert_eq(
        dict(a=a),
        """
        SELECT * FROM a
        WHERE c NOT BETWEEN 0 AND 1
        """,
        [[2, 3, 4]],
        list("abc"),
    )


def test_order_by_limit():
    a = pd.DataFrame([[1, "a"], [2, "b"], [None, "a"]], columns=["a", "b"])
    assert_eq(
        dict(a=a),
        """
        SELECT * FROM a ORDER BY a LIMIT 1*1
        """,
        [[None, "a"]],
        ["a", "b"],
    )
    assert_eq(
        dict(a=a),
        """
        SELECT * FROM a ORDER BY a NULLS LAST LIMIT 1*1
        """,
        [[1, "a"]],
        ["a", "b"],
    )


def test_drop_duplicates():
    a = pd.DataFrame([[1, "a"], [2, "b"], [1, "a"]], columns=["a", "b"])
    b = pd.DataFrame([[1, "b"], [4, "bb"]], columns=["a", "b"])
    assert_eq(
        dict(a=a, b=b),
        """
        SELECT ALL * FROM a
        """,
        [[1, "a"], [2, "b"], [1, "a"]],
        ["a", "b"],
    )
    assert_eq(
        dict(a=a, b=b),
        """
        SELECT DISTINCT * FROM a
        """,
        [[1, "a"], [2, "b"]],
        ["a", "b"],
    )


def test_from():
    a = pd.DataFrame([[0, 1], [0, 2], [1, 3]], columns=["a", "b"])
    b = pd.DataFrame([[0, 20], [2, 3]], columns=["a", "c"])
    c = pd.DataFrame([[0, 1], [0, 2], [1, 3]], columns=["a", "d"])
    d = pd.DataFrame([[0, 20], [2, 3]], columns=["a", "e"])
    e = pd.DataFrame([[0, 1], [0, 2], [1, 3]], columns=["a", "f"])
    dfs = dict(a=a, b=b, c=c, d=d, e=e)
    assert_eq(
        dfs,
        """
        SELECT * FROM a
        """,
        [[0, 1], [0, 2], [1, 3]],
        ["a", "b"],
    )
    assert_eq(
        dfs,
        """
        SELECT x.* FROM a AS x
        """,
        [[0, 1], [0, 2], [1, 3]],
        ["a", "b"],
    )
    assert_eq(
        dfs,
        """
        SELECT a.*,c FROM a INNER JOIN b ON b.a == a.a
        """,
        [[0, 1, 20], [0, 2, 20]],
        ["a", "b", "c"],
    )
    assert_eq(
        dfs,
        """
        SELECT x.*,c FROM a AS x INNER JOIN b AS y ON y.a == x.a
        """,
        [[0, 1, 20], [0, 2, 20]],
        ["a", "b", "c"],
    )


def test_join():
    # basic operations
    a = pd.DataFrame([[0, 1], [0, 2], [1, 3]], columns=["a", "b"])
    b = pd.DataFrame([[0, 20], [2, 3]], columns=["a", "c"])
    assert_eq(
        dict(a=a, b=b),
        """SELECT a.*,c AS x FROM a INNER JOIN b ON a.a=b.a""",
        [[0, 1, 20], [0, 2, 20]],
        ["a", "b", "x"],
    )
    assert_eq(
        dict(a=a, b=b),
        """SELECT b,c,a.a AS x FROM a INNER JOIN b ON c=b""",
        [[3, 3, 1]],
        ["b", "c", "x"],
    )

    # semi join
    a = pd.DataFrame([[0, 1], [0, 2], [1, 3]], columns=["a", "b"])
    b = pd.DataFrame([[0, 20], [2, 3]], columns=["a", "c"])
    assert_eq(
        dict(a=a, b=b),
        """SELECT a.* FROM a LEFT SEMI JOIN b ON a.a=b.a""",
        [[0, 1], [0, 2]],
        ["a", "b"],
    )
    assert_eq(
        dict(a=a, b=b),
        """SELECT * FROM a LEFT SEMI JOIN b ON a.a=b.a""",
        [[0, 1], [0, 2]],
        ["a", "b"],
    )

    # multiple conditions, and formula equations
    a = pd.DataFrame([[0, 1], [0, 2], [1, 3]], columns=["a", "b"])
    b = pd.DataFrame([[0, 20, 1], [2, 2, 1]], columns=["a", "c", "d"])
    assert_eq(
        dict(a=a, b=b),
        """SELECT b*c AS y,a.a AS x FROM a INNER JOIN b ON c+d=b AND a.a*2=b.a""",
        [[6, 1]],
        ["y", "x"],
    )

    # multiple joins
    a = pd.DataFrame([[0, 1], [0, 2], [1, 3]], columns=["a", "b"])
    b = pd.DataFrame([[2, 20], [3, 30]], columns=["b", "c"])
    c = pd.DataFrame([[20, 200]], columns=["c", "d"])
    assert_eq(
        dict(a=a, b=b, c=c),
        """SELECT a.*,b.c,c.d FROM a
                INNER JOIN b ON a.b=b.b
                INNER JOIN c ON c.c=b.c""",
        [[0, 2, 20, 200]],
        ["a", "b", "c", "d"],
    )
    assert_eq(
        dict(a=a, b=b, c=c),
        """SELECT a.*,b.c,c.d FROM a
                INNER JOIN b ON a.b=b.b
                INNER JOIN c ON c.c=b.c+(a.a+0)""",
        [[0, 2, 20, 200]],
        ["a", "b", "c", "d"],
    )


def test_where():
    # basic operations
    a = pd.DataFrame([[0, 1], [0, 2], [1, 3]], columns=["a", "b"])
    b = pd.DataFrame([[0, 20], [2, 3]], columns=["a", "c"])
    assert_eq(
        dict(a=a, b=b), """SELECT * FROM a WHERE b>=2""", [[0, 2], [1, 3]], ["a", "b"]
    )
    assert_eq(
        dict(a=a, b=b),
        """SELECT * FROM a WHERE b>=2 AND NOT (a==0)""",
        [[1, 3]],
        ["a", "b"],
    )
    assert_eq(
        dict(a=a, b=b), """SELECT * FROM a WHERE b>2 AND a!=0""", [[1, 3]], ["a", "b"]
    )
    assert_eq(
        dict(a=a, b=b),
        """SELECT a.*,c,TRUE AS t, FALSE AS f FROM a INNER JOIN b ON a.a=b.a
            WHERE a.a<=0 AND a.b*2<3 AND (TRUE OR FALSE)""",
        [[0, 1, 20, True, False]],
        ["a", "b", "c", "t", "f"],
    )

    a = pd.DataFrame([[None, "x", 0.5], [10, None, 0.6]], columns=["a", "b", "c"])
    assert_eq(
        dict(a=a, b=b),
        """SELECT * FROM a WHERE c IS NOT NULL AND (a<50 AND b IS NOT NULL)""",
        [],
        ["a", "b", "c"],
    )


def test_agg():
    # basic
    a = pd.DataFrame([[0, 1], [0, 2], [1, 3]], columns=["a", "b"])
    b = pd.DataFrame([[0, 20], [2, 3]], columns=["a", "c"])
    assert_eq(
        dict(a=a, b=b),
        """SELECT a, SUM(b) AS b FROM a GROUP BY a""",
        [[0, 3], [1, 3]],
        ["a", "b"],
    )
    assert_eq(
        dict(a=a, b=b),
        """SELECT a, SUM(b) AS sb, AVG(b) AS ab, MIN(b) AS mb, MAX(b) AS xb
            FROM a GROUP BY a""",
        [[0, 3, 1.5, 1, 2], [1, 3, 3, 3, 3]],
        ["a", "sb", "ab", "mb", "xb"],
    )
    assert_eq(
        dict(a=a, b=b),
        """SELECT a, FIRST(b) AS fb, LAST(b) AS lb
            FROM a GROUP BY a""",
        [[0, 1, 2], [1, 3, 3]],
        ["a", "fb", "lb"],
    )

    # select tests
    a = pd.DataFrame([[0, 1], [0, 2], [3, 2]], columns=["a", "b"])
    assert_eq(
        dict(a=a),
        """SELECT a,SUM(b) AS sa FROM a GROUP BY a
        """,
        [[0, 3], [3, 2]],
        ["a", "sa"],
    )
    assert_eq(
        dict(a=a),
        """SELECT a AS x,SUM(b) AS sa FROM a GROUP BY a
        """,
        [[0, 3], [3, 2]],
        ["x", "sa"],
    )
    a = pd.DataFrame([[0, 1, 4], [0, 2, 5], [3, 2, 6]], columns=["a", "b", "c"])
    assert_eq(
        dict(a=a),
        """SELECT a,SUM(b)+SUM(c) AS s, SUM(b*c) AS t FROM a GROUP BY a
        """,
        [[0, 12, 14], [3, 8, 12]],
        ["a", "s", "t"],
    )
    assert_eq(
        dict(a=a),
        """SELECT a,SUM(b)+a AS s FROM a GROUP BY a
        """,
        [[0, 3], [3, 5]],
        ["a", "s"],
    )

    # where
    assert_eq(
        dict(a=a),
        """SELECT a,SUM(b*b) AS sa FROM a WHERE b=2 GROUP BY a
        """,
        [[0, 4], [3, 4]],
        ["a", "sa"],
    )

    # having
    assert_eq(
        dict(a=a),
        """SELECT a,SUM(b*b) AS sa FROM a WHERE b=2 GROUP BY a
            HAVING SUM(b*b)=4 AND a=0
        """,
        [[0, 4]],
        ["a", "sa"],
    )
    assert_eq(
        dict(a=a),
        """SELECT a,SUM(b*b) AS sa FROM a GROUP BY a
            HAVING SUM(a+b)=3
        """,
        [[0, 5]],
        ["a", "sa"],
    )


def test_agg_count():
    a = pd.DataFrame([[0, 1], [0, 2], [1, 3]], columns=["a", "b"])
    b = pd.DataFrame([[0, 20], [2, 3]], columns=["a", "c"])
    assert_eq(
        dict(a=a, b=b),
        """SELECT a, COUNT() AS b FROM a GROUP BY a""",
        [[0, 2], [1, 1]],
        ["a", "b"],
    )
    assert_eq(
        dict(a=a, b=b),
        """SELECT a, COUNT(DISTINCT b) AS b FROM a GROUP BY a""",
        [[0, 2], [1, 1]],
        ["a", "b"],
    )
    a = pd.DataFrame(
        [[0, 1, None], [0, 1, None], [0, 4, 1], [1, None, None], [None, None, None]],
        columns=["a", "b", "c"],
    )
    nan = float("nan")
    assert_eq(
        dict(a=a),
        """
        SELECT
            a AS a1,
            COUNT(DISTINCT *) AS a2,
            c AS a3,
            COUNT(*) AS a4,
            MIN(c) AS a5,
            COUNT(DISTINCT b,c) AS a6
        FROM a GROUP BY a
        """,
        [[0, 2, nan, 3, 1, 2], [1, 1, nan, 1, nan, 1], [nan, 1, nan, 1, nan, 1]],
        ["a1", "a2", "a3", "a4", "a5", "a6"],
    )


def test_agg_no_groupby():
    # TODO: should also test this with group by
    a = pd.DataFrame(
        [[0, 1, None], [0, 1, None], [0, 4, 1], [1, None, None], [None, None, None]],
        columns=["a", "b", "c"],
    )
    assert_eq(
        dict(a=a),
        """
        SELECT
            FIRST(c) AS a,                  -- None
            FIRST(c IGNORE NULLS) AS b,     -- 1
            LAST(b) AS c,                   -- None
            LAST(b IGNORE NULLS) AS d,      -- 4
            MIN(a) AS e,                    -- 0
            MAX(a) AS f,                    -- 1
            AVG(b) AS g,                    -- 2
            SUM(b) AS h,                    -- 6
            COUNT(b) AS i,                  -- 3
            COUNT(DISTINCT b) AS j,         -- 2
            COUNT(*) AS k,                  -- 5
            COUNT(DISTINCT *) AS l,         -- 4
            COUNT(b, c) AS m,               -- 5
            COUNT(DISTINCT b, c) AS n       -- 3
        FROM a
        """,
        [[None, 1, None, 4, 0, 1, 2, 6, 3, 2, 5, 4, 5, 3]],
        list("abcdefghijklmn"),
    )


def test_join_agg():
    a = pd.DataFrame([[0, 1], [0, 2], [2, 3]], columns=["a", "b"])
    b = pd.DataFrame([[0, 20], [2, 30]], columns=["a", "c"])
    assert_eq(
        dict(a=a, b=b),
        """
        SELECT a.a,SUM(a.b)+SUM(c) AS x FROM a
        INNER JOIN b ON a.a=b.a
        WHERE c>=20
        GROUP BY a.a
        """,
        [[0, 43], [2, 33]],
        ["a", "x"],
    )
    assert_eq(
        dict(a=a, b=b),
        """
        SELECT a.a AS y,SUM(a.b)+SUM(c) AS x FROM a
        INNER JOIN b ON a.a=b.a
        WHERE c>=20
        GROUP BY a.a
        HAVING SUM(a.b)+SUM(c)<40
        """,
        [[2, 33]],
        ["y", "x"],
    )


def test_window():
    a = pd.DataFrame([[0, 1], [0, 4], [2, 3]], columns=["a", "b"])
    assert_eq(
        dict(a=a),
        """
        SELECT *, ROW_NUMBER() OVER () AS x
        FROM a
        """,
        [[0, 1, 1], [0, 4, 2], [2, 3, 3]],
        ["a", "b", "x"],
    )
    assert_eq(
        dict(a=a),
        """
        SELECT *, ROW_NUMBER() OVER (PARTITION BY a) AS x
        FROM a
        """,
        [[0, 1, 1], [0, 4, 2], [2, 3, 1]],
        ["a", "b", "x"],
    )
    assert_eq(
        dict(a=a),
        """
        SELECT *, ROW_NUMBER() OVER (ORDER BY b DESC) AS x
        FROM a
        """,
        [[0, 1, 3], [0, 4, 1], [2, 3, 2]],
        ["a", "b", "x"],
    )
    assert_eq(
        dict(a=a),
        """
        SELECT *, ROW_NUMBER() OVER (ORDER BY a ASC, b DESC) AS x
        FROM a
        """,
        [[0, 1, 2], [0, 4, 1], [2, 3, 3]],
        ["a", "b", "x"],
    )
    assert_eq(
        dict(a=a),
        """
        SELECT *, ROW_NUMBER() OVER (PARTITION BY a ORDER BY a,b DESC) AS x
        FROM a
        """,
        [[0, 1, 2], [0, 4, 1], [2, 3, 1]],
        ["a", "b", "x"],
    )
    assert_eq(
        dict(a=a),
        """
        SELECT *,
            ROW_NUMBER() OVER () AS c,
            ROW_NUMBER() OVER (PARTITION BY a) AS d,
            ROW_NUMBER() OVER (ORDER BY b DESC) AS e,
            ROW_NUMBER() OVER (ORDER BY a ASC, b DESC) AS f,
            ROW_NUMBER() OVER (PARTITION BY a ORDER BY a,b DESC) AS g
        FROM a
        """,
        [[0, 1, 1, 1, 3, 2, 2], [0, 4, 2, 2, 1, 1, 1], [2, 3, 3, 1, 2, 3, 1]],
        list("abcdefg"),
    )

    # if ordering by single column, the behavior should follow the SQL behavior on nulls
    # if ordering by multiple columns, the behavior may not follow
    # the SQL behavior on nulls because pandas does not support different na_positions
    # for each order by column
    a = pd.DataFrame([[0, 1], [0, 2], [0, None], [None, 3]], columns=["a", "b"])
    assert_eq(
        dict(a=a),
        """
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY a ORDER BY b DESC NULLS FIRST) AS c,
            ROW_NUMBER() OVER (PARTITION BY a ORDER BY b DESC NULLS LAST) AS d,
            ROW_NUMBER() OVER (PARTITION BY a ORDER BY b NULLS FIRST) AS e,
            ROW_NUMBER() OVER (PARTITION BY a ORDER BY b NULLS LAST) AS f,
            ROW_NUMBER() OVER (PARTITION BY a ORDER BY b DESC) AS g,
            ROW_NUMBER() OVER (PARTITION BY a ORDER BY b) AS h
        FROM a
        """,
        [
            [0, 1, 3, 2, 2, 1, 2, 2],
            [0, 2, 2, 1, 3, 2, 1, 3],
            [0, None, 1, 3, 1, 3, 3, 1],
            [None, 3, 1, 1, 1, 1, 1, 1],
        ],
        list("abcdefgh"),
    )


def test_inline_table():
    a = pd.DataFrame([[0, 1], [0, 4], [2, 3]], columns=["a", "b"])
    assert_eq(
        dict(a=a),
        """
        SELECT * FROM (SELECT * FROM a) AS b
        """,
        [[0, 1], [0, 4], [2, 3]],
        ["a", "b"],
    )
    assert_eq(
        dict(a=a),
        """
        SELECT * FROM (SELECT a AS aa, b AS bb FROM a) AS b
        """,
        [[0, 1], [0, 4], [2, 3]],
        ["aa", "bb"],
    )
    assert_eq(
        dict(a=a),
        """
        SELECT * FROM (SELECT a AS aa, b AS bb FROM a) AS a
        """,
        [[0, 1], [0, 4], [2, 3]],
        ["aa", "bb"],
    )
    assert_eq(
        dict(a=a),
        """
        SELECT * FROM (SELECT aa AS aaa, bb AS bbb FROM
            (SELECT a AS aa, b AS bb FROM a) AS a) AS a
        """,
        [[0, 1], [0, 4], [2, 3]],
        ["aaa", "bbb"],
    )

    assert_eq(
        dict(a=a),
        """
        SELECT * FROM (SELECT a AS aa, b AS bb FROM a)
        """,
        [[0, 1], [0, 4], [2, 3]],
        ["aa", "bb"],
    )
    assert_eq(
        dict(a=a),
        """
        SELECT * FROM (SELECT aa AS aaa, bb AS bbb FROM
            (SELECT a AS aa, b AS bb FROM a))
        """,
        [[0, 1], [0, 4], [2, 3]],
        ["aaa", "bbb"],
    )

    a = pd.DataFrame([[0, 1], [0, 4], [2, 3]], columns=["a", "b"])
    b = pd.DataFrame([[0, 10], [2, 30]], columns=["c", "d"])
    assert_eq(
        dict(a=a, b=b),
        """
        SELECT aa.*,d FROM
            (SELECT * FROM a WHERE a>0) AS aa INNER JOIN
            (SELECT c AS a, d FROM b) AS bb
            ON aa.a=bb.a
        """,
        [[2, 3, 30]],
        ["a", "b", "d"],
    )


def test_union():
    a = pd.DataFrame([["x", "a"], ["x", "a"], [None, None]], columns=["a", "b"])
    b = pd.DataFrame([["xx", "aa"], [None, None], ["a", "x"]], columns=["b", "a"])
    c = pd.DataFrame([["c", "d"]], columns=["a", "b"])
    assert_eq(
        dict(a=a, b=b),
        """
        SELECT * FROM a UNION SELECT * FROM b
        """,
        [["x", "a"], [None, None], ["xx", "aa"], ["a", "x"]],
        ["a", "b"],
    )
    assert_eq(
        dict(a=a, b=b),
        """
        SELECT * FROM a UNION DISTINCT SELECT * FROM b
        """,
        [["x", "a"], [None, None], ["xx", "aa"], ["a", "x"]],
        ["a", "b"],
    )
    assert_eq(
        dict(a=a, b=b),
        """
        SELECT * FROM a UNION ALL SELECT * FROM b
        """,
        [["x", "a"], ["x", "a"], [None, None], ["xx", "aa"], [None, None], ["a", "x"]],
        ["a", "b"],
    )
    assert_eq(
        dict(a=a, b=b, c=c),
        """
        SELECT * FROM a UNION SELECT * FROM b UNION SELECT * FROM c
        """,
        [["x", "a"], [None, None], ["xx", "aa"], ["a", "x"], ["c", "d"]],
        ["a", "b"],
    )


def test_intersect():
    a = pd.DataFrame([["x", "a"], ["x", "a"], [None, None]], columns=["a", "b"])
    b = pd.DataFrame(
        [["xx", "aa"], [None, None], [None, None], ["a", "x"]], columns=["b", "a"]
    )
    c = pd.DataFrame([["c", "d"], [None, None]], columns=["a", "b"])
    assert_eq(
        dict(a=a, b=b),
        """
        SELECT * FROM a INTERSECT SELECT * FROM b
        """,
        [[None, None]],
        ["a", "b"],
    )
    assert_eq(
        dict(a=a, b=b),
        """
        SELECT * FROM a INTERSECT DISTINCT SELECT * FROM b
        """,
        [[None, None]],
        ["a", "b"],
    )
    assert_eq(
        dict(a=a, b=b, c=c),
        """
        SELECT * FROM a
            INTERSECT ALL SELECT * FROM b
            INTERSECT ALL SELECT * FROM c
        """,
        [[None, None]],
        ["a", "b"],
    )


def test_except():
    a = pd.DataFrame([["x", "a"], ["x", "a"], [None, None]], columns=["a", "b"])
    b = pd.DataFrame(
        [["xx", "aa"], [None, None], [None, None], ["a", "x"]], columns=["b", "a"]
    )
    c = pd.DataFrame([["c", "d"], [None, None]], columns=["a", "b"])
    assert_eq(
        dict(a=a, b=b),
        """
        SELECT * FROM a EXCEPT SELECT * FROM b
        """,
        [["x", "a"]],
        ["a", "b"],
    )
    assert_eq(
        dict(a=a, b=b),
        """
        SELECT * FROM a EXCEPT DISTINCT SELECT * FROM b
        """,
        [["x", "a"]],
        ["a", "b"],
    )
    assert_eq(
        dict(a=a, b=b, c=c),
        """
        SELECT * FROM a EXCEPT ALL SELECT * FROM b EXCEPT ALL SELECT * FROM c
        """,
        [["x", "a"], ["x", "a"]],
        ["a", "b"],
    )


def test_with():
    a = pd.DataFrame([[1, "a"], [2, "b"]], columns=["a", "b"])
    b = pd.DataFrame([[1, "b"], [4, "bb"]], columns=["a", "b"])
    assert_eq(
        dict(a=a, b=b),
        """
        WITH
            a AS (
                SELECT a AS aa, b AS bb FROM a
            ),
            c AS (
                SELECT aa-1 AS aa, bb FROM a
            )
        SELECT * FROM c UNION SELECT * FROM b
        """,
        [[0, "a"], [1, "b"], [4, "bb"]],
        ["aa", "bb"],
    )


def assert_eq(dfs, sql, expected, expected_cols):
    df = _run(sql, **dfs)
    assert_df_eq(df, expected, expected_cols)


def _run(sql, **kwargs):
    return _debug_run(sql, "singleStatement", StatementVisitor, **kwargs)[0]


def _debug_run(sql, rule, visitor, **kwargs):
    sql = QPDSql(sql, rule)
    ctx = QPDWorkflowContext(QPDPandasEngine(), kwargs)
    wf = QPDWorkflow(ctx)
    v = visitor(
        VisitorContext(
            sql=sql, workflow=wf, dfs=wf.dfs
        )
    )
    wf.assemble_output(v.visit(sql.tree))
    wf.run()
    return ctx.result, v
