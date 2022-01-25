import unittest
import pickle
import tempfile
import zipfile
import io
import pandas

from dslibrary.front import DSLibraryException
from dslibrary.transport.to_mmlibrary import DSLibraryViaMMLibrary


class TestToMMLibrary(unittest.TestCase):

    def test_resources(self):
        resources = {}
        class MyMM(object):
            def get_binary_from_resource(self, resource_name):
                return resources[resource_name]
            def save_binary_to_resource(self, resource_name, data):
                resources[resource_name] = data
        dsl = DSLibraryViaMMLibrary(_mm=MyMM())
        with dsl.open_resource("a", mode='w') as f_w:
            f_w.write("hello")
        with dsl.open_resource("a", mode="r") as f_r:
            assert f_r.read() == "hello"
        with dsl.open_resource("a", mode='wb') as f_w:
            f_w.write(b"hello")
        with dsl.open_resource("a", mode="rb") as f_r:
            assert f_r.read() == b"hello"

    def test_parameters(self):
        params = {"x": 1}
        class MyMM(object):
            def get_argument(self, name):
                return params[name]
            param_dictionary = params
        dsl = DSLibraryViaMMLibrary(_mm=MyMM())
        r = dsl.get_parameters()
        assert r == {"x": 1}
        dsl.get_parameter("x")
        assert dsl.get_parameter("y", 222) == 222

    def test_open_run_data(self):
        class MyMM(object):
            def __init__(self):
                self.data = b''
            def save_temporary_data(self, data):
                self.data = data
            def get_temporary_data(self):
                return self.data
        dsl = DSLibraryViaMMLibrary(_mm=MyMM())
        # strings, bytes
        with dsl.open_run_data("x", mode='w') as f_w:
            f_w.write("this is x")
        with dsl.open_run_data("y", mode='wb') as f_w:
            f_w.write(b"this is y")
        with dsl.open_run_data("x", mode='r') as f_r:
            assert f_r.read() == "this is x"
        with dsl.open_run_data("y", mode='rb') as f_r:
            assert f_r.read() == b"this is y"
        self.assertRaises(FileNotFoundError, lambda: dsl.open_run_data("z", mode='rb'))
        # dataframe
        df = pandas.DataFrame({"x": [4, 5, 6]})
        dsl.write_run_data("modeldata.csv", df)
        with dsl.open_run_data("modeldata.csv", mode='r') as f_r:
            self.assertEqual(f_r.read(), "x\n4\n5\n6\n")

    def test_write_run_data__non_json_data(self):
        """
        Pre-existing mmlibrary.save_temporary_data() is not JSON.
        """
        class MyMM(object):
            def __init__(self):
                self.data = b'xyz'
            def save_temporary_data(self, data):
                self.data = data
            def get_temporary_data(self):
                return self.data
        dsl = DSLibraryViaMMLibrary(_mm=MyMM())
        # dataframe
        df = pandas.DataFrame({"x": [4, 5, 6]})
        self.assertWarns(Warning, lambda: dsl.write_run_data("modeldata.csv", df))
        with dsl.open_run_data("modeldata.csv", mode='r') as f_r:
            self.assertEqual(f_r.read(), "x\n4\n5\n6\n")

    def test_load_dataframe__default_options(self):
        """
        You can supply default options for loading a CSV file.
        """
        class MyMM(object):
            def get_binary_from_resource(self, resource_name):
                return b'a\tb\n1\t2\n3\t4\n'
        dsl = DSLibraryViaMMLibrary(_mm=MyMM())
        df = dsl.load_dataframe("x.csv", format_options={"delimiter": "\t"})
        assert list(df.columns) == ["a", "b"]
        assert list(df.a) == [1, 3]

    def test_get_sql_connection(self):
        class MyMM(object):
            def get_db_connection(self, resource_name):
                return resource_name
        dsl = DSLibraryViaMMLibrary(_mm=MyMM())
        r = dsl.get_sql_connection("x")
        self.assertEqual(r, "x")

    def test_load_pickled_model(self):
        with tempfile.NamedTemporaryFile() as f_tmp:
            pickle.dump({"x": 1}, f_tmp)
            f_tmp.flush()
            class MyMM(object):
                def get_model(self):
                    return f_tmp.name
            dsl = DSLibraryViaMMLibrary(_mm=MyMM())
            r = dsl.load_pickled_model()
            self.assertEqual(r, {"x": 1})

    def test_save_pickled_model(self):
        log = []
        class MyMM(object):
            def new_version(self, data):
                log.append(data)
        dsl = DSLibraryViaMMLibrary(_mm=MyMM())
        dsl.save_pickled_model({"x": 1})
        self.assertEqual(pickle.loads(log[0]), {"x": 1})

    def test_open_model_binary__parts(self):
        """
        You can send a ZIP file for the model-binary, and then use the 'part' argument of open_model_binary() to access them.
        """
        with tempfile.NamedTemporaryFile() as f_tmp:
            with zipfile.ZipFile(f_tmp, mode='w') as zf:
                zf.writestr("a", "AAA")
                zf.writestr("b", "BBB")
            f_tmp.flush()
            class MyMM(object):
                def get_model(self):
                    return f_tmp.name
            dsl = DSLibraryViaMMLibrary(_mm=MyMM())
            with dsl.open_model_binary("a", "r") as f_r:
                self.assertEqual(f_r.read(), "AAA")
            with dsl.open_model_binary("b", "r") as f_r:
                self.assertEqual(f_r.read(), "BBB")

    def test_named_filesystem_via_get_db_connection(self):
        """
        Access to something like an S3 bucket - with no implementation of a bucket_name override.
        """
        class MyMM(object):
            def get_db_connection(self, resource_name):
                assert resource_name == "fs123"
                class FH(object):
                    def open(self, filename, mode, **kwargs):
                        assert filename == "name"
                        assert mode == "r"
                        return io.StringIO("xyz")
                return FH()
        dsl = DSLibraryViaMMLibrary(_mm=MyMM())
        # bucket_name can't be overridden in this case
        self.assertRaises(DSLibraryException, lambda: dsl.open_resource("name", mode="r", filesystem="fs123", bucket_name="b1"))
        # we can use the data connection without a bucket_name override
        r = dsl.open_resource("name", mode="r", filesystem="fs123")
        assert r.read() == "xyz"

    def test_get_db_connection__db_or_bucket(self):
        """
        Read from s3 with a bucket_name override in the mmlibrary implementation.
        """
        class MyMM(object):
            def get_db_connection(self, resource_name, _db_or_bucket=None):
                assert resource_name == "fs123"
                assert _db_or_bucket == "b1"
                class FH(object):
                    def open(self, filename, mode, **kwargs):
                        assert filename == "name"
                        assert mode == "r"
                        return io.StringIO("xyz")
                return FH()
        dsl = DSLibraryViaMMLibrary(_mm=MyMM())
        r = dsl.open_resource("name", mode="r", filesystem="fs123", bucket_name="b1")
        assert r.read() == "xyz"
