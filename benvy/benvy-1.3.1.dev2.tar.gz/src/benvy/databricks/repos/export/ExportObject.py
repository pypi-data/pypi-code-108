class ExportObject:
    def __init__(
        self,
        databricks_object_id: int,
        databricks_object_type: str,
        databricks_path: str,
        local_path: str,
        src_content: str = None,
        dbc_content: dict = None,
    ):
        self._databricks_object_id = databricks_object_id
        self._databricks_object_type = databricks_object_type
        self._databricks_path = databricks_path
        self._local_path = local_path
        self._src_content = src_content
        self._dbc_content = dbc_content

    @property
    def databricks_object_id(self):
        return self._databricks_object_id

    @property
    def databricks_object_type(self):
        return self._databricks_object_type

    @property
    def databricks_path(self):
        return self._databricks_path

    @property
    def local_path(self):
        return self._local_path

    @property
    def src_content(self):
        return self._src_content

    @property
    def dbc_content(self):
        return self._dbc_content
