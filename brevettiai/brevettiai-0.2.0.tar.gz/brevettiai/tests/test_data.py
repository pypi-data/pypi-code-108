import unittest
from itertools import islice

import numpy as np
import pandas as pd

from brevettiai.data.data_generator import DataGenerator, OneHotEncoder
from brevettiai.data.sample_integrity import merge_sample_identification, SampleSplit
from brevettiai.utils.pandas_utils import explode


class TestDataGenerator(unittest.TestCase):
    n = 10
    samples = pd.DataFrame({
        "category": pd.Series(np.random.RandomState(20).randint(0, 3, size=n)).apply(lambda x: (x,)).astype("category"),
        "id": pd.Series(np.arange(n))
    })
    samples.category.cat.categories = [("A",), ("B",), ("A", "B")]
    samples["path"] = samples.id.map(str)

    def test_unshuffled_unbatched(self):
        ds = DataGenerator(self.samples)

        df = pd.DataFrame(ds.get_samples_numpy(batch=False))
        self.assertTrue((self.samples.id.values == df.id).all())

        df = pd.DataFrame(ds.get_samples_numpy(batch=False))
        self.assertTrue((self.samples.id.values == df.id).all())

    def test_unshuffled_batched(self, batch_size=3):
        ds = DataGenerator(self.samples[["id", "path"]], batch_size=batch_size)

        self.assertTrue(len(ds) == np.ceil(len(self.samples) / batch_size), "")

        df = pd.DataFrame(ds.get_samples_numpy(batch=True))
        self.assertTrue(len(ds) == len(df))
        self.assertTrue(all(len(b) == batch_size for b in df.id[:-1]))

        residual = len(self.samples) % batch_size
        residual = batch_size if residual == 0 else residual
        self.assertTrue(len(df.id.iloc[-1]) == residual)

        df = pd.DataFrame(ds.get_samples_numpy(batch=False))
        self.assertTrue((self.samples.id.values == df.id).all())

    def test_shuffled(self, batch_size=3):
        ds = DataGenerator(self.samples[["id", "path"]], batch_size=batch_size, shuffle=True)

        self.assertTrue(len(ds) == np.ceil(len(self.samples) / batch_size), "Epoch length mismatch")

        df = pd.DataFrame(ds.get_samples_numpy(batch=False))
        self.assertFalse((self.samples.id == df.id).all(), "Samples out of order")
        self.assertTrue((df.id.value_counts() == self.samples.id.value_counts()).all(),
                        "All samples in set same amount of times")

        self.assertTrue(
            all(a["id"] == b["id"] for a, b in
                zip(ds.get_samples_numpy(batch=False), ds.get_dataset_numpy(batch=False))),
            "Shuffled samples must match across instances"
        )

        df1 = pd.DataFrame(DataGenerator(self.samples, shuffle=True, seed=120).get_samples_numpy(batch=False))
        df2 = pd.DataFrame(DataGenerator(self.samples, shuffle=True, seed=120).get_samples_numpy(batch=False))
        self.assertTrue((df1.id.values == df2.id.values).all(), "Seed should make sequence equal")

        df3 = pd.DataFrame(DataGenerator(self.samples, shuffle=True, seed=121).get_samples_numpy(batch=False))
        self.assertTrue((df1.id.values != df3.id.values).any(), "Different seeds should make sequence different")

    def test_repeated(self, repeat=2):
        ds = DataGenerator(self.samples, batch_size=1, repeat=repeat)

        self.assertTrue(len(ds) == len(self.samples), "Epoch length mismatch")

        df = pd.DataFrame(ds.get_samples_numpy(batch=False))
        self.assertTrue((np.tile(self.samples.id.values, repeat) == df.id).all(), "Samples repeated in order")
        self.assertTrue((df.id.value_counts() == (self.samples.id.value_counts() * repeat)).all(),
                        "All samples in set repeat times")

    def test_shuffle_repeated(self, repeat=2):
        ds = DataGenerator(self.samples, batch_size=1, repeat=repeat, shuffle=True)

        self.assertTrue(len(ds) == len(self.samples), "Epoch length mismatch")

        df = pd.DataFrame(ds.get_samples_numpy(batch=False))
        self.assertFalse((np.tile(self.samples.id.values, repeat) == df.id).all(), "Samples repeated in order")
        self.assertTrue((df.id.value_counts() == (self.samples.id.value_counts() * repeat)).all(),
                        "All samples in set repeat times")

    def test_sample_weighing_unshuffled(self):
        dfs = [[g[1]] * cnt for g, cnt in zip(self.samples.groupby("category"), [10, 3, 1])]
        dfs = pd.concat([item for sublist in dfs for item in sublist])
        dfs = dfs.sort_values("id")

        df = self._get_df_through_dataset(dfs, repeat=-1, shuffle=False, sampling_groupby=["category"])
        counts = df.category.value_counts()
        self.assertAlmostEqual(0, counts.std() / counts.mean(), delta=0.01, msg="Counts must match")
        for k, g in df.groupby("category"):
            self.assertTrue(all(g.id.iloc[0] == g.id[g.id.diff() < 0]), "All groups must be sampled in input order")

        df2 = self._get_df_through_dataset(dfs, repeat=-1, shuffle=False, sampling_groupby=["category"])
        self.assertTrue((df2.values == df.values).all(),
                        "Repeated unshuffled dataset should match, even when oversampling")

        self._compare_weighting(np.sqrt, dfs, shuffle=False)

    def test_sample_weighing(self):
        dfs = [[g[1]] * cnt for g, cnt in zip(self.samples.groupby("category"), [10, 3, 1])]
        dfs = pd.concat([item for sublist in dfs for item in sublist])
        dfs = dfs.sort_values("id")
        self._compare_weighting(np.sqrt, dfs, shuffle=True)
        self._compare_weighting(lambda x: 1, dfs, shuffle=True)
        self._compare_weighting(lambda x: x, dfs, shuffle=True)

    @staticmethod
    def _get_df_through_dataset(samples, **kwargs):
        ds = DataGenerator(samples, **kwargs)
        df = pd.DataFrame(islice(ds.get_samples_numpy(batch=False), 1000))
        df.category = df.category.apply(tuple)
        return df

    def _compare_weighting(self, func, samples, delta=0.08, **kwargs):
        df = self._get_df_through_dataset(samples, sampling_groupby=["category"], sampling_group_weighing=func,
                                          repeat=-1, **kwargs)
        target = samples.category.value_counts().apply(func)
        target = target / target.sum()
        error = ((df.category.value_counts() / len(df))[target.index] - target).abs()
        print(func, error.max())
        self.assertAlmostEqual(0, error.max(), delta=delta,
                               msg=f"All groups must be sampled in correct amount for func {func}")


