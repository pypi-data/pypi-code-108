import builtins
from os.path import join
from unittest.mock import patch, mock_open

from azureml.automl.dnn.nlp.classification.io.write.save_utils import save_metrics
from azureml.automl.dnn.nlp.common.constants import OutputLiterals


class TestSaveFuncs:

    def test_save_metrics(self):
        mocked_metrics_dict = {
            "accuracy": [0.5],
            "precision": [0.6],
            "recall": [0.7]
        }
        mocked_file = mock_open()

        with patch.object(builtins, 'open', mocked_file, create=True):
            save_metrics(mocked_metrics_dict)

        save_path = join(OutputLiterals.OUTPUT_DIR, "metrics.csv")
        mocked_file.assert_called_once_with(save_path, 'w', encoding='utf-8', newline='')

        assert any("accuracy,precision,recall" in str(call) for call in mocked_file()._mock_mock_calls)
        assert any("0.5,0.6,0.7" in str(call) for call in mocked_file()._mock_mock_calls)
