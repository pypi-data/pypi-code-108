#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import itertools
import json
import random

import pytest
from six.moves.urllib.parse import urljoin

from datarobot import TARGET_TYPE


@pytest.fixture
def auglist_id():
    return "5eaafb57fcdb565e4d778f29"


@pytest.fixture
def visualai_url(project_url):
    return urljoin(project_url, "images/")


@pytest.fixture
def visualai_image_url(visualai_url, visualai_image_id):
    return urljoin(visualai_url, visualai_image_id + "/")


@pytest.fixture
def image_augmentations_url(unittest_endpoint):
    return urljoin(unittest_endpoint, "imageAugmentationLists/")


@pytest.fixture
def augmentation_list_samples_url(unittest_endpoint, auglist_id):
    return urljoin(unittest_endpoint, "imageAugmentationLists/{}/samples/".format(auglist_id))


@pytest.fixture
def augmentation_samples_url(unittest_endpoint):
    return urljoin(unittest_endpoint, "imageAugmentationSamples/")


@pytest.fixture
def status_id():
    return "91e49da5-c548-4a97-8a7d-bde7710a7f4f"


@pytest.fixture
def aug_pid():
    return "5e7e562528513130ab237875"


@pytest.fixture
def augmentation_options_url(unittest_endpoint, aug_pid):
    return urljoin(unittest_endpoint, "imageAugmentationOptions/{}".format(aug_pid))


@pytest.fixture
def status_url(unittest_endpoint, status_id):
    return unittest_endpoint + "/status/{}/".format(status_id)


@pytest.fixture
def visualai_image_id():
    return "5e7e562528513130ab237875"


@pytest.fixture
def visualai_embeddings_url(model_url):
    return urljoin(model_url, "imageEmbeddings/")


@pytest.fixture
def visualai_activationmaps_url(model_url):
    return urljoin(model_url, "imageActivationMaps/")


@pytest.fixture(
    params=itertools.product(
        ["aim", "eda", "eda2", "empty", "modeling"],
        [
            TARGET_TYPE.BINARY,
            TARGET_TYPE.MULTICLASS,
            TARGET_TYPE.MULTILABEL,
            TARGET_TYPE.REGRESSION,
        ],
    )
)
def visualai_project(request, project_with_target_json):
    ret = json.loads(project_with_target_json)
    stage, target_type = request.param
    ret["stage"] = stage
    ret["targetType"] = target_type
    return ret


@pytest.fixture
def visualai_image():
    return {"width": 256, "height": 256, "imageId": "5e7e562528513130ab237875"}


@pytest.fixture
def visualai_image_file():
    return bytes((random.randint(0, 255) for i in range(32)))


@pytest.fixture
def visualai_sample(visualai_project):
    target_type_to_eda2_sample_mapping = {
        TARGET_TYPE.BINARY: [
            {
                "imageId": "5e7e562528513130ab237875",
                "height": 256,
                "width": 256,
                "targetValue": "fake",
            },
            {
                "imageId": "5e7e562528513130ab237874",
                "height": 256,
                "width": 256,
                "targetValue": "real",
            },
        ],
        TARGET_TYPE.MULTICLASS: [
            {
                "imageId": "5e7e562528513130ab237875",
                "height": 256,
                "width": 256,
                "targetValue": "fake",
            },
            {
                "imageId": "5e7e562528513130ab237874",
                "height": 256,
                "width": 256,
                "targetValue": "real",
            },
        ],
        TARGET_TYPE.MULTILABEL: [
            {
                "imageId": "5e7e562528513130ab237875",
                "height": 256,
                "width": 256,
                "targetValue": ["foo", "bar"],
            },
            {
                "imageId": "5e7e562528513130ab237874",
                "height": 256,
                "width": 256,
                "targetValue": [],
            },
        ],
        TARGET_TYPE.REGRESSION: [
            {
                "imageId": "5e7e562528513130ab237875",
                "height": 256,
                "width": 256,
                "targetValue": 2.0,
            },
            {"imageId": "5e7e562528513130ab237874", "height": 256, "width": 256, "targetValue": 1},
        ],
    }

    if visualai_project["stage"] in ["eda2", "modeling"]:
        return {
            "next": None,
            "data": target_type_to_eda2_sample_mapping[visualai_project["targetType"]],
            "previous": None,
        }

    else:
        return {
            "next": None,
            "data": [
                {"imageId": "5e7e562528513130ab237875", "height": 256, "width": 256},
                {"imageId": "5e7e562528513130ab237874", "height": 256, "width": 256},
            ],
            "previous": None,
        }


