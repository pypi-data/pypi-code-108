"""
Module that includes helper methods to run
end to end tests on UP42 block images.

For instance you can setup a simple e2e test as such:
```python
from pathlib import Path

import geojson

from blockutils.e2e import E2ETest

# Disable unused params for assert
# pylint: disable=unused-argument
def asserts(input_dir: Path, output_dir: Path, quicklook_dir: Path, logger):
    # Print out bbox of one tile
    geojson_path = output_dir / "data.json"

    with open(str(geojson_path)) as f:
        feature_collection = geojson.load(f)

    logger.info(feature_collection.features[0].bbox)

    # Check number of files in output_prefix
    output_ndvi = output_dir / Path(
        feature_collection.features[0].properties["up42.data_path"]
    )

    logger.info(output_ndvi)

    assert output_ndvi.exists()


if __name__ == "__main__":
    e2e = E2ETest(image_name="ndvi")
    e2e.add_parameters({"output_original_raster": False})
    # you need to have access to the bucket
    e2e.add_gs_bucket("gs://blocks-e2e-testing/pleiades_rgbnir/input/*")
    e2e.asserts = asserts
    e2e.run()
```

"""
import os
import timeit
from typing import List, Tuple

import subprocess
from pathlib import Path
import shutil
import json
from logging import Logger
from blockutils.common import setup_test_directories
from blockutils.logging import get_logger

LOGGER = get_logger(__name__)


