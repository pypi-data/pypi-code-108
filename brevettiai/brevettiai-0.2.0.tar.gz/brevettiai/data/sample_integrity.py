import logging
import mmh3
import json

from brevettiai.interfaces import vue_schema_utils as vue
from brevettiai.io import io_tools

from io import BytesIO
import pandas as pd
import numpy as np

log = logging.getLogger(__name__)


def merge_sample_identification(df, dfid, on="etag"):
    """
    Merge sample identification traits onto dataframe, such that values (excluding NA) are transfered to the dataframe
    :param df: Dataframe
    :param dfid: identification dataframe, with index as parameter named by on, by default 'etag'
    :param on: column name on df to match with identification
    :return: df, extra_ids (merged dataframe and ids, and ids not present among samples
    """
    # Reindex id file to match new samples
    extra_ids = dfid[~dfid.index.isin(df[on])]
    dfid = dfid.reindex(df[on])

    # combine sample identification information with samples
    for c in dfid.columns:
        col = dfid[c]
        mask = col.isna()
        if mask.any() and c in df.columns:
            df[c][~mask.values] = col[~mask].values
        else:
            df[c] = col.values
    return df, extra_ids


def load_sample_identification(df, path, column="purpose", **kwargs):
    """
    Load and join sample identification information onto dataframe of samples
    :param df: sample dataframe
    :param path: path to sample id file
    :param column: name of split column
    :param kwargs: extra args for io_tools.read_file
    :return: df, extra_ids
    """
    dfid = pd.read_csv(BytesIO(io_tools.read_file(path, **kwargs)), index_col="etag")
    if column not in dfid.columns:
        dfid.rename(columns={dfid.columns[0]: column})
    return merge_sample_identification(df, dfid, on="etag")


def save_sample_identification(df, path, known_ids=None, column="purpose"):
    columns = ["etag", column]
    df = df[columns].set_index("etag")
    if df.index.has_duplicates:
        log.info("Duplicate etag entries among samples, saving highest priority purpose")
        df = df.iloc[np.argsort(df.purpose.map({"train": 1, "devel": 2, "development": 2, "test": 3}).fillna(4))]
        df = df[~df.index.duplicated(keep="first")]
    io_tools.write_file(path, df.append(known_ids).to_csv(header=True))


