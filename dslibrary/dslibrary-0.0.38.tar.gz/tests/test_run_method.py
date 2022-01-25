import unittest
import os
import json
import mock
import tempfile
import pandas
import shutil

import dslibrary
from dslibrary.front import PARAMS_ALIAS, METRICS_ALIAS
from dslibrary.run_models import ModelRunner
from tests.t_utils import reset_env


class TestRunMethod(unittest.TestCase):
    """
    The ModelRunner.run_method() method lets you call your model's main method directly, for development, testing or
    hyper-parameter tuning.
    """

    def test_run_method__intended_approach(self):
        """
        A dslibrary instance is passed to the code you want to run.
        """
        def my_model(dsl):
            assert dsl.get_parameter("x") == 123
        runner = ModelRunner()
        runner.set_parameter("x", 123)
        runner.run_method(my_model)

    def test_run_method__alternate_approach(self):
        """
        The model can also call dslibrary.instance()
        """
        def my_model():
            dsl = dslibrary.instance()
            assert dsl.get_parameter("x") == 123
        runner = ModelRunner()
        runner.set_parameter("x", 123)
        runner.run_method(my_model)

    def test_run_method__params_to_method(self):
        """
        Or the parameters can just be sent to the method.
        """
        def my_model(dsl, x):
            assert x == 123
        runner = ModelRunner()
        runner.set_parameter("x", 123)
        runner.run_method(my_model)

    def test_params_to_method__coerce_type(self):
        """
        Type annotation is applied.
        """
        def my_model(dsl, x: int):
            assert x == 12
        runner = ModelRunner()
        runner.set_parameter("x", "12")
        runner.run_method(my_model)

    def test_kwargs_to_method(self):
        """
        Method can request that all unspecified parameters be sent in kwargs.
        """
        def my_model(dsl, x, **kwargs):
            assert x == 123
            assert kwargs["y"] == 222
        runner = ModelRunner()
        runner.set_parameter("x", 123)
        runner.set_parameter("y", 222)
        runner.run_method(my_model)

    def test_read_dataframe_from_specified_file_with_format(self):
        """
        The model only knows there is an input called 'input1'.  It requests that it be loaded into a dataframe.
        """
        runner = ModelRunner()
        runner.set_input("input1", os.path.dirname(__file__) + "/test_data/test1.csv", format_options={"delim_whitespace": True})
        def my_model(dsl):
            df = dsl.load_dataframe("input1")
            assert list(df.columns) == ["a", "b"], list(df.columns)
            assert list(df.a) == [1, 2]
            assert list(df.b) == [2, 4]
        runner.run_method(my_model)

    def test_write_dataframe_to_specified_file_with_format(self):
        """
        The model has an output called 'output1', and doesn't want to care where that output data should go or what
        format to use.
        """
        with tempfile.NamedTemporaryFile(suffix=".csv") as f_tmp:
            runner = ModelRunner(uri="uri", entry_point="main")
            runner.set_output("output1", f_tmp.name, format_options={"sep": "\t"})
            def my_model(dsl):
                df = pandas.DataFrame({"x": [1, 2], "y": [3, 4]})
                dsl.write_resource("output1", df)
            runner.run_method(my_model)
            df = pandas.read_csv(f_tmp.name, sep='\t')
            assert list(df.columns) == ["x", "y"]
            assert list(df.x) == [1, 2]
            assert list(df.y) == [3, 4]

    def test_model_parameter_misc(self):
        """
        The model declares the type of its parameters, and such things as default values, validation and coercion
        are taken care of.
        """
        project = tempfile.mkdtemp()
        with open(os.path.join(project, "MLProject"), 'w') as f:
            f.write("entry_points:\n  one:\n    parameters:\n      x: {type: float, default: 2}")
        # pass a parameter
        runner = ModelRunner()
        def my_model_1(dsl):
            assert dsl.get_parameter("x") == 1
        runner.set_parameter("x", 1)
        runner.run_method(my_model_1, path=project)
        # use default parameter
        runner = ModelRunner(entry_point="one")
        def my_model_2(dsl):
            assert dsl.get_parameter("x") == 2
        runner.run_method(my_model_2, path=project)
        # coercion of parameter to type declared in metadata
        runner = ModelRunner(entry_point="one")
        def my_model_3(dsl):
            assert dsl.get_parameter("x") == 1.5
        runner.set_parameter("x", "1.5")
        runner.run_method(my_model_3, path=project)
        # validation of parameter
        runner = ModelRunner(entry_point="one")
        def my_model_4(dsl):
            self.assertRaises(ValueError, lambda: dsl.get_parameter("x"))
        runner.set_parameter("x", "not numeric")
        runner.run_method(my_model_4, path=project)
        # clean up
        shutil.rmtree(project)

    def test_model_parameter_mapping(self):
        """
        Parameters are injected if they match the method's signature.  They are also coerced to the proper types.
        """
        runner = ModelRunner()
        def my_model(dsl, x: int, y: str):
            assert x == 1
            assert y == "2"
            assert dsl.get_parameter("z") == 3
        runner.set_parameter("x", 1).set_parameter("y", "2").set_parameter("z", 3)
        runner.run_method(my_model)
        runner.set_parameter("x", "1").set_parameter("y", 2).set_parameter("z", 3)
        runner.run_method(my_model)

    def test_model_parameter_json_parse_and_schema_check(self):
        """
        In addition to the very limited set of checks the MLProject file specifies, a full JSON schema can be given
        to validate more advanced structures, passed as JSON.
        """
        project = tempfile.mkdtemp()
        with open(os.path.join(project, "MLProject"), 'w') as f:
            f.write("entry_points:\n  one:\n    parameters:\n      x: {type: string, default: 2, schema: {type: object, properties: {a: {type: integer}}}}")
        runner = ModelRunner(entry_point="one")
        def my_model(dsl):
            assert dsl.get_parameter("x") == {"a": 4}
        runner.set_parameter("x", '{"a": 4}')
        runner.run_method(my_model, path=project)
        # clean up
        shutil.rmtree(project)

    def test_load_input_from_sql(self):
        """
        The caller can request that data be loaded from an SQL data source, instead of the usual CSV file.
        """
        runner = ModelRunner()
        log = []
        class Cursor(object):
            def __init__(self):
                self.description = ("a", None), ("b", None)
            def execute(self, sql):
                log.append(sql)
            def __iter__(self):
                return iter([(1, 2), (3, 4)])
        class Conn(object):
            def __init__(self, resource_name, username=None):
                assert username == "xyz"
                log.append(resource_name)
            def cursor(self):
                return Cursor()
            def close(self):
                log.append("close")
        def my_model_1(dsl):
            with mock.patch("dslibrary.transport.to_local.DSLibraryLocal.get_sql_connection", Conn):
                df = dsl.load_dataframe("x")
            assert list(df.columns) == ["a", "b"]
            assert list(df.a) == [1, 3]
            assert list(df.b) == [2, 4]
        runner.set_input("x", "sql:etc", sql_table="tbl1", username="xyz")
        runner.run_method(my_model_1)

    def test_log_metrics_to_csv(self):
        """
        Simple case of redirecting metrics to a CSV file.
        """
        project = tempfile.mkdtemp()
        runner = ModelRunner(uri="my_uri", run_id="run001", user="user3")
        runner.send_metrics_to("metrics.csv", format="csv")
        T = [1000]
        with mock.patch("time.time", lambda: T[0]):
            def my_model(dsl):
                dsl.log_metric("x", 123)
                T[0] += 1
                dsl.log_metric("y", 456)
            runner.run_method(my_model, path=project)
        metrics_fn = os.path.join(project, "metrics.csv")
        with open(metrics_fn, 'r') as f:
            data = f.read()
        assert data == 'uri,run_id,user,time,name,value,step\nmy_uri,run001,user3,1000,x,123,0\nmy_uri,run001,user3,1001,y,456,0\n'
        shutil.rmtree(project)

    def test_log_params_with_default_format(self):
        project = tempfile.mkdtemp()
        runner = ModelRunner(uri="my_uri", run_id="run001", user="user3")
        T = [1000]
        with mock.patch("time.time", lambda: T[0]):
            def my_model(dsl):
                dsl.log_param("a", 'one')
                T[0] += 1
                dsl.log_param("b", 222)
            runner.run_method(my_model, path=project)
        params_fn = os.path.join(project, PARAMS_ALIAS)
        with open(params_fn, 'r') as f:
            lines = f.read().strip().split("\n")
        assert json.loads(lines[0]) == {"uri": "my_uri", "run_id": "run001", "user": "user3", "time": 1000, "name": "a", "value": "one"}
        assert json.loads(lines[1]) == {"uri": "my_uri", "run_id": "run001", "user": "user3", "time": 1001, "name": "b", "value": 222}
        shutil.rmtree(project)

    def test_supply_and_capture_data(self):
        """
        You can pass in a dataframe!
        """
        def my_model(dsl):
            df = dsl.load_dataframe("input")
            dsl.log_metric("tot_before", df.x.sum())
            df.x += 1
            dsl.log_metric("tot_after", df.x.sum())
            dsl.write_resource("output", df)
        runner = ModelRunner()
        runner.set_input("input", data=pandas.DataFrame({"x": [1, 2, 3]}))
        # TODO we should probably have a global flag that captures everything, otherwise files will be created while debugging
        runner.set_output("output", capture=True)
        runner.send_metrics_to(capture=True)
        outputs = runner.run_method(my_model)
        self.assertEqual(list(outputs["output"].x), [2, 3, 4])
        metrics = outputs[METRICS_ALIAS]
        assert metrics == {'tot_before': 6, 'tot_after': 9}

    def tearDown(self) -> None:
        reset_env("test_run_method")
