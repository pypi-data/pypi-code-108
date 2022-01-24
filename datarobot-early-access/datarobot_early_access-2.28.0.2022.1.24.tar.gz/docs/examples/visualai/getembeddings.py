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
"""Show image embedding vectors.

The following will open a project, get the first model id where the feature
name matches, and then print out the image id and the embedding vector.
"""
from datarobot.models import Project
from datarobot.models.visualai import ImageEmbedding


def print_vectors(project_name, feature_name):
    project = Project.list(search_params={"project_name": project_name})[0]
    model_id = next(mid for mid, name in ImageEmbedding.models(project.id) if name == feature_name)
    for embed in ImageEmbedding.list(project.id, model_id, feature_name):
        print("{0} [{1:1.6f}, {2:1.6f}]".format(embed.image.id, embed.position_x, embed.position_y))


if __name__ == "__main__":
    project_name = "dataset_2k.zip"
    feature_name = "image"
    print_vectors(project_name, feature_name)
