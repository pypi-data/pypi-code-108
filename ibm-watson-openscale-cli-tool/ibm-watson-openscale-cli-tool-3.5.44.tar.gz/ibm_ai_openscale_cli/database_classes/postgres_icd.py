# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8
from ibm_ai_openscale_cli.database_classes.postgres import Postgres

class PostgresICD(Postgres):

    def __init__(self, credentials):
        connection_data = credentials['connection']['postgres']
        hostname = connection_data['hosts'][0]['hostname']
        port = connection_data['hosts'][0]['port']
        dbname = connection_data['database']
        user = connection_data['authentication']['username']
        password = connection_data['authentication']['password'] #pragma: allowlist secret
        super().__init__(user, password, hostname, port, dbname)
