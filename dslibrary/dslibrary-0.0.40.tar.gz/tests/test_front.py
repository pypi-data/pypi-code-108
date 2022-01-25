import unittest
import mock
import io
import os
import numpy
import pandas
import shutil
import tempfile
import yaml
import dask.dataframe

from dslibrary import DSLibrary
from dslibrary.front import EVALUATION_RESULT_ALIAS, METRICS_ALIAS, DSLibraryException, DSLibraryDataFormatException
from dslibrary.metadata import Metadata
from dslibrary.transport.to_local import DSLibraryLocal
from dslibrary.utils.file_utils import write_stream_with_read_on_close


class TestFront(unittest.TestCase):

    def test_metadata(self):
        """
        The base class doesn't know how to get metadata so it returns a null instance.
        """
        dsl = DSLibrary()
        m = dsl.get_metadata()
        assert isinstance(m, Metadata)
        assert m.uri == ""
        assert m.entry_points == {}

    def test_open_resource__input_mapping(self):
        """
        Options for input come from mapping values, which override supplied values.
        """
        log = []
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                log.append((path, mode, kwargs))
                return "H"
        MyInst(spec={"inputs": {"a": {"uri": "aaa", "option1": 1, "option3": 3}}}).open_resource("a", option1=2, option2=22)
        assert log[0] == ('aaa', 'rb', {'option1': 1, 'option2': 22, 'option3': 3}), log[0]

    def test_open_resource__output_mapping(self):
        """
        Options for output come from mapping values, which override supplied values.
        """
        log = []
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                log.append((path, mode, kwargs))
                return "H"
        MyInst(spec={"outputs": {"a": {"uri": "aaa", "option1": 1, "option3": 3}}}).open_resource("a", 'w', option1=2, option2=22)
        self.assertEqual(log[0], ('aaa', 'w', {'option1': 1, 'option2': 22, 'option3': 3}))

    def test_open_resource__bypass_mapping(self):
        """
        Most inputs and outputs are mapped, but you can bypass mapping and specify a URI to open or a local file.
        """
        log = []
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                log.append((path, mode, kwargs))
                return "H"
        MyInst().open_resource("s3://bucket/path", open_option_1=1)
        assert log[0] == ('s3://bucket/path', 'rb', {'open_option_1': 1})
        MyInst().open_resource("./local/file")
        assert log[1] == ('./local/file', 'rb', {})

    def test_open_model_binary(self):
        """
        The default implementation just assumes certain filenames for the 'model-binary' data.
        """
        log = []
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                log.append((path, mode, kwargs))
                return "H"
        MyInst().open_model_binary()
        assert log[0] == ('model-binary', 'rb', {})
        MyInst().open_model_binary("part1")
        assert log[1] == ('model-binary/part1', 'rb', {})

    def test_set_evaluation_result(self):
        """
        Model evaluation code can use this hook to report whether the model passed or failed.
        """
        log = []
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                buf = io.StringIO()
                buf.close = lambda: None
                log.append((path, buf))
                return buf
        MyInst().set_evaluation_result(True)
        MyInst().set_evaluation_result(False, reason="because")
        assert log[0][0] == log[1][0] == EVALUATION_RESULT_ALIAS
        r = log[0][1].getvalue()
        assert r == '{"uri": "", "success": true}\n', r
        r = log[1][1].getvalue()
        assert r == '{"uri": "", "success": false, "reason": "because"}\n', r

    def test_get_sql_connection__mapping(self):
        """
        The normal use case is have the caller supply all the connection information.
        """
        dsl = DSLibrary(spec={"inputs": {"db": {"uri": "mysql://host/db", "username": "u"}}})
        with mock.patch("pymysql.connect", connect):
            r = dsl.get_sql_connection("db")
            assert r == "CONN"

    def test_load_dataframe_from_sql__flavors(self):
        """
        SQL has to be quoted different for different engines.
        """
        dsl = DSLibrary()
        for flavor in ("postgres", "mysql"):
            log = []

            def connect(uri, **kwargs):
                self.assertEqual(uri, 'postgresql://host/database')
                self.assertEqual(kwargs["username"], "u")
                class DbCursor(object):
                    description = [("x", None)]
                    def execute(self, sql):
                        log.append(sql)
                    def __iter__(self):
                        return iter([(1,), (2,)])
                class DbConn(object):
                    def cursor(self):
                        return DbCursor()
                    def close(self):
                        pass
                    _flavor = flavor
                return DbConn()
            with mock.patch("dslibrary.front.connect_to_database", connect):
                r = dsl.load_dataframe("postgresql://host/database", sql_table="TableName", username="u")
                self.assertEqual(list(r.x), [1, 2])
                if flavor == "postgres":
                    self.assertEqual(log, ['SELECT * from "TableName"'])
                else:
                    self.assertEqual(log, ['SELECT * from TableName'])

    def test_write_resources__dataframes_and_series(self):
        """
        Several types are supported for columnar data.
        """
        log = []
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                buf = io.StringIO()
                buf.close = lambda: None
                log.append((path, buf))
                return buf
        dsl = MyInst()
        # series
        dsl.write_resource("x", pandas.Series([1, 2, 3]))
        assert log[0][0] == "x"
        self.assertEqual(log[0][1].getvalue(), 'col1\n1\n2\n3\n')
        log.clear()
        # numpy array
        dsl.write_resource("x", numpy.array([1, 2, 3]))
        assert log[0][0] == "x"
        self.assertEqual(log[0][1].getvalue(), 'col1\n1\n2\n3\n')
        log.clear()
        # dataframe
        dsl.write_resource("x", pandas.DataFrame({"y": [1, 2, 3]}))
        assert log[0][0] == "x"
        self.assertEqual(log[0][1].getvalue(), 'y\n1\n2\n3\n')
        log.clear()

    def test_default_metrics_output(self):
        project = tempfile.mkdtemp()
        dsl = DSLibraryLocal(project)
        dsl.log_metric("x", 1)
        r = dsl.get_last_metric("x")
        assert r.value == 1
        # verify it was written as JSON
        fn = os.path.join(project, METRICS_ALIAS)
        assert os.path.exists(fn)
        with open(fn, 'r') as f_r:
            assert f_r.read().startswith("{")
        shutil.rmtree(project)

    def test_alt_metrics_output1(self):
        project = tempfile.mkdtemp()
        dsl = DSLibraryLocal(project, spec={"outputs": {METRICS_ALIAS: {"format": "csv"}}})
        dsl.log_metric("x", 1)
        # verify it was written as CSV
        fn = os.path.join(project, METRICS_ALIAS)
        assert os.path.exists(fn)
        with open(fn, 'r') as f_r:
            assert f_r.read().startswith("uri,")
        shutil.rmtree(project)

    def test_alt_metrics_output2(self):
        project = tempfile.mkdtemp()
        dsl = DSLibraryLocal(project, spec={"outputs": {METRICS_ALIAS: {"uri": "metrics.csv"}}})
        dsl.log_metric("x", 1)
        # verify it was written as CSV
        fn = os.path.join(project, "metrics.csv")
        assert os.path.exists(fn)
        with open(fn, 'r') as f_r:
            assert f_r.read().startswith("uri,")
        shutil.rmtree(project)

    def test_model_pickling(self):
        project = tempfile.mkdtemp()
        dsl = DSLibraryLocal(project, spec={"outputs": {METRICS_ALIAS: {"uri": "metrics.csv"}}})
        # save and restore
        my_model = {"x": 1}
        dsl.save_pickled_model(my_model)
        restored = dsl.load_pickled_model()
        assert restored == my_model
        # verify local storage
        assert os.path.exists(project + "/model-binary")
        shutil.rmtree(project)

    def test_open_resource__default_uri(self):
        """
        Specify a name and a default URI, for cleaner overriding.
        """
        log = []
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                log.append((path, kwargs))
                return "H"
        MyInst().open_resource("x", uri="default")
        MyInst(spec={"inputs": {"x": {"uri": "override", "option1": 1}}}).open_resource("x", uri="default")
        self.assertEqual(log, [('default', {}), ('override', {'option1': 1})])

    def test_load_dataframe__default_uri(self):
        log = []
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                log.append(path)
                return io.BytesIO(b"x\n1\n2")
        df = MyInst().load_dataframe("x", uri="default.csv")
        df = MyInst(spec={"inputs": {"x": {"uri": "override.csv"}}}).load_dataframe("x", uri="default.csv")
        self.assertEqual(log[0], 'default.csv')
        self.assertEqual(log[-1], 'override.csv')

    def test_load_dataframe__from_sql(self):
        log = []
        class MyInst(DSLibrary):
            def get_sql_connection(self, resource_name: str, for_write: bool=False, **kwargs):
                class DbCursor(object):
                    description = [("x", None)]
                    def execute(self, sql):
                        log.append(sql)
                    def __iter__(self):
                        return iter([(1,), (2,)])
                class DbConn(object):
                    def cursor(self):
                        return DbCursor()
                    def close(self):
                        log.append("close")
                return DbConn()
        df = MyInst().load_dataframe("x", sql_table="table1")
        self.assertEqual(list(df.x), [1, 2])
        self.assertEqual(log, ['SELECT * from table1', 'close'])

    def test_load_dataframe__from_nosql(self):
        class MyInst(DSLibrary):
            def get_nosql_connection(self, resource_name: str, for_write: bool=False, **kwargs):
                class MyNoSql(object):
                    def query(self, collection, **kwargs):
                        assert collection == "table1"
                        return [{"x": 1}, {"x": 2}]
                return MyNoSql()
        df = MyInst().load_dataframe("x", nosql_collection="table1")
        self.assertEqual(list(df.x), [1, 2])

    def test_load_dataframe__sql__custom_open_args(self):
        """
        Custom arguments can be passed through to get_sql_connection().
        """
        class MyInst(DSLibrary):
            def get_sql_connection(self, resource_name: str, database: str=None, for_write: bool=False, **kwargs):
                assert resource_name == "engine"
                assert database == "db"
                assert kwargs["custom1"] == 123
                class DbCursor(object):
                    description = [("x", None)]
                    def execute(self, sql):
                        pass
                    def __iter__(self):
                        return iter([])
                class DbConn(object):
                    def cursor(self):
                        return DbCursor()
                    def close(self):
                        pass
                return DbConn()
        MyInst().load_dataframe("engine", sql_table="table1", database="db", custom1=123)

    def test_open_resource__named_filesystem(self):
        """
        A resource can be opened through a specified filesystem engine/provider.
        """
        class MyInst(DSLibrary):
            def get_filesystem_connection(self, resource_name: str, for_write: bool=False, **kwargs):
                assert resource_name == "fs"
                assert kwargs.get("custom1") == 111
                class FS(object):
                    def open(self, path, mode):
                        assert path == "path"
                        assert mode == "r"
                        return "FH"
                return FS()
        r = MyInst().open_resource("path", mode="r", filesystem="fs", custom1=111)
        assert r == "FH"

    def test_load_dataframe__named_filesystem(self):
        """
        A dataframe can be opened through a specified filesystem engine/provider.
        """
        class MyInst(DSLibrary):
            def get_filesystem_connection(self, resource_name: str, for_write: bool=False, **kwargs):
                assert resource_name == "fs"
                class FS(object):
                    def open(self, path, mode):
                        assert path == "path"
                        assert mode == "rb"
                        return io.BytesIO(b"x\n1\n2\n3")
                return FS()
        df = MyInst().load_dataframe("path", filesystem="fs", format="csv")
        assert list(df.x) == [1, 2, 3]

    def test_rw_run_data(self):
        writes = {}
        class MyInst(DSLibrary):
            def open_run_data(self, filename: str, mode: str='rb'):
                if mode == 'rb':
                    v = writes[filename].getvalue()
                    return io.BytesIO(v)
                wr = io.BytesIO()
                writes[filename] = wr
                wr.close = lambda: None
                return wr
        dsl = MyInst()
        df = pandas.DataFrame({"x": [1, 2]})
        dsl.write_run_data("x.csv", df)
        self.assertEqual(writes["x.csv"].getvalue(), b'x\n1\n2\n')
        df2 = dsl.load_dataframe("x.csv", run_data=True)
        self.assertEqual(list(df2.x), list(df.x))
        self.assertEqual(dsl.read_run_data("x.csv"), b'x\n1\n2\n')

    def test_open_args_passed_through_to_opener(self):
        log = []
        inst = self
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                log.append(path)
                inst.assertEqual(kwargs, {'arg1': 123})
                return io.BytesIO(b"abc")
        # just a filename
        fh = MyInst().open_resource("x", arg1=123, format="xyz")
        assert fh.read() == b"abc"
        # uri overrides name
        fh = MyInst().open_resource("x", uri="default.csv", arg1=123, format="xyz")
        assert fh.read() == b"abc"
        # input mapping maps 'x' to something else
        fh = MyInst(spec={"inputs": {"x": {"uri": "override.csv"}}}).open_resource("x", uri="default.csv", arg1=123, format="xyz")
        assert fh.read() == b"abc"
        # verify filenames
        self.assertEqual(log, ['x', 'default.csv', 'override.csv'])

    def test_setup_code_paths(self):
        """
        You can cause 'sys.path' to be extended to include particular folders.
        This is normally done using an environment variable.  Here we are just testing the method that applies the
        changes.
        """
        inst = DSLibrary()
        inst._spec = {"code_paths": ["a", "b"]}
        mock_paths = []
        with mock.patch("sys.path", mock_paths):
            inst._setup_code_paths()
        self.assertEqual(mock_paths, ["a", "b"])

    def test_abstract_base_methods(self):
        """
        The methods that have to be filled in raise exceptions when called.
        """
        inst = DSLibrary()
        self.assertRaises(DSLibraryException, lambda: inst._opener("path", mode='r'))
        self.assertRaises(DSLibraryException, lambda: inst.open_run_data("fn"))

    def test_get_filesystem_connection(self):
        """
        The default filesystem accessor.
        """
        inst = DSLibrary()
        log = []
        with mock.patch("dslibrary.front.connect_to_filesystem", lambda **k: log.append(k) or "FS"):
            fs = inst.get_filesystem_connection("resource", for_write=True, arg1=123)
            self.assertEqual(fs, "FS")
        self.assertEqual(log, [{'uri': 'resource', 'for_write': True, 'arg1': 123}])

    def test_get_sql_connection(self):
        """
        The default SQL accessor.
        """
        inst = DSLibrary()
        log = []
        with mock.patch("dslibrary.front.connect_to_database", lambda **k: log.append(k) or "NoSqlConn"):
            fs = inst.get_sql_connection("resource", for_write=True, arg1=123)
            self.assertEqual(fs, "NoSqlConn")
        self.assertEqual(log, [{'uri': 'resource', 'library': None, 'for_write': True, 'arg1': 123}])

    def test_get_nosql_connection(self):
        """
        The default NoSQL accessor.
        """
        inst = DSLibrary()
        log = []
        with mock.patch("dslibrary.front.connect_to_nosql", lambda **k: log.append(k) or "SqlConn"):
            fs = inst.get_nosql_connection("resource", for_write=True, arg1=123)
            self.assertEqual(fs, "SqlConn")
        self.assertEqual(log, [{'uri': 'resource', 'library': None, 'for_write': True, 'arg1': 123}])

    def test_log_mlflow(self):
        inst = DSLibrary()
        inst._mlflow_all = True
        log = []
        with mock.patch("mlflow.log_param", lambda k, v: log.append((k, v))):
            inst.log_param("x", 1)
        self.assertEqual(log, [("x", 1)])
        log.clear()
        with mock.patch("mlflow.log_metric", lambda *a: log.append(a)):
            inst.log_metric("q", 222)
            inst.log_metrics({"z": 9}, step=2)
        self.assertEqual(log, [('q', 222, 0), ('z', 9, 2)])
        log.clear()
        with mock.patch("mlflow.log_dict", lambda *a: log.append(a)):
            inst.log_dict({"x": 1}, "f.json")
        self.assertEqual(log, [({'x': 1}, 'f.json')])
        log.clear()
        with mock.patch("mlflow.log_artifact", lambda *a: log.append(a)):
            inst.log_artifact("f_local", "f_store")
        self.assertEqual(log, [('f_local', 'f_store')])
        log.clear()
        # not a log function but close enough
        self.assertRaises(DSLibraryException, lambda: inst.get_metrics("x"))

    def test_mlflow_start_end(self):
        inst = DSLibrary()
        inst._mlflow_all = True
        log = []
        with mock.patch("mlflow.mlflow.start_run", lambda: log.append("start")):
            with mock.patch("mlflow.mlflow.end_run", lambda: log.append("end")):
                with mock.patch("mlflow.active_run", lambda: log.append("active_run")):
                    # TODO mock this: mlflow.active_run().info.run_id
                    with inst.start_run():
                        pass
        self.assertEqual(log, ['start', 'active_run', 'end'])

    def test_yaml(self):
        data = [
            {"age": 41, "name": {"first": "John", "last": "Smith"}}
        ]
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                return io.StringIO(yaml.dump(data))
        df = MyInst().load_dataframe("data.yaml")
        assert list(df.age) == [41]
        assert list(df["name.first"]) == ["John"]

    def test_xlsx(self):
        fn = os.path.join(os.path.dirname(__file__), "test_data/two_cols.xlsx")
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                return open(path, mode)
        df = MyInst().load_dataframe(fn)
        self.assertEqual(list(df.a), [2, 7])
        self.assertEqual(list(df.b), [5, 9])

    def test_xlsx__unseekable_stream(self):
        """
        The xlsx parser requires a seekable stream, so when we supply an unseekable stream
        it does some special processing.
        """
        fn = os.path.join(os.path.dirname(__file__), "test_data/two_cols.xlsx")
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                with open(path, mode) as f_r:
                    data = f_r.read()
                class Stream(io.RawIOBase):
                    def __init__(self, data):
                        self.data = data
                    def read(self, n=None):
                        if n is None:
                            n = len(self.data)
                        out = self.data[:n]
                        self.data = self.data[n:]
                        return out
                    def readable(self):
                        return True
                    def seekable(self):
                        return False
                    def __enter__(self):
                        return self
                    def __exit__(self, exc_type, exc_val, exc_tb):
                        pass
                return Stream(data)
        df = MyInst().load_dataframe(fn)
        self.assertEqual(list(df.a), [2, 7])
        self.assertEqual(list(df.b), [5, 9])

    def test_load_dataframe__strip_open_args(self):
        inst = self
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                inst.assertEqual(path, "x")
                inst.assertEqual(kwargs, {})
                return io.StringIO("x\n1\n2")
        r = MyInst().load_dataframe("x", dask=False, format="csv", format_options={}, fallback_to_text=False)
        assert list(r.x) == [1, 2]

    def test_load_dataframe__hello(self):
        """
        The default behavior for csv.Sniffer is very strange.  It will detect "L" as the delimiter, simply because
        that letter occurs twice.
        """
        inst = self
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                inst.assertEqual(path, "x")
                inst.assertEqual(kwargs, {})
                return io.StringIO("HELLO")
        r = MyInst().load_dataframe("x", dask=False, format="csv", format_options={}, fallback_to_text=False)
        assert list(r.HELLO) == []

    def test_load_dataframe__empty_cell_case(self):
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                return io.StringIO("x0,x1\nA,\n,B\nD,C")
        df = MyInst().load_dataframe("x.csv")
        self.assertEqual(list(df.fillna(value="").x0), ["A", "", "D"])

    def test_json_case(self):
        x = '{"uri":"","run_id":"","user":"","time":1634234451.674405098,"name":"x","value":1,"step":0}'
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                return io.StringIO(x)
        df = MyInst().load_dataframe("x")
        assert "run_id" in df.columns
        assert "name" in df.columns

    def test_write_resource_sql_table(self):
        log = []
        class MyInst(DSLibrary):
            def get_sql_connection(self, resource_name: str, for_write: bool=False, database=None, **kwargs):
                assert resource_name == "my_pg"
                assert database == "db4"
                class DbCursor(object):
                    def execute(self, sql, params):
                        log.append((sql, params))
                    def __iter__(self):
                        return iter([])
                class DbConn(object):
                    def cursor(self):
                        return DbCursor()
                    def close(self):
                        pass
                return DbConn()
        # JSON data
        MyInst().write_resource("my_pg", {"x": [1, 2, 3]}, append=False, sql_table="tbl1", database="db4")
        self.assertEqual(log, [
            ('DROP TABLE IF EXISTS tbl1', []),
            ('CREATE TABLE IF NOT EXISTS tbl1 (x INTEGER)', []),
            ('INSERT INTO tbl1 (x) VALUES (%s), (%s), (%s)', [1, 2, 3])
        ])
        log.clear()
        # a series
        MyInst().write_resource("my_pg", pandas.Series([1, 2, 3]), append=False, sql_table="tbl1", database="db4")
        self.assertEqual(log, [
            ('DROP TABLE IF EXISTS tbl1', []),
            ('CREATE TABLE IF NOT EXISTS tbl1 (col1 INTEGER)', []),
            ('INSERT INTO tbl1 (col1) VALUES (%s), (%s), (%s)', [1, 2, 3])
        ])

    def test_load_dataframe__dask_autodetect(self):
        """
        Size-based threshold.
        """
        with tempfile.NamedTemporaryFile(suffix=".csv") as f_tmp:
            f_tmp.write(b"x\n1\n2")
            f_tmp.flush()
            class MyInst(DSLibrary):
                def _opener(self, path: str, mode: str, **kwargs):
                    return io.BytesIO(b"x\n1\n2")
            # specifically don't use dask
            df = MyInst().load_dataframe(f_tmp.name, dask=False)
            self.assertIsInstance(df, pandas.DataFrame)
            # specifically do use dask
            df = MyInst().load_dataframe(f_tmp.name, dask=True)
            assert hasattr(df, "dask")
            # high threshold, don't use dask
            df = MyInst().load_dataframe(f_tmp.name, dask=1000)
            self.assertIsInstance(df, pandas.DataFrame)
            # low threshold, do use dask
            df = MyInst().load_dataframe(f_tmp.name, dask=3)
            assert hasattr(df, "dask")

    def test_load_dataframe__from_stream(self):
        """
        An already opened stream can be supplied instead of a named entity.
        """
        stream = io.BytesIO(b"x\n1\n2\n12")
        df = DSLibrary().load_dataframe(stream)
        self.assertEqual(list(df.x), [1, 2, 12])
        stream = io.StringIO("x\n1\n2\n12")
        df = DSLibrary().load_dataframe(stream)
        self.assertEqual(list(df.x), [1, 2, 12])

    def test_load_dataframe__from_iterable(self):
        """
        Data can be supplied to turn into a dataframe.
        """
        df = DSLibrary().load_dataframe({"x": [11, 12, 13]})
        self.assertEqual(list(df.x), [11, 12, 13])
        df = DSLibrary().load_dataframe([{"x": 9}, {"x": 8}])
        self.assertEqual(list(df.x), [9, 8])

    def test_hash_in_uri_for_formmatting_argumets(self):
        """
        Since the '#' has no effect on information returned from a URL, it is a safe place to place formatting arguments.
        """
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                assert path == "x", "the '#' is removed before opening the file"
                return io.BytesIO(b"a,b\n1,2\n2,3")
        # here the default format sniffer guesses there are two columns
        df = MyInst().load_dataframe("x")
        self.assertEqual(list(df.columns), ["a", "b"])
        # here we force the delimited to be a linefeed and now there is only one column
        df = MyInst().load_dataframe("x#delimiter=%0a")
        self.assertEqual(list(df.columns), ["a,b"])

    def test_hdf(self):
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                return open(path, mode)
        fn = os.path.join(os.path.dirname(__file__), "test_data/my.hdf")
        df = MyInst().load_dataframe(fn)
        assert list(df.columns) == ["x"]
        assert list(df.x) == [1, 2, 3]

    def test_report_encoding_error(self):
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                return io.BytesIO(b'a\n1\n2\n3\n\xC0\xC0\xFF\n4\n5\n6')
        try:
            MyInst().load_dataframe("x.csv")
            self.fail("expected error")
        except DSLibraryDataFormatException as err:
            assert "invalid start byte" in err.message
            assert "offset=8" in err.message
        df = MyInst().load_dataframe("x.csv", format_options={"encoding": 'iso8859-1'})
        self.assertEqual(list(df.columns), ["a"])

    def test_report_json_format_error(self):
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                return io.BytesIO(b'{"x":' + b' '*1000)
        try:
            MyInst().load_dataframe("x.json")
            self.fail("expected error")
        except DSLibraryDataFormatException as err:
            assert "JSON format error" in err.message

    def test_rw_folder(self):
        """
        Dask writes data into folders, in the manner of spark.
        """
        for dataframe_type in ("p", "d"):
            tmpdir = tempfile.mkdtemp()
            try:
                class MyInst(DSLibrary):
                    def _opener(self, path: str, mode: str, **kwargs):
                        return open(path, mode)
                fn = os.path.join(tmpdir, "x.csv")
                df = pandas.DataFrame({"x": list(range(100))})
                if dataframe_type == "d":
                    df = dask.dataframe.from_pandas(df, npartitions=2)
                parts = MyInst().write_resource(fn, df, dask=True)
                self.assertEqual(os.listdir(tmpdir), ["x.csv"])
                if dataframe_type == "d":
                    self.assertEqual(os.listdir(fn), ["0.part", "1.part"])
                    assert len(parts) == 2
                else:
                    self.assertEqual(os.listdir(fn), ["0.part"])
                    assert len(parts) == 1
                df = MyInst().load_dataframe(fn, dask=True, format_options={"delimiter": "\n"}).compute()
                self.assertEqual(list(df.x), list(range(100)))
            finally:
                shutil.rmtree(tmpdir)

    def test_write_dask_csv(self):
        """
        Dask is able to write to a single CSV file.
        """
        files = {}
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                files[path] = fh = io.BytesIO()
                fh.close = lambda: None
                return fh
        df = pandas.DataFrame({"x": list(range(7))})
        MyInst().write_resource("x.csv", dask.dataframe.from_pandas(df, npartitions=2), dask=False)
        self.assertEqual(files["x.csv"].getvalue(), b"x\n0\n1\n2\n3\n4\n5\n6\n")

    def test_read_write_resource__to_filesystem(self):
        """
        read_resource() and write_resource() accept a 'filesystem' argument which points them to a particular
        custom filesystem.
        """
        files = {}
        class MyInst(DSLibrary):
            def get_filesystem_connection(self, resource_name: str, for_write: bool=False, **kwargs):
                assert resource_name == "my-s3"
                assert kwargs == {}
                class MyFS(object):
                    def open(self, path, mode='rb'):
                        if 'r' in mode:
                            return io.BytesIO(files[path])
                        assert for_write
                        def written(fh):
                            files[path] = fh.read()
                        return write_stream_with_read_on_close(mode, r_mode='rb', on_close=written)
                return MyFS()
        MyInst().write_resource('new.txt', b'hello123', filesystem='my-s3')
        self.assertEqual(files["new.txt"], b'hello123')
        r = MyInst().read_resource('new.txt', filesystem='my-s3')
        self.assertEqual(r, b'hello123')

    def test_write_resource__dataframe__options(self):
        """
        Store a dataframe, passing options through to pandas to control formatting.
        """
        files = {}
        class MyInst(DSLibrary):
            def _opener(self, path: str, mode: str, **kwargs):
                def store(strm):
                    files[path] = strm.read()
                return write_stream_with_read_on_close(mode, 'r', on_close=store)
        MyInst().write_resource('f', pandas.DataFrame({"x": [1, 2], "y": [10, 20]}), format_options={"format": "csv", "sep": ";"})
        self.assertEqual(files["f"], 'x;y\n1;10\n2;20\n')
