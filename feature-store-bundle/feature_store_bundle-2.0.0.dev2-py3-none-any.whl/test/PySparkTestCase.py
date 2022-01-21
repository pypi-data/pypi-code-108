import unittest
import warnings
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from pyspark.sql import functions as f


class PySparkTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.master("local[1]").appName("PySparkTest").getOrCreate()
        cls.sc = cls.spark.sparkContext  # noqa

        warnings.filterwarnings("ignore", category=RuntimeWarning)
        warnings.filterwarnings("ignore", category=ResourceWarning)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    @classmethod
    def tearDownClass(cls):
        cls.sc.stop()  # noqa
        cls.spark.stop()  # noqa

    def compare_dataframes(self, df1: DataFrame, df2: DataFrame, sort_keys: list):
        df1_columns = sorted(df1.columns)
        df2_columns = sorted(df2.columns)

        df1 = df1.orderBy(sort_keys).select(df1_columns)
        df2 = df2.orderBy(sort_keys).select(df2_columns)

        self.assertEqual(df1.collect(), df2.collect())

    def delta_merge(self, target: DataFrame, source: DataFrame, primary_keys: list):  # noqa
        target_columns = target.columns
        source_columns = source.columns
        all_columns = list(set(target_columns) | set(source_columns))
        duplicate_columns = list((set(target_columns) & set(source_columns)) - set(primary_keys))
        unique_columns = list(set(all_columns) - set(primary_keys) - set(duplicate_columns))

        selection = []

        for col in all_columns:
            if col in unique_columns:
                selection.append(col)

            if col in duplicate_columns:
                selection.append(f.coalesce(f"source.{col}", f"target.{col}").alias(col))

        return target.alias("target").join(source.alias("source"), on=primary_keys, how="outer").select(*primary_keys, *selection)
