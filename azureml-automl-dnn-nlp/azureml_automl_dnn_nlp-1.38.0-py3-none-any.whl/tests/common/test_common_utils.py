import builtins
from os.path import join
from unittest.mock import patch, mock_open

import pytest

from azureml.automl.core.inference import inference
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.dnn.nlp.common._model_selector import get_model_from_language, get_path
from azureml.automl.dnn.nlp.common._utils import (is_data_labeling_run_with_file_dataset,
                                                  save_script,
                                                  prepare_run_properties,
                                                  prepare_post_run_properties,
                                                  save_conda_yml,
                                                  _get_language_code)
from azureml.automl.dnn.nlp.common.constants import ModelNames
from azureml.automl.dnn.nlp.common.constants import SystemSettings
from azureml.automl.runtime.featurizer.transformer.data.word_embeddings_info import EmbeddingInfo
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.environment import Environment
from ..mocks import MockRun


class TestCommonFuncs:
    @pytest.mark.parametrize(
        'dataset_language, expected', [
            ('eng', ModelNames.BERT_BASE_CASED),
            ('deu', ModelNames.BERT_BASE_GERMAN_CASED),
            ('ita', ModelNames.BERT_BASE_MULTILINGUAL_CASED),
            ('ENG', ModelNames.BERT_BASE_CASED),
            ('english', ModelNames.BERT_BASE_MULTILINGUAL_CASED),
            ('', ModelNames.BERT_BASE_MULTILINGUAL_CASED),
            ('DEU', ModelNames.BERT_BASE_GERMAN_CASED),
            ('Deu', ModelNames.BERT_BASE_GERMAN_CASED)]
    )
    def test_model_retrieval(self, dataset_language, expected):
        model, _ = get_model_from_language(dataset_language)
        assert model == expected

    def test_no_cdn_throws_exception(self):
        with patch("azureml.automl.dnn.nlp.common._model_selector.get_path", return_value=None):
            with pytest.raises(ClientException):
                model, _ = get_model_from_language("some_lanugage", need_path=True)

    @pytest.mark.parametrize(
        'input_language, input_multilabel, expected', [
            ('eng', True, EmbeddingInfo.BERT_BASE_UNCASED_AUTONLP_3_1_0),
            ('eng', False, EmbeddingInfo.BERT_BASE_CASED),
            ('deu', False, EmbeddingInfo.BERT_BASE_GERMAN_CASED_AUTONLP_3_1_0),
            ('ita', False, EmbeddingInfo.BERT_BASE_MULTLINGUAL_CASED_AUTONLP_3_1_0)]
    )
    def test_get_path(self, input_language, input_multilabel, expected):
        mock_path = "azureml.automl.dnn.nlp.common._model_selector.AutoMLPretrainedDNNProvider"
        with patch(mock_path) as mock_provider:
            get_path(input_language, input_multilabel)
        assert mock_provider.call_args[0][0] == expected

    @pytest.mark.parametrize(
        'input,expected', [
            ('auto', 'eng'),
            ({"_dataset_language": "eng"}, 'eng'),
            ({"_dataset_language": "deu"}, 'deu'),
            ({"_dataset_language": "ita"}, 'ita')]
    )
    def test_language_recognition(self, input, expected):
        language = _get_language_code(input)
        assert language == expected

    @pytest.mark.parametrize(
        'file_to_save', ['some_file', 'score', 'score_script']
    )
    def test_save_script(self, file_to_save):
        mocked_file = mock_open(read_data='some file contents to write')
        with patch.object(builtins, 'open', mocked_file, create=True):
            save_script(file_to_save, "some_directory")

        assert mocked_file.call_count == 2
        mocked_file.assert_any_call(join("some_directory", file_to_save))
        mocked_file.assert_called_with(join("./outputs", file_to_save), 'w')
        any('write(some file contents to write)' in str(call) for call in mocked_file()._mock_mock_calls)

    def test_prepare_run_properties(self):
        run = MockRun()
        prepare_run_properties(run, 'some_model')

        assert "runTemplate" in run.properties
        assert "run_algorithm" in run.properties
        assert run.properties['runTemplate'] == "automl_child"
        assert run.properties['run_algorithm'] == "some_model"

    def test_prepare_post_run_properties(self):
        run = MockRun()
        run.id = "some_run_id"
        with patch("azureml.automl.core.inference._get_model_name", return_value="some_model_id"):
            prepare_post_run_properties(run,
                                        "some_model_path",
                                        1234,
                                        "some_conda_file",
                                        'some_deploy_path',
                                        'accuracy',
                                        0.1234)

        artifact_path = "aml://artifact/ExperimentRun/dcid.some_run_id/"
        assert inference.AutoMLInferenceArtifactIDs.CondaEnvDataLocation in run.properties
        file_path = artifact_path + "some_conda_file"
        assert run.properties[inference.AutoMLInferenceArtifactIDs.CondaEnvDataLocation] == file_path

        assert inference.AutoMLInferenceArtifactIDs.ModelDataLocation in run.properties
        file_path = artifact_path + "some_model_path"
        assert run.properties[inference.AutoMLInferenceArtifactIDs.ModelDataLocation] == file_path

        assert inference.AutoMLInferenceArtifactIDs.ModelName in run.properties
        assert run.properties[inference.AutoMLInferenceArtifactIDs.ModelName] == "somerunid"

        assert inference.AutoMLInferenceArtifactIDs.ModelSizeOnDisk in run.properties
        assert run.properties[inference.AutoMLInferenceArtifactIDs.ModelSizeOnDisk] == 1234

        assert 'score' in run.properties
        assert run.properties['score'] == 0.1234

        assert 'primary_metric' in run.properties
        assert run.properties['primary_metric'] == "accuracy"

    def test_save_conda_yml(self):
        conda_deps = CondaDependencies()
        conda_deps.add_pip_package("horovod==0.1.2")
        conda_deps.add_pip_package("dummy_package==0.1.2")

        env = Environment(name="some_name")
        env.python.conda_dependencies = conda_deps

        mocked_file = mock_open()
        with patch.object(builtins, 'open', mocked_file, create=True):
            save_conda_yml(env)

        mocked_file.assert_called_once_with(join("./outputs", "conda_env.yml"), 'w')

        output_file_contents = str(mocked_file()._mock_mock_calls[1])

        assert 'dummy_package==0.1.2' in output_file_contents
        assert 'horovod==0.1.2' not in output_file_contents

    @pytest.mark.parametrize('run_source', ["automl", "Labeling"])
    @pytest.mark.parametrize('labeling_dataset_type', ["FileDataset", "TabularDataset", None])
    def test_is_data_labeling_run_with_file_dataset(self, run_source, labeling_dataset_type):
        mock_run = MockRun(
            run_source=run_source,
            label_column_name="label",
            labeling_dataset_type=labeling_dataset_type
        )
        result = is_data_labeling_run_with_file_dataset(mock_run)
        expected_result = True \
            if (run_source == SystemSettings.LABELING_RUNSOURCE
                and labeling_dataset_type == SystemSettings.LABELING_DATASET_TYPE_FILEDATSET) \
            else False
        assert result == expected_result
