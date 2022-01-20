import os
from penvy.string.string_in_file import file_contains_string


class DatabricksConnectDetector:
    def detect(self):
        poetry_lock_path = os.getcwd() + os.sep + "poetry.lock"

        if os.path.isfile(poetry_lock_path):
            databricks_connect_present = file_contains_string('name = "databricks-connect"', poetry_lock_path)
            pyspark_present = file_contains_string('name = "pyspark"', poetry_lock_path)

            return databricks_connect_present or pyspark_present

        pyproject_path = os.getcwd() + os.sep + "pyproject.toml"

        databricks_connect_present = file_contains_string("databricks-connect =", pyproject_path)
        pyspark_present = file_contains_string("pyspark =", pyproject_path)

        return databricks_connect_present or pyspark_present
