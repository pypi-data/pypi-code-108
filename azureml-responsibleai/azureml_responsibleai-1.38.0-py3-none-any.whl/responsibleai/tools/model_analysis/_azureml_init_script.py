# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Worker script to initialise model analysis in AzureML.

Tasks:
- Create training data snapshot (if required)
- Create test data snapshot (if required)
- Create root Model Analysis run
    - Make predictions from the Model
"""
from azureml.responsibleai.tools.model_analysis._init_utilities import init_wrapper


if __name__ == '__main__':
    init_wrapper()