class TestSampleIdentification(unittest.TestCase):
    samples = pd.DataFrame({
        "etag": ["1", "2", "3", "4", "5"],
    })

    sample_id = pd.DataFrame({
        "purpose": ["test", "test", "train", "train", pd.NA]
    }, index=["5", "2", "1", "4", "3"])

    def test_merge_sample_identification(self):
        df, known_ids = merge_sample_identification(self.samples, self.sample_id)

        pd.testing.assert_series_equal(df.etag, self.samples.etag)
        pd.testing.assert_series_equal(self.sample_id.purpose[df.etag].reset_index(drop=True),
                                       df.purpose.reset_index(drop=True))

        dfid = self.sample_id
        dfid.purpose = ["test", pd.NA, "train", "train", "new"]
        df2, known_ids = merge_sample_identification(df.copy(), self.sample_id)
        reord = self.sample_id.purpose[df.etag].reset_index(drop=True)

        # Check NA values in identification frame is not changed
        pd.testing.assert_frame_equal(df2.set_index("etag").loc[dfid[dfid.purpose.isna()].index],
                                      df.set_index("etag").loc[dfid[dfid.purpose.isna()].index])

        # Check non NA values are transfered
        pd.testing.assert_series_equal(reord[~reord.isna()],
                                       df2.purpose.reset_index(drop=True)[~reord.isna()])


