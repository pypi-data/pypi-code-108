from .__db_access_definition import DatabaseAccessObject

import os
import sqlite3
import pandas as pd


class SQLite(DatabaseAccessObject):
    def __init__(self, verbose=False):
        if verbose:
            self.installation_guide()

    def installation_guide(self):
        pass

    def meta_information(self):
        pass

    def connection(self):
        pass

    def execute(self):
        pass
