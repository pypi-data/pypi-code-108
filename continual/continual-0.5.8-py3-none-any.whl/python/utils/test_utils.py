import sys
import json
from collections import OrderedDict

import pytest
from continual.python.utils import utils


def test_renormalize_floats():
    dict_with_infty = {
        "test": OrderedDict(
            [
                (
                    "twitter.rating",
                    OrderedDict(
                        [
                            (
                                "loss",
                                [
                                    5.057579271721117,
                                    3.8239024769176138,
                                    2.024504459265507,
                                    0.653912977738814,
                                    1.9730541344844934,
                                    0.9534132408373284,
                                    0.7960169821074514,
                                    1.1693615768895005,
                                    1.1245469758004853,
                                ],
                            ),
                            (
                                "accuracy",
                                [
                                    0.6666666666666666,
                                    0.6666666666666666,
                                    0.6666666666666666,
                                    0.5151515151515151,
                                    0.3333333333333333,
                                    0.3333333333333333,
                                    0.6666666666666666,
                                    0.6666666666666666,
                                    0.6666666666666666,
                                ],
                            ),
                        ]
                    ),
                ),
                (
                    "combined",
                    {
                        "accuracy": [
                            0.6666666666666666,
                            float("inf"),
                            0.6666666666666666,
                            0.5151515151515151,
                            float("inf"),
                            float("inf"),
                            0.6666666666666666,
                            0.6666666666666666,
                            0.6666666666666666,
                        ],
                        "loss": [
                            5.057579271721117,
                            3.8239024769176138,
                            2.024504459265507,
                            0.653912977738814,
                            1.9730541344844934,
                            0.9534132408373284,
                            0.7960169821074514,
                            1.1693615768895005,
                            1.1245469758004853,
                        ],
                    },
                ),
            ]
        ),
        "train": OrderedDict(
            [
                (
                    "twitter.rating",
                    OrderedDict(
                        [
                            (
                                "loss",
                                [
                                    4.679015577885142,
                                    3.3940531412760415,
                                    1.6723367791426809,
                                    0.4038796341210081,
                                    1.5410312853361432,
                                    0.5831126832125479,
                                    0.4515161346970943,
                                    0.7001664680347108,
                                    0.5780835068016722,
                                ],
                            ),
                            (
                                "accuracy",
                                [
                                    0.6842105263157895,
                                    0.6842105263157895,
                                    0.6842105263157895,
                                    0.9824561403508771,
                                    0.3157894736842105,
                                    0.5350877192982456,
                                    0.7192982456140351,
                                    0.7017543859649122,
                                    0.7105263157894737,
                                ],
                            ),
                        ]
                    ),
                ),
                (
                    "combined",
                    {
                        "accuracy": [
                            0.6842105263157895,
                            0.6842105263157895,
                            0.6842105263157895,
                            0.9824561403508771,
                            0.3157894736842105,
                            0.5350877192982456,
                            0.7192982456140351,
                            0.7017543859649122,
                            0.7105263157894737,
                        ],
                        "loss": [
                            4.679015577885142,
                            3.3940531412760415,
                            1.6723367791426809,
                            0.4038796341210081,
                            float("inf"),
                            0.5831126832125479,
                            0.4515161346970943,
                            0.7001664680347108,
                            0.5780835068016722,
                        ],
                    },
                ),
            ]
        ),
        "validation": OrderedDict(
            [
                (
                    "twitter.rating",
                    OrderedDict(
                        [
                            (
                                "loss",
                                [
                                    4.156894207000732,
                                    3.1449267864227295,
                                    1.6688027381896973,
                                    0.6411380171775818,
                                    float("-inf"),
                                    1.029868721961975,
                                    0.7100352644920349,
                                    0.9764696955680847,
                                    0.9357074499130249,
                                ],
                            ),
                            (
                                "accuracy",
                                [
                                    0.6875,
                                    0.6875,
                                    0.6875,
                                    0.625,
                                    0.3125,
                                    0.3125,
                                    0.6875,
                                    0.6875,
                                    0.6875,
                                ],
                            ),
                        ]
                    ),
                ),
                (
                    "combined",
                    {
                        "accuracy": [
                            0.6875,
                            0.6875,
                            0.6875,
                            0.625,
                            0.3125,
                            0.3125,
                            0.6875,
                            0.6875,
                            0.6875,
                        ],
                        "loss": [
                            4.156894207000732,
                            3.1449267864227295,
                            1.6688027381896973,
                            0.6411380171775818,
                            2.0590686798095703,
                            1.029868721961975,
                            0.7100352644920349,
                            0.9764696955680847,
                            0.9357074499130249,
                        ],
                    },
                ),
            ]
        ),
        "misc": float("inf"),
    }

    pytest.raises(ValueError, json.dumps, dict_with_infty, allow_nan=False)
    json.dumps(
        utils.renormalize_floats(dict_with_infty, utils.float_dict), allow_nan=False
    )
    return


def test_parse_feature_set_name():
    test_str = "projects/ingesttest/featureSets/tweetsnowflake"
    resp = utils.parse_feature_set_name(test_str)
    assert "projects" in resp, "projects not found"
    assert "featureSets" in resp, "featureSets not found"

    test_str = "projects/ingesttest/featureSets/tweetsnowflake"
    resp = utils.parse_feature_set_name(test_str)
    assert "projects" in resp, "projects not found"
    assert "featureSets" in resp, "featureSets not found"


def test_generate_field_mask_paths():
    obj = {
        "a": 1,
        "b": {"c": {"d": 2}},
        "c": {},
        "d": "a",
    }
    paths = utils.generate_field_mask_paths(obj)

    assert "a" in paths
    assert "b.c.d" in paths
    assert "c" in paths
    assert "d" in paths


if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
