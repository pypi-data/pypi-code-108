# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
try:
    import azureml.automl.core
    import azureml.automl.runtime
except ImportError:
    pass

__path__ = __import__('pkgutil').extend_path(__path__, __name__)    # type: ignore
