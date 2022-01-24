from typing import List, Dict, Union
from pathlib import Path
import shutil
import json
import os


class Deployment:
    """
    Deployment is a container class for built artifacts and reports
    """
    META_FNAME = Path('.deployment.json')

    def __init__(self, path: Union[None, Path], report=None, logs=None):
        self._compiled_files: List = []
        self._report = report
        self._compile_logs = logs
        if path:
            self.base_path = Path(path)
            self.report_path = self.base_path / Path('report.json')
        else:
            self.base_path = Path("")
            self.report_path = Path('report.json')

    def __str__(self):
        try:
            with open(self.report_path, 'r') as f:
                report = json.load(f)
            return json.dumps(report, sort_keys=True, indent=2)
        except:
            return "{}"

    def __repr__(self):
        return json.dumps(self.meta, sort_keys=True, indent=2)

    @property
    def report(self) -> Dict:
        if not self._report:
            if os.path.exists(self.report_path):
                with open(self.report_path, 'r') as f:
                    return dict(json.load(f)["metrics"])
        else:
            return self._report

        return {}

    @property
    def compiled_files(self):
        if os.path.exists(self.base_path):
            model_src = self.base_path / Path('build')
            if model_src.exists():
                files = []
                # list all files recursively
                for i in os.walk(model_src):
                    if len(i[2]) > 0:
                        for j in i[2]:
                            files.append(os.path.join(i[0], j))
                return files

        return []

    @property
    def compile_logs(self):
        if not self._compile_logs:
            if os.path.exists(self.report_path):
                with open(self.report_path, 'r') as f:
                    return json.load(f)["logs"]
        else:
            return self._compile_logs

        return []

    @property
    def meta(self):
        return {"base_path": str(self.base_path),
                "compiled_files": [str(x) for x in self.compiled_files],
                "report_path": str(self.report_path),
                "report": self.report
                }

    def save(self):
        _path = self.base_path / self.META_FNAME
        open(_path, 'w').write(json.dumps(self.meta, sort_keys=True, indent=4))

    def load(self):
        meta = json.loads(open(self.base_path / self.META_FNAME, 'r').read())

        self.base_path = meta["base_path"]
        self.report_path = meta["report_path"]

    def load_raw(self):
        """Scan folder and construct the object"""
        pass

    def deploy(self, target: Path):
        """Copy the deployment folder to target

        Copy the deployment folder to target and reconstruct the meta

        """
        shutil.copytree(self.base_path, target)
        if os.path.exists(target / self.META_FNAME):
            os.remove(target / self.META_FNAME)
        deployment = Deployment(target)

        return deployment
