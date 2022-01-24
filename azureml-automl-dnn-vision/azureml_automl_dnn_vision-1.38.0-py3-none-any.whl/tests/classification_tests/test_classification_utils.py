import pytest
from azureml.automl.dnn.vision.classification.common.classification_utils import _CondaUtils


@pytest.mark.usefixtures('new_clean_dir')
class TestUtils:
    def test_conda_utils(self):
        # install a specific pip package
        cd = _CondaUtils.get_conda_dependencies()
        package_name = 'azureml-automl-dnn-vision'
        # find package in the list of packages
        package_with_version = None
        for package_str in cd.pip_packages:
            if package_name in package_str:
                package_with_version = package_str
        # make sure we have some version
        assert '==' in package_with_version or '~=' in package_with_version
        if '==' in package_with_version:
            assert package_with_version.split('==')[1] != ''
        if '~=' in package_with_version:
            assert package_with_version.split('~=')[1] != ''
