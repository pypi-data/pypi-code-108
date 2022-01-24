from unittest.mock import patch, Mock
import numpy as np

from azureml.automl.dnn.nlp.ner.model_wrapper import ModelWrapper


def test_predict():

    data = "This\nis\nsentence"
    model = Mock()
    label_list = ["label0", "label1"]

    return_val = (np.array([[[1.4, 0.2], [1.2, 1.0], [0.5, 0.6]]]), np.array([[1, 0, 1]]), "not_required")
    wrapper = ModelWrapper(model, label_list, "some_tokenizer")
    with patch("transformers.Trainer.predict", return_value=return_val):
        output = wrapper.predict(data)
    assert output == "This label0\nis label0\nsentence label1"
