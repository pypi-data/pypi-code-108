from ..logging_system import logger
from .__db_access_definition import DatabaseAccessObject

import os
import pandas as pd


installation = """
$ sudo apt update
$ sudo apt install postgresql postgresql-contrib
$ sudo service --status-all
$ sudo service postgresql start
"""

class PostgreSQL(DatabaseAccessObject):
    def __init__(self, verbose=False):
        if verbose:
            self.installation_guide()

    def installation_guide(self):
        logger['database'].info(installation)

    def meta_information(self):
        pass

    def connection(self):
        pass

    def execute(self):
        pass
