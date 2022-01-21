import unittest

from sqlalchemy.orm import Session

from sessionize.utils.setup_test import sqlite_setup, postgres_setup
from sessionize.utils.select import select_records
from sessionize.exceptions import ForceFail
from sessionize.utils.alter import rename_column, drop_column, add_column
from sessionize.utils.alter import rename_table, copy_table, replace_primary_key
from sessionize.utils.alter import create_primary_key, name_primary_key

# TODO: rename_column & drop_column

# TODO: drop_column & add_column

# TODO: add_column & rename_column

# TODO:rename_table & copy_table

# TODO: copy_table & replace_primary_key

# TODO: create_primary_key & replace_primary_key