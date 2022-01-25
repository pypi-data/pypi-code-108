import unittest
import os
import tempfile
import shutil
import sys
import inspect
import pandas

from dslibrary.front import METRICS_ALIAS
from dslibrary.run_models import ModelRunner
from tests.t_utils import reset_env


class TestRunLocal(unittest.TestCase):
    """
    Execute models locally as subprocesses.
    """

    def test_run_local__process_csv(self):
        """
        Here we pass in a CSV and have it processed.
        """
        def my_model():
            import dslibrary
            dsl = dslibrary.instance()
            incr = dsl.get_parameter("incr")
            df = dsl.load_dataframe("input1")
            df.x += incr
            dsl.write_resource("output1", df)
        with RunLocalTestFramework(my_model) as env:
            # store input file
            env.write_file("i1", "x\n1\n2\n3")
            # NOTE: '~/i1' points to a file inside the model
            # NOTE: output2 is directed to a file outside the model by using an absolute path
            env.runner.set_input("input1", "~/i1", format="csv")
            env.runner.set_output("output1", os.path.join(env.output_folder, "o1"), format="csv")
            # metadata defines input & output, entry point, etc..
            interpreter = sys.executable
            with open(os.path.join(env.project, "MLProject"), 'w') as f:
                f.write("entry_points:\n  e1:\n    parameters:\n      incr: {type: float, default: 1}\n    command: \"" + interpreter + " model.py\"")
            env.run()
            # verify output was written
            self.assertEqual(env.read_file("o1"), 'x\n2.0\n3.0\n4.0\n')

    def test_infer_command_from_path(self):
        """
        ModelRunner() lets us execute a given source file without having to hook it up as an official entry point.
        So, we need to know how to execute various source files.
        """
        r = ModelRunner.infer_command_from_path("abc.py")
        assert r == [sys.executable, "abc.py"], r
        r = ModelRunner.infer_command_from_path("abc.r")
        assert r == ['RScript', 'abc.r'], r
        r = ModelRunner.infer_command_from_path("abc.ipynb")
        assert r == ['nbconvert', '--to', 'notebook', '--execute', '--inplace', 'abc.ipynb'], r

    def test_supply_and_capture_data(self):
        """
        You can pass in a dataframe from memory and it will send it using a temporary file.  And if you request to
        capture an output, or the metrics, they will be stored in temporary files, parsed, and returned in memory.
        """
        def my_model():
            import dslibrary as dsl
            df = dsl.load_dataframe("input")
            dsl.log_metric("tot_before", df.x.sum())
            df.x += 1
            dsl.log_metric("tot_after", df.x.sum())
            dsl.write_resource("output", df)
        with RunLocalTestFramework(my_model) as env:
            env.runner.set_input("input", data=pandas.DataFrame({"x": [1, 2, 3]}))
            env.runner.set_output("output", capture=True)
            env.runner.send_metrics_to(capture=True)
            outputs = env.run("model.py")
            assert outputs
            self.assertEqual(list(outputs["output"].columns), ["x"])
            self.assertEqual(list(outputs["output"].x), [2, 3, 4])
            metrics = outputs[METRICS_ALIAS]
            assert metrics == {'tot_before': 6, 'tot_after': 9}

    def tearDown(self) -> None:
        reset_env("test_run_local")


class RunLocalTestFramework(object):
    def __init__(self, function_with_code):
        self.function_with_code = function_with_code

    def __enter__(self):
        self.project = tempfile.mkdtemp()
        self.output_folder = tempfile.mkdtemp()
        self.runner = ModelRunner(uri="uri", entry_point="e1", project_root=self.project)
        model_code = inspect.getsource(self.function_with_code)
        # store model code
        self.write_file("model.py", model_code.strip() + f"\n\n{self.function_with_code.__name__}()")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.project)
        shutil.rmtree(self.output_folder)

    def run(self, path: str=None):
        pkg_folder = os.path.join(os.path.dirname(__file__), "..")
        return self.runner.run_local(path, extra_env={"PYTHONPATH": pkg_folder})

    def write_file(self, path: str, content: str):
        with open(os.path.join(self.project, path), 'w') as f_w:
            f_w.write(content)

    def read_file(self, path: str) -> str:
        with open(os.path.join(self.output_folder, path), 'r') as f_r:
            return f_r.read()
