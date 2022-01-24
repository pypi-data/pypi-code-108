import builtins
import json
from unittest.mock import patch, mock_open

from azureml.automl.dnn.nlp.ner.io.write import score


class MockModel:

    def __init__(self):
        pass

    def predict(self, data):
        return "this label0\nis label1\nan label1\nexample label0"


def test_init():
    mocked_file = mock_open()

    with patch("os.getenv", return_value="some_dir"):
        with patch.object(builtins, 'open', mocked_file, create=True):
            with patch("pickle.load", return_value="mocked_model"):
                score.init()

    assert mocked_file.call_count == 1
    assert score.model == "mocked_model"


def test_score():
    mock_model = MockModel()
    data = "this is an example"
    score.model = mock_model
    json_result = json.loads(score.run(data))

    assert json_result["result"] == "this label0\nis label1\nan label1\nexample label0"


def test_score_raises_error_bad_model():

    mock_model = "bad model that fails prediction"
    data = "this is an example"
    score.model = mock_model

    json_result = json.loads(score.run(data))

    assert "error" in json_result, "Error JSON should be returned in case of exception"
    assert json_result["error"] == "'str' object has no attribute 'predict'"
