import pandas as pd
import numpy as np
import re
import json

from arthurai.explainability.arthur_explainer import ArthurExplainer
from arthurai.common.constants import InputType, OutputType


def test_arthur_explainer_nlp_regression() -> None:
    def regression_predict(feature_vecs):
        results = []
        for fv in feature_vecs:
            results.append(np.array([0.2, 0.8]))
        return np.array(results)

    sample_data = pd.DataFrame([
        ['this is a test'],
        ['a second test with more words'],
        ['and a third test']
    ])

    explainer = ArthurExplainer(model_type=OutputType.Regression,
                                model_input_type=InputType.NLP,
                                num_predicted_attributes=1,
                                predict_func=regression_predict,
                                data=sample_data,
                                enable_shap=False,
                                label_mapping=[None])

    raw_feat_vecs = [
        ['first test test'],
        ['and a longer second test']
    ]
    exps = explainer.explain_nlp("lime", raw_feature_vectors=raw_feat_vecs, nsamples=100)

    # confirm we got 2 explanations
    assert len(exps) == 2

    for i, exp in enumerate(exps):
        # ensure single class
        assert len(exp) == 1
        # assert one explanation per unique word
        assert len(exp[0]) == len(re.split(explainer.text_delimiter, raw_feat_vecs[i][0]))


def test_arthur_explainer_nlp_classification() -> None:
    def regression_predict(feature_vecs):
        results = []
        for fv in feature_vecs:
            results.append(np.array([0.2, 0.7, 0.1]))
        return np.array(results)

    sample_data = pd.DataFrame([
        ['this is a test'],
        ['a second test with more words'],
        ['and a third test']
    ])

    explainer = ArthurExplainer(model_type=OutputType.Multiclass,
                                model_input_type=InputType.NLP,
                                num_predicted_attributes=3,
                                predict_func=regression_predict,
                                data=sample_data,
                                enable_shap=False,
                                label_mapping=[None])

    raw_feat_vecs = [
        ['first test test'],
        ['and a longer second test']
    ]
    exps = explainer.explain_nlp("lime", raw_feature_vectors=raw_feat_vecs, nsamples=100)

    # confirm we got 2 explanations
    assert len(exps) == 2

    for i, exp in enumerate(exps):
        # ensure single class
        assert len(exp) == 3
        # assert one explanation per unique word
        assert len(exp[0]) == len(re.split(explainer.text_delimiter, raw_feat_vecs[i][0]))


def test_arthur_explainer_image_classification() -> None:
    def load_image(image_path):
        return np.array([
            [[20, 4, 6], [5, 7, 12], [5, 12, 4]],
            [[20, 4, 106], [5, 7, 112], [5, 12, 104]],
            [[20, 4, 206], [5, 7, 212], [5, 12, 204]],
        ])

    def cv_predict(images):
        results = []
        for image in images:
            results.append(np.array([0.2, 0.7, 0.1]))
        return np.array(results)

    sample_data = pd.DataFrame([
        ['this is a test'],
        ['a second test with more words'],
        ['and a third test']
    ])

    explainer = ArthurExplainer(model_type=OutputType.Multiclass,
                                model_input_type=InputType.Image,
                                num_predicted_attributes=3,
                                predict_func=cv_predict,
                                data=sample_data,
                                enable_shap=False,
                                label_mapping=[None],
                                load_image_func=load_image)

    image_paths = [
        'path/to/image',
        'path/to/another/image'
    ]
    exps = explainer.explain_image("lime", image_paths=image_paths)

    # confirm we got 2 explanations
    assert len(exps) == 2

    for i, exp in enumerate(exps):
        """
        Example Output:
            {
                "lime_segment_mask": [
                    [1, 1, 1, 3, 3, 1, 0],
                    [1, 1, 1, 3, 3, 1, 0],
                    [1, 1, 1, 3, 3, 1, 0],
                    [2, 2, 2, 3, 3, 1, 0]
                ],
                "lime_region_mapping": {
                    "0": [[0, 0.23], [1, 0.3], [2, 0.001], [3, -0.5]]
                }
            }
        """
        # confirm we got an appropriate-sized mask
        assert len(exp["lime_segment_mask"]) == len(load_image(image_paths[i]))

        # sanity check on mask values
        # ideally would actually check schema here
        sample_mask_value = exp["lime_segment_mask"][0][0]
        assert sample_mask_value >= 0
        assert next(iter(exp["lime_region_mapping"].values()))

        #ensure serializable
        assert json.dumps(exp)