class E2ETest:
    # Disable pylint check fo unitary E2E test class
    # pylint: disable=too-many-instance-attributes
    def __init__(
        self, image_name: str, variant: str = "", interactive_mode: bool = False
    ):
        """E2ETest main class.

        Args:
            image_name (str): The name you assigned to your docker image.
            variant (str, optional): An optional variant of e2e test in
                case you want to define more than one. Defaults to "".
            interactive_mode (bool): adds an additional -it flag to the docker run command in case debugging is needed
                while running e2e locally. For running e2e in Circle CI this needs to be False (default).
        """
        self.image_name = image_name
        self.variant = variant
        self.parameters: dict = {}
        self.additional_env: str = ""
        self.gs_bucket: str = ""
        self.local_files: str = ""
        # Only used when a certain local file needs to be mounted in docker container.
        self.add_files: List[Tuple] = []
        # Only deletes the output if ran in CI
        self.delete_output = self.in_ci
        self.interactive_mode: bool = interactive_mode

        self.test_dir = Path(f"/tmp/e2e_{self.image_name}")
        if self.variant:
            self.test_dir = Path(f"/tmp/e2e_{self.image_name}_{self.variant}")
        self.input_dir, self.output_dir, self.quicklook_dir = setup_test_directories(
            self.test_dir
        )
        self.expected_exit_code = 0

    @property
    def in_ci(self) -> bool:
        """Is this code being ran in a CI environment?

        Returns:
            bool
        """
        return os.environ.get("CI") == "true"

    def add_parameters(self, paramaters: dict):
        """Add specific job parameters for this e2e test.

        Args:
            paramaters (dict): A dictionary with parameters.
        """
        self.parameters = paramaters

    def add_additional_env(self, additional_env: str):
        """With this method you can pass additional environment variables
        in your docker run command.

        Args:
            additional_env (str): For example "-e `A_VAR=5`"
        """
        self.additional_env = additional_env

    def add_gs_bucket(self, gs_bucket: str):
        """Adds a GCS bucket location to fetch data from and places it
        in the input folder for the block run.

        Args:
            gs_bucket (str): A GCS style location (i.e. `gs://some-bucket/my-input/*`).
                You need to have access to this bucket and you need to be authenticated.
        """
        self.gs_bucket = gs_bucket

    def add_local_files(self, local_path: str):
        """Adds a local location of file to fetch data from and places it
        in the input folder for the block run.

        Args:
            gs_bucket (str): A GCS style location (i.e. `gs://some-bucket/my-input/*`).
                You need to have access to this bucket and you need to be authenticated.
        """
        self.local_files = local_path
        assert (
            Path(self.local_files).resolve().is_dir()
        ), "Local path should be a folder!"

    @staticmethod
    def asserts(
        input_dir: Path, output_dir: Path, quicklook_dir: Path, logger: Logger = LOGGER
    ):
        """Abstract method to be used to create asserts for an e2e test.

        Args:
            input_dir (Path): Input directory.
            output_dir (Path): Output directory.
            quicklook_dir (Path): Quicklook directory.
            logger (Logger, optional): A logger to use during asserts. Defaults to LOGGER.
        """
        pass  # pylint: disable=unnecessary-pass

    # Remove check from subprocess since we check the exit_code
    # pylint: disable=subprocess-run-check
    @staticmethod
    def run_subprocess(cmd: str, assert_return_code=True, exit_code=0):
        """Utility to run arbitrary commands.

        Args:
            cmd (str): Some bash style command (i.e. `rm file.txt`)
            assert_return_code (bool, optional): Make sure return code is exit_code. Defaults to True.
            exit_code (int, optional): Exit code to assert with. Defaults to 0.
        """
        sub = subprocess.run(cmd, shell=True)
        return_code = sub.returncode
        if assert_return_code:
            LOGGER.info(f"CMD: {cmd}")
            LOGGER.info(f"EXIT CODE: {return_code}")
            assert return_code == exit_code

    def download_input(self):
        """Downloads input and places it in the rigth folder."""
        LOGGER.info("Downloading input...")
        self.run_subprocess(f"gsutil -m cp -r {self.gs_bucket} {self.input_dir}")
        LOGGER.info(f"Contents of input {list(self.input_dir.glob('**/*'))}")

    def copy_local_file(self):
        LOGGER.info(f"Copying files from {self.local_files} to input")
        if self.input_dir.exists():
            self.input_dir.rmdir()
        shutil.copytree(self.local_files, self.input_dir)

    def create_volume(self):
        """Creates a docker volume with mounted folders (and copied folders in CI)."""
        LOGGER.info("Creating a volume...")
        base_cmd = (
            f"docker create -v {str(self.input_dir)}:/tmp/input "
            f"-v {str(self.output_dir)}:/tmp/output "
            f"-v {str(self.quicklook_dir)}:/tmp/quicklooks "
        )

        for in_file, dst_file in self.add_files:
            base_cmd += f"-v {str(in_file)}:{str(dst_file)} "

        create_cmd = base_cmd + f"--name e2e {self.image_name}"
        self.run_subprocess(create_cmd)
        if self.in_ci:
            for in_file, dst_file in self.add_files:
                self.run_subprocess(f"docker cp {str(in_file)} e2e:{str(dst_file)}")

            self.run_subprocess(f"docker cp {str(self.input_dir)}/. e2e:/tmp/input")

    def run_container(self):
        """Actual run of docker container"""
        default_run_cmd = f"docker run {'-it' if self.interactive_mode else ''} --volumes-from e2e --name job -e"

        LOGGER.info("Running container...")
        run_cmd = (
            f"{default_run_cmd} 'UP42_TASK_PARAMETERS={json.dumps(self.parameters)}'"
            f" {self.additional_env if self.additional_env else ''} {self.image_name}"
        )

        start = timeit.default_timer()
        self.run_subprocess(run_cmd, exit_code=self.expected_exit_code)
        stop = timeit.default_timer()
        LOGGER.info(f"Time: {stop - start}")

    def copy_results(self):
        """Copy results to output folder in local environment."""
        LOGGER.info("Copying results...")
        self.run_subprocess(f"docker cp job:/tmp/. {str(self.test_dir)}")

    def cleanup_volumes(self):
        """Cleanup created volumes."""
        LOGGER.info("Cleaning up volumes...")
        self.run_subprocess("docker rm -v e2e")
        self.run_subprocess("docker rm -v job")

    def run_asserts(self):
        """Run defined asserts."""
        self.asserts(self.input_dir, self.output_dir, self.quicklook_dir, LOGGER)

    def _delete_output(self):
        """Deletes the whole test folder."""
        LOGGER.info("Removing output...")
        shutil.rmtree(self.test_dir)

    def run(self):
        """Run defined end-to-end test."""
        if self.gs_bucket:
            self.download_input()

        if self.local_files:
            self.copy_local_file()

        # Make sure entire docker component passes,
        # Otherwise clean volumes and output
        try:
            self.create_volume()

            self.run_container()

            self.copy_results()
        except AssertionError:
            LOGGER.error(f"Test for {self.image_name} failed!")
            self.cleanup_volumes()
            self._delete_output()
            raise

        self.cleanup_volumes()

        self.run_asserts()

        if self.delete_output:
            self._delete_output()
