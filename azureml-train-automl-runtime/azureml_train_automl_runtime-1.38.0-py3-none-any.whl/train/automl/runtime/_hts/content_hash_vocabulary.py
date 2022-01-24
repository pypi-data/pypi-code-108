# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module holding the content to hash to vocabulary for data aggragation in HTS."""
from typing import Dict, List, cast
import hashlib
import inspect
import pandas as pd

from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.reference_codes import ReferenceCodes


class ContentHashVocabulary:
    """Class contains column content to hash then to vocabulary for count vectorizer information."""
    def __init__(self, hash_content_dict: Dict[str, str], hash_vocabulary_dict: Dict[str, int]):
        Contract.assert_true(
            len(set(hash_content_dict.keys()) ^ set((hash_vocabulary_dict.keys()))) == 0,
            message="Hash column name dict should contains the same keys as has vocabulary dict",
            reference_code=ReferenceCodes._HTS_HASH_VOCABULARY_UNEXPECTED_KEYS
        )
        self.hash_content_dict = hash_content_dict
        self.hash_vocabulary_dict = hash_vocabulary_dict

    @staticmethod
    def md5hash(input_str: str) -> str:
        """Get the md5 hash of a string."""
        return str(hashlib.md5(input_str.encode("utf-8")).hexdigest())

    @staticmethod
    def get_original_hash_content_dict(
            hash_series: pd.Series,
            content_series: pd.Series,
            hashed_keys: List[str]
    ) -> Dict[str, str]:
        """
        Look up hashed keys in the content_series from hash series.

        :param hash_series: The pd.Series contains the hashes.
        :param content_series: The pd.Series contains the original contents.
        :param hashed_keys: The hashed keeys that needs to be looking for.
        :return: Dict[str, str]
        """
        key_set = set(hashed_keys)
        df = pd.DataFrame({'original': content_series, 'hashed': hash_series})
        key_df = df.loc[lambda s: s['hashed'].isin(key_set)].drop_duplicates()
        hash_original_dict = {
            str(hashed): str(original) for hashed, original in zip(key_df['hashed'], key_df['original'])
        }
        return hash_original_dict

    @staticmethod
    def get_args_list() -> List[str]:
        """Return the list of arguments for this class."""
        return inspect.getfullargspec(ContentHashVocabulary).args[1:]

    def __eq__(self, other: object) -> bool:
        Contract.assert_type(other, "other", ContentHashVocabulary, ReferenceCodes._HTS_COLUMN_HASH_TYPE_ERROR)
        other = cast(ContentHashVocabulary, other)
        return self.hash_vocabulary_dict == other.hash_vocabulary_dict and \
            self.hash_content_dict == other.hash_content_dict
