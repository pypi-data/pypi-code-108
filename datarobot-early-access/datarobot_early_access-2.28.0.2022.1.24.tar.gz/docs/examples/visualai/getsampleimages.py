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
"""Show sample images for a project.

The following will open a project, get a list of sample images, and
then display a few images to the GUI.

The parameters may be adjusted to use your project name, feature name, and
the number of images to display.
"""
import io

import PIL.Image

from datarobot.models import Project
from datarobot.models.visualai import SampleImage


def display_images(project_name, feature_name, max_images):
    project = Project.list(search_params={"project_name": project_name})[0]
    for sample in SampleImage.list(project.id, feature_name)[:max_images]:
        with io.BytesIO(sample.image.image_bytes) as bio, PIL.Image.open(bio) as img:
            img.show()


if __name__ == "__main__":
    project_name = "dataset_2k.zip"
    feature_name = "image"
    max_images = 2
    display_images(project_name, feature_name, max_images)
