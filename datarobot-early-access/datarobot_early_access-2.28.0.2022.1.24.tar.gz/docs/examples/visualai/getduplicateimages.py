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
"""Show a small sample of duplicate images in a project.

The following will open a project, get the first model id where the
feature name matches, and then display a few of the duplicate images
in the GUI.
"""
import io

import PIL.Image

from datarobot.models import Project
from datarobot.models.visualai import DuplicateImage


def display_images(project_name, max_images):
    project = Project.list(search_params={"project_name": project_name})[0]
    for image in DuplicateImage.list(project.id, "image")[:max_images]:
        with io.BytesIO(image.image_bytes) as bio, PIL.Image.open(bio) as img:
            img.show()


if __name__ == "__main__":
    project_name = "dataset_2k.zip"
    max_images = 2
    display_images(project_name, max_images)
