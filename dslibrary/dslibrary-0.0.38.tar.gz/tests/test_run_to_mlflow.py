import unittest
import mock
import pandas
import tempfile

from dslibrary.run_models import ModelRunner


class TestRunToMLFlow(unittest.TestCase):
    """
    MLFlow can be made the target of some or all output operations.
    """
    def test_log_text(self):
        """
        The compatibility functions like log_text() just call the equivalent mlflow method.
        """
        runner = ModelRunner(uri="uri", entry_point="main", mlflow={"all": True})
        def my_model(dsl):
            log = []
            with mock.patch("mlflow.log_text", lambda txt, fn: log.append((txt, fn))):
                dsl.log_text("hello", "text1")
            assert log == [('hello', 'text1')]
        runner.run_method(my_model)

    def test_write_df_to_log_artifact(self):
        """
        Writing of data frames uses filename appropriate format and sends via log_artifact().
        """
        runner = ModelRunner(uri="uri", entry_point="main", mlflow={"all": True})
        def my_model(dsl):
            df = pandas.DataFrame({"x": [1, 2], "y": [3, 4]})
            log = []
            def log_artifact(fn, rmt):
                with open(fn) as f_r:
                    data = f_r.read()
                log.append((data, rmt))
            with mock.patch("mlflow.log_artifact", log_artifact):
                dsl.write_resource("data.csv", df)
            assert log == [('x,y\n1,3\n2,4\n', 'data.csv')]
        runner.run_method(my_model)

    def test_write_df_with_format_options(self):
        """
        Writing of data frames uses filename appropriate format and sends via log_artifact().
        """
        runner = ModelRunner(uri="uri", entry_point="main", mlflow={"all": True})
        def my_model(dsl):
            df = pandas.DataFrame({"x": [1, 2], "y": [3, 4]})
            log = []
            def log_artifact(fn, rmt):
                with open(fn) as f_r:
                    data = f_r.read()
                log.append((data, rmt))
            with mock.patch("mlflow.log_artifact", log_artifact):
                dsl.write_resource("data.csv", df)
            self.assertEqual(log, [('x\ty\n1\t3\n2\t4\n', 'data.csv')])
        runner.set_output("data.csv", "", format_options={"sep": "\t"})
        runner.run_method(my_model)

    def test_mapped_input(self):
        """
        Input mapping is unchanged by the mlflow settings.
        """
        with tempfile.NamedTemporaryFile(suffix=".csv") as f_tmp:
            runner = ModelRunner(uri="uri", entry_point="main", mlflow=True)
            def my_model(dsl):
                df = dsl.load_dataframe("data.csv")
                assert list(df.x) == [1, 2, 3]
            f_tmp.write(b"x\n1\n2\n3\n")
            f_tmp.flush()
            runner.set_input("data.csv", f_tmp.name)
            runner.run_method(my_model)
