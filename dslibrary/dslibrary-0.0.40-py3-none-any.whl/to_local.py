"""
Implementation of calls for local development, experimentation and testing.
"""
import json
import os
import time

from .utils.file_utils import FileOpener
from .front import DSLibrary, DSLibraryException
from .metadata import Metadata


class DSLibraryLocal(DSLibrary):
    """
    Functionality is configured through 'spec'.
    """
    def __init__(self, filesystem_root: str=None, spec: (dict, str)=None):
        super(DSLibraryLocal, self).__init__(spec)
        self._root = os.path.expanduser(filesystem_root or ".")
        self._metadata = None
        self._params = None

    def get_metadata(self):
        """
        Information about parameters, inputs, outputs.  We check for a few specific filenames in the model's root
        folder.
        """
        if self._metadata is None:
            self._metadata = Metadata.from_folder(self._root, fill_default=True)
        return self._metadata

    def _opener(self, path: str, mode: str, **kwargs):
        """
        Open files.

        :param path:    Path to file, or URI of file.
        :param mode:    Open mode (r, rb, w, wb, a, ab)
        :param kwargs:  Additional arguments to customize details of the operation.
        :return:    File-like object.
        """
        return FileOpener(self._root).open(path, mode, **kwargs)

    def open_run_data(self, filename: str, mode: str = 'r'):
        """
        We put all the 'run data' in a sibling folder, shared across all related models.
        """
        if self._mlflow_all:
            raise DSLibraryException("open_run_data() is not yet supported for use in MLFlow")
        tmp_folder = os.path.join(self._root, "../__run_data__")
        if not os.path.exists(tmp_folder) and ('w' in mode or 'a' in mode):
            os.mkdir(tmp_folder)
        return self._opener(os.path.join(tmp_folder, filename.strip("/")), mode)

    def scoring_response(self, score) -> None:
        """
        Scores are appended to a CSV file.
        """
        self.write_resource("scores.json", json.dumps({"time": time.time(), "score": score}) + "\n", append=True)

    def iter_scoring_requests(self, callback=None):
        """
        This implementation supports a very simple way to test a scoring engine.  You drop JSON files into a
        folder to make a request.  When the folder is deleted, iteration ends and the scoring engine exits.
        """
        folder = os.path.join(self._root, "scoring_requests")
        while True:
            if callback:
                callback()
            time.sleep(0.2)
            if not os.path.exists(folder):
                continue
            for f in os.listdir(folder):
                if not f.endswith(".json"):
                    continue
                fn = os.path.join(folder, f)
                try:
                    with open(fn, 'r') as f_r:
                        request = json.load(f_r)
                except ValueError:
                    # ignore invalid format (file may not be completely written)
                    # - note that invalid files will stack up
                    continue
                os.remove(fn)
                yield request
