from pyspark.dbutils import DBUtils


class DatabricksContext:
    def __init__(self, dbutils: DBUtils):
        self._dbutils = dbutils

    def get_host(self):
        return self._dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()

    def get_token(self):
        return self._dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
