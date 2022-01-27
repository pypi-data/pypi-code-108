from typing import Union

import pandas as pd
from pandas.testing import assert_frame_equal

from akerbp.mlpet import Dataset, utilities
from akerbp.mlpet.tests.data import PREPROCESSED_DF, TEST_DF, TRAIN_DF


def main(test_type="", train_df=None) -> Union[pd.DataFrame, Dataset]:
    # Instantiate an empty dataset object using the example settings and mappings provided
    ds = Dataset(
        settings=r"tests/test_settings.yaml",
        mappings=r"tests/test_mappings.yaml",
        folder_path=r"tests/",
    )
    if test_type == "dataset":
        return ds

    # Populate the dataset with data from a loaded dataframe
    ds.save_df_to_cls(TEST_DF)

    # The original data will be kept in ds.df_original and will remain unchanged
    print(ds.df_original.head())

    # Split the data into train-validation sets
    df_train, df_test = utilities.train_test_split(
        df=ds.df_original,
        target_column=ds.label_column,
        id_column=ds.id_column,
        test_size=0.2,
    )

    # Preprocess the data for training according to default workflow
    # print(ds.default_preprocessing_workflow) <- Uncomment to see what the workflow does
    if train_df is not None:
        df_preprocessed = ds.preprocess(train_df)
    else:
        df_preprocessed = ds.preprocess(df_train)

    if test_type == "default_preprocessing":
        return df_preprocessed

    # Preprocessing can also be fully controlled by specifying the workflow manually
    # Either by relying on default options already in the dataset class
    df_select_default = ds.preprocess(df_train, select_curves={})
    # The above will fall back to the defaults for select_curves which is to select
    # curves found in the self.curves attribute of the Dataset class instance which in
    # turn was set by what was passed in the settings.yaml

    # PLEASE NOTE that the order in which kwargs are passed to preprocess will be
    # the order in which they are executed in the preprocessing method!

    # Or by expliclity overriding the defaults
    df_select_manual = ds.preprocess(df_train, select_curves={"curves": ["GR"]})

    print(df_preprocessed.head())
    print(df_select_default.head())
    print(df_select_manual.head())

    return ds


def test_dataset():
    main(test_type="dataset")


def test_default_preprocessing():
    df_preprocessed = main(test_type="default_preprocessing", train_df=TRAIN_DF)
    # Sorting columns because column order is not so important
    assert_frame_equal(
        PREPROCESSED_DF.sort_index(axis=1), df_preprocessed.sort_index(axis=1)
    )
    return True


if __name__ == "__main__":
    main()