class TestDataPurposeAssignment(unittest.TestCase):
    samples = pd.DataFrame({
        "etag": np.arange(10000),
        "path": [str(i) for i in range(10000)],
        "group1": np.random.randint(0, 5, 10000),
        "group2": np.random.randint(0, 5, 10000),
        "group3": np.random.randint(0, 5, 10000),
    })

    def test_basic_assignment(self):
        split = np.random.rand()
        df = SampleSplit(split=split).assign(self.samples.copy(), remainder="test")
        df2 = SampleSplit(split=split, seed=1234).assign(self.samples.copy(), remainder="test")
        df3 = SampleSplit(split=split, seed=1234).assign(self.samples.copy(), remainder="test")
        self.assertAlmostEqual((df.purpose == "train").mean(), split, delta=0.001, msg="Split should match")

        self.assertFalse((df.purpose == df2.purpose).all(), "Unseeded should result in different assignment")
        self.assertTrue((df3.purpose == df2.purpose).all(), "Seeding should result in equal assignment")

    def test_basic_assignment_mmh3(self):
        split = np.random.rand()
        mmhmode = SampleSplit.MODE_MURMURHASH3
        df = SampleSplit(split=split, mode=mmhmode).assign(self.samples.copy(), remainder="test")
        df2 = SampleSplit(split=split, seed=1234, mode=mmhmode).assign(self.samples.copy(), remainder="test")
        df3 = SampleSplit(split=split, seed=1234, mode=mmhmode).assign(self.samples.copy(), remainder="test")
        self.assertAlmostEqual((df.purpose == "train").mean(), split, delta=0.04, msg="Split should match")

        self.assertFalse((df.purpose == df2.purpose).all(), "Unseeded should result in different assignment")
        self.assertTrue((df3.purpose == df2.purpose).all(), "Seeding should result in equal assignment")

    def test_no_data(self):
        df = SampleSplit().assign(self.samples.iloc[:0].copy())
        self.assertTrue(df.empty, "Empty in -> empty out")

    def test_stratification(self):
        split = np.random.rand()
        with self.assertRaises(AssertionError):
            SampleSplit(stratification=["column_not_in_samples"], split=split).assign(self.samples.copy())

        df = SampleSplit(stratification=r"(\d)$", split=split).assign(self.samples.copy())

        self.assertAlmostEqual((df.purpose == "train").mean(), split, delta=0.01, msg="Split should match")
        self.assertAlmostEqual(
            (df.groupby(df.path.str[-1]).purpose.apply(lambda x: (x == 'train').mean()) - split).abs().max(), 0,
            delta=0.01, msg="All shards must be split accordingly")

        grouping = ["group1"]
        df = SampleSplit(stratification=grouping, split=split).assign(self.samples.copy())
        self.assertAlmostEqual((df.purpose == "train").mean(), split, delta=0.01, msg="Split should match")
        self.assertAlmostEqual(
            (df.groupby(grouping).purpose.apply(lambda x: (x == 'train').mean()) - split).abs().max(), 0,
            delta=0.01, msg="All shards must be split accordingly")

        grouping = ["group1", "group2"]
        df = SampleSplit(stratification=grouping, split=split).assign(self.samples.copy())
        self.assertAlmostEqual((df.purpose == "train").mean(), split, delta=0.03, msg="Split should match")
        self.assertAlmostEqual(
            (df.groupby(grouping).purpose.apply(lambda x: (x == 'train').mean()) - split).abs().max(), 0,
            delta=0.04, msg="All shards must be split accordingly")

    def assertAlmostEqual(self, first: float, second: float, delta, *args, **kwargs) -> None:
        print(first - second, "<=", delta )
        super().assertAlmostEqual(first, second, delta=delta, *args, **kwargs)

    def test_uniqueness(self, split=0.5):
        with self.assertRaises(AssertionError):
            SampleSplit(uniqueness=["column_not_in_samples"], split=split).assign(self.samples.copy())

        df = SampleSplit(uniqueness=r"^(\d)", split=split).assign(self.samples.copy())
        self.assertTrue(df.groupby(df.path.str[0]).purpose.apply(lambda x: (x == "train").mean()).isin((0,1)).all(),
                        "must be split according to uniqueness")
        self.assertAlmostEqual((df.purpose == "train").mean(), split, delta=0.7, msg="Split should match")

        grouping = ["group1"]
        df = SampleSplit(uniqueness=grouping, split=split).assign(self.samples.copy())
        self.assertTrue(df.groupby(grouping).purpose.apply(lambda x: (x == "train").mean()).isin((0, 1)).all(),
                        "must be split according to uniqueness")
        self.assertAlmostEqual((df.purpose == "train").mean(), split, delta=0.13, msg="Split should match")

        grouping = ["group1", "group2"]
        df = SampleSplit(uniqueness=grouping, split=split).assign(self.samples.copy())
        self.assertTrue(df.groupby(grouping).purpose.apply(lambda x: (x == "train").mean()).isin((0, 1)).all(),
                        "must be split according to uniqueness")
        self.assertAlmostEqual((df.purpose == "train").mean(), split, delta=0.05, msg="Split should match")

    def test_uniqueness_mmh3(self, split=0.5):
        mmhmode = SampleSplit.MODE_MURMURHASH3
        with self.assertRaises(AssertionError):
            SampleSplit(uniqueness=["column_not_in_samples"], split=split, mode=mmhmode).assign(self.samples.copy())

        df = SampleSplit(uniqueness=r"^(\d)", split=split, mode=mmhmode).assign(self.samples.copy())
        self.assertTrue(df.groupby(df.path.str[0]).purpose.apply(lambda x: (x == "train").mean()).isin((0, 1)).all(),
                        "must be split according to uniqueness")
        self.assertAlmostEqual((df.purpose == "train").mean(), split, delta=0.7, msg="Split should match")

        grouping = ["group1"]
        df = SampleSplit(uniqueness=grouping, split=split, mode=mmhmode).assign(self.samples.copy())
        self.assertTrue(df.groupby(grouping).purpose.apply(lambda x: (x == "train").mean()).isin((0, 1)).all(),
                        "must be split according to uniqueness")
        self.assertAlmostEqual((df.purpose == "train").mean(), split, delta=0.6, msg="Split should match")

        grouping = ["group1", "group2"]
        df = SampleSplit(uniqueness=grouping, split=split, mode=mmhmode).assign(self.samples.copy())
        self.assertTrue(df.groupby(grouping).purpose.apply(lambda x: (x == "train").mean()).isin((0, 1)).all(),
                        "must be split according to uniqueness")
        self.assertAlmostEqual((df.purpose == "train").mean(), split, delta=0.6, msg="Split should match")


class TestSamplesExplosion(unittest.TestCase):
    samples = pd.DataFrame({
        "cat": [("A", "B"), ("A",), "B", ("A", "B", "C"), "D", ("A", "B"), pd.NA],
        "idx": np.arange(7)
    })

    def test_sample_explode(self):
        df = explode(self.samples)
        self.assertTrue((self.samples.cat.explode().fillna("N/A") == df.cat).all(),
                        "exploded column matches pd.DataFrame.explode")

        self.assertEqual(df.groupby(df.columns.tolist()).size().reset_index(name="c_").drop_duplicates("id").c_.sum(),
                         self.samples.shape[0],
                         "Duplicates excluded by dropping duplicate id after grouping")


if __name__ == '__main__':
    unittest.main()
