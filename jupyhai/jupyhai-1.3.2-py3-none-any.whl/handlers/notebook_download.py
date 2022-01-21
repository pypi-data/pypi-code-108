import os
from typing import Optional

import requests
from valohai_cli.commands.execution.outputs import get_execution_outputs

from jupyhai.handlers.base import JupyhaiHandler
from jupyhai.utils.executions import get_execution_by_id
from jupyhai.utils.outputs import get_datum_download_url


class NotebookDownloadHandler(JupyhaiHandler):
    def initialize(self, root_dir: str) -> None:
        self.root_dir = root_dir

    def post(self, execution_id: Optional[str] = None) -> None:
        if execution_id:
            self.log.info("Downloading notebook for %s..." % (execution_id))
            args = self.get_json_body()
            path = args['path'].lstrip(os.sep)
            local_path = os.path.join(self.root_dir, path)

            try:
                local_path = self.download_notebook(execution_id, local_path)
            except Exception as err:
                self.log.error(err, exc_info=True)
                raise

            filename = os.path.basename(local_path)
            relative_path = os.path.join(path, filename)
            self.finish({'path': relative_path})
        else:
            self.log.error("Error downloading notebook: No execution ID.")

    def download_notebook(self, execution_id: str, path: str) -> str:
        execution = get_execution_by_id(execution_id)
        outputs = get_execution_outputs(execution)
        out_path = ""

        with requests.Session() as dl_sess:
            for output in outputs:
                if ".ipynb" in output['name']:
                    filename = f'{str(execution.get("counter", 0))}_{output["name"]}'
                    out_path = os.path.join(path, filename)
                    url = get_datum_download_url(output["id"])
                    resp = dl_sess.get(url, stream=True)
                    resp.raise_for_status()
                    with open(out_path, 'wb') as outf:
                        for chunk in resp.iter_content(chunk_size=131072):
                            outf.write(chunk)

        self.log.info("Download finished.")
        return out_path
