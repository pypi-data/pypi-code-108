# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: skip-file
"""IPython config."""

c = get_config()

if not c.InteractiveShellApp.extensions:
    c.InteractiveShellApp.extensions = []

c.InteractiveShellApp.extensions.append('azureml.synapse.magics')
