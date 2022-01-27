from typing import Any, Dict

import pandas as pd
from cognite.client import CogniteClient
from pandas.core.frame import DataFrame

[
    "apply_depth_trend_imputation",
    "enable_iterative_imputer",
    "generate_imputation_models",
    "impute_depth_trend",
    "individual_imputation_models",
    "iterative_impute",
    "simple_impute",
]


class DataLoader(object):
    """
    A helper class that performs the data loading part of processing MLPet data.
    This is an **internal** class only. It is **strictly** to be used as a super
    of the Dataset class.

    """

    def save_df_to_cls(self, df: DataFrame) -> DataFrame:
        """
        Simple wrapper function to save a df to the class instance

        Args:
            df (DataFrame): Dataframe to be saved to class instance

        Returns:
            DataFrame: Returns the passed dataframe.
        """
        self.df_original = df
        return df

    def load_from_cdf(
        self, client: CogniteClient, metadata: Dict[str, str], save_as: str = ""
    ) -> DataFrame:
        """
        Retrieves data from CDF for the provided metadata config

        Args:
            client (CogniteClient): The CDF client object to retrieve data from
            metadata (dict): The metadata config to pass to the CDF client
            save_as (str): If wanting to save the retrieved data, a filepath can
                be passed to this arg and the data will be pickled at the provided
                filepath.
        Returns:
            DataFrame: Returns the data retrieved from CDF.
        """
        # Save client instance to class instance
        self.cdf_client = client
        heads = client.sequences.list(metadata=metadata, limit=None)
        data = []
        for head in heads:
            training_data = client.sequences.data.retrieve_dataframe(
                id=head.id, start=None, end=None
            )
            training_data["well_name"] = head.metadata["wellbore"]
            data.append(training_data)

        df = pd.concat(data)
        if save_as:
            df.to_pickle(save_as)
        return self.save_df_to_cls(df)

    def load_from_csv(self, filepath: str, **kwargs: Any) -> DataFrame:
        """
        Loads data from csv files

        Args:
            filepath (string): path to csv file

        Returns:
            DataFrame: Returns the data loaded from the provided csv file.
        """
        return self.save_df_to_cls(pd.read_csv(filepath, **kwargs))

    def load_from_pickle(self, filepath: str, **kwargs: Any) -> DataFrame:
        """
        Loads data from pickle files

        Args:
            filepath (string): path to pickle file

        Returns:
            DataFrame: Returns the data loaded from the provided csv file.
        """
        return self.save_df_to_cls(pd.read_pickle(filepath, **kwargs))

    def load_from_dict(self, data_dict: Dict[str, Any], **kwargs: Any) -> DataFrame:
        """
        Loads data from a dictionary

        Args:
            data_dict (dict): dictionary with data

        Returns:
            DataFrame: Returns the data loaded from the provided dictionary.
        """
        return self.save_df_to_cls(pd.DataFrame.from_dict(data_dict, **kwargs))
