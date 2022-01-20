from arthurai.explainability.explanation_packager import ExplanationPackager
from arthurai.core.models import ArthurModel
from arthurai.common.constants import InputType, OutputType

import pkg_resources
import os

#TODO Katie figure out if tests are needed here for image input type (if image loading logic is added etc)
def test_validate_requirements() -> None:
    # build dict of installed packages and versions
    
    # gather user env, skipping sklearn, since we don't want to grab that when we build test req file
    cur_env = [
        (pkg.project_name, pkg.version)
        for pkg in pkg_resources.working_set
        if pkg.project_name != 'scikit-learn'
    ]

    # generate a requirements file that should succeed
    req_path = '/tmp/user_requirements.txt'
    with open(req_path, 'w') as f:
        test_package, test_version = cur_env[0]
        f.write(f"{test_package}=={test_version}")
    
    model = ArthurModel("123", InputType.Tabular, OutputType.Regression)
    packager = ExplanationPackager(model, requirements_file=req_path)

    # validate no errors
    errors = packager.validate_requirements_add_sklearn()
    assert len(errors) == 0

    # validate sklearn was added
    # we should always have sklearn in testing environment, since bunlded with shap
    with open(req_path, 'r') as f:
        req_lines = f.readlines()

    assert len(req_lines) == 2
    assert 'scikit-learn' in req_lines[1]

    # change version in req file to fail
    with open(req_path, 'w+') as f:
        test_package, test_version = cur_env[0]
        test_version = "-1.-1.-1"
        f.write(f"{test_package}=={test_version}")

    packager = ExplanationPackager(model, requirements_file=req_path)

    # validate no errors
    errors = packager.validate_requirements_add_sklearn()
    assert len(errors) == 1


def test_ignore_hidden_files():
    """Tests to make sure we don't bundle up hidden files in a given directory"""
    # Create a requirements file
    cur_env = [
        (pkg.project_name, pkg.version)
        for pkg in pkg_resources.working_set
        if pkg.project_name != 'scikit-learn'
    ]

    req_path = '/tmp/user_requirements.txt'
    with open(req_path, 'w') as f:
        test_package, test_version = cur_env[0]
        f.write(f"{test_package}=={test_version}")

    # Create a hidden file directory
    project_directory_path = '/tmp/.venv'
    if not os.path.exists(project_directory_path):
        os.makedirs(project_directory_path)

    model = ArthurModel("123", InputType.Tabular, OutputType.Regression)
    packager = ExplanationPackager(model, requirements_file=req_path, project_directory='/tmp')

    # Ensure the hidden directory is in ignore dirs (which will be handled by ignore dirs logic)
    assert('.venv' in packager.ignore_dirs)