import os
from urllib import request
from benvy.databricks.DatabricksContext import DatabricksContext


class RepoFileUploader:
    def __init__(
        self,
        databricks_context: DatabricksContext,
    ):
        self._databricks_context = databricks_context

    def upload_files_to_repo(self, src_file_path: str, dst_dir: str):
        dbx_host = self._databricks_context.get_host()
        dbx_token = self._databricks_context.get_token()

        dst_file_name = os.path.basename(os.path.normpath(src_file_path))

        dst_url = f"{dbx_host}/api/2.0/workspace-files/{dst_dir}/{dst_file_name}?overwrite=true"
        headers = {
            "Authorization": f"Bearer {dbx_token}",
        }

        with open(src_file_path, "rb") as f:
            body = f.read()

        self._api_post(dst_url, headers, body)

    def _api_post(self, url: str, headers: dict, body: bytes):
        req = request.Request(url, data=body)

        for key, value in headers.items():
            req.add_header(key, value)

        return request.urlopen(req)
