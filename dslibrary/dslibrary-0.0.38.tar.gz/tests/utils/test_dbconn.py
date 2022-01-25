import unittest
from dslibrary.utils import dbconn
from dslibrary.utils.dbconn import sql_enquote_id


class TestDBConn(unittest.TestCase):

    def test__is_read_operation(self):
        assert dbconn._is_read_operation("\nselect\n  something") is True
        assert dbconn._is_read_operation("insert whatever") is False
        assert dbconn._is_read_operation("Select x") is True
        assert dbconn._is_read_operation("show databases") is True

    def test__is_table_name(self):
        for v in ["", "select something", "a b", "`table` x", "4"]:
            assert dbconn._is_table_name(v) is None
        for v, expect in {"x": "x", "_x": "_x", "`x`": "x", "x4": "x4", '"x"': "x", "[x]": "x", "_": "_", "` `": " "}.items():
            assert dbconn._is_table_name(v) == expect

    def test_read(self):
        log = []
        cols = ("c1", "c2")
        rows = [(1, 2), (10, 20), (100, 200), (1000, 2000)]
        def read(operation, parameters):
            log.append((operation, parameters))
            return tuple([col] + [None]*5 for col in cols), rows, None
        cursor = dbconn.Connection(read).cursor()
        cursor.execute("select %s, %s", ("a", "b"))
        assert log[0] == ("select %s, %s", ["a", "b"])
        descr = cursor.description
        assert descr[0][0] == cols[0]
        assert descr[1][0] == cols[1]
        assert cursor.rowcount == 4
        assert cursor.fetchone() == rows[0]
        assert cursor.fetchmany(2) == [rows[1], rows[2]]
        assert cursor.fetchall() == [rows[3]]
        assert cursor.fetchone() is None
        assert cursor.fetchmany(1) == []
        assert cursor.fetchall() == []
        # table only
        log.clear()
        cursor.execute("table")
        assert log == [('select * from "table"', [])]
        descr = cursor.description
        assert descr[0][0] == cols[0]
        assert descr[1][0] == cols[1]
        assert cursor.fetchall() == rows

    def test_read_mult(self):
        log = []
        cols = ("c1", "c2")
        rows = [(1, 2), (10, 20)]
        def read(operation, parameters):
            log.append((operation, parameters))
            return tuple([col] + [None]*5 for col in cols), rows, None
        cursor = dbconn.Connection(read).cursor()
        cursor.execute("select %s; select %s", ("a", "b"))
        assert len(log) == 1
        assert log[0] == ("select %s", ["a"])
        assert cursor.fetchall() == rows
        cursor.nextset()
        assert len(log) == 2
        assert log[1] == ("select %s", ["b"])
        assert cursor.fetchall() == rows
        self.assertRaises(Exception, lambda: cursor.nextset())

    def test_write(self):
        log = []
        def read(operation, parameters):
            raise Exception()
        def write(operation, parameters):
            log.append((operation, parameters))
        cursor = dbconn.Connection(read, write).cursor()
        cursor.execute("update 1")
        assert log[0] == ('update 1', None)
        log.clear()
        cursor.executemany("update %s", [(1,), (2,)])
        assert log[0] == ('update %s', (1,))
        assert log[1] == ('update %s', (2,))

    def test_read_quotes(self):
        log = []
        cols = ("c1", "c2")
        rows = [(1, 2), (10, 20), (100, 200), (1000, 2000)]
        def read(operation, parameters):
            log.append((operation, parameters))
            return tuple([col] + [None]*5 for col in cols), rows, None
        cursor = dbconn.Connection(read).cursor()
        cursor.execute('select * from "quoted"')
        assert log[0] == ('select * from "quoted"', [])

    def test_read_more(self):
        cols = ("c1",)
        for mode in ["fetchone", "fetchall", "fetchmany"]:
            rows = [(_,) for _ in range(100)]
            def chunk():
                out = []
                for _ in range(30):
                    if not rows:
                        break
                    out.append(rows.pop(0))
                return out

            def read(operation, parameters):
                out = chunk()
                return cols, out, 1
            def read_more(more):
                out = chunk()
                return out, 1 if rows else None
            cursor = dbconn.Connection(read, read_more=read_more).cursor()
            cursor.execute('select ...')
            if mode == "fetchone":
                for _ in range(100):
                    assert cursor.fetchone() == (_,)
                assert cursor.fetchone() is None
            elif mode == "fetchmany":
                batch = cursor.fetchmany(25)
                assert batch == [(_,) for _ in range(25)]
                batch = cursor.fetchmany(100)
                assert batch == [(_,) for _ in range(25, 100)]
                assert cursor.fetchmany(100) == []
            elif mode == "fetchall":
                batch = cursor.fetchall()
                assert batch == [(_,) for _ in range(100)]
                assert cursor.fetchall() == []

    # TODO it doesn't many any sense to emulate sqlite - remove all of this code
    '''
    def test_to_sql(self):
        log = []
        df = pandas.DataFrame({"x": [1, 2]})
        def read(operation, parameters):
            if "sqlite_master" in operation:
                return ["name"], [], None
            raise Exception()
        def write(operation, parameters):
            log.append((operation, parameters))
        conn = dbconn.Connection(read, write)
        df.to_sql("TABLE", conn)
        assert "CREATE TABLE" in log[0][0]
        assert "CREATE INDEX" in log[1][0]
        assert "INSERT INTO" in log[2][0]
        assert "INSERT INTO" in log[3][0]
    '''

    def test_misc(self):
        cols = ("c1", "c2")
        rows = [(1, 2), (10, 20), (100, 200), (1000, 2000)]
        def read(operation, *parameters):
            return tuple([col] + [None]*5 for col in cols), rows, None
        cursor = dbconn.Connection(read).cursor()
        rows = list(cursor.execute("select * from X"))
        cols = [v[0] for v in cursor.description]
        assert rows == [(1, 2), (10, 20), (100, 200), (1000, 2000)]
        assert cols == ["c1", "c2"]

    def test_limited_cache_size(self):
        """
        Rows would pile up forever if we didn't throw them out.
        """
        cols = ("x", None, None, None, None, None)
        def read(operation, *parameters):
            return cols, [[_] for _ in range(2000)], None
        cursor = dbconn.Connection(read).cursor()
        cursor.execute("whatever")
        rows = cursor.fetchmany(1500)
        assert rows == [[_] for _ in range(1500)]
        rows = cursor.fetchmany(100)
        assert rows == [[_] for _ in range(1500, 1600)]
        assert len(cursor._rows) == 500, "here we see the cache has been truncated"
        rows = cursor.fetchall()
        assert rows == [[_] for _ in range(1600, 2000)]

    def test_sql_enquote_id(self):
        self.assertEqual(sql_enquote_id("x"), 'x')
        self.assertEqual(sql_enquote_id("x y"), '"x y"')
        self.assertEqual(sql_enquote_id("x", always=True), '"x"')
        self.assertEqual(sql_enquote_id("x", dotted=True), 'x')
        self.assertEqual(sql_enquote_id("x.y", dotted=True), 'x.y')
        self.assertEqual(sql_enquote_id("x.y z", dotted=True), 'x."y z"')
        self.assertEqual(sql_enquote_id(("x", "y")), 'x.y')
        self.assertEqual(sql_enquote_id(("x", "y z")), 'x."y z"')
        self.assertEqual(sql_enquote_id("x", always=True, mode="mysql"), '`x`')
        self.assertEqual(sql_enquote_id("AbC", "mysql"), 'AbC')
        self.assertEqual(sql_enquote_id("AbC", "postgres"), '"AbC"')
