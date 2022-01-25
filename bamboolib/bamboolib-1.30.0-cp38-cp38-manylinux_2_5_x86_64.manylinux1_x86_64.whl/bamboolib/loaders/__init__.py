# Copyright (c) 8080 Labs GmbH.
# Distributed under the terms of our End-User License Agreement (see bamboolib.com/eula
# for more information).

"""
Setup loader plugins. The import order defines the order in the search results.
"""

from bamboolib.loaders.databricks_database_table_loader import (
    DatabricksDatabaseTableLoader,
)
from bamboolib.loaders.dummy_data import DummyData
