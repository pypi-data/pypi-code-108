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
import json

import pytest
import responses
from six.moves.urllib.parse import urljoin

from datarobot import errors
from datarobot.models.visualai.augmentation import (
    ImageAugmentationList,
    ImageAugmentationOptions,
    ImageAugmentationSample,
)
from datarobot.utils import from_api


@responses.activate
def test_augmentation_options(visualai_aug_options, augmentation_options_url, aug_pid):
    responses.add(
        responses.GET,
        augmentation_options_url,
        status=200,
        content_type="application/json",
        body=json.dumps(visualai_aug_options),
    )
    options = ImageAugmentationOptions.get(aug_pid)
    assert isinstance(options, ImageAugmentationOptions)

    data = from_api(visualai_aug_options)
    expected = ImageAugmentationOptions(**data)
    assert options.project_id == expected.project_id
    assert options.id == expected.id


@responses.activate
def test_augmentation_list_get(visualai_augmentation_list, image_augmentations_url):
    aug_id = visualai_augmentation_list["id"]
    aug_list_url = urljoin(image_augmentations_url, str(aug_id) + "/")
    responses.add(
        responses.GET,
        aug_list_url,
        status=200,
        content_type="application/json",
        body=json.dumps(visualai_augmentation_list),
    )
    aug_list = ImageAugmentationList.get(aug_id)
    assert isinstance(aug_list, ImageAugmentationList)
    assert aug_list.id == visualai_augmentation_list["id"]
    assert aug_list.project_id == visualai_augmentation_list["projectId"]


@responses.activate
def test_augmentation_list_create(visualai_augmentation_list, image_augmentations_url):
    aug_id = visualai_augmentation_list["id"]
    responses.add(
        responses.POST,
        image_augmentations_url,
        status=200,
        content_type="application/json",
        body=json.dumps({"augmentationListId": aug_id}),
    )
    aug_list_url = urljoin(image_augmentations_url, str(aug_id) + "/")
    responses.add(
        responses.GET,
        aug_list_url,
        status=200,
        content_type="application/json",
        body=json.dumps(visualai_augmentation_list),
    )

    data = from_api(visualai_augmentation_list)
    del data["id"]
    name = data.pop("name")
    pid = data.pop("project_id")
    new_aug_list = ImageAugmentationList.create(name, pid, **data)
    assert isinstance(new_aug_list, ImageAugmentationList)


@responses.activate
def test_augmentation_sample_compute(
    visualai_augmentation_list, augmentation_samples_url, status_url, status_id
):
    responses.add(
        responses.POST,
        augmentation_samples_url,
        content_type="application/json",
        body=json.dumps({"status_id": status_id}),
        status=202,
        adding_headers={"Location": status_url},
    )

    data = from_api(visualai_augmentation_list)
    control_list = ImageAugmentationList(**data)
    ret_status_url = ImageAugmentationSample.compute(control_list, 4)
    assert ret_status_url == status_url


def verify_sample(aug_samples, expected_dict):
    assert len(aug_samples) == 1
    assert aug_samples[0].image_id == expected_dict["imageId"]
    assert aug_samples[0].height == expected_dict["height"]
    assert aug_samples[0].width == expected_dict["width"]
    assert aug_samples[0].original_image_id == expected_dict["originalImageId"]


@responses.activate
def test_augmentation_sample_retrieve(augmentation_samples_url, samples_result):
    sample_url = urljoin(augmentation_samples_url, "5e7e562528513130ab237875/")
    responses.add(responses.GET, sample_url, body=json.dumps(samples_result), status=200)
    ret_samples = ImageAugmentationSample.list("5e7e562528513130ab237875")
    verify_sample(ret_samples, samples_result["data"][0])


@responses.activate
def test_auglist_augmentation_sample_retrieve_using_auglist(
    augmentation_list_samples_url, auglist_id, samples_result
):
    responses.add(
        responses.GET, augmentation_list_samples_url, body=json.dumps(samples_result), status=200
    )
    ret_samples = ImageAugmentationSample.list(auglist_id=auglist_id)
    verify_sample(ret_samples, samples_result["data"][0])


@responses.activate
def test_auglist_retrive_samples(
    visualai_augmentation_list, augmentation_list_samples_url, auglist_id, samples_result
):
    data = from_api(visualai_augmentation_list)
    aug_list = ImageAugmentationList(**data)

    responses.add(
        responses.GET,
        augmentation_list_samples_url,
        status=404,
        content_type="application/json",
        body=json.dumps(""),
    )

    responses.add(
        responses.GET,
        augmentation_list_samples_url,
        status=200,
        content_type="application/json",
        body=json.dumps(samples_result),
    )

    # assert error call
    with pytest.raises(errors.ClientError):
        aug_list.retrieve_samples()
    # assert success call
    ret_samples = aug_list.retrieve_samples()
    verify_sample(ret_samples, samples_result["data"][0])


@responses.activate
def test_augmentation_list_compute_samples(
    visualai_augmentation_list, augmentation_list_samples_url, status_url, status_id, samples_result
):
    responses.add(
        responses.POST,
        augmentation_list_samples_url,
        content_type="application/json",
        body=json.dumps({"status_id": status_id}),
        status=202,
        adding_headers={"Location": status_url},
    )

    # first call - job still running
    responses.add(
        responses.GET,
        status_url,
        content_type="application/json",
        body=json.dumps(
            {
                "status": "RUNNING",
                "message": "",
                "code": 0,
                "created": "2016-07-22T12:00:00.123456Z",
            }
        ),
        status=200,
    )

    # second call - job completed
    responses.add(
        responses.GET,
        status_url,
        content_type="application/json",
        body=json.dumps(
            {
                "status": "COMPLETED",
                "message": "",
                "code": 0,
                "created": "2016-07-22T12:00:00.123456Z",
            }
        ),
        status=200,
    )

    responses.add(
        responses.GET,
        augmentation_list_samples_url,
        content_type="application/json",
        body=json.dumps(samples_result),
        status=200,
    )

    data = from_api(visualai_augmentation_list)
    ret_samples = ImageAugmentationList(**data).compute_samples()
    verify_sample(ret_samples, samples_result["data"][0])
