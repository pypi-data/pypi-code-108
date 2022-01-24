# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Iterator, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ._unprocessed_featurizer import BaseFeaturizer


class FeaturizerContainer:
    """
    Container class holding a list of featurizer objects generated from the results of feature sweeping.
    Any custom logic or properties not specific to any one featurizer should reside in this class.
    """
    def __init__(self, featurizer_list: List['BaseFeaturizer'], **kwargs: Any):
        """
        Initialize a featurizer container.

        :param featurizer_list: The list of featurizers.
        """
        self.featurizers = featurizer_list  # type: List['BaseFeaturizer']

    def __iter__(self) -> Iterator['BaseFeaturizer']:
        """
        Make this class iterable. Iterate through the instance's list of featurizer objects.

        :return: Iterator object.
        """
        return iter(self.featurizers)
