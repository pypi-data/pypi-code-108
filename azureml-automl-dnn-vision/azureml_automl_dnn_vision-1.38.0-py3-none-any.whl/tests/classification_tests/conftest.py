import pytest
import os
import shutil
import tempfile


def _copy_data(target_path='.'):
    dirname = os.path.dirname(__file__)
    shutil.copytree(os.path.join(dirname, '../data/classification_data'),
                    os.path.join(target_path, 'classification_data'))


@pytest.fixture(scope="session")
def new_clean_dir():
    oldpath = os.getcwd()
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)
    _copy_data()
    yield
    os.chdir(oldpath)
    shutil.rmtree(newpath)


@pytest.fixture(scope='session')
def src_image_list_file_name():
    return 'src_image_class_list_file.txt'


@pytest.fixture(scope='session')
def image_list_file_name():
    return 'image_class_list_file.txt'


@pytest.fixture(scope='session')
def image_dir():
    return 'classification_data/images'


@pytest.fixture(scope='session')
def root_dir():
    return 'classification_data'
