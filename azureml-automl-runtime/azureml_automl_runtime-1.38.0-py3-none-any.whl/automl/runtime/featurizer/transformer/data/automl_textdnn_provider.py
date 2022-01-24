# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""AutoML word embeddings provider."""
from typing import cast, Optional, Any

import os
import threading
import logging

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import FeatureUnsupportedForIncompatibleArguments
from gensim.models.keyedvectors import KeyedVectors

from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared.exceptions import ConfigException
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core._downloader import Downloader
from azureml.automl.runtime.distributed.utilities import get_unique_download_path
from .abstract_wordembeddings_provider import AbstractWordEmbeddingsProvider
from .word_embeddings_info import WordEmbeddingsInfo, EmbeddingInfo

_logger = logging.getLogger(__name__)


class AutoMLPretrainedDNNProvider(AbstractWordEmbeddingsProvider):
    """AutoML word embeddings provider."""

    def __init__(self, model_name: str = "bert-base-uncased"):
        """Initialize class for providing word embeddings."""
        embeddings_info = WordEmbeddingsInfo.get(model_name)  # type: Optional[EmbeddingInfo]
        if embeddings_info is None:
            raise ConfigException._with_error(
                AzureMLError.create(
                    FeatureUnsupportedForIncompatibleArguments, target="model_name",
                    feature_name='Pretrained DNN', arguments="model_name({})".format(model_name),
                    reference_code=ReferenceCodes._TEXT_DNN_PROVIDER_INIT
                )
            )

        self._model = None
        self._dnn_zip_file = None  # type: Optional[KeyedVectors]
        self._embedding_info = embeddings_info
        self._already_printed_credits = False
        super().__init__(embeddings_name=model_name)

    def __repr__(self):
        return "{}(model_name='{}')".format(self.__class__.__name__, self._embeddings_name)

    def _get_model(self) -> Any:
        # The .model api is not used for pretrained text dnn
        return None

    def get_model_dirname(self) -> Any:
        """
        Return the embeddings model.

        :return: The embeddings model.
        """
        if not self._model:
            self._initialize()
        return self._model

    def _is_lower(self) -> bool:
        """
        Return whether the embeddings trained only on lower cased words.

        :return: Whether the embeddings trained only on lower cased words.
        """
        return self._embedding_info._lower_case

    def _get_vector_size(self) -> int:
        """
        Returns the vector size of the model

        :return: vector size of the model
        """
        return cast(int, self._model.vector_size)\
            if isinstance(self._model, KeyedVectors) else 0

    def _print_credits(self) -> None:
        """
        Print credits for the model being used.

        :return: None.
        """
        if not self._already_printed_credits:
            line_break = "--------------------------------------------------"
            print(line_break)
            print("Credits for document embeddings being used in the SDK.")
            print("Credits: {0}".format(self._embedding_info._credits))
            print("License: {0}".format(self._embedding_info._license))
            print(line_break)
            self._already_printed_credits = True

    def _load_from_disk(self) -> None:
        """
        Load an existing pickled model file.

        :return: None.
        """
        if self._dnn_zip_file is None or \
                Downloader.md5(self._dnn_zip_file) !=\
                self._embedding_info._md5hash:
            self._print_credits()
            self._download()

        if self._dnn_dir_name is None:
            _logger.warning("Model loading failed as the directory name is None")
        else:
            self._model = self._dnn_dir_name  # return the model name

    def _download(self) -> None:
        """
        Download the pretrained zip file and extract into folder

        :return: None.
        """
        # TODO This should move to a logger.
        extract_folder = get_unique_download_path(self._download_folder_name)  # "data" folder

        line_break = "------------------------------------------------------"
        _logger.info(line_break)
        _logger.info("Downloading {0}.".format(self._embedding_info._user_friendly_name))

        # Download file.
        self._dnn_zip_file = Downloader.download(
            download_prefix=self._embedding_info._download_prefix,
            file_name=self._embedding_info._file_name,
            target_dir=self.embeddings_dir,
            prefix=str(self.__class__.__name__),
            md5hash=self._embedding_info._md5hash,
            retries=4)

        # Unzip file
        self._dnn_file_info = Downloader.unzip_file(zip_fname=self._dnn_zip_file,
                                                    extract_path=os.path.join(os.getcwd(), extract_folder))

        # Get the path of one of the unzipped files, and get the directory name
        self._dnn_dir_name = os.path.join(extract_folder, os.path.dirname(self._dnn_file_info[0].filename))

    def __getstate__(self):
        """
        Overriden to remove model object when pickling.

        :return: this object's state as a dictionary
        """
        state = self.__dict__
        state['_lock'] = None
        state['_tried_loading'] = False
        state['_model'] = None
        return state

    def __setstate__(self, state):
        """
        Overriden to set needed objects.

        :param state:
        :return:
        """
        self.__dict__.update(state)
        self._lock = threading.Lock()
