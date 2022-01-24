# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains functionality for defining a storage policy on explanations in Azure Machine Learning."""

from azureml.interpret.common.constants import History


# Note: this method is actually publicly exposed and re-imported as a public function in the init file
def _storage_policy(block_size=None, max_num_blocks=None, **kwargs):
    """Set of parameters for defining the storage policy on explanations.

    :param block_size: The size of each block for the summary stored in artifacts storage.
    :type block_size: int
    :param max_num_blocks: The maximum number of blocks to store.
    :type max_num_blocks: int
    :rtype: dict
    :return: The arguments for the storage policy
    """
    kwargs[History.BLOCK_SIZE] = block_size
    kwargs[History.MAX_NUM_BLOCKS] = max_num_blocks
    return kwargs
