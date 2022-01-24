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
"""Display a single image in a project.

The image id must be known before using this code. That may be obtained
through getting sample iamges, activation maps, or embeddings. See
examples in the same directory as this file to see how that is done.
"""
import io

import PIL.Image

from datarobot.models import Project
from datarobot.models.visualai import Image

image_id = "5e7e562528513130ab237875"
project = Project.list(search_params={"project_name": "dataset_2k.zip"})[0]
image = Image.get(project.id, image_id)
print(image)
with io.BytesIO(image.image_bytes) as bio, PIL.Image.open(bio) as img:
    img.show()
