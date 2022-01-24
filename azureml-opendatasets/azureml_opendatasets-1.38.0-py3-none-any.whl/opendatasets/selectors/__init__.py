# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""
Contains functionality for selecting and joining data from a customer dataset with data from a public dataset.

Selectors define logic that enable you to enrich your data with public datasets based on time and distance measures.
For example, with a selector you can find public data to join with your data based on nearest location, or by
rounding to the same time granularity.

Specify selectors when working with one of the classes in the :mod:`azureml.opendatasets.enrichers` package.
"""
