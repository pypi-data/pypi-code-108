# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines serialization API for models interfacing with interpretability SDK."""

import os
import logging

from azureml._common._error_definition import AzureMLError
from azureml._logging import ChainedIdentity
from azureml.interpret.common._errors.error_definitions import (
    DeserializationFailure, ModelNotKeras, OptionalDependencyMissing)
from azureml.interpret.common.constants import LoggingNamespace, Serialization
from azureml.interpret.common.exceptions import (
    SerializationException, OptionalDependencyMissingException,
    UnsupportedModelException)

KERAS_MODEL_FILE = 'KERAS_MODEL_FILE'


def _is_keras_model(model):
    try:
        import tensorflow as tf
    except Exception:
        tf = None
    return str(type(model)).endswith("keras.engine.sequential.Sequential'>") or \
        str(type(model)).endswith("keras.models.Sequential'>") or \
        str(type(model)).endswith("keras.engine.training.Model'>") or \
        (tf is not None and isinstance(model, tf.keras.Model))


class KerasSerializer(ChainedIdentity):
    """Serialize non-picklable Keras models.

    Base class for serializing non-picklable models.
    """

    def __init__(self, **kwargs):
        """Serialize non-picklable Keras models.

        Base class for serializing non-picklable models.
        """
        super(KerasSerializer, self).__init__(**kwargs)
        self._logger.debug('Initializing KerasSerializer')

    def save(self, model):
        """Save the Keras model.

        :param model: The model to save.
        :type model: tf.keras.Model
        :return: The state to be pickled.
        :rtype: dict
        :raises azureml.interpret.common.exceptions.UnsupportedModelException: Unsupported model type.
        """
        if not _is_keras_model(model):
            raise UnsupportedModelException._with_error(AzureMLError.create(ModelNotKeras))
        # Save the keras model to string
        import tempfile
        temp_filename = os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
        model.save(temp_filename)
        with open(temp_filename, "rb") as temp_file:
            read_model = temp_file.read()
        os.remove(temp_filename)
        return {KERAS_MODEL_FILE: read_model}

    def load(self, state):
        """Load the Keras model.

        :param state: The unpickled state to be loaded.
        :type state: dict
        :return: The loaded model.
        :rtype: tf.keras.Model
        :raises azureml.interpret.common.exceptions.OptionalDependencyMissingException: TensorFlow package missing.
        """
        read_model = state[KERAS_MODEL_FILE]
        if isinstance(read_model, bytes):
            try:
                import tensorflow as tf
            except Exception:
                raise OptionalDependencyMissingException._with_error(
                    AzureMLError.create(
                        OptionalDependencyMissing, dependency_name="tensorflow",
                    )
                )
            # Load the keras model to string
            import tempfile
            temp_filename = os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
            with open(temp_filename, "wb") as temp_file:
                temp_file.write(read_model)
            read_model = tf.keras.models.load_model(temp_file.name)
            os.remove(temp_filename)
        else:
            raise SerializationException._with_error(AzureMLError.create(DeserializationFailure))
        return read_model

    def __getstate__(self):
        """Influence how KerasSerializer is pickled.

        Removes logger which is not serializable.

        :return state: The state to be pickled, with logger removed.
        :rtype state: dict
        """
        odict = self.__dict__.copy()
        del odict[Serialization.LOGGER]
        return odict

    def __setstate__(self, dict):
        """Influence how KerasSerializer is unpickled.

        Re-adds logger which is not serializable.

        :param dict: A dictionary of deserialized state.
        :type dict: dict
        """
        self.__dict__.update(dict)
        parent = logging.getLogger(LoggingNamespace.AZUREML)
        self._logger = parent.getChild(self._identity)
