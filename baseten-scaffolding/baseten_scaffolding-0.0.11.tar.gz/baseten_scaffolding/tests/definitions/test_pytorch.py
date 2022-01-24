from baseten_scaffolding.definitions.pytorch import _serialize_pytorch_model
from baseten_scaffolding.errors import ModelFilesMissingError
from baseten_scaffolding.tests.conftest import temp_dir

import pytest


def test_serialize_pytorch_model_requires_model_class_file(pytorch_model, tmp_path, useless_file):
    model, model_file = pytorch_model
    with temp_dir(model_file.parent) as tmp_dir:
        with pytest.raises(ModelFilesMissingError):
            _serialize_pytorch_model(model, str(tmp_dir))
        with pytest.raises(ModelFilesMissingError):
            not_the_model_file = str(useless_file.relative_to(tmp_path))
            _serialize_pytorch_model(model, str(tmp_dir), model_files=[not_the_model_file])


def test_serialize_pytorch_model(pytorch_model, tmp_path):
    model, model_file = pytorch_model
    model_file_relative = str(model_file.relative_to(tmp_path))
    model_file_contents = open(model_file, 'r').read()
    with temp_dir(tmp_path) as tmp_dir:
        model_files_dict = _serialize_pytorch_model(model, str(tmp_dir), model_files=[model_file_relative])
        assert model_files_dict == {
            'files': {
                model_file_relative: model_file_contents
            },
            'model_class': 'MyModel',
            'class_def_file': model_file_relative
        }
