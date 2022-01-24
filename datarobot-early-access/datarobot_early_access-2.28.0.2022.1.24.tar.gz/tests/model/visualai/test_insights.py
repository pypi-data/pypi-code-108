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

from datarobot.models.visualai import ImageActivationMap, ImageEmbedding


@responses.activate
def test_image_embeddings(
    visualai_embeddings,
    visualai_embeddings_url,
    project_server_data,
    project_url,
    project_id,
    model_id,
):
    responses.add(
        responses.GET,
        project_url,
        status=200,
        content_type="application/json",
        body=json.dumps(project_server_data),
    )
    responses.add(
        responses.GET,
        visualai_embeddings_url,
        status=200,
        content_type="application/json",
        body=json.dumps(visualai_embeddings),
    )
    img0, img1 = ImageEmbedding.list(project_id, model_id, "image")
    assert isinstance(img0, ImageEmbedding)
    assert img0.image.id == visualai_embeddings.get("embeddings")[0].get("imageId")
    assert img0.project_id == project_id
    assert img0.image.project_id == project_id
    assert img0.model_id == model_id
    assert img0.feature_name == "image"
    assert img0.position_x == visualai_embeddings.get("embeddings")[0].get("positionX")
    assert img0.position_y == visualai_embeddings.get("embeddings")[0].get("positionY")
    assert img0.actual_target_value == visualai_embeddings.get("embeddings")[0].get(
        "actualTargetValue"
    )
    assert isinstance(img1, ImageEmbedding)
    assert img1.image.id == visualai_embeddings.get("embeddings")[1].get("imageId")
    assert img1.project_id == project_id
    assert img1.image.project_id == project_id
    assert img1.model_id == model_id
    assert img1.feature_name == "image"
    assert img1.position_x == visualai_embeddings.get("embeddings")[1].get("positionX")
    assert img1.position_y == visualai_embeddings.get("embeddings")[1].get("positionY")
    assert img1.actual_target_value == visualai_embeddings.get("embeddings")[1].get(
        "actualTargetValue"
    )


@responses.activate
def test_image_activationmpas(
    visualai_activationmaps,
    visualai_activationmaps_url,
    project_server_data,
    project_url,
    project_id,
    model_id,
):
    responses.add(
        responses.GET,
        project_url,
        status=200,
        content_type="application/json",
        body=json.dumps(project_server_data),
    )
    responses.add(
        responses.GET,
        visualai_activationmaps_url,
        status=200,
        content_type="application/json",
        body=json.dumps(visualai_activationmaps),
    )
    img0, img1 = ImageActivationMap.list(project_id, model_id, "image")
    assert isinstance(img0, ImageActivationMap)
    assert img0.image.id == visualai_activationmaps.get("activationMaps")[0].get("imageId")
    assert img0.overlay_image.id == visualai_activationmaps.get("activationMaps")[0].get(
        "overlayImageId"
    )
    assert img0.project_id == project_id
    assert img0.image.project_id == project_id
    assert img0.overlay_image.project_id == project_id
    assert img0.model_id == model_id
    assert img0.feature_name == "image"
    assert img0.actual_target_value == visualai_activationmaps.get("activationMaps")[0].get(
        "actualTargetValue"
    )
    assert img0.predicted_target_value == visualai_activationmaps.get("activationMaps")[0].get(
        "predictedTargetValue"
    )
    assert img0.activation_values == visualai_activationmaps.get("activationMaps")[0].get(
        "activationValues"
    )
    assert isinstance(img1, ImageActivationMap)
    assert img1.image.id == visualai_activationmaps.get("activationMaps")[1].get("imageId")
    assert img1.overlay_image.id == visualai_activationmaps.get("activationMaps")[1].get("imageId")
    assert img1.project_id == project_id
    assert img1.image.project_id == project_id
    assert img1.overlay_image.project_id == project_id
    assert img1.model_id == model_id
    assert img1.feature_name == "image"
    assert img1.actual_target_value == visualai_activationmaps.get("activationMaps")[1].get(
        "actualTargetValue"
    )
    assert img1.predicted_target_value == visualai_activationmaps.get("activationMaps")[1].get(
        "predictedTargetValue"
    )
    assert img1.activation_values == visualai_activationmaps.get("activationMaps")[1].get(
        "activationValues"
    )
