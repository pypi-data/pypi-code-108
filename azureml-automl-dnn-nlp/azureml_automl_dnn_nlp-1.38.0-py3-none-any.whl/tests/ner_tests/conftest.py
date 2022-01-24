import os
import pytest
import shutil
import tempfile

try:
    from transformers import AutoTokenizer
    has_transformers = True
except ImportError:
    has_transformers = False


def _copy_data(target_path='.'):
    dirname = os.path.dirname(__file__)
    shutil.copytree(os.path.join(dirname, '../data/ner_data'),
                    os.path.join(target_path, 'ner_data'))


@pytest.fixture(scope="session")
def new_clean_dir():
    oldpath = os.getcwd()
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)
    _copy_data()
    yield
    os.chdir(oldpath)
    shutil.rmtree(newpath)


@pytest.fixture
def get_tokenizer():
    return AutoTokenizer.from_pretrained("bert-base-cased")
