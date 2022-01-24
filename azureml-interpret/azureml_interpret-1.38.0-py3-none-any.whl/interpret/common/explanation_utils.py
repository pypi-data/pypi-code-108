# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines helpful utilities for summarizing and uploading data."""

import os
from math import ceil
import numpy as np
import json
import pickle
from interpret_community.common.serialization_utils import _serialize_json_safe
from azureml._restclient.constants import RUN_ORIGIN
from azureml.interpret.common.constants import History, IO
from azureml._logging import ChainedIdentity


class ArtifactUploader(ChainedIdentity):
    """Uploads explanation data to run history."""

    def __init__(self, run, max_num_blocks=None, block_size=None, **kwargs):
        """Initialize the upload mixin by setting up the storage policy."""
        self.storage_policy = {History.MAX_NUM_BLOCKS: 3, History.BLOCK_SIZE: 100}
        self._update_storage_policy(max_num_blocks, block_size)
        super(ArtifactUploader, self).__init__(**kwargs)
        self._logger.debug('Initializing ArtifactUploader')
        self.run = run

    def _update_storage_policy(self, max_num_blocks, block_size):
        if max_num_blocks is not None:
            self.storage_policy[History.MAX_NUM_BLOCKS] = max_num_blocks
        if block_size is not None:
            self.storage_policy[History.BLOCK_SIZE] = block_size

    def _create_upload_dir(self, explanation_id):
        self._logger.debug('Creating upload directory')
        # create the outputs folder
        upload_dir = './explanation/{}/'.format(explanation_id[:History.ID_PATH_2004])
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

    def _create_file_path(self, upload_dir, artifact_name, upload_type):
        INTERPRET_EXT = '.interpret'
        file_string = '{}{}{}.{}'.format(upload_dir.lstrip('./'), artifact_name, INTERPRET_EXT, upload_type)
        file_path = os.path.split(file_string)[0]
        os.makedirs(file_path, exist_ok=True)
        return file_string

    def _serialize_via_json(self, values, file_string):
        if isinstance(values, np.ndarray):
            # Memory optimization to write a chunk of the numpy array at a time instead
            # of converting to string in memory.
            # If array is not 3D or 2D we convert to list and use json serialization directly.
            if len(values.shape) == 2 or len(values.shape) == 3:
                with open(file_string, 'w') as f:
                    f.write("[")
                    size = values.shape[0]
                    for i in range(size):
                        row = values[i, ...].tolist()
                        row_values = _serialize_json_safe(row)
                        json_row = json.dumps(row_values, allow_nan=False)
                        if i != size - 1:
                            json_row = json_row + ", "
                        f.write(json_row)
                    f.write("]")
                return
            else:
                values = values.tolist()
        try:
            json_string = json.dumps(values, allow_nan=False)
            with open(file_string, 'w') as f:
                f.write(json_string)
        except MemoryError:
            with open(file_string, 'w') as f:
                json.dump(values, f, allow_nan=False)

    def _upload_artifact(self, upload_dir, artifact_name, values, upload_type=None):
        self._logger.debug('Uploading artifact')
        try:
            if upload_type is None or upload_type == IO.JSON:
                file_string = self._create_file_path(upload_dir, artifact_name, IO.JSON)
                try:
                    # NOTE: if allow_nan is false there will be a ValueError when serializing
                    # out of range float values (nan, inf, -inf)
                    self._serialize_via_json(values, file_string)
                except (ValueError, TypeError) as e:
                    if isinstance(e, ValueError):
                        warn_msg = 'Cannot serialize JSON, possibly due to NaN or Inf, '\
                                   'scrubbing to zero and retrying...'
                    else:
                        warn_msg = 'Cannot serialize JSON possibly due to timestamp, retrying'
                    self._logger.warn(warn_msg)
                    # try to convert out of range values in case there are any and retry json encoding
                    if isinstance(values, list) or isinstance(values, np.ndarray):
                        values = _serialize_json_safe(values)
                    self._serialize_via_json(values, file_string)
            else:
                pickle_string = pickle.dumps(values)
                file_string = self._create_file_path(upload_dir, artifact_name, IO.PICKLE)
                with open(file_string, 'w') as f:
                    f.write(pickle_string)
        except ValueError:
            self._logger.error('Cannot serialize numpy arrays as JSON')

    def _get_num_of_blocks(self, num_of_columns):
        block_size = self.storage_policy[History.BLOCK_SIZE]
        num_blocks = ceil(num_of_columns / block_size)
        max_num_blocks = self.storage_policy[History.MAX_NUM_BLOCKS]
        if num_blocks > max_num_blocks:
            num_blocks = max_num_blocks
        return num_blocks

    def _get_model_summary_artifacts(self, upload_dir, name, summary):
        self._logger.debug('Uploading model summary')
        num_columns = summary.shape[len(summary.shape) - 1]
        num_blocks = self._get_num_of_blocks(num_columns)
        block_size = self.storage_policy[History.BLOCK_SIZE]
        storage_metadata = {
            History.NAME: name,
            History.MAX_NUM_BLOCKS: self.storage_policy[History.MAX_NUM_BLOCKS],
            History.BLOCK_SIZE: self.storage_policy[History.BLOCK_SIZE],
            History.NUM_FEATURES: num_columns,
            History.NUM_BLOCKS: num_blocks
        }
        artifacts = [{} for _ in range(num_blocks)]
        # Chunk the summary and save it to Artifact
        start = 0
        for idx in range(num_blocks):
            if idx == num_blocks - 1:
                # on last iteration, grab everything that's left for the last block
                cols = slice(start, num_columns)
            else:
                cols = slice(start, start + block_size)
            block = summary[..., cols]
            block_name = '{}/{}'.format(name, idx)
            self._logger.debug('Uploading artifact for block: {}'.format(block_name))
            self._upload_artifact(upload_dir, block_name, block.tolist())
            artifacts[idx][History.PREFIX] = os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN,
                                                                                   self.run.id,
                                                                                   upload_dir,
                                                                                   block_name))
            start += block_size
        return artifacts, storage_metadata

    def upload_single_artifact_list(self, summary_object, artifact_tuple_list, explanation_id):
        """Upload data to individual run history artifacts from a list.

        :param summary_object: The object which aggregates metadata about the uploaded artifacts.
        :type summary_object: azureml.interpret.common.ModelSummary
        :param artifact_tuple_list: A list with names, values, optional metadata and
            serialization format for each data type. The serialization format can be
            JSON or pickle.
        :type artifact_tuple_list: (str, list, dict or None, str)
        :param explanation_id: The explanation ID the artifacts should be uploaded under
        :type explanation_id: str
        """
        upload_dir = self._create_upload_dir(explanation_id)
        for name, values, optional_metadata, upload_type in artifact_tuple_list:
            self._logger.debug('Uploading single {} artifact'.format(name))
            self._upload_artifact(upload_dir, name, values, upload_type)
            artifact_info = [{
                History.PREFIX: os.path.normpath('{}/{}/{}/{}'.format(RUN_ORIGIN,
                                                                      self.run.id,
                                                                      upload_dir,
                                                                      name))
            }]
            metadata_info = {History.NAME: name}
            if optional_metadata is not None:
                metadata_info.update(optional_metadata)
            summary_object.add_from_get_model_summary(name, (artifact_info, metadata_info))

    def upload_sharded_artifact_list(self, summary_object, artifact_tuple_list, explanation_id):
        """Upload data to sharded run history artifacts from a list.

        :param summary_object: The object which aggregates metadata about the uploaded artifacts.
        :type summary_object: azureml.interpret.common.ModelSummary
        :param artifact_tuple_list: A list with names and values for each data type.
        :type artifact_tuple_list: (str, list)
        :param explanation_id: The explanation ID the artifacts should be uploaded under.
        :type explanation_id: str
        """
        upload_dir = self._create_upload_dir(explanation_id)
        for name, values in artifact_tuple_list:
            self._logger.debug('Uploaded sharded {} artifacts'.format(name))
            artifacts = self._get_model_summary_artifacts(upload_dir, name, values)
            summary_object.add_from_get_model_summary(name, artifacts)
