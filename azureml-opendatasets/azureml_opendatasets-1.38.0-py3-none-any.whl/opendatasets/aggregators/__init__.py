# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Contains functionality for defining how joined data is aggregated.

Aggregators define operations that can be performed on the result of joining data from two datasets.
For example, when you use one of the classes in :mod:`azureml.opendatasets.enrichers`, you can specify
an aggregator as part of the operation. If no aggregation is needed, use
:class:`azureml.opendatasets.aggregators.aggregator_all.AggregatorAll`.
"""