class SampleSplit(vue.VueSettingsModule):
    MODE_MURMURHASH3 = "murmurhash3"
    MODE_SORTED_PERMUTATION = "sorted_permutation"

    def __init__(self, stratification: list = None, uniqueness: list = None, split: float = 0.8, seed: int = -1,
                 mode=MODE_SORTED_PERMUTATION):
        """
        :param stratification: As regex string performed on df.path or list selecting columns
        :param uniqueness: As regex string performed on df.path or list selecting columns
        :param split: fraction of samples to apply the purpose on
        :param seed: seeding for assignment
        :param mode: ' or 'murmurhash3'
        :return:
        """
        self.stratification = stratification
        try:
            if isinstance(uniqueness, str):
                uniqueness = json.loads(uniqueness)
        except json.JSONDecodeError:
            pass
        self.uniqueness = uniqueness or ["etag"]
        self.split = split
        self.seed = seed
        self.mode = mode
        assert self.mode in {self.MODE_MURMURHASH3, self.MODE_SORTED_PERMUTATION}

    def assign(self, df, purpose="train", remainder=None, column="purpose"):
        """
        Assign purpose column randomly to non-assigned samples based on stratification, uniqueness and split strategy.

        Definitions:
        * Stratification: Grouping of samples which should be treated as individual groups.
        meaning every group must be split according to the sample split target percentage,
        and uniqueness is performed on a per group basis
        * Uniqueness: grouping of samples which must be treated as a single sample, thus be assigned the same purpose.

        :param df: pd.DataFrame of samples if purpose column does not exist it is added
        :param purpose: purpose to be assigned
        :param remainder: purpose to assign remainder samples, or None to leave unassigned
        :param column: column for assignment of split category
        """
        # Ensure columns
        if column not in df:
            df[column] = pd.NA
        columns = df.columns

        split = self.split
        stratification = self.stratification
        uniqueness = self.uniqueness

        if split == 0 or ~df.purpose.isna().any():  # Assign no samples
            pass
        elif split == 1:  # Assign all samples
            df.loc[df.purpose.isna(), column] = purpose
        else:
            # Parse regex stratification and uniqueness strategies
            if isinstance(stratification, str) and stratification:
                df["_stratification"] = df.path.str.extract(stratification)[0]
                stratification = ["_stratification"]
            assert stratification is None or all(x in df.columns for x in stratification), \
                "stratification should be None or in columns"

            if isinstance(uniqueness, str) and uniqueness:
                df["_uniqueness"] = df.path.str.extract(uniqueness)[0]
                uniqueness = ["_uniqueness"]
            assert uniqueness is None or all(x in df.columns for x in uniqueness), \
                "uniqueness should be None or in columns"

            seed = None if self.seed < 0 else self.seed
            rng = seed if isinstance(seed, np.random.RandomState) else np.random.RandomState(seed)

            def _split(g):
                if uniqueness:
                    items = g[uniqueness + [column]].copy()
                    items["_purpose_prio"] = items.purpose.map({"train": 1, "test": 2})
                    items = items.sort_values("_purpose_prio")[uniqueness + [column]]
                    unique_items = items.groupby(uniqueness).purpose.agg(["size", "first"])
                    unique_items.columns = ["samples", column]
                    unique_items = unique_items.reset_index()
                else:
                    unique_items = g[[column]].reset_index(drop=True)
                    unique_items["samples"] = 1

                # split unmarked items
                unmarked = unique_items[unique_items.purpose.isna()]

                # mode
                if unmarked.size > 0:
                    if self.mode == self.MODE_MURMURHASH3:
                        # Random seed for this stratified group
                        mmh_seed = rng.randint(0x7FFFFFFF)

                        # Extract uniqueness for hashing
                        if uniqueness:
                            unique_df = unmarked[uniqueness]
                        else:
                            unique_df = pd.DataFrame(unmarked.index)

                        # Apply mmh3 hashing
                        hash_ = unique_df.apply(lambda x: mmh3.hash("_".join(map(str, x)), seed=mmh_seed, signed=False),
                                                axis=1)

                        # Assign
                        unique_items.loc[hash_[hash_ < 0xFFFFFFFF * split].index, column] = purpose
                    elif self.mode == self.MODE_SORTED_PERMUTATION or True:  # default
                        # Select unmarked to assign
                        items_count = unique_items.samples.sum()
                        marked_count = unique_items.samples[unique_items.purpose == purpose].sum()
                        assign_count = items_count * split - marked_count
                        unmarked = rng.permutation(unmarked.index)

                        cdf = unique_items.samples[unmarked].cumsum()
                        ix = np.searchsorted(cdf.values, assign_count, side="right")
                        if len(cdf.values) > ix:
                            ix = ix - (rng.rand() > ((assign_count - cdf.values[ix - 1]) / (cdf.values[ix] - cdf.values[ix - 1])))

                        # Assign
                        unique_items.loc[cdf.iloc[:ix+1].index, column] = purpose

                if uniqueness:
                    g.loc[:, column] = unique_items.set_index(uniqueness) \
                        .loc[g[uniqueness].set_index(uniqueness).index].purpose.values
                else:
                    g.loc[:, column] = unique_items.purpose.values
                return g

            if stratification:
                df = df.groupby(stratification).apply(_split)
            else:
                df = _split(df)

        if remainder:
            df.loc[df.purpose.isna(), column] = remainder

        # Ensure etag is unique across all stratified groups
        #df.loc[:, column] = df.groupby("etag").first()[column].reindex(df.etag).values
        return df[columns]

    def update_unassigned(self, df, id_path,
                          purpose="train", remainder="devel", column="purpose"):
        """
        Updates sample purpose in id_path that may hold previous dataset splits and sample ids
        Unassigned samples are also assigned and id_path is updated
        :param df: pd.DataFrame containing the samples
        :param id_path: path to the identification csv file
        :param purpose: Purpose to assign
        :param remainder: Purpose to assign to remainder or none to leave unassigned
        :param column: Column to assign split purposes to
        :return:
        """

        log.info("Looking for previous train / development split")

        known_ids = None
        if io_tools.isfile(id_path):
            #df, known_ids = load_sample_identification(df, id_path, column=column)
            log.info("Using train / development split from run cached in artifacts")
        else:
            log.info("No initial sample identification file found")

        df = self.assign(df, purpose=purpose, remainder=remainder, column=column)

        save_sample_identification(df, id_path, known_ids=known_ids, column=column)

        return df
