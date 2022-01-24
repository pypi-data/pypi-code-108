# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from .reinforcement_learning_service_api import ReinforcementLearningServiceAPI
from .models.error_response import ErrorResponseException
from .version import VERSION

__all__ = [
    'ReinforcementLearningServiceAPI',
    'ErrorResponseException'
]

__version__ = VERSION
