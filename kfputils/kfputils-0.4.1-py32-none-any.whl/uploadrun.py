from .pipeline import (
    upload_pipeline,
    _extract_pipeline_name,
)
from .run import Runner
from .utils import read_params


class UploaderRunner:
    def __init__(self, client, package_file) -> None:
        self.client = client
        self.runner = Runner(self.client)
        self.package_file = package_file
        self.pipeline_name = _extract_pipeline_name(package_file)

    def upload(
        self,
        pipeline_version,
    ):
        """Upload a KFP pipeline."""
        upload_res, is_first_version = upload_pipeline(
            self.client, self.pipeline_name, self.package_file, pipeline_version
        )
        # if is_first_version:
        #     print(f"[OK] created first version of pipeline: {self.pipeline_name}")
        # else:
        #     print(
        #         f"[OK] created updated version of pipeline: {self.pipeline_name}, version: {pipeline_version}"
        #     )
        return upload_res, is_first_version

    def upload_run(
        self,
        pipeline_version,
        experiment_name,
        params_file,
    ):
        """Upload and trigger a run of a KFP pipeline."""
        upload_res, is_first_version = self.upload(self.client, pipeline_version)
        if upload_res is None:
            raise Exception("Upload failed")
        if params_file is not None:
            params = read_params(params_file)
        run_res = self.runner.run(upload_res.id, experiment_name, params)
        return run_res, upload_res, is_first_version