@pytest.fixture
def visualai_duplicate():
    return {
        "count": 0,
        "next": None,
        "data": [
            {"imageId": "5e7e562528513130ab237875", "rowCount": 3},
            {"imageId": "5e7e562528513130ab237874", "rowCount": 7},
        ],
        "previous": None,
    }


@pytest.fixture
def visualai_embeddings():
    return {
        "targetValues": ["fake", "real"],
        "targetBins": None,
        "embeddings": [
            {
                "imageId": "5e7e562b28513130ab23792e",
                "positionX": 0.5935041904449463,
                "positionY": 0.6990952491760254,
                "actualTargetValue": "fake",
            },
            {
                "imageId": "5e7e563528513130ab237a6d",
                "positionX": 0.708981454372406,
                "positionY": 0.6228484511375427,
                "actualTargetValue": "fake",
            },
        ],
    }


@pytest.fixture
def visualai_activationmaps():
    return {
        "activationMapWidth": 56,
        "activationMaps": [
            {
                "imageId": "5eaafb57fcdb565e4d778f29",
                "overlayImageId": "5e7e563528513130ab237a6d",
                "predictedTargetValue": "fake",
                "featureName": "image",
                "actualTargetValue": "fake",
                "imageHeight": 256,
                "imageWidth": 256,
                "activationValues": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            },
            {
                "imageId": "5eaafb58fcdb565e2f7790d0",
                "predictedTargetValue": "real",
                "featureName": "image",
                "actualTargetValue": "real",
                "imageHeight": 256,
                "imageWidth": 256,
                "activationValues": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            },
        ],
        "activationMapHeight": 56,
        "targetBins": None,
        "targetValues": ["fake", "real"],
    }


@pytest.fixture
def visualai_augmentation_list(auglist_id):
    a_param = {"name": "pixels", "currentValue": 10}
    b_param = {"name": "pixels", "currentValue": 12.3}
    trans = {"name": "blur", "params": [a_param]}
    trans2 = {"name": "scale", "params": [b_param]}
    return {
        "id": auglist_id,
        "name": "my aug list",
        "projectId": "5eaafb57fcdb565e4d778f29",
        "featureName": "image",
        "inUse": False,
        "initialList": True,
        "transformationProbability": 0.5,
        "numberOfNewImages": 1,
        "transformations": [trans, trans2],
    }


@pytest.fixture
def visualai_aug_options():
    a_param = {"name": "pixels", "currentValue": 10}
    b_param = {"name": "pixels", "currentValue": 12.3}
    trans = {"name": "blur", "params": [a_param]}
    trans2 = {"name": "scale", "params": [b_param]}
    return {
        "id": "5eaafb57fcdb565e4d778f29",
        "name": "my aug list",
        "projectId": "5eaafb57fcdb565e4d778f29",
        "minTransformationProbability": 0.1,
        "maxTransformationProbability": 1.0,
        "currentTransformationProbability": 0.5,
        "minNumberOfNewImages": 1,
        "currentNumberOfNewImages": 100,
        "maxNumberOfNewImages": 1796,
        "transformations": [trans, trans2],
    }


@pytest.fixture
def samples_result():
    a_sample = {
        "imageId": "1234",
        "width": 256,
        "height": 256,
        "originalImageId": "5678",
        "project_id": "1234",
    }
    return {"totalCount": 1, "next": None, "previous": None, "data": [a_sample]}
