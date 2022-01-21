from jupyhai.handlers.base import JupyhaiHandler
from jupyhai.utils.outputs import get_datum_download_url


class OutputDownloadURLHandler(JupyhaiHandler):
    def get(self, output_id: str) -> None:
        self.finish({"url": get_datum_download_url(output_id)})
