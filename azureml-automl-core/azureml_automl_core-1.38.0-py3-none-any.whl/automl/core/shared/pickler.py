# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Class for automl picklers."""
import errno
import logging
import os
import pickle
from abc import ABC, abstractmethod
from typing import Any

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared import logging_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InsufficientMemory, DiskFull
from azureml.automl.core.shared.exceptions import ResourceException


logger = logging.getLogger(__name__)

# This is the highest protocol number for 3.6.
# Protocol 4 is needed for models greater than 4Gb.
DEFAULT_PICKLE_PROTOCOL_VERSION = 4

# No of retries
DEFAULT_NO_OF_RETRIES = 3


class Pickler(ABC):
    """Pickler abstract class."""

    def __init__(self):
        """Pickler class constructor."""
        pass

    @abstractmethod
    def dump(self, obj: Any, path: str, file: Any = None) -> str:
        """
        Dump the object to file.

        :param obj: object to pickle
        :param path: pickler path
        :param file: optional file object if the file is already open
        :return: path of pickler
        """
        pass

    @abstractmethod
    def load(self, path: str) -> Any:
        """
        Load the object from path.

        :param path: Path for loading.
        """
        pass

    def get_name_without_extn(self, path):
        """
        Get the key without extension.

        :param path: The path of the file.
        :return: The key without extension.
        """
        return os.path.splitext(path)[0]


class DefaultPickler(Pickler):
    """Default pickler based on python cPickler."""

    def __init__(self, protocol=DEFAULT_PICKLE_PROTOCOL_VERSION):
        """Create a default pickler."""
        super(DefaultPickler, self).__init__()
        self.protocol = protocol

    def dump(self, obj: Any, path: str, file: Any = None) -> str:
        """
        Dump the object to a file.

        :param obj: The object to pickle.
        :param path: The path the pickler will use.
        :param file: optional file object if the file is already open
        :return: The path.
        """
        try:
            if file is not None:
                pickle.dump(obj, file, protocol=self.protocol)
            else:
                with open(path, "wb") as f:
                    pickle.dump(obj, f, protocol=self.protocol)
        except MemoryError as me:
            raise ResourceException._with_error(AzureMLError.create(InsufficientMemory), inner_exception=me) from me
        except OSError as oe:
            if oe.errno == errno.ENOSPC:
                raise ResourceException._with_error(
                    AzureMLError.create(DiskFull, target="pickle.dump", operation_name="pickle.dump"),
                    inner_exception=oe
                ) from oe
            else:
                logger.error("Failed to pickle the file to disk. OS Error Code: {}".format(str(oe.errno)))
                raise
        except Exception as e:
            logging_utilities.log_traceback(e, None)
            raise

        return path

    def load(self, path: str) -> Any:
        """
        Unpickle the file.

        :param path: The file path used by the pickler.
        :return: The unpickled object.
        """
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except MemoryError as me:
            raise ResourceException._with_error(AzureMLError.create(InsufficientMemory), inner_exception=me) from me
        except Exception as e:
            if isinstance(e, OSError):
                logger.error("Failed to load the pickled file from disk. OS Error Code: {}".format(str(e.errno)))
            logging_utilities.log_traceback(e, None)
            raise


class NoOpPickler(Pickler):
    """No operation pickler for memory based."""

    def __init__(self):
        """Create a no operation pickler."""
        super(NoOpPickler, self).__init__()
        pass

    def dump(self, obj: Any, path: str, file: Any = None) -> str:
        """
        No Operation.

        :param obj: The object to pickle.
        :param path: The path the pickler will use.
        :param file: optional file object if the file is already open
        :return:
        """
        return path

    def load(self, path: str) -> str:
        """
        No Operation.

        :param path: The path to the file to unpickle.
        :return: The unpickled object.
        """
        return path
