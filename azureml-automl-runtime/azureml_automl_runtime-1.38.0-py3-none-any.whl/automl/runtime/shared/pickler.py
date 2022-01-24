# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Backwards compatible pass through during package migration."""
try:
    from azureml.automl.core.shared import pickler
    from azureml.automl.core.shared.pickler import DefaultPickler
except ImportError:
    pass
