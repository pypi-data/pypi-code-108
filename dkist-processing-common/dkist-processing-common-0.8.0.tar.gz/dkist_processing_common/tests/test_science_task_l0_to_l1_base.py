import json
import logging
from configparser import ConfigParser
from pathlib import Path

import pytest

import dkist_processing_common
from dkist_processing_common.tasks.base import ScienceTaskL0ToL1Base


logger = logging.getLogger(__name__)


class Task(ScienceTaskL0ToL1Base):
    def run(self):
        ...


@pytest.fixture(scope="function")
def science_l0_task(tmp_path, recipe_run_id):
    with Task(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        yield task


@pytest.fixture()
def package_dependencies() -> set:
    """
    Extract dependencies from setup.cfg and format into a set of package names
    """
    module_path = Path(dkist_processing_common.__path__[0])
    setup_cfg = module_path.parent / "setup.cfg"
    logger.info(setup_cfg)
    config = ConfigParser()
    config.read(setup_cfg)
    install_requires = [d for d in config["options"]["install_requires"].splitlines() if d]
    requirements = install_requires + ["dkist-processing-common"]
    dependencies = {pkg.split(" ")[0] for pkg in requirements}
    dependencies_without_optionals = {d.split("[")[0] for d in dependencies}
    return dependencies_without_optionals


def test_library_versions(science_l0_task, package_dependencies):
    """
    Given: An instance of a TaskBase subclass
    When: accessing library_versions attr
    Then: Result contains the dkist-processing-core package and packages specified in setup.cfg
      - options.install_requires
      - options.extras_require.test
      Result does not contain any other packages
      Result structure is Dict[str,str] where the key is library name and value is the version
    """
    library_names = json.loads(science_l0_task.library_versions).keys()
    assert len(library_names) == len(set(library_names))  # no duplicates
    for package in package_dependencies:
        assert package in set(library_names)
    library_versions = json.loads(science_l0_task.library_versions).values()
    assert all(library_versions)  # values for all versions
