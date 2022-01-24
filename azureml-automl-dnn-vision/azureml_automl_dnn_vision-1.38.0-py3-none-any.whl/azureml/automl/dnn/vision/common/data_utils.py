# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Helper Utils for reading input data."""

import os

from pathlib import Path

from .constants import SettingsLiterals
from .exceptions import AutoMLVisionValidationException
from .utils import is_aml_dataset_input

from typing import Dict, Any, Tuple, Optional


def validate_labels_files_paths(settings: Dict[str, Any]) -> None:
    """Validates that labels files paths passed as arguments are compatible and valid.

    :param settings: Dictionary with all training and model settings
    :type settings: dict
    """
    if is_aml_dataset_input(settings):
        if settings.get(SettingsLiterals.LABELS_FILE, None) or \
                settings.get(SettingsLiterals.VALIDATION_LABELS_FILE, None):
            raise AutoMLVisionValidationException("Labels files should not be provided when using AML Datasets.",
                                                  has_pii=False)
    else:
        labels_path, validation_labels_path = get_labels_files_paths_from_settings(settings)

        if not labels_path:
            raise AutoMLVisionValidationException("A labels file should be provided when AML Datasets are not used.",
                                                  has_pii=False)

        if not Path(labels_path).is_file():
            raise AutoMLVisionValidationException("The labels file path provided is invalid.", has_pii=False)

        if validation_labels_path and not Path(validation_labels_path).is_file():
            raise AutoMLVisionValidationException("The validation labels file path provided is invalid.",
                                                  has_pii=False)


def get_labels_files_paths_from_settings(settings: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """Parse the settings and get file paths for training labels file and validation labels file.

    :param settings: Dictionary with all training and model settings
    :type settings: dict
    :return: Tuple of training file path, validation file path
    :rtype: Tuple[str, str]
    """
    labels_file = settings.get(SettingsLiterals.LABELS_FILE, None)
    validation_labels_file = settings.get(SettingsLiterals.VALIDATION_LABELS_FILE, None)
    labels_path: Optional[str] = None
    validation_labels_path: Optional[str] = None

    if labels_file is not None:
        labels_path = os.path.join(settings[SettingsLiterals.LABELS_FILE_ROOT], labels_file)
    if validation_labels_file is not None:
        validation_labels_path = os.path.join(settings[SettingsLiterals.LABELS_FILE_ROOT], validation_labels_file)

    return labels_path, validation_labels_path
