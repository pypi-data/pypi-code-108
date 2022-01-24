#! /usr/bin/env python3
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
"""Show a small sample of images and associated activation maps images.

The following will open a project, get the first model id where the feature
name matches, and then get a list of the activation maps. Then it will
display a few of the images and the associated images with overlay in the
GUI.

The parameters may be adjusted to use your project name, feature name, and
the number of images to display.
"""
import io

import PIL.Image

from datarobot.models import Project
from datarobot.models.visualai import ImageActivationMap


def display_images(project_name, feature_name, max_images):
    project = Project.list(search_params={"project_name": project_name})[0]
    model_id = next(
        mid for mid, name in ImageActivationMap.models(project.id) if name == feature_name
    )
    for amap in ImageActivationMap.list(project.id, model_id, feature_name)[:max_images]:
        with io.BytesIO(amap.image.image_bytes) as bio, PIL.Image.open(bio) as img:
            img.show()
        with io.BytesIO(amap.overlay_image.image_bytes) as bio, PIL.Image.open(bio) as img:
            img.show()


if __name__ == "__main__":
    project_name = "dataset_2k.zip"
    feature_name = "image"
    max_images = 2
    display_images(project_name, feature_name, max_images)
