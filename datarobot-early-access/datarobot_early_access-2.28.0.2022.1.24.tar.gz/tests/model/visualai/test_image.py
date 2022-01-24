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

import responses
from six.moves.urllib.parse import urljoin

from datarobot.models.visualai import DuplicateImage, Image, SampleImage


@responses.activate
def test_get_image(visualai_image_url, visualai_image_id, visualai_image, project_id):
    responses.add(
        responses.GET,
        visualai_image_url,
        status=200,
        content_type="application/json",
        body=json.dumps(visualai_image),
    )
    image = Image.get(project_id, visualai_image_id)
    assert isinstance(image, Image)
    assert image.id == visualai_image["imageId"]
    assert image.project_id == project_id
    assert image.width == visualai_image["width"]
    assert image.height == visualai_image["height"]


@responses.activate
def test_get_image_bytes(visualai_image_url, visualai_image_id, visualai_image_file, project_id):
    responses.add(
        responses.GET,
        urljoin(visualai_image_url, "file/"),
        status=200,
        content_type="image/jpeg",
        body=visualai_image_file,
    )
    image = Image(project_id=project_id, image_id=visualai_image_id, width=256, height=256)
    assert image.image_type == "image/jpeg"
    assert image.image_bytes == visualai_image_file


@responses.activate
def test_get_sample_images(visualai_project, visualai_sample, project_url, project_id):
    responses.add(
        responses.GET,
        project_url,
        status=200,
        content_type="application/json",
        body=json.dumps(visualai_project),
    )
    stage_url = {
        "aim": "imageSamples/?featureName=image",
        "eda": "imageSamples/?featureName=image",
        "eda2": "images/?featureName=image",
        "empty": "imageSamples/?featureName=image",
        "modeling": "images/?featureName=image",
    }[visualai_project["stage"]]
    responses.add(
        responses.GET,
        urljoin(project_url, stage_url),
        status=200,
        content_type="application/json",
        body=json.dumps(visualai_sample),
    )
    img0, img1 = SampleImage.list(project_id, "image")
    assert isinstance(img0, SampleImage)
    assert img0.image.id == visualai_sample.get("data")[0].get("imageId")
    assert img0.project_id == project_id
    assert img0.target_value == visualai_sample.get("data")[0].get("targetValue")
    assert isinstance(img1, SampleImage)
    assert img1.image.id == visualai_sample.get("data")[1].get("imageId")
    assert img1.project_id == project_id
    assert img1.target_value == visualai_sample.get("data")[1].get("targetValue")


@responses.activate
def test_get_duplicate_images(visualai_project, visualai_duplicate, project_url, project_id):
    responses.add(
        responses.GET,
        project_url,
        status=200,
        content_type="application/json",
        body=json.dumps(visualai_project),
    )
    responses.add(
        responses.GET,
        urljoin(project_url, "duplicateImages/image/"),
        status=200,
        content_type="application/json",
        body=json.dumps(visualai_duplicate),
    )
    img0, img1 = DuplicateImage.list(project_id, "image")
    assert isinstance(img0, DuplicateImage)
    assert img0.image.id == visualai_duplicate.get("data")[0].get("imageId")
    assert img0.project_id == project_id
    assert img0.count == visualai_duplicate.get("data")[0].get("rowCount")
    assert isinstance(img1, DuplicateImage)
    assert img1.image.id == visualai_duplicate.get("data")[1].get("imageId")
    assert img1.project_id == project_id
    assert img1.count == visualai_duplicate.get("data")[1].get("rowCount")
