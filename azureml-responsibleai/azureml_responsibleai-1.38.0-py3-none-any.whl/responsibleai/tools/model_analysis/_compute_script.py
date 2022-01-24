# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Worker script to compute RAI requests."""

try:
    from azureml.responsibleai.tools.model_analysis._utilities import _compute_wrapper
except ImportError:
    # Fix backward compat issue when sumitting RAI run.
    # The namespace for _compute_wrapper() was changed
    # after 1.33.0 was shipped which leads to failure of
    # remote submissions of individual explain, CFE,
    # error analysis and causal runs in scenarios where
    # locally a user is using master env but remotely a
    # user uses prod SDK 1.33.0. Hence, the retry of the
    # import from the prod SDK version.
    from azureml.responsibleai.tools.model_analysis._compute_utilities import _compute_wrapper  # type: ignore


if __name__ == '__main__':
    _compute_wrapper()
