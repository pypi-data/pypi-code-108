import pytest
import os
import shutil
import tempfile


def _copy_data(target_path='.'):
    dirname = os.path.dirname(__file__)
    shutil.copytree(os.path.join(dirname, '../data/object_detection_data'),
                    os.path.join(target_path, 'object_detection_data'))


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
def image_list_file_name():
    return 'src_image_od_list_file.txt'


@pytest.fixture(scope='session')
def data_root():
    return 'object_detection_data'
